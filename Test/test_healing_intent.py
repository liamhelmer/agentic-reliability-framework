"""
HealingIntent Integration Tests
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch


@pytest.fixture
def mock_healing_intent():
    """Create a mock HealingIntent for testing"""
    class MockHealingIntent:
        def __init__(self):
            self.action = "restart_container"
            self.component = "api-service"
            self.parameters = {"force": True}
            self.justification = "High latency detected"
            self.confidence = 0.85
            self.incident_id = "inc_123"
            self.detected_at = datetime.now().timestamp()
            
        def to_enterprise_request(self):
            return {
                "intent_id": "test_intent_123",
                "action": self.action,
                "component": self.component,
                "parameters": self.parameters,
                "justification": self.justification,
                "confidence": self.confidence,
                "requires_enterprise": True,
            }
    
    return MockHealingIntent()


@pytest.mark.asyncio
class TestHealingIntentIntegration:
    """Integration tests for HealingIntent OSS→Enterprise flow"""
    
    async def test_oss_creates_healing_intent(self):
        """Test that OSS creates HealingIntent properly"""
        from agentic_reliability_framework.engine.mcp_server import MCPServer
        
        server = MCPServer()
        
        # Mock request
        request_dict = {
            "tool": "restart_container",
            "component": "api-service",
            "parameters": {"force": True},
            "justification": "High latency detected",
            "metadata": {"incident_id": "inc_123"}
        }
        
        # Mock the OSS client if available
        if hasattr(server, 'oss_client') and server.oss_client:
            server.oss_client = AsyncMock()
            server.oss_client.analyze_and_recommend = AsyncMock(
                return_value=mock_healing_intent()
            )
        
        response = await server.execute_tool(request_dict)
        
        # Verify OSS advisory response
        assert response.status == "completed"
        assert not response.executed  # OSS never executes
        assert response.result["requires_enterprise"] is True
        
        # Verify HealingIntent if available
        if "healing_intent" in response.result:
            intent = response.result["healing_intent"]
            assert intent["action"] == "restart_container"
            assert intent["requires_enterprise"] is True
    
    async def test_enterprise_handoff_ready(self):
        """Test that HealingIntent is ready for Enterprise handoff"""
        try:
            from arf_core.models.healing_intent import HealingIntent
            
            # Create a HealingIntent
            intent = HealingIntent(
                action="rollback",
                component="database",
                parameters={"revision": "previous"},
                justification="Critical error rate detected",
                confidence=0.9,
                incident_id="inc_456"
            )
            
            # Convert to Enterprise format
            enterprise_request = intent.to_enterprise_request()
            
            # Verify Enterprise handoff format
            assert "intent_id" in enterprise_request
            assert enterprise_request["requires_enterprise"] is True
            assert enterprise_request["action"] == "rollback"
            
        except ImportError:
            pytest.skip("HealingIntent model not available")
    
    async def test_oss_purity_enforcement(self):
        """Test that OSS server enforces purity"""
        from agentic_reliability_framework.engine.mcp_server import MCPServer
        
        server = MCPServer()
        
        # Test advisory mode enforcement
        assert server.mode.value == "advisory"
        
        # Try to bypass with non-advisory mode (should be rejected)
        request_dict = {
            "tool": "restart_container",
            "component": "api-service",
            "mode": "autonomous",  # ❌ OSS should reject this
            "justification": "Test"
        }
        
        response = await server.execute_tool(request_dict)
        
        # Should reject non-advisory modes
        assert response.status == "rejected" or "advisory" in response.message.lower()
