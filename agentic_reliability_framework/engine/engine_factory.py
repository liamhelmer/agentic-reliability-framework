"""
Engine Factory - OSS Edition Only
Creates OSS-compatible reliability engines with hard limits
Apache 2.0 Licensed

Copyright 2025 Juan Petter

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from typing import Dict, Any, Optional, Union, Type, cast, overload, TYPE_CHECKING

# Handle Literal for different Python versions
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from .reliability import V3ReliabilityEngine, EnhancedReliabilityEngine
from .v3_reliability import V3ReliabilityEngine as EnhancedV3ReliabilityEngine
from ..config import config

logger = logging.getLogger(__name__)

# Type aliases
EngineType = Union[V3ReliabilityEngine, EnhancedReliabilityEngine, EnhancedV3ReliabilityEngine]
EngineConfig = Dict[str, Any]


def get_engine_class() -> Type[EngineType]:
    """
    Get the appropriate engine class based on OSS configuration
    
    OSS EDITION: Always returns OSS-compatible engines
    """
    # OSS Edition: Check for OSS compatibility
    if not config.is_oss_edition:
        logger.warning(
            "Configuration appears to have Enterprise features. "
            "Using OSS-compatible engine with limited features."
        )
    
    # Check RAG configuration (OSS limited)
    if config.rag_enabled:
        logger.info("Using EnhancedV3ReliabilityEngine with RAG (OSS limits apply)")
        # Verify OSS limits
        if config.rag_max_incident_nodes > 1000:
            logger.warning(
                f"RAG limit exceeded: {config.rag_max_incident_nodes} > 1000 (OSS max). "
                "Will be limited to 1000 nodes."
            )
        return EnhancedV3ReliabilityEngine
    
    # Default to V3 engine for OSS
    logger.info("Using V3ReliabilityEngine (OSS Edition)")
    return V3ReliabilityEngine


def create_reliability_engine(
    engine_config: Optional[EngineConfig] = None,
    force_engine_type: Optional[str] = None
) -> EngineType:
    """
    Create a reliability engine instance
    
    OSS EDITION: Only creates OSS-compatible engines
    
    Args:
        engine_config: Engine configuration dictionary
        force_engine_type: Force specific engine type (for testing)
            Options: "v3", "enhanced_v3", "legacy"
    
    Returns:
        Configured reliability engine instance
    """
    # Start with default config
    final_config: EngineConfig = {
        "max_events_stored": config.max_events_stored,
        "faiss_batch_size": config.faiss_batch_size,
        "rag_enabled": config.rag_enabled,
        "rag_max_incident_nodes": min(config.rag_max_incident_nodes, 1000),  # OSS limit
        "rag_max_outcome_nodes": min(config.rag_max_outcome_nodes, 5000),  # OSS limit
        "mcp_mode": "advisory",  # OSS: Always advisory
        "demo_mode": config.demo_mode,
        "oss_edition": True,  # Mark as OSS edition
    }
    
    # Merge with provided config
    if engine_config:
        # Enforce OSS limits on provided config
        if "rag_max_incident_nodes" in engine_config:
            engine_config["rag_max_incident_nodes"] = min(
                engine_config["rag_max_incident_nodes"], 1000
            )
        if "rag_max_outcome_nodes" in engine_config:
            engine_config["rag_max_outcome_nodes"] = min(
                engine_config["rag_max_outcome_nodes"], 5000
            )
        if "mcp_mode" in engine_config and engine_config["mcp_mode"] != "advisory":
            logger.warning(
                f"OSS only supports advisory mode. "
                f"Ignoring requested mode: {engine_config['mcp_mode']}"
            )
            engine_config["mcp_mode"] = "advisory"
        
        final_config.update(engine_config)
    
    # Determine engine type
    engine_class: Type[EngineType]
    
    if force_engine_type:
        # Forced type (testing/debugging)
        if force_engine_type == "v3":
            engine_class = V3ReliabilityEngine
        elif force_engine_type == "enhanced_v3":
            engine_class = EnhancedV3ReliabilityEngine
        elif force_engine_type == "legacy":
            engine_class = EnhancedReliabilityEngine
        else:
            logger.warning(f"Unknown engine type: {force_engine_type}. Using default.")
            engine_class = get_engine_class()
    else:
        # Auto-detect based on config
        engine_class = get_engine_class()
    
    # Create engine instance
    try:
        engine = engine_class(final_config)
        
        # Add OSS metadata
        engine.oss_edition = True
        engine.requires_enterprise = (
            final_config.get("rag_max_incident_nodes", 0) >= 1000 or
            final_config.get("rag_max_outcome_nodes", 0) >= 5000 or
            final_config.get("mcp_mode", "advisory") != "advisory"
        )
        
        logger.info(f"Created {engine_class.__name__} (OSS Edition)")
        
        if engine.requires_enterprise:
            logger.info(
                "💡 Configuration requires Enterprise upgrade for full features: "
                "https://arf.dev/enterprise"
            )
        
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create reliability engine: {e}")
        # Fallback to basic engine
        logger.info("Falling back to basic V3ReliabilityEngine")
        return V3ReliabilityEngine(final_config)


def create_enhanced_engine(
    enable_rag: bool = False,
    rag_nodes_limit: int = 1000,
    enable_learning: bool = False  # OSS: Always False
) -> EnhancedV3ReliabilityEngine:
    """
    Create enhanced V3 engine with specific features
    
    OSS EDITION: Learning always disabled, RAG limited to 1000 nodes
    
    Args:
        enable_rag: Enable RAG graph (OSS limited to 1000 nodes)
        rag_nodes_limit: Maximum RAG nodes (capped at 1000 in OSS)
        enable_learning: IGNORED in OSS - always False
    
    Returns:
        Enhanced V3 reliability engine
    """
    # OSS: Force learning disabled
    enable_learning = False
    
    # OSS: Cap RAG nodes
    if rag_nodes_limit > 1000:
        logger.warning(
            f"RAG nodes limit capped at 1000 (OSS max). "
            f"Requested: {rag_nodes_limit}"
        )
        rag_nodes_limit = 1000
    
    config_dict: EngineConfig = {
        "rag_enabled": enable_rag,
        "rag_max_incident_nodes": rag_nodes_limit,
        "rag_max_outcome_nodes": min(rag_nodes_limit * 5, 5000),  # OSS limit
        "learning_enabled": False,  # OSS: Always False
        "mcp_mode": "advisory",  # OSS: Always advisory
        "oss_edition": True,
    }
    
    engine = EnhancedV3ReliabilityEngine(config_dict)
    
    # Add OSS capabilities info
    engine.oss_capabilities = {
        "rag_enabled": enable_rag,
        "rag_nodes_limit": rag_nodes_limit,
        "learning_enabled": False,
        "execution_enabled": False,
        "upgrade_available": rag_nodes_limit >= 1000,
        "upgrade_url": "https://arf.dev/enterprise",
    }
    
    return engine


def get_oss_engine_capabilities() -> Dict[str, Any]:
    """
    Get OSS engine capabilities and limits
    
    Returns:
        Dictionary of OSS capabilities
    """
    return {
        "edition": "oss",
        "license": "Apache 2.0",
        "engines_available": {
            "V3ReliabilityEngine": True,
            "EnhancedV3ReliabilityEngine": True,
            "EnhancedReliabilityEngine": True,  # Legacy compatibility
        },
        "limits": {
            "max_rag_incident_nodes": 1000,
            "max_rag_outcome_nodes": 5000,
            "mcp_modes": ["advisory"],
            "learning_enabled": False,
            "persistent_storage": False,
        },
        "capabilities": {
            "rag_analysis": config.rag_enabled,
            "anomaly_detection": True,
            "business_impact": True,
            "forecasting": True,
            "self_healing_advisory": True,
            "self_healing_execution": False,  # OSS: Advisory only
        },
        "requires_enterprise": (
            config.rag_max_incident_nodes >= 1000 or
            config.rag_max_outcome_nodes >= 5000 or
            config.mcp_mode != "advisory"
        ),
        "enterprise_features": [
            "autonomous_execution",
            "approval_workflows",
            "learning_engine",
            "persistent_storage",
            "unlimited_rag_nodes",
            "audit_trails",
        ],
        "upgrade_url": "https://arf.dev/enterprise",
    }


def validate_oss_compatibility(engine_config: EngineConfig) -> Dict[str, Any]:
    """
    Validate engine configuration for OSS compatibility
    
    Args:
        engine_config: Engine configuration to validate
    
    Returns:
        Validation results
    """
    violations = []
    warnings = []
    
    # Check RAG limits
    rag_nodes = engine_config.get("rag_max_incident_nodes", 0)
    if rag_nodes > 1000:
        violations.append(
            f"rag_max_incident_nodes exceeds OSS limit (1000): {rag_nodes}"
        )
    
    rag_outcomes = engine_config.get("rag_max_outcome_nodes", 0)
    if rag_outcomes > 5000:
        violations.append(
            f"rag_max_outcome_nodes exceeds OSS limit (5000): {rag_outcomes}"
        )
    
    # Check MCP mode
    mcp_mode = engine_config.get("mcp_mode", "advisory")
    if mcp_mode != "advisory":
        violations.append(
            f"MCP mode must be 'advisory' in OSS, got: {mcp_mode}"
        )
    
    # Check for Enterprise-only features
    if engine_config.get("learning_enabled", False):
        violations.append("learning_enabled requires Enterprise edition")
    
    if engine_config.get("beta_testing_enabled", False):
        violations.append("beta_testing_enabled requires Enterprise edition")
    
    if engine_config.get("rollout_percentage", 0) > 0:
        violations.append("rollout_percentage requires Enterprise edition")
    
    # Check for deprecated/removed fields
    enterprise_fields = [
        "license_key",
        "audit_trail_enabled",
        "compliance_mode",
        "multi_tenant",
    ]
    
    for field in enterprise_fields:
        if field in engine_config:
            warnings.append(
                f"Field '{field}' is Enterprise-only and will be ignored in OSS"
            )
    
    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "requires_enterprise": len(violations) > 0,
        "oss_compatible": len(violations) == 0,
    }


# Backward compatibility functions
@overload
def get_engine(
    engine_config: Optional[EngineConfig] = None
) -> EngineType: ...

@overload
def get_engine(
    engine_config: Optional[EngineConfig] = None,
    use_enhanced: bool = False
) -> EngineType: ...

def get_engine(
    engine_config: Optional[EngineConfig] = None,
    use_enhanced: bool = False
) -> EngineType:
    """
    Backward compatibility function for getting engine
    
    OSS EDITION: Returns OSS-compatible engine only
    """
    if use_enhanced:
        logger.info("Creating enhanced engine (OSS limits apply)")
        return create_enhanced_engine(
            enable_rag=engine_config.get("rag_enabled", False) if engine_config else False,
            rag_nodes_limit=engine_config.get("rag_max_incident_nodes", 1000) if engine_config else 1000,
        )
    
    return create_reliability_engine(engine_config)


# Export
__all__ = [
    "get_engine_class",
    "create_reliability_engine",
    "create_enhanced_engine",
    "get_oss_engine_capabilities",
    "validate_oss_compatibility",
    "get_engine",  # Backward compatibility
]
