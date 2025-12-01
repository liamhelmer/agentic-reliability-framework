"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone
from models import ReliabilityEvent, EventSeverity, HealingPolicy, HealingAction, PolicyCondition
from healing_policies import PolicyEngine
from app import (
    ThreadSafeEventStore,
    AdvancedAnomalyDetector,
    BusinessImpactCalculator,
    SimplePredictiveEngine,
    EnhancedReliabilityEngine,
    OrchestrationManager
)


@pytest.fixture
def sample_event():
    """Create a sample reliability event for testing"""
    return ReliabilityEvent(
        component="test-service",
        latency_p99=250.0,
        error_rate=0.08,
        throughput=1000.0,
        cpu_util=0.75,
        memory_util=0.65,
        severity=EventSeverity.MEDIUM
    )


@pytest.fixture
def critical_event():
    """Create a critical reliability event"""
    return ReliabilityEvent(
        component="critical-service",
        latency_p99=600.0,
        error_rate=0.35,
        throughput=500.0,
        cpu_util=0.95,
        memory_util=0.92,
        severity=EventSeverity.CRITICAL
    )


@pytest.fixture
def normal_event():
    """Create a normal (healthy) reliability event"""
    return ReliabilityEvent(
        component="healthy-service",
        latency_p99=80.0,
        error_rate=0.01,
        throughput=2000.0,
        cpu_util=0.40,
        memory_util=0.35,
        severity=EventSeverity.LOW
    )


@pytest.fixture
def sample_policy():
    """Create a sample healing policy"""
    return HealingPolicy(
        name="test_policy",
        conditions=[
            PolicyCondition(metric="latency_p99", operator="gt", threshold=300.0)
        ],
        actions=[HealingAction.RESTART_CONTAINER],
        priority=2,
        cool_down_seconds=60,
        max_executions_per_hour=5
    )


@pytest.fixture
def policy_engine():
    """Create a fresh policy engine for testing"""
    return PolicyEngine(max_cooldown_history=100, max_execution_history=100)


@pytest.fixture
def event_store():
    """Create a fresh event store"""
    return ThreadSafeEventStore(max_size=100)


@pytest.fixture
def anomaly_detector():
    """Create a fresh anomaly detector"""
    return AdvancedAnomalyDetector()


@pytest.fixture
def business_calculator():
    """Create a business impact calculator"""
    return BusinessImpactCalculator()


@pytest.fixture
def predictive_engine():
    """Create a predictive engine"""
    return SimplePredictiveEngine(history_window=20)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_faiss_index(temp_dir):
    """Create a mock FAISS index for testing"""
    # This would require FAISS to be installed
    # For now, return None to allow tests to skip FAISS operations
    return None


@pytest.fixture
async def reliability_engine(
    policy_engine,
    event_store,
    anomaly_detector,
    business_calculator
):
    """Create a fully initialized reliability engine"""
    orchestrator = OrchestrationManager()
    
    engine = EnhancedReliabilityEngine(
        orchestrator=orchestrator,
        policy_engine=policy_engine,
        event_store=event_store,
        anomaly_detector=anomaly_detector,
        business_calculator=business_calculator
    )
    
    return engine