# arf_core/models/__init__.py
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

# Import from main package for backward compatibility
try:
    from agentic_reliability_framework.models import ReliabilityEvent, EventSeverity
except ImportError:
    # Create stub classes if they don't exist
    from enum import Enum
    
    class EventSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    from dataclasses import dataclass
    from datetime import datetime
    
    @dataclass
    class ReliabilityEvent:
        component: str
        severity: EventSeverity
        latency_p99: float
        error_rate: float
        throughput: float
        cpu_util: float
        memory_util: float
        timestamp: datetime

__all__ = [
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
    "ReliabilityEvent",
    "EventSeverity",
]
