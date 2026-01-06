"""
ARF Core Module - OSS Edition
Production-grade multi-agent AI for reliability monitoring
OSS Edition: Advisory mode only, Apache 2.0 Licensed

IMPORTANT: This module ONLY exports OSS components - no circular imports
Enhanced with OSS boundary validation and simplified lazy loading
"""

__version__ = "3.3.6"  # FIXED: Updated to match release version v3.3.6
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
# DIRECT IMPORTS - RESOLVE CIRCULAR DEPENDENCIES WITH OSS VALIDATION
# ============================================================================

# First: Validate we're in OSS mode at import time
import os
import sys

# Check OSS boundary before importing anything
def _validate_oss_import_environment():
    """Validate OSS boundaries at module import time"""
    # Check for environment variables that indicate enterprise mode
    enterprise_vars = [
        "ARF_TIER",
        "ARF_DEPLOYMENT_TYPE",
    ]
    
    for var in enterprise_vars:
        value = os.getenv(var)
        if value and value.lower() != "oss":
            print(f"⚠️  Warning: Non-OSS environment variable: {var}={value}")
    
    # Check for test environment to avoid false positives
    is_test = "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules
    if not is_test:
        # Try to import OSS compliance check
        try:
            from .constants import check_oss_compliance
            if not check_oss_compliance():
                print("⚠️  Warning: Environment may not be OSS compliant")
        except ImportError:
            # If we can't check, assume OSS for safety
            pass

# Run validation silently
try:
    _validate_oss_import_environment()
except Exception:
    # Don't fail imports on validation errors
    pass

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
    validate_oss_config,
    get_oss_capabilities,
)

# ============================================================================
# LAZY LOAD OSSMCPClient - SIMPLIFIED VERSION
# ============================================================================

_oss_mcp_client_class = None

def _get_oss_mcp_client_class():
    """Dynamically import OSSMCPClient on first use with safe fallback"""
    global _oss_mcp_client_class
    if _oss_mcp_client_class is not None:
        return _oss_mcp_client_class
    
    try:
        # Import from the correct file (oss_mcp_client.py)
        from agentic_reliability_framework.arf_core.engine.oss_mcp_client import OSSMCPClient
        _oss_mcp_client_class = OSSMCPClient
        return _oss_mcp_client_class
    except ImportError as e:
        # Create minimal fallback class for emergency use
        class EmergencyOSSMCPClient:
            def __init__(self, config=None):
                self.mode = "advisory"
                self.config = config or {}
                self.oss_edition = OSS_EDITION
                self.oss_license = OSS_LICENSE
            
            async def execute_tool(self, request_dict):
                return {
                    "request_id": request_dict.get("request_id", "oss-emergency"),
                    "status": "advisory",
                    "message": f"OSS Advisory mode - {request_dict.get('tool', 'unknown')} analysis",
                    "executed": False,
                    "result": {
                        "mode": "advisory",
                        "requires_enterprise": True,
                        "upgrade_url": "https://arf.dev/enterprise",
                        "error": f"OSSMCPClient import failed: {str(e)[:100]}"
                    },
                    "oss_edition": OSS_EDITION,
                    "execution_allowed": False,
                }
            
            def get_client_info(self):
                return {
                    "mode": "advisory",
                    "edition": OSS_EDITION,
                    "license": OSS_LICENSE,
                    "requires_enterprise": True,
                    "import_error": str(e)[:200]
                }
        
        _oss_mcp_client_class = EmergencyOSSMCPClient
        print(f"⚠️  Warning: Using emergency OSSMCPClient due to import error: {e}")
        return _oss_mcp_client_class

def __getattr__(name):
    """Lazy loading for OSSMCPClient"""
    if name == "OSSMCPClient":
        return _get_oss_mcp_client_class()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def create_mcp_client(config=None):
    """
    Factory function for OSSMCPClient
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        OSSMCPClient instance (advisory mode only)
    """
    # Validate config against OSS boundaries
    if config:
        try:
            validate_oss_config(config)
        except OSSBoundaryError as e:
            print(f"⚠️  Config validation warning: {str(e)[:200]}")
            # Fall back to empty config
            config = {}
    
    OSSMCPClientClass = _get_oss_mcp_client_class()
    return OSSMCPClientClass(config=config)

# Export OSSMCPClient for static analysis
try:
    OSSMCPClient = _get_oss_mcp_client_class()
except Exception:
    # This should never happen due to the fallback above
    OSSMCPClient = None

# ============================================================================
# MODULE METADATA AND UTILITIES
# ============================================================================

ENTERPRISE_UPGRADE_URL = "https://arf.dev/enterprise"

def get_oss_info():
    """
    Get comprehensive OSS edition information
    
    Returns:
        Dictionary with OSS capabilities, limits, and upgrade info
    """
    try:
        capabilities = get_oss_capabilities()
    except Exception:
        capabilities = {
            "edition": OSS_EDITION,
            "license": OSS_LICENSE,
            "execution": {"modes": ["advisory"], "allowed": False},
            "upgrade_url": ENTERPRISE_UPGRADE_URL,
        }
    
    return {
        **capabilities,
        "module_version": __version__,
        "python_version": sys.version.split()[0],
        "import_path": __file__,
    }

def validate_environment():
    """
    Validate current environment against OSS requirements
    
    Returns:
        tuple: (is_valid, violations)
    """
    violations = []
    
    # Check for enterprise environment variables
    if os.getenv("ARF_TIER", "oss").lower() != "oss":
        violations.append(f"ARF_TIER={os.getenv('ARF_TIER')} should be 'oss'")
    
    # Check for OSS compliance
    try:
        from .constants import check_oss_compliance
        if not check_oss_compliance():
            violations.append("Environment not OSS compliant")
    except ImportError:
        violations.append("Cannot import OSS compliance check")
    
    # Check import sanity
    try:
        OSSMCPClientClass = _get_oss_mcp_client_class()
        if OSSMCPClientClass.__name__ == "EmergencyOSSMCPClient":
            violations.append("Using emergency fallback OSSMCPClient")
    except Exception as e:
        violations.append(f"Cannot access OSSMCPClient: {e}")
    
    return len(violations) == 0, violations

# ============================================================================
# IMPORT-TIME VALIDATION (NON-BLOCKING)
# ============================================================================

def _run_silent_validation():
    """Run validation silently at import time"""
    try:
        # Check if we're in a test environment
        is_test = "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules
        
        if not is_test:
            # Run quick OSS validation
            valid, violations = validate_environment()
            if not valid and violations:
                # Only print warnings, don't fail
                print(f"⚠️  OSS environment validation warnings: {', '.join(violations[:3])}")
    except Exception:
        # Never fail on import validation
        pass

# Run silent validation
_run_silent_validation()
