"""
Pytest configuration and shared fixtures for timeline tests
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

# Add your shared fixtures here


@pytest.fixture
def sample_timeline_metrics():
    """Create sample TimelineMetrics for testing"""
    # TODO: Return a standard TimelineMetrics instance
    pass


@pytest.fixture
def timeline_calculator():
    """Create TimelineCalculator with test defaults"""
    # TODO: Return calculator instance
    pass


@pytest.fixture
def timeline_formatter():
    """Create TimelineFormatter instance"""
    # TODO: Return formatter instance
    pass


@pytest.fixture
def mock_business_metrics():
    """Mock BusinessMetricsTracker"""
    # TODO: Return mock with predefined behavior
    pass


@pytest.fixture
def mock_enhanced_engine():
    """Mock EnhancedReliabilityEngine"""
    # TODO: Return mock engine
    pass


@pytest.fixture
def sample_incident_data():
    """Create sample incident data for testing"""
    return {
        "component": "api-service",
        "latency": 450.0,
        "error_rate": 0.22,
        "throughput": 8500,
        "cpu_util": 0.95,
        "memory_util": 0.88,
        "severity": "CRITICAL"
    }


@pytest.fixture
def sample_timeline_display():
    """Create sample timeline markdown display"""
    # TODO: Return formatted markdown string
    pass


# Markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as performance benchmark"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )