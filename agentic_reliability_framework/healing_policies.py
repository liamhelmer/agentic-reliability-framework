"""
Policy Engine for Automated Healing Actions
Fixed version with thread safety and memory leak prevention

ENHANCEMENT: Added confidence basis and deterministic guarantee detection
to support v3 engine requirements.
"""

import datetime
import threading
import logging
from collections import OrderedDict
from typing import Dict, List, Optional, Any, cast, TypedDict
from .models import HealingPolicy, HealingAction, ReliabilityEvent, PolicyCondition
from ..config import config  # Added for OSS/Enterprise detection

logger = logging.getLogger(__name__)


# Action metadata structure for v3 engine compatibility
class ActionMetadata(TypedDict, total=False):
    """Enhanced action metadata for v3 engine"""
    action: str
    confidence: float
    confidence_basis: str
    parameters: Dict[str, Any]
    reason: str
    deterministic_guarantee: bool
    safety_features: List[str]
    reversible: bool
    metadata: Dict[str, Any]


# Default healing policies with structured conditions and enhanced metadata
DEFAULT_HEALING_POLICIES = [
    HealingPolicy(
        name="high_latency_restart",
        conditions=[
            PolicyCondition(metric="latency_p99", operator="gt", threshold=500.0)
        ],
        actions=[HealingAction.RESTART_CONTAINER, HealingAction.ALERT_TEAM],
        priority=1,
        cool_down_seconds=300,
        max_executions_per_hour=5
    ),
    HealingPolicy(
        name="critical_error_rate_rollback",
        conditions=[
            PolicyCondition(metric="error_rate", operator="gt", threshold=0.3)
        ],
        actions=[HealingAction.ROLLBACK, HealingAction.CIRCUIT_BREAKER, HealingAction.ALERT_TEAM],
        priority=1,
        cool_down_seconds=600,
        max_executions_per_hour=3
    ),
    HealingPolicy(
        name="high_error_rate_traffic_shift",
        conditions=[
            PolicyCondition(metric="error_rate", operator="gt", threshold=0.15)
        ],
        actions=[HealingAction.TRAFFIC_SHIFT, HealingAction.ALERT_TEAM],
        priority=2,
        cool_down_seconds=300,
        max_executions_per_hour=5
    ),
    HealingPolicy(
        name="resource_exhaustion_scale",
        conditions=[
            PolicyCondition(metric="cpu_util", operator="gt", threshold=0.9),
            PolicyCondition(metric="memory_util", operator="gt", threshold=0.9)
        ],
        actions=[HealingAction.SCALE_OUT],
        priority=2,
        cool_down_seconds=600,
        max_executions_per_hour=10
    ),
    HealingPolicy(
        name="moderate_latency_circuit_breaker",
        conditions=[
            PolicyCondition(metric="latency_p99", operator="gt", threshold=300.0)
        ],
        actions=[HealingAction.CIRCUIT_BREAKER],
        priority=3,
        cool_down_seconds=180,
        max_executions_per_hour=8
    )
]


