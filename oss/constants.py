# agentic_reliability_framework/oss/constants.py
"""
OSS HARD LIMITS - Build-time enforced boundaries for OSS edition
These constants define what's allowed in the Open Source edition
"""

from typing import Final, Dict, Any
import sys
import os

# ==================== OSS ARCHITECTURAL BOUNDARIES ====================

# === EXECUTION BOUNDARIES ===
MAX_INCIDENT_HISTORY: Final[int] = 1_000
MAX_RAG_LOOKBACK_DAYS: Final[int] = 7
MCP_MODES_ALLOWED: Final[tuple] = ("advisory",)  # ONLY advisory
EXECUTION_ALLOWED: Final[bool] = False
GRAPH_STORAGE: Final[str] = "in_memory"
MAX_COOLDOWN_ENTRIES: Final[int] = 100

# === FEATURE BOUNDARIES ===
MAX_TOOLS: Final[int] = 6  # Current tool count
MAX_CONCURRENT_ANALYSIS: Final[int] = 10
MAX_EVENT_RATE_PER_SECOND: Final[int] = 100

# === SECURITY BOUNDARIES ===
MAX_API_KEYS: Final[int] = 1  # Only HuggingFace API key
ALLOWED_ENVIRONMENTS: Final[tuple] = ("development", "staging", "production")
DISALLOWED_ACTIONS: Final[tuple] = (
    "DATABASE_DROP",
    "FULL_ROLLOUT", 
    "SYSTEM_SHUTDOWN",
    "SECRET_ROTATION",
)

# === VERSION & EDITION ===
OSS_EDITION: Final[str] = "open-source"
OSS_LICENSE: Final[str] = "Apache 2.0"
OSS_VERSION: Final[str] = "3.3.0-oss"

# ==================== VALIDATION & ENFORCEMENT ====================

class OSSBoundaryError(RuntimeError):
    """Error raised when OSS boundaries are violated"""
    pass


def validate_oss_config(config: Dict[str, Any]) -> None:
    """
    Validate runtime configuration against OSS boundaries
    
    Args:
        config: Current configuration dictionary
        
    Raises:
        OSSBoundaryError: If any OSS boundary is violated
    """
    violations = []
    
    # Check MCP mode
    mcp_mode = config.get("mcp_mode", "advisory").lower()
    if mcp_mode != "advisory":
        violations.append(f"MCP mode must be 'advisory', got '{mcp_mode}'")
    
    # Check execution capability
    if config.get("mcp_enabled", False) and mcp_mode != "advisory":
        violations.append("MCP execution not allowed in OSS edition")
    
    # Check storage limits
    max_events = config.get("max_events_stored", 1000)
    if max_events > MAX_INCIDENT_HISTORY:
        violations.append(f"max_events_stored exceeds OSS limit: {max_events} > {MAX_INCIDENT_HISTORY}")
    
    # Check RAG limits
    rag_nodes = config.get("rag_max_incident_nodes", 1000)
    if rag_nodes > MAX_INCIDENT_HISTORY:
        violations.append(f"rag_max_incident_nodes exceeds OSS limit: {rag_nodes} > {MAX_INCIDENT_HISTORY}")
    
    # Check feature flags
    if config.get("learning_enabled", False):
        violations.append("Learning engine requires Enterprise edition")
    
    if config.get("beta_testing_enabled", False):
        violations.append("Beta testing features require Enterprise edition")
    
    if violations:
        raise OSSBoundaryError(
            f"OSS boundary violations detected:\n" +
            "\n".join(f"  • {v}" for v in violations) +
            f"\n\nEdition: {OSS_EDITION} ({OSS_LICENSE})" +
            f"\nVersion: {OSS_VERSION}" +
            f"\n\nUpgrade to Enterprise edition for these features: https://arf.dev/enterprise"
        )


def get_oss_capabilities() -> Dict[str, Any]:
    """
    Get OSS edition capabilities for documentation and UI
    
    Returns:
        Dictionary of OSS capabilities and limits
    """
    return {
        "edition": OSS_EDITION,
        "license": OSS_LICENSE,
        "version": OSS_VERSION,
        "execution": {
            "modes": list(MCP_MODES_ALLOWED),
            "allowed": EXECUTION_ALLOWED,
            "max_incidents": MAX_INCIDENT_HISTORY,
            "max_rag_lookback_days": MAX_RAG_LOOKBACK_DAYS,
        },
        "storage": {
            "type": GRAPH_STORAGE,
            "max_cooldown_entries": MAX_COOLDOWN_ENTRIES,
        },
        "features": {
            "rag_enabled": True,
            "mcp_advisory_enabled": True,
            "learning_enabled": False,
            "audit_trails": False,
            "persistent_storage": False,
            "enterprise_integration": False,
            "beta_features": False,
        },
        "limits": {
            "max_tools": MAX_TOOLS,
            "max_concurrent_analysis": MAX_CONCURRENT_ANALYSIS,
            "max_event_rate": MAX_EVENT_RATE_PER_SECOND,
            "max_api_keys": MAX_API_KEYS,
        },
        "upgrade_available": True,
        "upgrade_url": "https://arf.dev/enterprise",
        "enterprise_features": [
            "autonomous_execution",
            "approval_workflows",
            "learning_engine",
            "persistent_graph_storage",
            "enterprise_audit_trails",
            "compliance_reporting",
            "multi_tenant_support",
            "sso_integration",
            "24_7_support",
            "beta_feature_access",
            "commercial_license",
            "priority_support",
        ]
    }


def check_oss_compliance() -> bool:
    """
    Check if current runtime is OSS compliant
    
    Returns:
        True if OSS compliant, False otherwise
    """
    try:
        # Check environment
        tier = os.getenv("ARF_TIER", "oss").lower()
        if tier != "oss":
            return False
        
        # Check license
        license_key = os.getenv("ARF_LICENSE_KEY", "")
        if license_key.startswith("ARF-ENT-") or license_key.startswith("ARF-TRIAL-"):
            return False
        
        return True
    except Exception:  # Changed from bare except
        return True  # Default to OSS if cannot determine


# Export
__all__ = [
    "MAX_INCIDENT_HISTORY",
    "MAX_RAG_LOOKBACK_DAYS", 
    "MCP_MODES_ALLOWED",
    "EXECUTION_ALLOWED",
    "GRAPH_STORAGE",
    "MAX_COOLDOWN_ENTRIES",
    "OSS_EDITION",
    "OSS_LICENSE",
    "OSS_VERSION",
    "OSSBoundaryError",
    "validate_oss_config",
    "get_oss_capabilities",
    "check_oss_compliance",
]
