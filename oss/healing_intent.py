# agentic_reliability_framework/oss/healing_intent.py
"""
Healing Intent - OSS creates, Enterprise executes
Core boundary pattern between OSS intelligence and Enterprise execution
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List, ClassVar
from datetime import datetime
import hashlib
import json
import uuid
import time


@dataclass(frozen=True)
class HealingIntent:
    """
    OSS-generated healing recommendation
    
    This is the clean boundary between OSS intelligence and Enterprise execution:
    - OSS creates HealingIntent through analysis
    - Enterprise executes HealingIntent through MCP server
    """
    
    # === CORE ACTION FIELDS (Sent to Enterprise) ===
    action: str                          # Tool name, e.g., "restart_container"
    component: str                       # Target component
    parameters: Dict[str, Any] = field(default_factory=dict)  # Action parameters
    justification: str = ""              # OSS reasoning chain
    
    # === CONFIDENCE & METADATA ===
    confidence: float = 0.85             # OSS confidence score (0.0 to 1.0)
    incident_id: str = ""                # Source incident identifier
    detected_at: float = field(default_factory=time.time)  # When OSS detected
    
    # === OSS ANALYSIS CONTEXT (Stays in OSS) ===
    reasoning_chain: Optional[List[Dict[str, Any]]] = None
    similar_incidents: Optional[List[Dict[str, Any]]] = None
    policy_applied: Optional[str] = None
    rag_similarity_score: Optional[float] = None
    
    # === IMMUTABLE IDENTIFIER ===
    intent_id: str = field(default_factory=lambda: f"intent_{uuid.uuid4().hex[:16]}")
    
    # Class constants for validation
    MIN_CONFIDENCE: ClassVar[float] = 0.0
    MAX_CONFIDENCE: ClassVar[float] = 1.0
    MAX_JUSTIFICATION_LENGTH: ClassVar[int] = 1000
    
    def __post_init__(self):
        """Validate HealingIntent after initialization"""
        # Validate confidence range
        if not (self.MIN_CONFIDENCE <= self.confidence <= self.MAX_CONFIDENCE):
            raise ValueError(
                f"Confidence must be between {self.MIN_CONFIDENCE} and "
                f"{self.MAX_CONFIDENCE}, got {self.confidence}"
            )
        
        # Validate justification length
        if len(self.justification) > self.MAX_JUSTIFICATION_LENGTH:
            raise ValueError(
                f"Justification exceeds max length {self.MAX_JUSTIFICATION_LENGTH}"
            )
        
        # Ensure parameters is serializable
        try:
            json.dumps(self.parameters)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Parameters must be JSON serializable: {e}")
    
    @property
    def deterministic_id(self) -> str:
        """
        Deterministic ID for idempotency based on action + component + parameters
        """
        data = {
            "action": self.action,
            "component": self.component,
            "parameters": self._normalize_parameters(self.parameters),
            "incident_id": self.incident_id,
            "detected_at": int(self.detected_at),
        }
        
        json_str = json.dumps(data, sort_keys=True, default=str)
        hash_digest = hashlib.sha256(json_str.encode()).hexdigest()
        return f"intent_{hash_digest[:16]}"
    
    def to_enterprise_request(self) -> Dict[str, Any]:
        """
        Convert to Enterprise API request format
        """
        return {
            # Core execution fields
            "intent_id": self.deterministic_id,
            "action": self.action,
            "component": self.component,
            "parameters": self.parameters,
            "justification": self.justification,
            
            # OSS metadata for Enterprise context
            "confidence": self.confidence,
            "incident_id": self.incident_id,
            "detected_at": self.detected_at,
            
            # Enterprise flag
            "requires_enterprise": True,
            
            # Minimal OSS context
            "oss_metadata": {
                "similar_incidents_count": len(self.similar_incidents) if self.similar_incidents else 0,
                "rag_similarity_score": self.rag_similarity_score,
                "has_reasoning_chain": self.reasoning_chain is not None,
            }
        }
    
    def to_mcp_request(self, mode: str = "advisory") -> Dict[str, Any]:
        """
        Convert to existing MCP request format for backward compatibility
        """
        return {
            "request_id": self.intent_id,
            "tool": self.action,
            "component": self.component,
            "parameters": self.parameters,
            "justification": self.justification,
            "mode": mode,
            "timestamp": self.detected_at,
            "metadata": {
                "intent_id": self.deterministic_id,
                "oss_confidence": self.confidence,
                "requires_enterprise": True,
                "oss_generated": True,
            }
        }
    
    @classmethod
    def from_mcp_request(cls, request: Dict[str, Any]) -> "HealingIntent":
        """Create HealingIntent from existing MCP request"""
        return cls(
            action=request.get("tool", ""),
            component=request.get("component", ""),
            parameters=request.get("parameters", {}),
            justification=request.get("justification", ""),
            incident_id=request.get("metadata", {}).get("incident_id", ""),
            detected_at=request.get("timestamp", time.time()),
        )
    
    @classmethod
    def from_analysis(
        cls,
        action: str,
        component: str,
        parameters: Dict[str, Any],
        justification: str,
        confidence: float,
        similar_incidents: Optional[List[Dict[str, Any]]] = None,
        reasoning_chain: Optional[List[Dict[str, Any]]] = None,
        incident_id: str = "",
    ) -> "HealingIntent":
        """Factory method for creating HealingIntent from OSS analysis"""
        enhanced_confidence = confidence
        if similar_incidents:
            enhanced_confidence = min(confidence * 1.1, cls.MAX_CONFIDENCE)
        
        rag_score = None
        if similar_incidents and len(similar_incidents) > 0:
            rag_score = sum(
                inc.get("similarity", 0.0) 
                for inc in similar_incidents[:3]
            ) / min(3, len(similar_incidents))
        
        return cls(
            action=action,
            component=component,
            parameters=parameters,
            justification=justification,
            confidence=enhanced_confidence,
            incident_id=incident_id,
            similar_incidents=similar_incidents,
            reasoning_chain=reasoning_chain,
            rag_similarity_score=rag_score,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealingIntent":
        """Create from dictionary"""
        return cls(**data)
    
    def _normalize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize parameters for deterministic hashing"""
        normalized = {}
        
        for key, value in sorted(params.items()):
            if isinstance(value, (int, float, str, bool, type(None))):
                normalized[key] = value
            elif isinstance(value, (list, tuple)):
                normalized[key] = tuple(self._normalize_parameters(v) if isinstance(v, dict) else v 
                                      for v in value)
            elif isinstance(value, dict):
                normalized[key] = self._normalize_parameters(value)
            else:
                normalized[key] = str(value)
        
        return normalized
    
    def get_oss_context(self) -> Dict[str, Any]:
        """Get OSS analysis context (stays in OSS)"""
        return {
            "reasoning_chain": self.reasoning_chain,
            "similar_incidents": self.similar_incidents,
            "policy_applied": self.policy_applied,
            "rag_similarity_score": self.rag_similarity_score,
            "analysis_timestamp": datetime.fromtimestamp(self.detected_at).isoformat(),
        }


# Serializer for versioned serialization
class HealingIntentSerializer:
    """Versioned serialization for backward compatibility"""
    
    @staticmethod
    def serialize(intent: HealingIntent, version: int = 1) -> Dict[str, Any]:
        """Serialize HealingIntent with versioning"""
        if version == 1:
            return {
                "version": 1,
                "data": intent.to_dict(),
                "schema": "healing_intent_v1",
            }
        else:
            raise ValueError(f"Unsupported version: {version}")
    
    @staticmethod
    def deserialize(data: Dict[str, Any]) -> HealingIntent:
        """Deserialize HealingIntent with version detection"""
        version = data.get("version", 1)
        
        if version == 1:
            return HealingIntent.from_dict(data["data"])
        else:
            raise ValueError(f"Unsupported version: {version}")


__all__ = [
    "HealingIntent",
    "HealingIntentSerializer",
]
