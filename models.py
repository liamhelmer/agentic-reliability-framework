from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum
import datetime
import hashlib

class EventSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class HealingAction(Enum):
    RESTART_CONTAINER = "restart_container"
    SCALE_OUT = "scale_out"
    TRAFFIC_SHIFT = "traffic_shift"
    CIRCUIT_BREAKER = "circuit_breaker"
    ROLLBACK = "rollback"
    ALERT_TEAM = "alert_team"
    NO_ACTION = "no_action"

class ReliabilityEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    component: str
    service_mesh: str = "default"
    
    # Core metrics
    latency_p99: float = Field(ge=0)
    error_rate: float = Field(ge=0, le=1)
    throughput: float = Field(ge=0)
    
    # Resource metrics  
    cpu_util: Optional[float] = Field(default=None, ge=0, le=1)
    memory_util: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Business metrics
    revenue_impact: Optional[float] = Field(default=None, ge=0)
    user_impact: Optional[int] = Field(default=None, ge=0)
    
    # Topology context
    upstream_deps: List[str] = Field(default_factory=list)
    downstream_deps: List[str] = Field(default_factory=list)
    
    severity: EventSeverity = EventSeverity.LOW
    fingerprint: str = Field(default="")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Generate fingerprint for deduplication
        if not self.fingerprint:
            fingerprint_str = f"{self.component}_{self.latency_p99}_{self.error_rate}_{self.timestamp}"
            self.fingerprint = hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    class Config:
        use_enum_values = True

class HealingPolicy(BaseModel):
    name: str
    conditions: Dict[str, Any]
    actions: List[HealingAction]
    priority: int = Field(ge=1, le=5)
    cool_down_seconds: int = 300
    enabled: bool = True

class AnomalyResult(BaseModel):
    is_anomaly: bool
    confidence: float
    predicted_cause: str
    recommended_actions: List[HealingAction]
    similar_incidents: List[str] = Field(default_factory=list)
    business_impact: Optional[Dict[str, Any]] = None