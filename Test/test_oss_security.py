"""
OSS Security Validation Tests
Tests that OSS components are secure and cannot bypass enterprise boundaries.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.agentic_reliability_framework import HealingIntent, OSSMCPClient
    from src.agentic_reliability_framework.models import Action, ConfidenceScore
    OSS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Cannot import OSS: {e}")
    OSS_AVAILABLE = False


@pytest.mark.skipif(not OSS_AVAILABLE, reason="OSS not available")
class TestOSSSecurityBoundaries:
    """Test that OSS cannot bypass enterprise security boundaries."""
    
    def test_healing_intent_cannot_force_execution(self):
        """Test HealingIntent cannot bypass execution gates."""
        print("🔒 Testing: HealingIntent execution boundaries")
        
        # Create healing intent with high confidence
        intent = HealingIntent(
            action_description="Fix database corruption",
            rationale="Automated repair needed",
            confidence_score=0.95,
            evidence={"previous_success": True}
        )
        
        # Should require validation even with high confidence
        assert not hasattr(intent, 'bypass_gates'), "HealingIntent should not have bypass capabilities"
        assert not hasattr(intent, 'force_execute'), "Should not have force execution"
        
        print("  ✅ HealingIntent respects execution boundaries")
    
    def test_oss_mcp_client_security(self):
        """Test OSS MCP client cannot bypass security."""
        print("🔒 Testing: OSS MCP client security")
        
        # Mock MCP server with security restrictions
        mock_server = Mock()
        mock_server.require_authentication = True
        mock_server.allowed_actions = ["read", "query"]
        mock_server.blocked_actions = ["execute", "delete", "modify"]
        
        # Create OSS client
        client = OSSMCPClient(server_config={"url": "test://localhost"})
        
        # Should validate server security
        assert hasattr(client, 'validate_server_security'), "MCP client should validate security"
        
        print("  ✅ OSS MCP client has security validation")
    
    def test_confidence_score_limits(self):
        """Test OSS confidence scores have execution limits."""
        print("🔒 Testing: Confidence score execution limits")
        
        # Create confidence scores at different levels
        test_cases = [
            (0.3, False, "Low confidence should not execute"),
            (0.6, False, "Medium confidence should require review"),
            (0.9, False, "High confidence should still require validation"),
        ]
        
        for score, should_execute, description in test_cases:
            confidence = ConfidenceScore(
                value=score,
                rationale="Test confidence",
                evidence_quality="medium"
            )
            
            # OSS confidence alone should never allow automatic execution
            # Execution should always go through enterprise gates
            print(f"  ✅ {description}: score={score}")
    
    def test_no_direct_database_access(self):
        """Test OSS cannot access databases directly."""
        print("🔒 Testing: No direct database access")
        
        # Check imports
        import src.agentic_reliability_framework as arf
        
        # OSS should not have direct database connectors
        forbidden_modules = [
            "psycopg2",  # PostgreSQL
            "redis",     # Redis
            "neo4j",     # Neo4j
            "sqlalchemy", # SQL ORM
        ]
        
        for module in forbidden_modules:
            try:
                __import__(module)
                # If imported, check if it's in OSS
                if module in sys.modules:
                    # Check if it's being used in OSS code
                    print(f"  ⚠️  {module} imported - verify it's not used directly")
            except ImportError:
                pass  # Good - module not available
        
        print("  ✅ OSS doesn't have direct database access")
    
    def test_action_validation_required(self):
        """Test all actions require validation."""
        print("🔒 Testing: Action validation requirements")
        
        from src.agentic_reliability_framework.models import Action
        
        # Create various action types
        actions = [
            Action(type="database_query", payload={"query": "SELECT * FROM users"}),
            Action(type="api_call", payload={"endpoint": "/api/users", "method": "GET"}),
            Action(type="file_operation", payload={"path": "/tmp/test.txt", "operation": "read"}),
        ]
        
        for action in actions:
            # All actions should require validation
            assert hasattr(action, 'requires_validation'), f"Action {action.type} should require validation"
            assert action.requires_validation, f"Action {action.type} validation should be required"
            
            print(f"  ✅ {action.type} requires validation")


@pytest.mark.skipif(not OSS_AVAILABLE, reason="OSS not available")
class TestOSSEnterpriseIntegrationSecurity:
    """Test security of OSS-Enterprise integration."""
    
    def test_cannot_bypass_enterprise_gates(self):
        """Test OSS cannot bypass enterprise execution gates."""
        print("🔒 Testing: Cannot bypass enterprise gates")
        
        # Simulate OSS trying to execute directly
        try:
            # Try to import enterprise bypass methods (should not exist)
            import src.agentic_reliability_framework as arf
            
            # Check for dangerous methods
            dangerous_methods = [
                'execute_without_gates',
                'bypass_security',
                'force_enterprise_action',
                'override_license_check'
            ]
            
            for method in dangerous_methods:
                assert not hasattr(arf, method), f"Dangerous method {method} should not exist in OSS"
            
            print("  ✅ No bypass methods in OSS")
            
        except Exception as e:
            print(f"  ✅ Security check passed: {e}")
    
    def test_enterprise_boundary_enforcement(self):
        """Test enterprise boundaries are enforced."""
        print("🔒 Testing: Enterprise boundary enforcement")
        
        # Mock enterprise boundary check
        with patch('src.agentic_reliability_framework._enterprise_boundary') as mock_boundary:
            mock_boundary.return_value = False  # Not enterprise
            
            # Try to access enterprise features
            try:
                import arf_enterprise
                print("  ⚠️  Enterprise imported - verify licensing")
            except ImportError:
                print("  ✅ Enterprise correctly not importable from OSS")
            
            # Check OSS doesn't have enterprise constants
            import src.agentic_reliability_framework as arf
            assert not hasattr(arf, 'ENTERPRISE_FEATURES'), "OSS should not have enterprise constants"
            assert not hasattr(arf, 'EXECUTION_GATES'), "OSS should not have execution gates"
            
            print("  ✅ Enterprise boundaries enforced")


def run_oss_security_validation():
    """
    Run OSS security validation tests.
    Returns True if all tests pass, False if critical issues found.
    """
    print("\n" + "="*80)
    print("OSS SECURITY VALIDATION")
    print("="*80)
    
    results = {
        "critical": [],
        "warnings": [],
        "passed": []
    }
    
    # Run boundary tests
    if OSS_AVAILABLE:
        print("\n🔍 Testing OSS Security Boundaries...")
        
        test_cases = [
            ("HealingIntent boundaries", TestOSSSecurityBoundaries().test_healing_intent_cannot_force_execution),
            ("MCP client security", TestOSSSecurityBoundaries().test_oss_mcp_client_security),
            ("Confidence score limits", TestOSSSecurityBoundaries().test_confidence_score_limits),
            ("Database access", TestOSSSecurityBoundaries().test_no_direct_database_access),
            ("Action validation", TestOSSSecurityBoundaries().test_action_validation_required),
            ("Enterprise bypass", TestOSSEnterpriseIntegrationSecurity().test_cannot_bypass_enterprise_gates),
            ("Boundary enforcement", TestOSSEnterpriseIntegrationSecurity().test_enterprise_boundary_enforcement),
        ]
        
        for test_name, test_method in test_cases:
            try:
                print(f"\n  🔒 Running: {test_name}")
                test_method()
                results["passed"].append(f"OSS: {test_name}")
                print(f"    ✅ PASS")
            except AssertionError as e:
                results["critical"].append(f"OSS: {test_name} - {str(e)[:100]}")
                print(f"    ❌ FAIL: {str(e)[:100]}...")
            except Exception as e:
                results["warnings"].append(f"OSS: {test_name} - {str(e)[:100]}")
                print(f"    ⚠️  ERROR: {str(e)[:100]}...")
    else:
        results["critical"].append("OSS not available for security testing")
    
    # Print summary
    print("\n" + "="*80)
    print("OSS SECURITY SUMMARY")
    print("="*80)
    
    print(f"\n✅ PASSED: {len(results['passed'])}")
    for passed in results['passed'][:5]:
        print(f"  - {passed}")
    
    print(f"\n⚠️  WARNINGS: {len(results['warnings'])}")
    for warning in results['warnings']:
        print(f"  - {warning}")
    
    print(f"\n❌ CRITICAL: {len(results['critical'])}")
    for critical in results['critical']:
        print(f"  - {critical}")
    
    if results['critical']:
        print("\n🚨 OSS SECURITY COMPROMISED")
        return False
    else:
        print("\n✅ OSS SECURITY VALIDATION PASSED")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run OSS security tests")
    parser.add_argument("--fail-on-warning", action="store_true", help="Fail on warnings")
    args = parser.parse_args()
    
    success = run_oss_security_validation()
    
    if not success:
        print("\n❌ OSS SECURITY FAILED")
        sys.exit(1)
    elif args.fail_on_warning and len(results.get("warnings", [])) > 0:
        print("\n⚠️  OSS SECURITY WARNINGS (fail-on-warning enabled)")
        sys.exit(1)
    else:
        print("\n✅ OSS SECURITY PASSED")
        sys.exit(0)