class PolicyEngine:
    """
    Thread-safe policy engine with cooldown and rate limiting
    
    ENHANCED for v3:
    - Returns rich action dicts with confidence metadata
    - Adds confidence_basis for v3 engine compatibility
    - Detects deterministic guarantees
    - Integrates with OSS/Enterprise boundaries
    """
    
    def __init__(
        self,
        policies: Optional[List[HealingPolicy]] = None,
        max_cooldown_history: int = 100,
        max_execution_history: int = 1000
    ) -> None:
        """
        Initialize policy engine
        
        Args:
            policies: List of healing policies (uses defaults if None)
            max_cooldown_history: Maximum cooldown entries to keep (LRU)
            max_execution_history: Maximum execution history per policy
        """
        self.policies = policies or DEFAULT_HEALING_POLICIES
        
        # FIXED: Added RLock for thread safety
        self._lock = threading.RLock()
        
        # FIXED: Use OrderedDict for LRU eviction (prevents memory leak)
        self.last_execution: OrderedDict[str, float] = OrderedDict()
        self.max_cooldown_history = max_cooldown_history
        
        # Rate limiting: track executions per hour per policy
        self.execution_timestamps: Dict[str, List[float]] = {}
        self.max_execution_history = max_execution_history
        
        # Sort policies by priority (lower number = higher priority)
        self.policies = sorted(self.policies, key=lambda p: p.priority)
        
        # OSS/Enterprise detection
        self.is_oss_edition = getattr(config, 'is_oss_edition', True)
        
        logger.info(
            f"Initialized PolicyEngine with {len(self.policies)} policies, "
            f"OSS Edition: {self.is_oss_edition}"
        )
    
    def evaluate_policies(self, event: ReliabilityEvent) -> List[ActionMetadata]:
        """
        Evaluate all policies against the event and return enhanced actions
        
        ENHANCED: Returns rich action dicts with confidence metadata for v3 compatibility
        
        Args:
            event: Reliability event to evaluate
            
        Returns:
            List of enhanced healing actions with metadata
        """
        applicable_actions: List[ActionMetadata] = []
        current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()
        
        # Evaluate policies in priority order
        for policy in self.policies:
            if not policy.enabled:
                continue
            
            policy_key = f"{policy.name}_{event.component}"
            
            # All cooldown operations under lock (atomic)
            with self._lock:
                # Check cooldown
                last_exec = self.last_execution.get(policy_key, 0)
                
                if current_time - last_exec < policy.cool_down_seconds:
                    logger.debug(
                        f"Policy {policy.name} for {event.component} on cooldown "
                        f"({current_time - last_exec:.0f}s / {policy.cool_down_seconds}s)"
                    )
                    continue
                
                # Check rate limit
                if self._is_rate_limited(policy_key, policy, current_time):
                    logger.warning(
                        f"Policy {policy.name} for {event.component} rate limited "
                        f"(max {policy.max_executions_per_hour}/hour)"
                    )
                    continue
                
                # Evaluate conditions first
                should_execute = self._evaluate_conditions(policy.conditions, event)
                
                if should_execute:
                    # Convert policy actions to enhanced action dicts
                    enhanced_actions = self._enhance_actions(
                        policy.actions, 
                        policy, 
                        event
                    )
                    applicable_actions.extend(enhanced_actions)
                    
                    # Update cooldown timestamp
                    self._update_cooldown(policy_key, current_time)
                    
                    # Track execution for rate limiting
                    self._record_execution(policy_key, current_time)
                    
                    logger.info(
                        f"Policy {policy.name} triggered for {event.component}: "
                        f"actions={[a.get('action', 'unknown') for a in enhanced_actions]}"
                    )
        
        # If no actions, return NO_ACTION with advisory metadata
        if not applicable_actions:
            return [self._create_no_action_metadata(event)]
        
        # Deduplicate actions while preserving order
        seen = set()
        unique_actions: List[ActionMetadata] = []
        for action in applicable_actions:
            action_key = action.get("action", "")
            if action_key not in seen:
                seen.add(action_key)
                unique_actions.append(action)
        
        return unique_actions
    
    def _enhance_actions(
        self, 
        actions: List[HealingAction], 
        policy: HealingPolicy,
        event: ReliabilityEvent
    ) -> List[ActionMetadata]:
        """
        Convert HealingAction enums to rich action dicts with metadata
        
        CRITICAL: Adds confidence_basis, deterministic guarantees, and other
        metadata required by v3 engine.
        
        Args:
            actions: List of HealingAction enums
            policy: Source policy
            event: Triggering event
            
        Returns:
            List of enhanced action dicts
        """
        enhanced: List[ActionMetadata] = []
        
        for action_enum in actions:
            action_name = action_enum.value
            
            # Base action metadata
            action_meta: ActionMetadata = {
                "action": action_name,
                "confidence": self._calculate_confidence(action_enum, policy, event),
                "confidence_basis": "policy_only",  # Default, can be enhanced
                "parameters": self._get_action_parameters(action_enum, event),
                "reason": f"Triggered by policy '{policy.name}' for {event.component}",
                "deterministic_guarantee": self._has_deterministic_guarantee(action_enum),
                "safety_features": self._get_safety_features(action_enum),
                "reversible": self._is_reversible(action_enum),
                "metadata": {
                    "policy_name": policy.name,
                    "policy_priority": policy.priority,
                    "event_component": event.component,
                    "event_severity": getattr(event.severity, 'value', 'low'),
                    "oss_edition": self.is_oss_edition,
                    "execution_allowed": not self.is_oss_edition,  # OSS never executes
                    "requires_enterprise": self.is_oss_edition,
                }
            }
            
            # Enhance confidence basis based on action type
            if action_meta["deterministic_guarantee"]:
                action_meta["confidence_basis"] = "deterministic_guarantee"
                action_meta["confidence"] = min(0.98, action_meta["confidence"] + 0.2)
            elif action_enum in [HealingAction.RESTART_CONTAINER, HealingAction.SCALE_OUT]:
                action_meta["confidence_basis"] = "policy_plus_safety"
                action_meta["confidence"] = min(0.9, action_meta["confidence"] + 0.1)
            
            # Add OSS advisory flag if needed
            if self.is_oss_edition:
                action_meta["metadata"]["oss_advisory"] = True
                action_meta["metadata"]["advisory_reason"] = "OSS edition only supports advisory mode"
            
            enhanced.append(action_meta)
        
        return enhanced
    
    def _calculate_confidence(
        self, 
        action: HealingAction, 
        policy: HealingPolicy,
        event: ReliabilityEvent
    ) -> float:
        """
        Calculate confidence score for an action
        
        Args:
            action: Healing action
            policy: Source policy
            event: Triggering event
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.7
        
        # Adjust based on policy priority (higher priority = more confidence)
        priority_boost = (4 - min(policy.priority, 4)) * 0.05
        base_confidence += priority_boost
        
        # Adjust based on action type
        action_confidence_map = {
            HealingAction.ALERT_TEAM: 0.1,
            HealingAction.CIRCUIT_BREAKER: 0.15,
            HealingAction.TRAFFIC_SHIFT: 0.2,
            HealingAction.SCALE_OUT: 0.25,
            HealingAction.RESTART_CONTAINER: 0.3,
            HealingAction.ROLLBACK: 0.35,
            HealingAction.NO_ACTION: 0.0,
        }
        
        base_confidence += action_confidence_map.get(action, 0.0)
        
        # Adjust based on event severity
        severity = getattr(event.severity, 'value', 'low')
        severity_boost = {
            'low': 0.0,
            'medium': 0.05,
            'high': 0.1,
            'critical': 0.15,
        }.get(severity, 0.0)
        
        base_confidence += severity_boost
        
        # Cap at 0.95 (leave room for RAG/historical enhancement)
        return min(0.95, base_confidence)
    
    def _get_action_parameters(
        self, 
        action: HealingAction, 
        event: ReliabilityEvent
    ) -> Dict[str, Any]:
        """
        Get default parameters for an action
        
        Args:
            action: Healing action
            event: Triggering event
            
        Returns:
            Action parameters
        """
        base_params = {
            "component": event.component,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        
        # Action-specific parameters
        if action == HealingAction.RESTART_CONTAINER:
            base_params["force"] = True
            base_params["timeout_seconds"] = 30
        elif action == HealingAction.SCALE_OUT:
            base_params["scale_factor"] = 2
            base_params["min_replicas"] = 1
            base_params["max_replicas"] = 10
        elif action == HealingAction.ROLLBACK:
            base_params["revision"] = "previous"
            base_params["preserve_config"] = True
        elif action == HealingAction.CIRCUIT_BREAKER:
            base_params["failure_threshold"] = 3
            base_params["timeout_seconds"] = 60
        
        return base_params
    
    def _has_deterministic_guarantee(self, action: HealingAction) -> bool:
        """
        Check if action has deterministic safety guarantees
        
        Args:
            action: Healing action
            
        Returns:
            True if action has deterministic guarantees
        """
        deterministic_actions = {
            HealingAction.RESTART_CONTAINER,
            HealingAction.SCALE_OUT,
            HealingAction.TOGGLE_FEATURE_FLAG,
            HealingAction.CLEAR_CACHE,
            HealingAction.RESET_CONNECTION_POOL,
        }
        
        return action in deterministic_actions
    
    def _get_safety_features(self, action: HealingAction) -> List[str]:
        """
        Get safety features for an action
        
        Args:
            action: Healing action
            
        Returns:
            List of safety features
        """
        safety_map = {
            HealingAction.RESTART_CONTAINER: ["rollback", "health_check", "timeout"],
            HealingAction.SCALE_OUT: ["auto_scaling", "resource_limits", "monitoring"],
            HealingAction.ROLLBACK: ["revision_control", "health_check", "gradual_rollout"],
            HealingAction.CIRCUIT_BREAKER: ["automatic_recovery", "monitoring", "alerting"],
            HealingAction.TRAFFIC_SHIFT: ["canary", "gradual", "rollback"],
        }
        
        return safety_map.get(action, [])
    
    def _is_reversible(self, action: HealingAction) -> bool:
        """
        Check if action is reversible
        
        Args:
            action: Healing action
            
        Returns:
            True if action is reversible
        """
        reversible_actions = {
            HealingAction.SCALE_OUT,
            HealingAction.TOGGLE_FEATURE_FLAG,
            HealingAction.TRAFFIC_SHIFT,
            HealingAction.CIRCUIT_BREAKER,
        }
        
        return action in reversible_actions
    
    def _create_no_action_metadata(self, event: ReliabilityEvent) -> ActionMetadata:
        """
        Create NO_ACTION metadata for when no policies trigger
        
        Args:
            event: Reliability event
            
        Returns:
            NO_ACTION metadata
        """
        return {
            "action": "no_action",
            "confidence": 0.95,
            "confidence_basis": "policy_only",
            "parameters": {
                "component": event.component,
                "reason": "No applicable policies matched the event",
            },
            "reason": "Event did not match any policy conditions",
            "deterministic_guarantee": False,
            "safety_features": [],
            "reversible": True,
            "metadata": {
                "event_component": event.component,
                "policy_evaluated": True,
                "oss_edition": self.is_oss_edition,
            }
        }
    
    def _evaluate_conditions(
        self,
        conditions: List[PolicyCondition],
        event: ReliabilityEvent
    ) -> bool:
        """
        Evaluate all conditions against event (AND logic)
        
        Args:
            conditions: List of policy conditions
            event: Reliability event
            
        Returns:
            True if all conditions match, False otherwise
        """
        for condition in conditions:
            # Get event value
            event_value = getattr(event, condition.metric, None)
            
            # Handle None values
            if event_value is None:
                logger.debug(
                    f"Condition failed: {condition.metric} is None on event"
                )
                return False
            
            # Evaluate operator
            if not self._compare_values(
                float(event_value),  # Ensure float type
                condition.operator,
                condition.threshold
            ):
                logger.debug(
                    f"Condition failed: {event_value} {condition.operator} "
                    f"{condition.threshold} = False"
                )
                return False
        
        return True
    
    def _compare_values(
        self,
        event_value: float,
        operator: str,
        threshold: float
    ) -> bool:
        """
        Compare values based on operator with type safety
        
        FIXED: Added type checking and better error handling
        
        Args:
            event_value: Value from event
            operator: Comparison operator
            threshold: Threshold value
            
        Returns:
            Comparison result
        """
        try:
            # Operator evaluation
            if operator == "gt":
                return event_value > threshold
            elif operator == "lt":
                return event_value < threshold
            elif operator == "eq":
                return abs(event_value - threshold) < 1e-6  # Float equality
            elif operator == "gte":
                return event_value >= threshold
            elif operator == "lte":
                return event_value <= threshold
            else:
                logger.error(f"Unknown operator: {operator}")
                return False
                
        except (TypeError, ValueError) as e:
            logger.error(f"Comparison error: {e}", exc_info=True)
            return False
    
    def _update_cooldown(self, policy_key: str, timestamp: float) -> None:
        """
        Update cooldown timestamp with LRU eviction
        
        FIXED: Prevents unbounded memory growth
        
        Args:
            policy_key: Policy identifier
            timestamp: Current timestamp
        """
        # Update timestamp
        self.last_execution[policy_key] = timestamp
        
        # Move to end (most recently used)
        self.last_execution.move_to_end(policy_key)
        
        # LRU eviction if too large
        while len(self.last_execution) > self.max_cooldown_history:
            old_key = next(iter(self.last_execution))
            self.last_execution.popitem(last=False)
            logger.debug(f"Evicted cooldown entry: {old_key}")
    
    def _is_rate_limited(
        self,
        policy_key: str,
        policy: HealingPolicy,
        current_time: float
    ) -> bool:
        """
        Check if policy is rate limited
        
        Args:
            policy_key: Policy identifier
            policy: Policy configuration
            current_time: Current timestamp
            
        Returns:
            True if rate limited, False otherwise
        """
        if policy_key not in self.execution_timestamps:
            return False
        
        # Remove executions older than 1 hour
        one_hour_ago = current_time - 3600
        timestamps = self.execution_timestamps[policy_key]
        recent_executions = [
            ts for ts in timestamps
            if ts > one_hour_ago
        ]
        
        self.execution_timestamps[policy_key] = recent_executions
        
        # Check rate limit
        return len(recent_executions) >= policy.max_executions_per_hour
    
    def _record_execution(self, policy_key: str, timestamp: float) -> None:
        """
        Record policy execution for rate limiting
        
        Args:
            policy_key: Policy identifier
            timestamp: Execution timestamp
        """
        if policy_key not in self.execution_timestamps:
            self.execution_timestamps[policy_key] = []
        
        self.execution_timestamps[policy_key].append(timestamp)
        
        # Limit history size (memory management)
        if len(self.execution_timestamps[policy_key]) > self.max_execution_history:
            # Keep only the most recent entries
            timestamps = self.execution_timestamps[policy_key]
            self.execution_timestamps[policy_key] = \
                timestamps[-self.max_execution_history:]
    
    def get_policy_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics about policy execution
        
        Returns:
            Dictionary of policy statistics
        """
        with self._lock:
            stats: Dict[str, Dict[str, Any]] = {}
            
            for policy in self.policies:
                # Count components for this policy
                total_components = 0
                for key in self.last_execution.keys():
                    if key.startswith(f"{policy.name}_"):
                        total_components += 1
                
                policy_stats = {
                    "name": policy.name,
                    "priority": policy.priority,
                    "enabled": policy.enabled,
                    "cooldown_seconds": policy.cool_down_seconds,
                    "max_per_hour": policy.max_executions_per_hour,
                    "total_components": total_components,
                    "oss_edition": self.is_oss_edition,
                }
                
                stats[policy.name] = policy_stats
            
            return stats


