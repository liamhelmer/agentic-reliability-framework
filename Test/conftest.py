"""
Pytest configuration and shared fixtures for ARF tests

This file contains:
1. Shared fixtures for all test modules
2. Custom pytest markers configuration
3. Test data generators
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone
import asyncio

# ARF imports
from models import (
    ReliabilityEvent, 
    HealingPolicy, 
    PolicyCondition, 
    HealingAction, 
    EventSeverity,
    AnomalyResult,
    ForecastResult
)
from healing_policies import PolicyEngine

# ====================================================================
# ORIGINAL FIXTURES (KEPT FOR BACKWARD COMPATIBILITY)
# ====================================================================

@pytest.fixture
def sample_timeline_metrics():
    """Create sample TimelineMetrics for testing"""
    # Return dict matching what timeline formatter expects
    return {
        "industry_time": 60.0,
        "arf_time": 5.0,
        "time_savings": 55.0,
        "cost_per_minute": 50000.0,
        "cost_savings": 2750000.0,
        "time_improvement_percentage": 91.67
    }


@pytest.fixture
def timeline_calculator():
    """Create TimelineCalculator with test defaults"""
    # Mock calculator since module doesn't exist
    calculator = Mock()
    calculator.calculate_metrics = Mock(return_value=sample_timeline_metrics())
    return calculator


@pytest.fixture
def timeline_formatter():
    """Create TimelineFormatter instance"""
    # Mock formatter
    formatter = Mock()
    formatter.format_markdown = Mock(return_value="# Test Timeline\nTest content")
    return formatter


@pytest.fixture
def mock_business_metrics():
    """Mock BusinessMetricsTracker"""
    tracker = Mock()
    tracker.record_incident = Mock()
    tracker.get_total_savings = Mock(return_value=2750000.0)
    tracker.get_incident_count = Mock(return_value=5)
    return tracker


@pytest.fixture
def mock_enhanced_engine():
    """Mock EnhancedReliabilityEngine"""
    engine = Mock()
    engine.analyze = Mock(return_value={"severity": "CRITICAL", "confidence": 0.95})
    engine.predict = Mock(return_value={"risk_level": "HIGH", "time_to_failure": 15})
    return engine


@pytest.fixture
def sample_incident_data():
    """Create sample incident data for testing"""
    return {
        "component": "api-service",
        "latency": 450.0,
        "latency_p99": 650.0,
        "error_rate": 0.22,
        "throughput": 8500.0,
        "cpu_utilization": 0.95,
        "memory_utilization": 0.88,
        "severity": "CRITICAL",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def sample_timeline_display():
    """Create sample timeline markdown display"""
    return """# Incident Timeline Comparison

## ⏱️ Industry Average Timeline: 60.0 minutes
███ 60.0 min (Industry)

## 🚀 ARF Response Timeline: 5.0 minutes
█ 5.0 min (ARF)

