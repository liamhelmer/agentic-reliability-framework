"""
Simple lazy loading for ARF - No circular dependencies!
Pythonic improvements with type safety
"""

import threading
import logging
from typing import Callable, Optional, Dict, Any, TypeVar
from contextlib import suppress

from .engine.interfaces import ReliabilityEngineProtocol, MCPProtocol, RAGProtocol

logger = logging.getLogger(__name__)

T = TypeVar('T')


class LazyLoader:
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


# ========== MODULE-LEVEL IMPORTS ==========

def _load_rag_graph() -> Optional[RAGProtocol]:
    """Create RAGGraphMemory for v3 features with graceful fallback"""
    with suppress(ImportError, Exception):
        from .memory.rag_graph import RAGGraphMemory
        from ..config import config
        
        # Get FAISS index first (could return None)
        faiss_index = _load_faiss_index_safe()
        
        if faiss_index and config.rag_enabled:
            # Create RAG graph with the FAISS index
            rag_graph = RAGGraphMemory(faiss_index)
            logger.info("Initialized RAGGraphMemory for v3 features")
            return rag_graph
        else:
            logger.debug("RAG disabled or FAISS index not available")
    
    return None


def _load_mcp_server() -> Optional[MCPProtocol]:
    """Create MCP Server for v3 features with graceful fallback"""
    with suppress(ImportError, Exception):
        from .mcp_server import MCPServer, MCPMode
        from ..config import config
        
        if config.mcp_enabled:
            mcp_mode = MCPMode(config.mcp_mode)
            mcp_server = MCPServer(mode=mcp_mode)
            logger.info(f"Initialized MCPServer in {mcp_mode.value} mode")
            return mcp_server
        else:
            logger.debug("MCP disabled")
    
    return None


def _load_engine() -> Optional[ReliabilityEngineProtocol]:
    """Load the reliability engine without circular imports"""
    with suppress(ImportError, Exception):
        # Use a factory pattern to avoid direct import
        from .engine_factory import create_engine
        logger.info("Loading reliability engine via factory")
        return create_engine()
    
    # Fallback to direct import only if factory fails
    with suppress(ImportError, Exception):
        from .app import EnhancedReliabilityEngine
        logger.info("Loading EnhancedReliabilityEngine directly")
        return EnhancedReliabilityEngine()
    
    logger.error("Failed to load reliability engine")
    return None


def _load_agents() -> Optional[Any]:
    """Load agent orchestrator"""
    with suppress(ImportError, Exception):
        from .app import OrchestrationManager
        logger.info("Loading OrchestrationManager")
        return OrchestrationManager()
    
    logger.error("Failed to load agents")
    return None


def _load_faiss_index_safe() -> Optional[Any]:
    """Load FAISS index with safe error handling"""
    with suppress(ImportError, Exception):
        from .memory.faiss_index import create_faiss_index
        logger.info("Loading FAISS index")
        return create_faiss_index()
    
    logger.warning("FAISS index not available")
    return None


def _load_business_metrics() -> Optional[Any]:
    """Load business metrics tracker"""
    with suppress(ImportError, Exception):
        from .engine.business import BusinessMetricsTracker
        logger.info("Loading BusinessMetricsTracker")
        return BusinessMetricsTracker()
    
    logger.warning("Business metrics tracker not available")
    return None


# ========== CREATE LAZY LOADERS ==========

rag_graph_loader = LazyLoader(_load_rag_graph)
mcp_server_loader = LazyLoader(_load_mcp_server)
engine_loader = LazyLoader(_load_engine)
agents_loader = LazyLoader(_load_agents)
faiss_index_loader = LazyLoader(_load_faiss_index_safe)
business_metrics_loader = LazyLoader(_load_business_metrics)


# ========== PUBLIC API ==========

def get_rag_graph() -> Optional[RAGProtocol]:
    """
    Get or create RAGGraphMemory (v3 feature)
    
    Returns:
        RAGGraphMemory instance or None if not available
    """
    return rag_graph_loader()


def get_mcp_server() -> Optional[MCPProtocol]:
    """
    Get or create MCPServer (v3 feature)
    
    Returns:
        MCPServer instance or None if not available
    """
    return mcp_server_loader()


def get_engine() -> Optional[ReliabilityEngineProtocol]:
    """
    Get or create reliability engine
    
    Returns:
        EnhancedReliabilityEngine instance or None if not available
    """
    return engine_loader()


def get_agents() -> Optional[Any]:
    """
    Get or create agent orchestrator
    
    Returns:
        OrchestrationManager instance or None if not available
    """
    return agents_loader()


def get_faiss_index() -> Optional[Any]:
    """
    Get or create FAISS index
    
    Returns:
        ProductionFAISSIndex instance or None if not available
    """
    return faiss_index_loader()


def get_business_metrics() -> Optional[Any]:
    """
    Get or create business metrics tracker
    
    Returns:
        BusinessMetricsTracker instance or None if not available
    """
    return business_metrics_loader()


def enhanced_engine() -> Optional[ReliabilityEngineProtocol]:
    """
    Get enhanced reliability engine (alias for get_engine)
    
    Returns:
        EnhancedReliabilityEngine instance or None if not available
    """
    return get_engine()


def get_v3_status() -> Dict[str, Any]:
    """Get v3 feature status"""
    from ..config import config
    from .engine_factory import EngineFactory
    
    return {
        "engine_info": EngineFactory.get_engine_info(),
        "rag_available": rag_graph_loader.is_loaded,
        "mcp_available": mcp_server_loader.is_loaded,
        "rag_enabled": config.rag_enabled,
        "mcp_enabled": config.mcp_enabled,
        "learning_enabled": config.learning_enabled,
        "rollout_percentage": config.rollout_percentage,
        "beta_testing": config.beta_testing_enabled,
    }
