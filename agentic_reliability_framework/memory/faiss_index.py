# Standard imports
import threading
from typing import Tuple, Optional
import numpy as np

# FAISS import
import faiss  # fixed import

# Project imports
# from agentic_reliability_framework.models import ReliabilityEvent


class ProductionFAISSIndex:
    """Existing FAISS index wrapper"""

    def __init__(self, dim: int) -> None:
        self.index: faiss.IndexFlatL2 = faiss.IndexFlatL2(dim)
        self._lock: threading.Lock = threading.Lock()

    def add(self, vector: np.ndarray) -> int:
        """Add a vector to the FAISS index and return the ID of the last inserted vector."""
        with self._lock:
            if len(vector.shape) == 1:
                vector = vector.reshape(1, -1)
            self.index.add(vector)
            return int(self.index.ntotal - 1)

    def get_count(self) -> int:
        """Return the total number of vectors in the index."""
        with self._lock:
            # Access ntotal directly - it's already an integer
            return self.index.ntotal

    def add_async(self, vector: np.ndarray) -> int:
        """Async version of add (if needed for RAG graph compatibility)."""
        # Simply call the synchronous version for now
        # This maintains compatibility with rag_graph.py expectations
        return self.add(vector)


class EnhancedFAISSIndex(ProductionFAISSIndex):
    """Adds thread-safe search capability"""

    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """Return top-k nearest neighbors and distances for the query vector."""
        with self._lock:
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            distances, indices = self.index.search(query_vector, k)
            return distances[0], indices[0]


# Factory function for compatibility with lazy.py
def create_faiss_index(dim: int) -> ProductionFAISSIndex:
    """Create a new FAISS index instance.
    
    Args:
        dim: Dimensionality of vectors
        
    Returns:
        ProductionFAISSIndex instance
    """
    return ProductionFAISSIndex(dim)