## 💰 Business Impact
- **Time Saved**: 55.0 minutes (91.7% faster)
- **Cost Saved**: $2,750,000.00
- **Revenue Protected**: $2,750,000.00
"""


# ====================================================================
# POLICY ENGINE FIXTURES (FIXED VERSION)
# ====================================================================

@pytest.fixture
def policy_engine():
    """Create a real PolicyEngine instance for testing"""
    policies = [
        HealingPolicy(
            name="high_latency_policy",
            conditions=[
                PolicyCondition(metric="latency_p99", operator="gt", threshold=500.0)
            ],
            actions=[HealingAction.RESTART_CONTAINER],
            priority=1,
            enabled=True,
            cool_down_seconds=300,
            max_executions_per_hour=10
        ),
        HealingPolicy(
            name="high_error_rate_policy",
            conditions=[
                PolicyCondition(metric="error_rate", operator="gt", threshold=0.3)
            ],
            actions=[HealingAction.ROLLBACK],
            priority=2,
            enabled=True,
            cool_down_seconds=600,
            max_executions_per_hour=5
        ),
        HealingPolicy(
            name="high_cpu_policy",
            conditions=[
                PolicyCondition(metric="cpu_utilization", operator="gt", threshold=0.9)
            ],
            actions=[HealingAction.SCALE_OUT],
            priority=3,
            enabled=True,
            cool_down_seconds=300
        )
    ]
    return PolicyEngine(policies=policies)


@pytest.fixture
def sample_policy():
    """Create a sample healing policy for testing"""
    return HealingPolicy(
        name="test_policy",
        conditions=[
            PolicyCondition(metric="latency_p99", operator="gt", threshold=500.0)
        ],
        actions=[HealingAction.RESTART_CONTAINER],
        priority=1,
        enabled=True,
        cool_down_seconds=300,
        max_executions_per_hour=10
    )


@pytest.fixture
def sample_event():
    """Create a sample event for policy testing"""
    return ReliabilityEvent(
        component="test-service",
        latency=600.0,
        latency_p99=800.0,
        error_rate=0.1,
        throughput=1000.0,
        cpu_utilization=0.5,
        memory_utilization=0.6,
        severity=EventSeverity.MEDIUM,
        timestamp=datetime.now(timezone.utc),
        dependencies=[],
        metadata={"test": "data"}
    )


@pytest.fixture
def normal_event():
    """Event that won't trigger policies"""
    return ReliabilityEvent(
        component="test-service",
        latency=100.0,
        latency_p99=150.0,
        error_rate=0.01,
        throughput=1000.0,
        cpu_utilization=0.3,
        memory_utilization=0.4,
        severity=EventSeverity.LOW,
        timestamp=datetime.now(timezone.utc),
        dependencies=[],
        metadata={"environment": "test"}
    )


@pytest.fixture
def critical_event():
    """Event that will trigger critical policies"""
    return ReliabilityEvent(
        component="test-service",
        latency=800.0,
        latency_p99=1200.0,
        error_rate=0.5,
        throughput=1000.0,
        cpu_utilization=0.95,
        memory_utilization=0.95,
        severity=EventSeverity.CRITICAL,
        timestamp=datetime.now(timezone.utc),
        dependencies=[],
        metadata={"alert": "critical"}
    )


@pytest.fixture
def high_latency_event():
    """Event specifically for testing latency policies"""
    return ReliabilityEvent(
        component="api-service",
        latency=550.0,
        latency_p99=750.0,  # Above 500 threshold
        error_rate=0.05,
        throughput=1200.0,
        cpu_utilization=0.4,
        memory_utilization=0.5,
        severity=EventSeverity.HIGH,
        timestamp=datetime.now(timezone.utc),
        dependencies=["database-service", "cache-service"],
        metadata={"region": "us-east-1"}
    )


@pytest.fixture
def high_error_rate_event():
    """Event specifically for testing error rate policies"""
    return ReliabilityEvent(
        component="payment-service",
        latency=200.0,
        latency_p99=300.0,
        error_rate=0.45,  # Above 0.3 threshold
        throughput=800.0,
        cpu_utilization=0.6,
        memory_utilization=0.7,
        severity=EventSeverity.HIGH,
        timestamp=datetime.now(timezone.utc),
        dependencies=["auth-service", "fraud-service"],
        metadata={"payment_gateway": "stripe"}
    )


@pytest.fixture
def high_cpu_event():
    """Event specifically for testing CPU policies"""
    return ReliabilityEvent(
        component="compute-service",
        latency=300.0,
        latency_p99=450.0,
        error_rate=0.02,
        throughput=2000.0,
        cpu_utilization=0.92,  # Above 0.9 threshold
        memory_utilization=0.65,
        severity=EventSeverity.MEDIUM,
        timestamp=datetime.now(timezone.utc),
        dependencies=["load-balancer"],
        metadata={"instance_type": "c5.4xlarge"}
    )


# ====================================================================
# METRICS & FORMATTER FIXTURES
# ====================================================================

