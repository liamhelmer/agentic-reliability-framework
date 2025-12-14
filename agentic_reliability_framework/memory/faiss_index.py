# === FAISS Integration ===
class ProductionFAISSIndex:
    """Production-safe FAISS index with single-writer pattern"""
    
    def __init__(self, index, texts: List[str]):
        self.index = index
        self.texts = texts
        self._lock = threading.RLock()
        
        self._shutdown = threading.Event()
        
        # Single writer thread
        self._write_queue: Queue = Queue()
        self._writer_thread = threading.Thread(
            target=self._writer_loop,
            daemon=True,
            name="FAISSWriter"
        )
        self._writer_thread.start()
        
        self._encoder_pool = ProcessPoolExecutor(max_workers=2)
        
        logger.info(
            f"Initialized ProductionFAISSIndex with {len(texts)} vectors"
        )
    
    def add_async(self, vector: np.ndarray, text: str) -> None:
        """Add vector and text asynchronously"""
        self._write_queue.put((vector, text))
        logger.debug(f"Queued vector for indexing: {text[:50]}...")
    
    def _writer_loop(self) -> None:
        """Single writer thread - processes queue in batches"""
        batch = []
        last_save = datetime.datetime.now()
        save_interval = datetime.timedelta(
            seconds=Constants.FAISS_SAVE_INTERVAL_SECONDS
        )
        
        while not self._shutdown.is_set():
            try:
                import queue
                try:
                    item = self._write_queue.get(timeout=1.0)
                    batch.append(item)
                except queue.Empty:
                    pass
                
                if len(batch) >= Constants.FAISS_BATCH_SIZE or \
                   (batch and datetime.datetime.now() - last_save > save_interval):
                    self._flush_batch(batch)
                    batch = []
                    
                    if datetime.datetime.now() - last_save > save_interval:
                        self._save_atomic()
                        last_save = datetime.datetime.now()
                        
            except Exception as e:
                logger.error(f"Writer loop error: {e}", exc_info=True)
    
    def _flush_batch(self, batch: List[Tuple[np.ndarray, str]]) -> None:
        """Flush batch to FAISS index"""
        if not batch:
            return
        
        try:
            vectors = np.vstack([v for v, _ in batch])
            texts = [t for _, t in batch]
            
            self.index.add(vectors)
            
            with self._lock:
                self.texts.extend(texts)
            
            logger.info(f"Flushed batch of {len(batch)} vectors to FAISS index")
            
        except Exception as e:
            logger.error(f"Error flushing batch: {e}", exc_info=True)
    
    def _save_atomic(self) -> None:
        """Atomic save with fsync for durability"""
        try:
            import faiss
            
            with tempfile.NamedTemporaryFile(
                mode='wb',
                delete=False,
                dir=os.path.dirname(config.INDEX_FILE),
                prefix='index_',
                suffix='.tmp'
            ) as tmp:
                temp_path = tmp.name
            
            faiss.write_index(self.index, temp_path)
            
            with open(temp_path, 'r+b') as f:
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(temp_path, config.INDEX_FILE)
            
            with self._lock:
                texts_copy = self.texts.copy()
            
            with atomicwrites.atomic_write(
                config.TEXTS_FILE,
                mode='w',
                overwrite=True
            ) as f:
                json.dump(texts_copy, f)
            
            logger.info(
                f"Atomically saved FAISS index with {len(texts_copy)} vectors"
            )
            
        except Exception as e:
            logger.error(f"Error saving index: {e}", exc_info=True)
    
    def get_count(self) -> int:
        """Get total count of vectors"""
        with self._lock:
            return len(self.texts) + self._write_queue.qsize()
    
    def force_save(self) -> None:
        """Force immediate save of pending vectors"""
        logger.info("Forcing FAISS index save...")
        
        timeout = 10.0
        start = datetime.datetime.now()
        
        while not self._write_queue.empty():
            if (datetime.datetime.now() - start).total_seconds() > timeout:
                logger.warning("Force save timeout - queue not empty")
                break
            import time
            time.sleep(0.1)
        
        self._save_atomic()
    
    def shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Shutting down FAISS index...")
        self._shutdown.set()
        self.force_save()
        self._writer_thread.join(timeout=5.0)
        self._encoder_pool.shutdown(wait=True)


# === FAISS & Embeddings Setup ===
model = None

def get_model():
    """Lazy-load SentenceTransformer model on first use"""
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading SentenceTransformer model...")
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Model loaded on demand")
    return model

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    
    if os.path.exists(config.INDEX_FILE):
        logger.info(f"Loading existing FAISS index from {config.INDEX_FILE}")
        index = faiss.read_index(config.INDEX_FILE)
        
        if index.d != Constants.VECTOR_DIM:
            logger.warning(
                f"Index dimension mismatch: {index.d} != {Constants.VECTOR_DIM}. "
                f"Creating new index."
            )
            index = faiss.IndexFlatL2(Constants.VECTOR_DIM)
            incident_texts = []
        else:
            with open(config.TEXTS_FILE, "r") as f:
                incident_texts = json.load(f)
            logger.info(f"Loaded {len(incident_texts)} incident texts")
    else:
        logger.info("Creating new FAISS index")
        index = faiss.IndexFlatL2(Constants.VECTOR_DIM)
        incident_texts = []
    
    thread_safe_index = ProductionFAISSIndex(index, incident_texts)
    
except ImportError as e:
    logger.warning(f"FAISS or SentenceTransformers not available: {e}")
    index = None
    incident_texts = []
    model = None
    thread_safe_index = None
except Exception as e:
    logger.error(f"Error initializing FAISS: {e}", exc_info=True)
    index = None
    incident_texts = []
    model = None
    thread_safe_index = None
