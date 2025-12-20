"""
MCP Server Factory - OSS Edition Only
Returns OSSMCPClient with advisory mode only
Maintains backward compatibility while enforcing OSS boundaries
"""

import logging
from typing import Dict, Any, Optional, Union, Type, cast, overload, TYPE_CHECKING

# Handle Literal for different Python versions
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from .mcp_client import OSSMCPClient, create_mcp_client

# Type checking only imports to avoid circular dependencies
if TYPE_CHECKING:
    from ..oss.healing_intent import HealingIntent

logger = logging.getLogger(__name__)

# Type alias for factory returns
MCPInstance = "OSSMCPClient"


def detect_edition() -> str:
    """
    Detect edition - OSS Edition always returns "oss"
    
    OSS EDITION: No enterprise detection, always OSS
    
    Returns:
        Always "oss"
    """
    logger.debug("OSS Edition detected (enterprise features not available)")
    return "oss"


def get_edition_info() -> Dict[str, Any]:
    """
    Get detailed OSS edition information
    
    Returns:
        Dictionary with OSS edition details
    """
    info = {
        "edition": "oss",
        "tier": "oss",
        "oss_restricted": True,
        "execution_allowed": False,
        "license_key_present": False,
        "license_key_type": "none",
        "upgrade_url": "https://arf.dev/enterprise",
    }
    
    # Add OSS capabilities
    try:
        from ..oss.constants import get_oss_capabilities
        info["capabilities"] = get_oss_capabilities()
        info["limits"] = get_oss_capabilities()["limits"]
    except ImportError:
        info["capabilities"] = {
            "edition": "oss", 
            "license": "Apache 2.0",
            "execution": {"modes": ["advisory"], "allowed": False},
            "upgrade_available": True
        }
    
    return info


@overload
def create_mcp_server(
    mode: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    force_edition: None = None
) -> OSSMCPClient: ...

@overload
def create_mcp_server(
    mode: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    force_edition: Literal["oss"] = "oss"
) -> OSSMCPClient: ...

def create_mcp_server(
    mode: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    force_edition: Optional[str] = None
) -> OSSMCPClient:
    """
    Factory function that creates OSS MCP client only
    
    OSS EDITION: Only returns OSSMCPClient, advisory mode only
    
    Args:
        mode: Ignored in OSS edition (always advisory)
            Provided for backward compatibility only
        config: Configuration dictionary
            If None, uses default configuration
        force_edition: Ignored in OSS edition (always OSS)
            Provided for backward compatibility only
    
    Returns:
        OSSMCPClient instance (advisory mode only)
    
    Raises:
        ValueError: If mode is anything other than "advisory" or None
    """
    # OSS EDITION: Log warning if trying to use enterprise features
    if mode and mode != "advisory":
        logger.warning(
            f"OSS edition only supports advisory mode. "
            f"Ignoring requested mode: '{mode}'"
        )
        
        if mode in ["approval", "autonomous"]:
            logger.info(
                f"Mode '{mode}' requires Enterprise edition. "
                f"Upgrade at: https://arf.dev/enterprise"
            )
    
    # OSS EDITION: Force edition to OSS
    logger.info("📦 Creating OSS MCP Client (advisory mode only)")
    
    # Create OSS client
    client = create_mcp_client(config)
    
    # Log OSS capabilities
    try:
        from ..oss.constants import get_oss_capabilities
        capabilities = get_oss_capabilities()
        logger.info(f"OSS Edition: {capabilities['edition']} ({capabilities['license']})")
        logger.info(f"OSS Limits: {capabilities['limits']}")
        
        # Add upgrade reminder
        if capabilities.get("upgrade_available", True):
            logger.info(
                "💡 Upgrade to Enterprise for execution capabilities: "
                "https://arf.dev/enterprise"
            )
            
    except ImportError:
        logger.info("OSS Edition: Apache 2.0 License")
        logger.info("OSS Limits: Advisory mode only, no execution")
    
    return client