@pytest.fixture
def sample_metrics():
    """Create sample metrics for timeline formatter tests"""
    return {
        "industry_time": 60.0,
        "arf_time": 5.0,
        "time_savings": 55.0,
        "cost_per_minute": 50000.0,
        "cost_savings": 2750000.0,
        "time_improvement_percentage": 91.67,
        "component": "api-service",
        "severity": "CRITICAL"
    }


@pytest.fixture
def sample_anomaly_result():
    """Create sample AnomalyResult for testing"""
    return AnomalyResult(
        component="test-service",
        anomaly_score=0.85,
        confidence=0.92,
        detected_at=datetime.now(timezone.utc),
        metrics={
            "latency_p99": 650.0,
            "error_rate": 0.25,
            "cpu_utilization": 0.88
        },
        reason="Latency spike detected with high confidence"
    )


@pytest.fixture
def sample_forecast_result():
    """Create sample ForecastResult for testing"""
    return ForecastResult(
        component="test-service",
        predicted_metric="latency_p99",
        predicted_value=750.0,
        confidence=0.78,
        trend="INCREASING",
        risk_level="HIGH",
        time_to_failure_minutes=25,
        forecasted_at=datetime.now(timezone.utc)
    )


# ====================================================================
# ASYNC & PERFORMANCE FIXTURES
# ====================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def async_policy_engine():
    """Async version of policy engine for testing"""
    from healing_policies import PolicyEngine
    from models import HealingPolicy, PolicyCondition, HealingAction
    
    policies = [
        HealingPolicy(
            name="async_test_policy",
            conditions=[
                PolicyCondition(metric="latency_p99", operator="gt", threshold=400.0)
            ],
            actions=[HealingAction.ALERT_TEAM],
            priority=2,
            enabled=True
        )
    ]
    return PolicyEngine(policies=policies)


# ====================================================================
# TEST DATA GENERATORS
# ====================================================================

@pytest.fixture
def generate_events():
    """Generate multiple events for testing"""
    def _generate_events(count=10, base_latency=100.0, severity=EventSeverity.MEDIUM):
        events = []
        for i in range(count):
            event = ReliabilityEvent(
                component=f"service-{i}",
                latency=base_latency + (i * 10),
                latency_p99=(base_latency + (i * 10)) * 1.5,
                error_rate=0.01 + (i * 0.02),
                throughput=float(1000 + (i * 100)),
                cpu_utilization=0.3 + (i * 0.05),
                memory_utilization=0.4 + (i * 0.04),
                severity=severity,
                timestamp=datetime.now(timezone.utc),
                dependencies=[f"dependency-{j}" for j in range(i % 3)],
                metadata={"index": i, "generated": True}
            )
            events.append(event)
        return events
    return _generate_events


@pytest.fixture
def generate_policies():
    """Generate multiple policies for testing"""
    def _generate_policies(count=5):
        policies = []
        for i in range(count):
            policy = HealingPolicy(
                name=f"policy-{i}",
                conditions=[
                    PolicyCondition(
                        metric="latency_p99",
                        operator="gt",
                        threshold=200.0 + (i * 100)
                    )
                ],
                actions=[HealingAction.RESTART_CONTAINER],
                priority=i + 1,
                enabled=True,
                cool_down_seconds=300
            )
            policies.append(policy)
        return policies
    return _generate_policies


# ====================================================================
# EDGE CASE FIXTURES
# ====================================================================

@pytest.fixture
def minimal_event():
    """Event with minimal required fields (for testing defaults)"""
    return ReliabilityEvent(
        component="minimal-service",
        latency=0.0,
        latency_p99=0.0,
        error_rate=0.0,
        throughput=0.0,
        cpu_utilization=0.0,
        memory_utilization=0.0,
        severity=EventSeverity.LOW,
        timestamp=datetime.now(timezone.utc),
        dependencies=[],
        metadata={}
    )


