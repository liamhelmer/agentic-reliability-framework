"""
OSS Models Module - ARF Core
Apache 2.0 Licensed

Exports OSS-compatible models from the main models module.
Uses lazy imports to avoid circular dependencies and handle OSS/Enterprise differences.
"""

import sys
from typing import TYPE_CHECKING, Any, Dict, Optional
from datetime import datetime
from enum import Enum

# Use TYPE_CHECKING for static type analysis only
if TYPE_CHECKING:
    from agentic_reliability_framework.models import (
        ReliabilityEvent as PydanticReliabilityEvent,
        EventSeverity as PydanticEventSeverity,
        create_compatible_event as pydantic_create_compatible_event,
        HealingPolicy,
        PolicyCondition,
        HealingAction,
        AnomalyResult,
        ForecastResult,
    )

# Export healing intent components (these are in arf_core, no circular issue)
from .healing_intent import (
    HealingIntent,
    HealingIntentSerializer,
    HealingIntentError,
    SerializationError,
    ValidationError,
    IntentSource,
    IntentStatus,
    create_rollback_intent,
    create_restart_intent,
    create_scale_out_intent,
    create_oss_advisory_intent,
)

# ============================================================================
# OSS EVENT SEVERITY (ALWAYS AVAILABLE)
# ============================================================================

class OSSEventSeverity(Enum):
    """OSS version of EventSeverity - always available"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================================================
# LAZY IMPORT SYSTEM FOR MAIN MODELS
# ============================================================================

# Singleton cache for main models
_MAIN_MODELS_CACHE = {
    "ReliabilityEvent": None,
    "EventSeverity": None,
    "create_compatible_event": None,
    "HealingPolicy": None,
    "PolicyCondition": None,
    "HealingAction": None,
    "AnomalyResult": None,
    "ForecastResult": None,
    "is_pydantic": False,  # Track if we're using Pydantic models
}

def _lazy_import_main_models():
    """Lazily import main models to avoid circular dependencies"""
    try:
        # Try to import from main models module (Pydantic v2)
        from agentic_reliability_framework.models import (
            ReliabilityEvent as PydanticReliabilityEvent,
            EventSeverity as PydanticEventSeverity,
            create_compatible_event as pydantic_create_compatible_event,
            HealingPolicy,
            PolicyCondition,
            HealingAction,
            AnomalyResult,
            ForecastResult,
        )
        
        # Store Pydantic models
        _MAIN_MODELS_CACHE["ReliabilityEvent"] = PydanticReliabilityEvent
        _MAIN_MODELS_CACHE["EventSeverity"] = PydanticEventSeverity
        _MAIN_MODELS_CACHE["create_compatible_event"] = pydantic_create_compatible_event
        _MAIN_MODELS_CACHE["HealingPolicy"] = HealingPolicy
        _MAIN_MODELS_CACHE["PolicyCondition"] = PolicyCondition
        _MAIN_MODELS_CACHE["HealingAction"] = HealingAction
        _MAIN_MODELS_CACHE["AnomalyResult"] = AnomalyResult
        _MAIN_MODELS_CACHE["ForecastResult"] = ForecastResult
        _MAIN_MODELS_CACHE["is_pydantic"] = True
        
        # Log successful import (debug only)
        if "pytest" not in sys.modules:
            import logging
            logging.getLogger(__name__).debug("Loaded Pydantic models from main module")
            
    except ImportError as e:
        # If main models aren't available, create minimal OSS-compatible dataclass versions
        # These are for OSS edition use only
        
        from dataclasses import dataclass, field
        from typing import List
        
        # Use OSS EventSeverity
        _MAIN_MODELS_CACHE["EventSeverity"] = OSSEventSeverity
        
        # Minimal ReliabilityEvent dataclass for OSS
        @dataclass
        class OSSReliabilityEvent:
            component: str
            severity: Any
            latency_p99: float = 100.0
            error_rate: float = 0.05
            throughput: float = 1000.0
            cpu_util: float = 0.5
            memory_util: float = 0.5
            timestamp: datetime = field(default_factory=datetime.now)
            service_mesh: str = "default"
            metadata: Dict[str, Any] = field(default_factory=dict)
            
            def __post_init__(self):
                """Convert severity to string if it's an enum"""
                if hasattr(self.severity, 'value'):
                    self.severity = self.severity.value
                elif isinstance(self.severity, OSSEventSeverity):
                    self.severity = self.severity.value
            
            def to_dict(self) -> Dict[str, Any]:
                """Convert to dictionary format"""
                return {
                    "component": self.component,
                    "severity": self.severity,
                    "latency_p99": self.latency_p99,
                    "error_rate": self.error_rate,
                    "throughput": self.throughput,
                    "cpu_util": self.cpu_util,
                    "memory_util": self.memory_util,
                    "timestamp": self.timestamp.isoformat(),
                    "service_mesh": self.service_mesh,
                    "metadata": self.metadata
                }
            
            @property
            def fingerprint(self) -> str:
                """Generate deterministic fingerprint for event deduplication (OSS version)"""
                import hashlib
                components = [
                    self.component,
                    self.service_mesh,
                    f"{self.latency_p99:.2f}",
                    f"{self.error_rate:.4f}",
                    f"{self.throughput:.2f}"
                ]
                fingerprint_str = ":".join(components)
                return hashlib.sha256(fingerprint_str.encode()).hexdigest()
        
        def oss_create_compatible_event(
            component: str,
            severity: Any,
            latency_p99: float = 100.0,
            error_rate: float = 0.05,
            throughput: float = 1000.0,
            cpu_util: float = 0.5,
            memory_util: float = 0.5,
            timestamp: Optional[datetime] = None,
            service_mesh: str = "default",
            **extra_kwargs: Any
        ) -> OSSReliabilityEvent:
            """Create compatibility event (OSS version)"""
            event_kwargs = {
                "component": component,
                "severity": severity,
                "latency_p99": latency_p99,
                "error_rate": error_rate,
                "throughput": throughput,
                "cpu_util": cpu_util,
                "memory_util": memory_util,
                "service_mesh": service_mesh,
            }
            
            if timestamp is not None:
                event_kwargs["timestamp"] = timestamp
            
            if extra_kwargs:
                event_kwargs["metadata"] = extra_kwargs
            
            return OSSReliabilityEvent(**event_kwargs)
        
        # Store OSS versions
        _MAIN_MODELS_CACHE["ReliabilityEvent"] = OSSReliabilityEvent
        _MAIN_MODELS_CACHE["create_compatible_event"] = oss_create_compatible_event
        _MAIN_MODELS_CACHE["is_pydantic"] = False
        
        # Create minimal stubs for other models (not used in OSS)
        @dataclass
        class StubModel:
            pass
        
        _MAIN_MODELS_CACHE["HealingPolicy"] = StubModel
        _MAIN_MODELS_CACHE["PolicyCondition"] = StubModel
        _MAIN_MODELS_CACHE["HealingAction"] = StubModel
        _MAIN_MODELS_CACHE["AnomalyResult"] = StubModel
        _MAIN_MODELS_CACHE["ForecastResult"] = StubModel

