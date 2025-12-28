"""
ARF Core Module - OSS Edition
Production-grade multi-agent AI for reliability monitoring
OSS Edition: Advisory mode only, Apache 2.0 Licensed

IMPORTANT: This module ONLY exports OSS components - no circular imports
"""

__version__ = "3.3.4"
__all__ = [
    "HealingIntent",
    "HealingIntentSerializer",
    "create_rollback_intent",
    "create_restart_intent",
    "create_scale_out_intent",
    "OSSMCPClient",
    "create_mcp_client",
    "OSS_EDITION",
    "OSS_LICENSE",
    "EXECUTION_ALLOWED",
    "MCP_MODES_ALLOWED",
    "OSSBoundaryError",
]

# ============================================================================
# DIRECT IMPORTS - RESOLVE CIRCULAR DEPENDENCIES
# ============================================================================

# Import from absolute paths to avoid circular imports
from agentic_reliability_framework.arf_core.models.healing_intent import (
    HealingIntent,
    HealingIntentSerializer,
    create_rollback_intent,
    create_restart_intent,
    create_scale_out_intent,
)

from agentic_reliability_framework.arf_core.constants import (
    OSS_EDITION,
    OSS_LICENSE,
    EXECUTION_ALLOWED,
    MCP_MODES_ALLOWED,
    OSSBoundaryError,
)

# Lazy load OSSMCPClient to avoid circular dependencies
_oss_mcp_client = None

def __getattr__(name):
    """Lazy loading for OSSMCPClient"""
    if name == "OSSMCPClient":
        from agentic_reliability_framework.arf_core.engine.simple_mcp_client import OSSMCPClient
        return OSSMCPClient
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def create_mcp_client(config=None):
    """Factory function for OSSMCPClient"""
    from agentic_reliability_framework.arf_core.engine.simple_mcp_client import OSSMCPClient
    return OSSMCPClient(config=config)

# Export OSSMCPClient for static analysis
try:
    from agentic_reliability_framework.arf_core.engine.simple_mcp_client import OSSMCPClient
except ImportError:
    OSSMCPClient = None

# ============================================================================
# MODULE METADATA
# ============================================================================

ENTERPRISE_UPGRADE_URL = "https://arf.dev/enterprise"