# Helper function to create a default policy engine
def create_default_policy_engine() -> PolicyEngine:
    """
    Create a default policy engine with standard policies
    
    Returns:
        PolicyEngine instance
    """
    return PolicyEngine()


# Helper function to test if a policy would trigger for an event
def would_policy_trigger(
    policy: HealingPolicy,
    event: ReliabilityEvent,
    last_execution_time: Optional[float] = None,
    execution_count_last_hour: int = 0
) -> bool:
    """
    Test if a policy would trigger for an event without actually executing it
    
    Args:
        policy: The policy to test
        event: The event to test against
        last_execution_time: Optional last execution time (for cooldown check)
        execution_count_last_hour: Number of executions in last hour (for rate limit)
        
    Returns:
        True if policy would trigger, False otherwise
    """
    # Check if policy is enabled
    if not policy.enabled:
        return False
    
    # Check cooldown if last_execution_time provided
    if last_execution_time is not None:
        current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if current_time - last_execution_time < policy.cool_down_seconds:
            return False
    
    # Check rate limit if execution count provided
    if execution_count_last_hour >= policy.max_executions_per_hour:
        return False
    
    # Check conditions
    engine = PolicyEngine(policies=[policy], max_cooldown_history=0)
    
    # Use a temporary evaluation (not thread-safe, but okay for testing)
    for condition in policy.conditions:
        # Get event value
        event_value = getattr(event, condition.metric, None)
        
        # Handle None values
        if event_value is None:
            return False
        
        # Evaluate operator
        if not engine._compare_values(
            float(event_value),
            condition.operator,
            condition.threshold
        ):
            return False
    
    return True
