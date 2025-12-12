"""
Basic tests for Agentic Reliability Framework
"""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_reliability_framework.models import ReliabilityEvent, EventSeverity
from agentic_reliability_framework.config import config


def test_config_loaded():
    """Test that configuration is loaded"""
    assert config is not None
    assert hasattr(config, 'hf_api_key')
    assert hasattr(config, 'max_events_stored')
    assert config.max_events_stored > 0


def test_event_creation():
    """Test that ReliabilityEvent can be created"""
    event = ReliabilityEvent(
        component="test-service",
        latency_p99=100.0,
        error_rate=0.05,
        throughput=1000.0
    )
    
    assert event.component == "test-service"
    assert event.latency_p99 == 100.0
    assert event.error_rate == 0.05
    assert event.throughput == 1000.0
    assert event.severity == EventSeverity.LOW


def test_event_validation():
    """Test event validation"""
    # Valid event
    event = ReliabilityEvent(
        component="test-service",
        latency_p99=100.0,
        error_rate=0.05,
        throughput=1000.0
    )
    assert event is not None
    
    # Test invalid component name (should raise ValueError)
    with pytest.raises(ValueError):
        ReliabilityEvent(
            component="Invalid_Component",  # Underscore not allowed
            latency_p99=100.0,
            error_rate=0.05,
            throughput=1000.0
        )


@pytest.mark.asyncio
async def test_lazy_loading():
    """Test lazy loading functionality"""
    from agentic_reliability_framework.lazy import get_engine, get_agents
    
    # These should not raise errors
    engine = get_engine()
    agents = get_agents()
    
    assert engine is not None
    assert agents is not None
    assert 'detective' in agents
    assert 'diagnostician' in agents
    assert 'predictive' in agents


class TestConstants:
    """Test constants from app.py"""
    
    def test_constants_import(self):
        """Test that constants can be imported"""
        from agentic_reliability_framework.app import Constants
        
        assert Constants.LATENCY_WARNING == 150.0
        assert Constants.LATENCY_CRITICAL == 300.0
        assert Constants.LATENCY_EXTREME == 500.0
        assert Constants.ERROR_RATE_WARNING == 0.05


if __name__ == "__main__":
    pytest.main([__file__])
