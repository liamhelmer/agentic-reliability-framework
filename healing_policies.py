import datetime
from models import HealingPolicy, HealingAction, EventSeverity
from typing import Dict, List

# Default healing policies
DEFAULT_HEALING_POLICIES = [
    HealingPolicy(
        name="high_latency_restart",
        conditions={
            "latency_p99": {"operator": ">", "value": 300},
            "error_rate": {"operator": "<", "value": 0.1},
        },
        actions=[HealingAction.RESTART_CONTAINER],
        priority=2
    ),
    HealingPolicy(
        name="cascading_failure", 
        conditions={
            "error_rate": {"operator": ">", "value": 0.15},
        },
        actions=[HealingAction.CIRCUIT_BREAKER, HealingAction.ALERT_TEAM],
        priority=1
    ),
    HealingPolicy(
        name="resource_exhaustion",
        conditions={
            "cpu_util": {"operator": ">", "value": 0.85},
            "memory_util": {"operator": ">", "value": 0.85}
        },
        actions=[HealingAction.SCALE_OUT, HealingAction.ALERT_TEAM],
        priority=1
    ),
    HealingPolicy(
        name="moderate_performance_issue",
        conditions={
            "latency_p99": {"operator": ">", "value": 200},
            "error_rate": {"operator": ">", "value": 0.05}
        },
        actions=[HealingAction.TRAFFIC_SHIFT],
        priority=3
    ),
    HealingPolicy(
        name="critical_failure",
        conditions={
            "latency_p99": {"operator": ">", "value": 500},
            "error_rate": {"operator": ">", "value": 0.1}
        },
        actions=[HealingAction.RESTART_CONTAINER, HealingAction.ALERT_TEAM, HealingAction.TRAFFIC_SHIFT],
        priority=1
    )
]

class PolicyEngine:
    def __init__(self, policies: List[HealingPolicy] = None):
        self.policies = policies or DEFAULT_HEALING_POLICIES
        self.last_execution: Dict[str, float] = {}
    
    def evaluate_policies(self, event) -> List[HealingAction]:
        """Evaluate all policies against the event and return matching actions"""
        applicable_actions = []
        
        for policy in self.policies:
            if not policy.enabled:
                continue
                
            # Check cooldown
            policy_key = f"{policy.name}_{event.component}"
            current_time = datetime.datetime.now().timestamp()
            last_exec = self.last_execution.get(policy_key, 0)
            
            if current_time - last_exec < policy.cool_down_seconds:
                continue
                
            if self._evaluate_conditions(policy.conditions, event):
                applicable_actions.extend(policy.actions)
                self.last_execution[policy_key] = current_time
        
        # Remove duplicates while preserving order
        seen = set()
        unique_actions = []
        for action in applicable_actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)
                
        return unique_actions or [HealingAction.NO_ACTION]
    
    def _evaluate_conditions(self, conditions: Dict, event) -> bool:
        """Evaluate individual conditions against event data"""
        for field, condition in conditions.items():
            operator = condition["operator"]
            value = condition["value"]
            
            # Get event field value
            event_value = getattr(event, field, None)
            
            if not self._compare_values(event_value, operator, value):
                return False
                
        return True
    
    def _compare_values(self, event_value, operator: str, condition_value) -> bool:
        """Compare values based on operator"""
        try:
            if operator == ">":
                return event_value > condition_value
            elif operator == "<":
                return event_value < condition_value
            elif operator == ">=":
                return event_value >= condition_value
            elif operator == "<=":
                return event_value <= condition_value
            elif operator == "==":
                return event_value == condition_value
            elif operator == "in":
                return event_value in condition_value
            elif operator == "not_empty":
                if isinstance(event_value, list):
                    return len(event_value) > 0 == condition_value
                return bool(event_value) == condition_value
            else:
                return False
        except (TypeError, ValueError):
            return False