@pytest.fixture
def extreme_values_event():
    """Event with extreme values for boundary testing"""
    return ReliabilityEvent(
        component="extreme-service",
        latency=999999.0,
        latency_p99=1999999.0,
        error_rate=1.0,  # Maximum
        throughput=9999999.0,
        cpu_utilization=1.0,  # Maximum
        memory_utilization=1.0,  # Maximum
        severity=EventSeverity.CRITICAL,
        timestamp=datetime.now(timezone.utc),
        dependencies=["dep1", "dep2", "dep3", "dep4", "dep5"],
        metadata={
            "test": "extreme",
            "load": "very_high",
            "region": "moon-base-alpha"
        }
    )


@pytest.fixture
def event_with_dependencies():
    """Event with complex dependency tree"""
    return ReliabilityEvent(
        component="main-service",
        latency=150.0,
        latency_p99=225.0,
        error_rate=0.03,
        throughput=5000.0,
        cpu_utilization=0.45,
        memory_utilization=0.55,
        severity=EventSeverity.MEDIUM,
        timestamp=datetime.now(timezone.utc),
        dependencies=[
            "database-primary",
            "database-replica",
            "redis-cache",
            "auth-service",
            "payment-service",
            "notification-service"
        ],
        metadata={
            "tier": "production",
            "version": "v2.5.1",
            "team": "platform-engineering"
        }
    )


# ====================================================================
# PYTEST CONFIGURATION
# ====================================================================

def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", 
        "integration: mark test as integration test (requires external services)"
    )
    config.addinivalue_line(
        "markers", 
        "unit: mark test as unit test (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", 
        "benchmark: mark test as performance benchmark"
    )
    config.addinivalue_line(
        "markers", 
        "slow: mark test as slow running (>1 second)"
    )
    config.addinivalue_line(
        "markers",
        "async_test: mark test as async test (requires event loop)"
    )
    config.addinivalue_line(
        "markers",
        "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers",
        "production: mark test as production-only (requires prod-like environment)"
    )


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test"""
    pass  # Placeholder for any global test setup


# ====================================================================
# TEST HELPER FUNCTIONS
# ====================================================================

@pytest.fixture
def assert_event_equal():
    """Helper to assert two events are equal"""
    def _assert_event_equal(event1, event2, ignore_timestamp=False):
        assert event1.component == event2.component
        assert event1.latency == event2.latency
        assert event1.latency_p99 == event2.latency_p99
        assert event1.error_rate == event2.error_rate
        assert event1.throughput == event2.throughput
        assert event1.cpu_utilization == event2.cpu_utilization
        assert event1.memory_utilization == event2.memory_utilization
        assert event1.severity == event2.severity
        assert event1.dependencies == event2.dependencies
        assert event1.metadata == event2.metadata
        if not ignore_timestamp:
            assert event1.timestamp == event2.timestamp
    return _assert_event_equal


@pytest.fixture
def validate_policy():
    """Helper to validate a policy is correctly formed"""
    def _validate_policy(policy):
        assert policy.name is not None
        assert len(policy.name) > 0
        assert len(policy.conditions) > 0
        assert len(policy.actions) > 0
        assert 1 <= policy.priority <= 5
        assert policy.cool_down_seconds >= 0
        assert policy.max_executions_per_hour >= 0
        return True
    return _validate_policy


@pytest.fixture
def create_custom_event():
    """Helper to create custom events with specific values"""
    def _create_custom_event(**kwargs):
        defaults = {
            "component": "custom-service",
            "latency": 100.0,
            "latency_p99": 150.0,
            "error_rate": 0.01,
            "throughput": 1000.0,
            "cpu_utilization": 0.3,
            "memory_utilization": 0.4,
            "severity": EventSeverity.MEDIUM,
            "timestamp": datetime.now(timezone.utc),
            "dependencies": [],
            "metadata": {}
        }
        defaults.update(kwargs)
        return ReliabilityEvent(**defaults)
    return _create_custom_event
