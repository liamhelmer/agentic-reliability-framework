"""
Engine factory for creating v2/v3 engines without circular imports
"""

import logging
from typing import Optional, Dict
from contextlib import suppress

from ..config import config
from .interfaces import ReliabilityEngineProtocol

logger = logging.getLogger(__name__)


def create_engine() -> Optional[ReliabilityEngineProtocol]:
    """
    Factory function to create appropriate reliability engine
    
    Returns:
        v2 or v3 engine based on configuration
    """
    # Check if v3 features should be enabled
    should_use_v3 = (
        config.rag_enabled or 
        config.mcp_enabled or 
        config.learning_enabled or 
        config.rollout_percentage > 0
    )
    
    if should_use_v3:
        with suppress(ImportError, Exception):
            # Try to create v3 engine
            return _create_v3_engine()
    
    # Fallback to v2 engine
    return _create_v2_engine()


def _create_v2_engine() -> ReliabilityEngineProtocol:
    """Create v2 reliability engine"""
    with suppress(ImportError):
        from .reliability import EnhancedReliabilityEngine
        logger.info("Creating v2 reliability engine")
        return EnhancedReliabilityEngine()
    
    # Fallback to basic engine if Enhanced not available
    from .reliability import ReliabilityEngine
    logger.info("Creating basic reliability engine")
    return ReliabilityEngine()


def _create_v3_engine() -> Optional[ReliabilityEngineProtocol]:
    """Create v3 reliability engine with RAG and MCP"""
    try:
        # Import lazily to avoid circular dependencies
        from ..lazy import get_rag_graph, get_mcp_server
        from .v3_reliability import V3ReliabilityEngine
        
        rag_graph = get_rag_graph()
        mcp_server = get_mcp_server()
        
        # Check if we have the required v3 components
        if not (rag_graph and mcp_server):
            logger.warning("v3 components not available, falling back to v2")
            return _create_v2_engine()
        
        logger.info("Creating v3 reliability engine with RAG and MCP")
        return V3ReliabilityEngine(rag_graph=rag_graph, mcp_server=mcp_server)
        
    except ImportError as e:
        logger.warning(f"v3 engine not available: {e}")
        return _create_v2_engine()


class EngineFactory:
    """Engine factory with metadata"""
    
    @staticmethod
    def get_engine() -> Optional[ReliabilityEngineProtocol]:
        """Get engine instance (singleton pattern)"""
        return create_engine()
    
    @staticmethod
    def get_engine_info() -> Dict[str, Any]:
        """Get engine information"""
        from ..lazy import (
            rag_graph_loader, 
            mcp_server_loader, 
            engine_loader
        )
        
        return {
            "engine_loaded": engine_loader.is_loaded,
            "rag_loaded": rag_graph_loader.is_loaded,
            "mcp_loaded": mcp_server_loader.is_loaded,
            "v3_features_enabled": {
                "rag": config.rag_enabled,
                "mcp": config.mcp_enabled,
                "learning": config.learning_enabled,
                "rollout": config.rollout_percentage,
            },
            "engine_type": "v3" if (
                rag_graph_loader.is_loaded and 
                mcp_server_loader.is_loaded and 
                config.rollout_percentage > 0
            ) else "v2",
        }