def get_mcp_server_class() -> Type[OSSMCPClient]:
    """
    Get the OSS MCP server class
    
    OSS EDITION: Always returns OSSMCPClient
    
    Returns:
        OSSMCPClient class
    """
    logger.debug("Returning OSSMCPClient class (OSS edition)")
    return OSSMCPClient


def create_healing_intent_from_request(request_dict: Dict[str, Any]) -> Any:
    """
    Create HealingIntent from request (OSS only feature)
    
    OSS creates HealingIntent, Enterprise executes it
    This is the clean boundary between OSS and Enterprise
    
    Args:
        request_dict: MCP request dictionary
        
    Returns:
        HealingIntent object
        
    Raises:
        ImportError: If OSS features not available
    """
    try:
        from ..oss.healing_intent import HealingIntent
        
        logger.debug("Creating HealingIntent from request (OSS analysis)")
        
        # Create healing intent
        intent = HealingIntent.from_mcp_request(request_dict)
        
        # Add OSS metadata
        intent_dict = intent.to_dict()
        intent_dict["oss_edition"] = True
        intent_dict["requires_enterprise"] = True
        
        logger.info(
            f"HealingIntent created: {intent.action} for {intent.component} "
            f"(confidence: {intent.confidence:.2f})"
        )
        
        return intent
        
    except ImportError as e:
        logger.error(f"Failed to import HealingIntent: {e}")
        raise ImportError(
            "HealingIntent feature requires OSS module. "
            "Make sure arf-core is properly installed. "
            "If this is an Enterprise installation, use EnterpriseMCPServer.execute_healing_intent() instead."
        ) from e


def create_advisory_response(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create advisory response for OSS edition
    
    Helper function for creating consistent OSS advisory responses
    
    Args:
        request_dict: MCP request dictionary
        
    Returns:
        Advisory response dictionary
    """
    tool = request_dict.get("tool", "unknown")
    component = request_dict.get("component", "unknown")
    justification = request_dict.get("justification", "")
    
    return {
        "request_id": request_dict.get("request_id", "oss-advisory"),
        "status": "completed",
        "message": f"OSS Advisory: Would execute {tool} on {component}",
        "executed": False,
        "requires_enterprise": True,
        "result": {
            "mode": "advisory",
            "would_execute": True,
            "justification": justification,
            "upgrade_url": "https://arf.dev/enterprise",
            "enterprise_features": [
                "autonomous_execution",
                "approval_workflows", 
                "persistent_storage",
                "learning_engine",
                "audit_trails",
                "compliance_reports"
            ]
        }
    }


def check_oss_compatibility(mode: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if requested features are compatible with OSS edition
    
    Args:
        mode: Requested MCP mode
        
    Returns:
        Compatibility check result
    """
    result = {
        "compatible": True,
        "edition": "oss",
        "mode_supported": True,
        "execution_supported": False,
        "upgrade_required": False,
    }
    
    # Check mode compatibility
    if mode and mode != "advisory":
        result["compatible"] = False
        result["mode_supported"] = False
        result["upgrade_required"] = True
        
        if mode in ["approval", "autonomous"]:
            result["message"] = f"Mode '{mode}' requires Enterprise edition"
    
    # Check for execution attempts
    if mode == "autonomous":
        result["execution_supported"] = False
        result["upgrade_required"] = True
        result["message"] = "Autonomous execution requires Enterprise edition"
    
    return result


# Backward compatibility aliases
def get_mcp_server(*args: Any, **kwargs: Any) -> OSSMCPClient:
    """Backward compatibility alias for create_mcp_server"""
    return create_mcp_server(*args, **kwargs)


# Export
__all__ = [
    "detect_edition",
    "get_edition_info",
    "create_mcp_server",
    "get_mcp_server_class",
    "create_healing_intent_from_request",
    "create_advisory_response",
    "check_oss_compatibility",
    "get_mcp_server",  # Backward compatibility
]
