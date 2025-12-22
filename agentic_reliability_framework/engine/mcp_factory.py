"""
MCP Server Factory with OSS↔Enterprise Integration
Apache 2.0 Licensed for OSS, Commercial license required for Enterprise

Provides automatic detection and integration between:
1. OSS Edition (advisory only, Apache 2.0)
2. Enterprise Edition (all modes, commercial license)

Key Features:
- Auto-detects Enterprise installation
- Validates license when available
- Provides seamless OSS→Enterprise handoff
- Maintains backward compatibility
- Clear upgrade prompts for OSS users
"""

import os
import logging
from typing import Dict, Any, Optional, Union, Type, overload, Literal, TYPE_CHECKING

# Handle Literal for different Python versions
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# OSS imports
from .mcp_client import OSSMCPClient, create_mcp_client

# Type checking only imports to avoid circular dependencies
if TYPE_CHECKING:
    from arf_enterprise.mcp_server import EnterpriseMCPServer

logger = logging.getLogger(__name__)

# Type alias for factory returns
MCPInstance = Union["OSSMCPClient", "EnterpriseMCPServer"]


class MCPIntegrationManager:
    """
    Manages OSS↔Enterprise integration with automatic detection
    
    Key Features:
    1. Auto-detects Enterprise installation
    2. Validates license when Enterprise available
    3. Provides seamless OSS→Enterprise handoff
    4. Maintains OSS fallback when Enterprise not available
    5. Clear logging of edition and capabilities
    
    Architecture:
        User Code → MCPIntegrationManager → [EnterpriseMCPServer | OSSMCPClient]
                                             (if licensed)        (fallback)
    """
    
    def __init__(self):
        """Initialize integration manager"""
        self._enterprise_available = self._check_enterprise_available()
        self._license_key = self._get_license_key()
        self._enterprise_server = None
        self._oss_client = None
        
        logger.debug(f"MCP Integration Manager initialized")
        logger.debug(f"  Enterprise available: {self._enterprise_available}")
        logger.debug(f"  License configured: {bool(self._license_key)}")
    
    def _check_enterprise_available(self) -> bool:
        """
        Check if Enterprise package is installed
        
        Returns:
            True if arf_enterprise package is importable
        """
        try:
            import arf_enterprise
            return True
        except ImportError:
            return False
    
    def _get_license_key(self) -> Optional[str]:
        """
        Get license key from environment variables
        
        Checks multiple environment variables for license key:
        1. ARF_LICENSE_KEY (primary)
        2. ARF_ENTERPRISE_LICENSE (backup)
        3. ARF_COMMERCIAL_LICENSE (legacy)
        
        Returns:
            License key string or None
        """
        # Try multiple environment variable names
        env_vars = [
            "ARF_LICENSE_KEY",
            "ARF_ENTERPRISE_LICENSE", 
            "ARF_COMMERCIAL_LICENSE"
        ]
        
        for env_var in env_vars:
            license_key = os.getenv(env_var)
            if license_key and license_key.strip():
                logger.debug(f"Found license key in {env_var}")
                return license_key.strip()
        
        return None
    
    def create_integrated_server(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> MCPInstance:
        """
        Create MCP server with automatic OSS/Enterprise detection
        
        Returns EnterpriseMCPServer if:
        1. Enterprise package is installed
        2. Valid license key is configured
        3. License validation succeeds
        
        Otherwise returns OSSMCPClient (advisory only)
        
        Args:
            config: Configuration dictionary (passed to server constructor)
            
        Returns:
            OSSMCPClient or EnterpriseMCPServer instance
            
        Raises:
            RuntimeError: If neither OSS nor Enterprise can be initialized
        """
        # Try Enterprise first if available and licensed
        if self._enterprise_available and self._license_key:
            try:
                return self._create_enterprise_server(config)
            except Exception as e:
                logger.warning(f"Enterprise initialization failed: {e}")
                logger.info("Falling back to OSS edition")
        
        # Fall back to OSS
        return self._create_oss_server(config)
    
    def _create_enterprise_server(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> "EnterpriseMCPServer":
        """
        Create Enterprise MCP server with license validation
        
        Args:
            config: Configuration dictionary
            
        Returns:
            EnterpriseMCPServer instance
            
        Raises:
            ImportError: If Enterprise package not available
            LicenseError: If license validation fails
        """
        try:
            from arf_enterprise.mcp_server import create_enterprise_mcp_server
            
            logger.info("🚀 Attempting to initialize Enterprise MCP Server...")
            
            # Create Enterprise server
            enterprise_server = create_enterprise_mcp_server(
                license_key=self._license_key
            )
            
            # Store reference
            self._enterprise_server = enterprise_server
            
            # Log successful initialization
            license_info = enterprise_server.license_info
            logger.info("✅ Enterprise MCP Server initialized successfully")
            logger.info(f"   Customer: {license_info.get('customer_name', 'Unknown')}")
            logger.info(f"   Tier: {license_info.get('tier', 'Unknown')}")
            logger.info(f"   Features: {', '.join(license_info.get('features', []))}")
            logger.info(f"   Modes available: {enterprise_server.allowed_modes}")
            
            return enterprise_server
            
        except ImportError as e:
            logger.error(f"Enterprise package import failed: {e}")
            raise ImportError(
                "Enterprise package not found. "
                "Install with: pip install agentic-reliability-enterprise"
            ) from e
        except Exception as e:
            logger.error(f"Enterprise server creation failed: {e}")
            raise
    
    def _create_oss_server(
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
        
        # Show upgrade prompt if Enterprise is available but not licensed
        if self._enterprise_available and not self._license_key:
            logger.info(
                "💡 Enterprise package detected but no license key found.\n"
                "   Set ARF_LICENSE_KEY environment variable to enable:\n"
                "   • Autonomous execution\n"
                "   • Approval workflows\n"
                "   • Learning engine\n"
                "   • Audit trails\n"
                "   Upgrade at: https://arf.dev/enterprise"
            )
        elif not self._enterprise_available:
            logger.info(
                "💡 Install Enterprise package for execution capabilities:\n"
                "   pip install agentic-reliability-enterprise\n"
                "   Then set ARF_LICENSE_KEY environment variable"
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
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get detailed integration status
        
        Returns:
            Dictionary with integration status information
        """
        status = {
            "enterprise_package_available": self._enterprise_available,
            "license_key_configured": bool(self._license_key),
            "enterprise_server_active": self._enterprise_server is not None,
            "oss_client_active": self._oss_client is not None,
            "recommended_action": None,
        }
        
        # Add license info if available
        if self._license_key:
            status["license_key_present"] = True
            status["license_key_type"] = (
                "enterprise" if self._license_key.startswith("ARF-ENT-") 
                else "unknown"
            )
        else:
            status["license_key_present"] = False
        
        # Add active server info
        if self._enterprise_server:
            try:
                license_info = self._enterprise_server.license_info
                status.update({
                    "edition": "enterprise",
                    "customer": license_info.get("customer_name"),
                    "tier": license_info.get("tier", {}).value if hasattr(license_info.get("tier"), "value") 
                            else str(license_info.get("tier")),
                    "features": license_info.get("features", []),
                    "modes": getattr(self._enterprise_server, "allowed_modes", []),
                })
            except Exception:
                status["edition"] = "enterprise"
        
        elif self._oss_client:
            status["edition"] = "oss"
            status["mode"] = "advisory"
            status["execution_allowed"] = False
        
        # Determine recommended action
        if self._enterprise_available and not self._license_key:
            status["recommended_action"] = "set_license_key"
        elif not self._enterprise_available:
            status["recommended_action"] = "install_enterprise"
        elif self._enterprise_server:
            status["recommended_action"] = "ready_for_production"
        
        return status
    
    def force_oss_mode(self) -> OSSMCPClient:
        """
        Force OSS mode even if Enterprise is available
        
        Useful for testing or explicit OSS-only scenarios
        
        Returns:
            OSSMCPClient instance
        """
        logger.info("🔧 Forcing OSS mode (ignoring Enterprise)")
        return self._create_oss_server()


# ========== PUBLIC FACTORY FUNCTIONS ==========

@overload
def create_mcp_server(
    mode: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    force_edition: None = None
) -> MCPInstance: ...

@overload
def create_mcp_server(
    mode: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    force_edition: Literal["oss"] = "oss"
) -> OSSMCPClient: ...

@overload
def create_mcp_server(
    mode: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    force_edition: Literal["enterprise"] = "enterprise"
) -> "EnterpriseMCPServer": ...

def create_mcp_server(
    mode: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    force_edition: Optional[str] = None
) -> MCPInstance:
    """
    Main factory function for creating MCP servers
    
    Provides automatic OSS↔Enterprise integration with manual override options
    
    Args:
        mode: Requested execution mode
            - "advisory": Analysis only (OSS compatible)
            - "approval": Human-in-loop (Enterprise only)
            - "autonomous": Fully automated (Enterprise only)
            If None, uses environment variable or default
        config: Configuration dictionary
        force_edition: Force specific edition
            - None: Auto-detect (default)
            - "oss": Force OSS edition
            - "enterprise": Force Enterprise edition (requires license)
    
    Returns:
        OSSMCPClient or EnterpriseMCPServer instance
        
    Raises:
        ValueError: If force_edition="enterprise" but license not available
    """
    integration_manager = MCPIntegrationManager()
    
    # Handle force edition
    if force_edition == "oss":
        logger.info("User requested OSS edition explicitly")
        return integration_manager.force_oss_mode()
    
    elif force_edition == "enterprise":
        if not integration_manager._enterprise_available:
            raise ValueError(
                "Enterprise edition requested but package not installed. "
                "Install with: pip install agentic-reliability-enterprise"
            )
        if not integration_manager._license_key:
            raise ValueError(
                "Enterprise edition requested but no license key found. "
                "Set ARF_LICENSE_KEY environment variable."
            )
        logger.info("User requested Enterprise edition explicitly")
        return integration_manager._create_enterprise_server(config)
    
    # Auto-detect mode (default behavior)
    server = integration_manager.create_integrated_server(config)
    
    # Log mode compatibility
    if mode and mode != "advisory":
        if hasattr(server, "oss_edition") and server.oss_edition:
            logger.warning(
                f"OSS edition cannot fulfill mode '{mode}'. "
                f"Requested mode requires Enterprise edition."
            )
        else:
            # Enterprise server - check if mode is allowed
            logger.info(f"Enterprise server will use mode: {mode}")
    
    return server


def detect_edition() -> str:
    """
    Detect current edition
    
    Returns:
        "oss" or "enterprise" based on available packages and license
    """
    integration_manager = MCPIntegrationManager()
    status = integration_manager.get_integration_status()
    
    if status.get("edition") == "enterprise":
        return "enterprise"
    return "oss"


def get_edition_info() -> Dict[str, Any]:
    """
    Get detailed edition information
    
    Returns:
        Dictionary with edition details, capabilities, and upgrade info
    """
    integration_manager = MCPIntegrationManager()
    status = integration_manager.get_integration_status()
    
    info = {
        "edition": status.get("edition", "oss"),
        "integration_status": status,
        "upgrade_url": "https://arf.dev/enterprise",
        "documentation_url": "https://docs.arf.dev",
    }
    
    # Add OSS capabilities if in OSS mode
    if status.get("edition") == "oss":
        try:
            from ..oss.constants import get_oss_capabilities
            info["capabilities"] = get_oss_capabilities()
            info["limits"] = get_oss_capabilities().get("limits", {})
        except ImportError:
            info["capabilities"] = {
                "edition": "oss", 
                "license": "Apache 2.0",
                "execution": {"modes": ["advisory"], "allowed": False},
                "upgrade_available": True
            }
    
    # Add Enterprise info if in Enterprise mode
    elif status.get("edition") == "enterprise":
        info["capabilities"] = {
            "edition": "enterprise",
            "license": "commercial",
            "execution": {"modes": status.get("modes", ["advisory", "approval", "autonomous"]), "allowed": True},
            "features": status.get("features", []),
        }
    
    return info


def create_healing_intent_from_request(request_dict: Dict[str, Any]) -> Any:
    """
    Create HealingIntent from request
    
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
        # Try OSS imports first
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
        # Try Enterprise imports as fallback
        try:
            from arf_enterprise.mcp_server import EnterpriseMCPServer
            logger.debug("Using Enterprise context for HealingIntent")
            # In Enterprise context, HealingIntent might come from different module
            raise ImportError(
                "HealingIntent creation depends on OSS analysis. "
                "In Enterprise mode, use execute_healing_intent() instead."
            )
        except ImportError:
            raise ImportError(
                "HealingIntent feature requires OSS module. "
                "Make sure arf-core is properly installed."
            ) from e


def check_oss_compatibility(mode: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if requested features are compatible with current edition
    
    Args:
        mode: Requested MCP mode
        
    Returns:
        Compatibility check result with upgrade recommendations
    """
    integration_manager = MCPIntegrationManager()
    status = integration_manager.get_integration_status()
    
    result = {
        "compatible": True,
        "current_edition": status.get("edition", "oss"),
        "mode_supported": True,
        "execution_supported": False,
        "upgrade_required": False,
        "upgrade_url": "https://arf.dev/enterprise",
    }
    
    # Check mode compatibility
    if mode and mode != "advisory":
        if status.get("edition") == "oss":
            result["compatible"] = False
            result["mode_supported"] = False
            result["upgrade_required"] = True
            
            if mode in ["approval", "autonomous"]:
                result["message"] = f"Mode '{mode}' requires Enterprise edition"
                result["action_required"] = "install_enterprise_and_set_license"
        
        elif status.get("edition") == "enterprise":
            # Check if mode is in allowed modes
            allowed_modes = status.get("modes", [])
            if mode not in allowed_modes:
                result["compatible"] = False
                result["mode_supported"] = False
                result["message"] = f"Mode '{mode}' not allowed by license tier"
                result["action_required"] = "upgrade_license_tier"
    
    # Check execution capability
    if mode == "autonomous":
        result["execution_supported"] = status.get("edition") == "enterprise"
        if not result["execution_supported"]:
            result["upgrade_required"] = True
    
    return result


def get_mcp_server_class() -> Type:
    """
    Get the appropriate MCP server class based on available edition
    
    Returns:
        OSSMCPClient or EnterpriseMCPServer class
    """
    integration_manager = MCPIntegrationManager()
    status = integration_manager.get_integration_status()
    
    if status.get("edition") == "enterprise":
        try:
            from arf_enterprise.mcp_server import EnterpriseMCPServer
            logger.debug("Returning EnterpriseMCPServer class")
            return EnterpriseMCPServer
        except ImportError:
            pass
    
    logger.debug("Returning OSSMCPClient class")
    return OSSMCPClient


def create_advisory_response(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create advisory response (OSS fallback)
    
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
            ],
            "integration_available": detect_edition() == "enterprise"
        }
    }


# ========== BACKWARD COMPATIBILITY ==========

def get_mcp_server(*args: Any, **kwargs: Any) -> MCPInstance:
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
    
    Use this when you explicitly want OSS edition, even if Enterprise is available.
    
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
    
    integration_manager = MCPIntegrationManager()
    return integration_manager.force_oss_mode()


# Export
__all__ = [
    # Main factory functions
    "create_mcp_server",
    "create_integrated_server",  # Alias for clarity
    "create_oss_only_mcp_server",
    
    # Edition detection
    "detect_edition",
    "get_edition_info",
    "check_oss_compatibility",
    
    # Server classes
    "get_mcp_server_class",
    
    # HealingIntent utilities
    "create_healing_intent_from_request",
    "create_advisory_response",
    
    # Backward compatibility
    "get_mcp_server",
    
    # Integration manager (advanced use)
    "MCPIntegrationManager",
]