# ============================================================================
# PUBLIC API - LAZY LOADED ATTRIBUTES
# ============================================================================

class _ModelsModule:
    """Module proxy that provides lazy-loaded main models"""
    
    @property
    def ReliabilityEvent(self):
        """Get ReliabilityEvent class (lazy loaded)"""
        if _MAIN_MODELS_CACHE["ReliabilityEvent"] is None:
            _lazy_import_main_models()
        return _MAIN_MODELS_CACHE["ReliabilityEvent"]
    
    @property
    def EventSeverity(self):
        """Get EventSeverity enum (lazy loaded)"""
        if _MAIN_MODELS_CACHE["EventSeverity"] is None:
            _lazy_import_main_models()
        return _MAIN_MODELS_CACHE["EventSeverity"]
    
    @property
    def create_compatible_event(self):
        """Get create_compatible_event function (lazy loaded)"""
        if _MAIN_MODELS_CACHE["create_compatible_event"] is None:
            _lazy_import_main_models()
        return _MAIN_MODELS_CACHE["create_compatible_event"]
    
    @property
    def HealingPolicy(self):
        """Get HealingPolicy class (lazy loaded)"""
        if _MAIN_MODELS_CACHE["HealingPolicy"] is None:
            _lazy_import_main_models()
        return _MAIN_MODELS_CACHE["HealingPolicy"]
    
    @property
    def PolicyCondition(self):
        """Get PolicyCondition class (lazy loaded)"""
        if _MAIN_MODELS_CACHE["PolicyCondition"] is None:
            _lazy_import_main_models()
        return _MAIN_MODELS_CACHE["PolicyCondition"]
    
    @property
    def HealingAction(self):
        """Get HealingAction enum (lazy loaded)"""
        if _MAIN_MODELS_CACHE["HealingAction"] is None:
            _lazy_import_main_models()
        return _MAIN_MODELS_CACHE["HealingAction"]
    
    @property
    def AnomalyResult(self):
        """Get AnomalyResult class (lazy loaded)"""
        if _MAIN_MODELS_CACHE["AnomalyResult"] is None:
            _lazy_import_main_models()
        return _MAIN_MODELS_CACHE["AnomalyResult"]
    
    @property
    def ForecastResult(self):
        """Get ForecastResult class (lazy loaded)"""
        if _MAIN_MODELS_CACHE["ForecastResult"] is None:
            _lazy_import_main_models()
        return _MAIN_MODELS_CACHE["ForecastResult"]
    
    @property
    def is_pydantic(self) -> bool:
        """Check if we're using Pydantic models"""
        return _MAIN_MODELS_CACHE.get("is_pydantic", False)

