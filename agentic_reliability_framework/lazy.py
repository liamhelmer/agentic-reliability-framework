"""
Simple lazy loading for ARF - No circular dependencies!
Pythonic improvements with type safety
"""

# ========== ALL IMPORTS MUST BE HERE AT THE TOP ==========
import logging
import threading
from contextlib import suppress
from typing import Callable, Optional, Dict, Any, TypeVar, Generic, cast, TYPE_CHECKING

logger = logging.getLogger(__name__)

# ========== TYPE CHECKING IMPORTS ==========
# This is NOT an import - it's conditional code that runs during type checking
if TYPE_CHECKING:
    from .memory.rag_graph import RAGGraphMemory
    from .engine.mcp_server import MCPServer
    from .engine.interfaces import ReliabilityEngineProtocol
    from .app import OrchestrationManager
    from .memory.faiss_index import ProductionFAISSIndex
    from .engine.business import BusinessMetricsTracker

# ========== REST OF YOUR CODE STARTS HERE ==========
T = TypeVar('T')

class LazyLoader(Generic[T]):
    """Thread-safe lazy loader with better typing support"""
    
    def __init__(self, loader_func: Callable[[], Optional[T]]) -> None:
        self._loader_func = loader_func
        self._lock = threading.RLock()
        self._instance: Optional[T] = None
    
    def __call__(self) -> Optional[T]:
        """Get or create instance (double-checked locking)"""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._loader_func()
        return self._instance
    
    def reset(self) -> None:
        """Reset instance (for testing)"""
        with self._lock:
            self._instance = None
    
    @property
    def is_loaded(self) -> bool:
        """Check if instance is loaded"""
        return self._instance is not None


# ========== GLOBAL INSTANCES WITH CONCRETE TYPES ==========
# These instances use concrete types for type safety in v3 engine
_rag_graph_instance: Optional['RAGGraphMemory'] = None
_mcp_server_instance: Optional['MCPServer'] = None
_engine_instance: Optional['ReliabilityEngineProtocol'] = None


# ========== TYPE-SAFE LOADER FUNCTIONS ==========
def _load_rag_graph() -> Optional['RAGGraphMemory']:
    """Create RAGGraphMemory for v3 features with graceful fallback"""
    global _rag_graph_instance
    
    if _rag_graph_instance is not None:
        return _rag_graph_instance
    
    with suppress(ImportError, Exception):
        from .memory.rag_graph import RAGGraphMemory
        from .config import config
        
        # Get FAISS index first (could return None)
        faiss_index = _load_faiss_index_safe()
        
        if faiss_index and config.rag_enabled:
            # Create RAG graph with the FAISS index
            _rag_graph_instance = RAGGraphMemory(faiss_index)
            logger.info("Initialized RAGGraphMemory for v3 features")
            return _rag_graph_instance
        else:
            logger.debug("RAG disabled or FAISS index not available")
    
    return None

# [Continue with the rest of your file...]
# Include all your other functions: _load_mcp_server, _load_engine, etc.
# Then the lazy loader instances, public API functions, etc.
