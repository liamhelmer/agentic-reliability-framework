"""
MCP Server Factory - OSS Edition Only
Apache 2.0 Licensed - Enterprise execution requires commercial license

OSS EDITION: Advisory mode only, no execution capability
Provides clear upgrade path to Enterprise edition
"""

import os
import logging
from typing import Dict, Any, Optional, Type, overload, Literal

# Handle Literal for different Python versions
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# OSS imports only
from .mcp_client import OSSMCPClient, create_mcp_client

logger = logging.getLogger(__name__)

# Type alias - OSS only returns OSSMCPClient
MCPInstance = OSSMCPClient


class OSSIntegrationManager:
    """
    OSS Integration Manager - No Enterprise capabilities
    
    Provides:
    - OSS advisory mode only
    - Clear upgrade prompts
    - No execution capability
    - Environment variable checks for upgrade path
    """
    
    def __init__(self):
        """Initialize OSS integration manager"""
        self._oss_client = None
        self._license_key_detected = self._check_license_key_env()
        
        logger.debug("OSS Integration Manager initialized (advisory only)")
    
    def _check_license_key_env(self) -> bool:
        """
        OSS EDITION: Never checks license keys
        
        Returns:
            Always False in OSS edition
        """
        # OSS EDITION: Never checks license keys
        # This is an Enterprise-only feature
        
        # We can check for environment variables to provide upgrade prompts
        # but we never validate or use them
        env_vars = [
            "ARF_LICENSE_KEY",
            "ARF_ENTERPRISE_LICENSE", 
            "ARF_COMMERCIAL_LICENSE"
        ]
        
        # Only check to provide helpful upgrade messages
        for env_var in env_vars:
            if os.getenv(env_var):
                logger.debug(f"Environment variable {env_var} found")
                # Return True ONLY to trigger upgrade message
                # NOT for actual license validation
                return True
        
        return False
    
    def create_oss_server(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> OSSMCPClient:
        """
        Create OSS MCP client (advisory only)
        
        Args:
            config: Configuration dictionary
            
        Returns:
            OSSMCPClient instance
        """
        logger.info("📦 Creating OSS MCP Client (advisory mode only)")
        
        # Create OSS client
        oss_client = create_mcp_client(config)
        self._oss_client = oss_client
        
        # Log OSS capabilities and limitations
        self._log_oss_capabilities()
        
        # Show upgrade prompt if license key detected
        if self._license_key_detected:
            logger.info(
                "🔑 License key detected. To use Enterprise features:\n"
                "   1. Install Enterprise package:\n"
                "      pip install agentic-reliability-enterprise\n"
                "   2. Use create_enterprise_mcp_server() from Enterprise package\n"
                "   3. Set ARF_LICENSE_KEY environment variable"
            )
        else:
            logger.info(
                "💡 Upgrade to Enterprise for execution capabilities:\n"
                "   • Autonomous execution\n"
                "   • Approval workflows\n"
                "   • Learning engine\n"
                "   • Audit trails\n"
                "   • Unlimited storage\n"
                "   Visit: https://arf.dev/enterprise"
            )
        
        return oss_client
    
    def _log_oss_capabilities(self) -> None:
        """Log OSS edition capabilities and limitations"""
        try:
            from ..oss.constants import get_oss_capabilities
            capabilities = get_oss_capabilities()
            
            logger.info(f"OSS Edition: {capabilities['edition']} ({capabilities['license']})")
            logger.info(f"OSS Mode: {capabilities['execution']['modes'][0]} only")
            logger.info(f"OSS Limits: {capabilities['limits']}")
            
            if capabilities.get("upgrade_available", True):
                logger.info(
                    "🔒 OSS Restrictions:\n"
                    "   • No tool execution\n"
                    "   • No approval workflows\n"
                    "   • No autonomous mode\n"
                    "   • No learning engine\n"
                    "   • No audit trails\n"
                    "   • Limited storage (in-memory only)"
                )
                
        except ImportError:
            logger.info("OSS Edition: Apache 2.0 License")
            logger.info("OSS Mode: Advisory only")
            logger.info("OSS Capability: Analysis and recommendations only")
    
    def get_oss_status(self) -> Dict[str, Any]:
        """
        Get OSS integration status
        
        Returns:
            Dictionary with OSS status information
        """
        status = {
            "edition": "oss",
            "mode": "advisory",
            "license_key_detected": self._license_key_detected,
            "oss_client_active": self._oss_client is not None,
            "execution_allowed": False,
            "upgrade_available": True,
            "upgrade_url": "https://arf.dev/enterprise",
        }
        
        return status


# ========== PUBLIC FACTORY FUNCTIONS ==========

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
    
    # OSS EDITION: Create OSS server
    integration_manager = OSSIntegrationManager()
    server = integration_manager.create_oss_server(config)
    
    return server


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
            "Make sure arf-core is properly installed."
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


def is_enterprise_available() -> bool:
    """
    Check if Enterprise edition might be available
    
    OSS EDITION: Always returns False, but provides helpful message
    
    Returns:
        Always False in OSS edition
    """
    # Check for license key environment variable
    license_keys = [
        "ARF_LICENSE_KEY",
        "ARF_ENTERPRISE_LICENSE",
        "ARF_COMMERCIAL_LICENSE"
    ]
    
    has_license_key = any(os.getenv(key) for key in license_keys)
    
    if has_license_key:
        logger.info(
            "📋 License key detected. "
            "To use Enterprise features, install: "
            "pip install agentic-reliability-enterprise"
        )
    
    return False


# ========== BACKWARD COMPATIBILITY ==========

def get_mcp_server(*args: Any, **kwargs: Any) -> OSSMCPClient:
    """
    Backward compatibility alias for create_mcp_server
    
    Deprecated: Use create_mcp_server() instead
    """
    import warnings
    warnings.warn(
        "get_mcp_server() is deprecated, use create_mcp_server() instead",
        DeprecationWarning,
        stacklevel=2
    )
    return create_mcp_server(*args, **kwargs)


def create_oss_only_mcp_server(
    mode: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> OSSMCPClient:
    """
    Create OSS-only MCP server (explicitly OSS, no Enterprise check)
    
    Use this when you explicitly want OSS edition.
    
    Args:
        mode: Ignored in OSS edition (always advisory)
        config: Configuration dictionary
        
    Returns:
        OSSMCPClient instance
    """
    logger.info("🔧 Creating OSS-only MCP Client (explicit OSS mode)")
    
    if mode and mode != "advisory":
        logger.warning(
            f"OSS-only server requested with mode '{mode}'. "
            f"OSS only supports advisory mode."
        )
    
    integration_manager = OSSIntegrationManager()
    return integration_manager.create_oss_server(config)


# Export
__all__ = [
    # Main factory functions
    "create_mcp_server",
    "create_oss_only_mcp_server",
    
    # Edition detection
    "detect_edition",
    "get_edition_info",
    "check_oss_compatibility",
    "is_enterprise_available",
    
    # Server classes
    "get_mcp_server_class",
    
    # HealingIntent utilities
    "create_healing_intent_from_request",
    "create_advisory_response",
    
    # Backward compatibility
    "get_mcp_server",
    
    # OSS integration manager (OSS only)
    "OSSIntegrationManager",
]