# Create module proxy instance
_models_proxy = _ModelsModule()

# Export attributes through the proxy
ReliabilityEvent = _models_proxy.ReliabilityEvent
EventSeverity = _models_proxy.EventSeverity
create_compatible_event = _models_proxy.create_compatible_event
HealingPolicy = _models_proxy.HealingPolicy
PolicyCondition = _models_proxy.PolicyCondition
HealingAction = _models_proxy.HealingAction
AnomalyResult = _models_proxy.AnomalyResult
ForecastResult = _models_proxy.ForecastResult
is_pydantic = _models_proxy.is_pydantic

# ============================================================================
# COMPATIBILITY WRAPPERS
# ============================================================================

class ModelCompatibility:
    """
    Compatibility utilities for working with both Pydantic and dataclass models
    
    This provides a consistent API regardless of which implementation is loaded.
    """
    
    @staticmethod
    def create_event(event_data: Dict[str, Any]) -> Any:
        """Create a ReliabilityEvent from data"""
        if _MAIN_MODELS_CACHE["ReliabilityEvent"] is None:
            _lazy_import_main_models()
        
        EventClass = _MAIN_MODELS_CACHE["ReliabilityEvent"]
        
        # Check if it's a Pydantic model
        if hasattr(EventClass, 'model_validate'):
            return EventClass.model_validate(event_data)
        elif hasattr(EventClass, 'parse_obj'):
            # Older Pydantic v1 compatibility
            return EventClass.parse_obj(event_data)
        else:
            # Assume it's a dataclass
            return EventClass(**event_data)
    
    @staticmethod
    def to_dict(obj: Any) -> Dict[str, Any]:
        """Convert any model to dictionary"""
        if hasattr(obj, 'model_dump'):
            # Pydantic v2
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            # Pydantic v1
            return obj.dict()
        elif hasattr(obj, 'to_dict'):
            # Our OSS dataclass
            return obj.to_dict()
        else:
            # Fallback: use __dict__
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    
    @staticmethod
    def to_json(obj: Any) -> str:
        """Convert any model to JSON"""
        import json
        obj_dict = ModelCompatibility.to_dict(obj)
        return json.dumps(obj_dict, default=str)
    
    @staticmethod
    def get_fingerprint(event: Any) -> str:
        """Get fingerprint from event (works with both Pydantic and dataclass)"""
        if hasattr(event, 'fingerprint'):
            return event.fingerprint
        elif hasattr(event, 'fingerprint'):
            # Property access
            return event.fingerprint
        else:
            # Generate fingerprint from data
            import hashlib
            event_dict = ModelCompatibility.to_dict(event)
            key_fields = ["component", "service_mesh", "latency_p99", "error_rate", "throughput"]
            components = [str(event_dict.get(field, "")) for field in key_fields]
            fingerprint_str = ":".join(components)
            return hashlib.sha256(fingerprint_str.encode()).hexdigest()

# Create compatibility instance
model_compat = ModelCompatibility()

# ============================================================================
# OSS-SPECIFIC UTILITIES
# ============================================================================

def is_oss_edition() -> bool:
    """Check if we're running in OSS edition"""
    # Check if we're using Pydantic models (Enterprise) or dataclass (OSS)
    if _MAIN_MODELS_CACHE["is_pydantic"] is None:
        _lazy_import_main_models()
    return not _MAIN_MODELS_CACHE["is_pydantic"]

def get_model_type() -> str:
    """Get the type of models being used"""
    if _MAIN_MODELS_CACHE["is_pydantic"] is None:
        _lazy_import_main_models()
    return "pydantic" if _MAIN_MODELS_CACHE["is_pydantic"] else "dataclass"

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Healing Intent (from arf_core)
    "HealingIntent",
    "HealingIntentSerializer",
    "HealingIntentError",
    "SerializationError",
    "ValidationError",
    "IntentSource",
    "IntentStatus",
    "create_rollback_intent",
    "create_restart_intent",
    "create_scale_out_intent",
    "create_oss_advisory_intent",
    
    # Main models (lazy loaded)
    "ReliabilityEvent",
    "EventSeverity",
    "create_compatible_event",
    "HealingPolicy",
    "PolicyCondition",
    "HealingAction",
    "AnomalyResult",
    "ForecastResult",
    
    # Model info
    "is_pydantic",
    "is_oss_edition",
    "get_model_type",
    
    # Compatibility utilities
    "model_compat",
    "ModelCompatibility",
]

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Pre-load main models if we're not in a test environment
# This ensures they're available when needed
if "pytest" not in sys.modules and "test" not in sys.argv[0]:
    try:
        _lazy_import_main_models()
    except Exception:
        # Silently fail - models will be loaded on demand
        pass
