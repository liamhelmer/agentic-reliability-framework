"""
Test OSS HealingIntent creation for Enterprise handoff
Run this in OSS environment only
"""

import json
import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_create_healing_intent():
    """Create a HealingIntent in OSS and prepare for Enterprise"""
    print("=" * 60)
    print("OSS HealingIntent Creation Test")
    print("=" * 60)
    
    try:
        # Import from your exact structure
        from arf_core.models.healing_intent import (
            HealingIntent,
            IntentSource,
            IntentStatus,
            HealingIntentSerializer,
            create_rollback_intent,
            create_restart_intent,
            create_scale_out_intent,
            create_oss_advisory_intent
        )
        
        # Also import OSS constants to verify
        try:
            from arf_core.constants import (
                OSS_EDITION,
                OSS_LICENSE,
                ENTERPRISE_UPGRADE_URL,
                EXECUTION_ALLOWED
            )
            print("✅ Imported OSS constants:")
            print(f"   Edition: {OSS_EDITION}")
            print(f"   License: {OSS_LICENSE}")
            print(f"   Execution allowed: {EXECUTION_ALLOWED}")
        except ImportError:
            print("⚠️  Could not import OSS constants, using defaults")
        
        print("✅ Imported HealingIntent from arf_core.models.healing_intent")
        
        # Test 1: Create rollback intent using factory function
        print("\n🔧 Test 1: Creating rollback intent...")
        rollback_intent = create_rollback_intent(
            component="api-service",
            revision="previous",
            justification="High latency spike detected (p99: 450ms vs 200ms SLA)",
            incident_id="inc_20241220_001",
            similar_incidents=[
                {
                    "incident_id": "inc_20241115_003",
                    "similarity": 0.85,
                    "action_taken": "rollback",
                    "success": True,
                    "resolution_time_minutes": 2.5
                }
            ]
        )
        
        print(f"✅ Created rollback intent:")
        print(f"   Action: {rollback_intent.action}")
        print(f"   Component: {rollback_intent.component}")
        print(f"   Confidence: {rollback_intent.confidence:.2f}")
        print(f"   OSS Edition: {rollback_intent.oss_edition}")
        print(f"   Execution allowed: {rollback_intent.execution_allowed}")
        print(f"   Status: {rollback_intent.status.value}")
        
        # Test 2: Verify OSS restrictions
        print("\n🔒 Test 2: Verifying OSS restrictions...")
        if rollback_intent.oss_edition != "oss":
            print(f"❌ ERROR: Expected OSS edition 'oss', got '{rollback_intent.oss_edition}'")
            return False
        
        if rollback_intent.execution_allowed:
            print("❌ ERROR: OSS intent should not allow execution")
            return False
        
        if rollback_intent.status != IntentStatus.OSS_ADVISORY_ONLY:
            print(f"❌ ERROR: OSS intent should be OSS_ADVISORY_ONLY, got {rollback_intent.status}")
            return False
        
        print("✅ OSS restrictions verified correctly")
        
        # Test 3: Create Enterprise request
        print("\n📤 Test 3: Creating Enterprise request...")
        enterprise_request = rollback_intent.to_enterprise_request()
        
        required_fields = ["intent_id", "action", "component", "requires_enterprise", "oss_edition"]
        for field in required_fields:
            if field not in enterprise_request:
                print(f"❌ ERROR: Missing required field: {field}")
                return False
        
        print(f"✅ Enterprise request created:")
        print(f"   Intent ID: {enterprise_request.get('intent_id', 'N/A')}")
        print(f"   Requires Enterprise: {enterprise_request.get('requires_enterprise', False)}")
        print(f"   OSS Edition: {enterprise_request.get('oss_edition', 'N/A')}")
        print(f"   Execution allowed: {enterprise_request.get('execution_allowed', False)}")
        
        if not enterprise_request.get("requires_enterprise"):
            print("❌ ERROR: OSS intent should require Enterprise")
            return False
        
        # Test 4: Serialization to JSON
        print("\n📄 Test 4: Testing serialization...")
        
        # Save to file for handoff
        output_dir = Path(__file__).parent / "test_outputs"
        output_dir.mkdir(exist_ok=True)
        
        # Enterprise-ready JSON
        enterprise_json = HealingIntentSerializer.to_enterprise_json(rollback_intent)
        enterprise_file = output_dir / "healing_intent_for_enterprise.json"
        with open(enterprise_file, "w") as f:
            f.write(enterprise_json)
        
        # Human-readable version
        serialized = HealingIntentSerializer.serialize(rollback_intent)
        human_file = output_dir / "healing_intent_human_readable.json"
        with open(human_file, "w") as f:
            json.dump(serialized, f, indent=2)
        
        print(f"✅ Files saved:")
        print(f"   Enterprise JSON: {enterprise_file}")
        print(f"   Human readable: {human_file}")
        print(f"   Enterprise JSON size: {len(enterprise_json)} bytes")
        
        # Test 5: Verify upgrade information
        print("\n🔼 Test 5: Checking upgrade information...")
        if "upgrade_url" not in enterprise_request:
            print("⚠️  WARNING: Missing upgrade_url in Enterprise request")
        else:
            print(f"✅ Upgrade URL: {enterprise_request['upgrade_url']}")
        
        if "enterprise_features" in enterprise_request:
            features = enterprise_request["enterprise_features"]
            print(f"✅ Enterprise features available: {len(features)} total")
            if features:
                print(f"   Sample: {features[0]}, {features[1]}, ...")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nAvailable modules in arf_core.models:")
        print("  - Try: from arf_core.models.healing_intent import HealingIntent")
        print("  - Check path: agentic_reliability_framework/arf_core/models/healing_intent.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_integration():
    """Test that OSS MCP server correctly uses HealingIntent"""
    print("\n" + "=" * 60)
    print("OSS MCP Server Integration Test")
    print("=" * 60)
    
    try:
        # Import MCP server
        from agentic_reliability_framework.engine.mcp_server import MCPServer
        
        print("✅ Imported OSS MCPServer")
        
        # Create server instance
        server = MCPServer()
        stats = server.get_server_stats()
        
        print(f"\n📊 OSS MCP Server Stats:")
        print(f"   Edition: {stats.get('edition', 'unknown')}")
        print(f"   Mode: {stats.get('mode', 'unknown')}")
        print(f"   Tools registered: {stats.get('registered_tools', 0)}")
        
        # Verify OSS restrictions
        oss_limits = stats.get('oss_limits', {})
        if oss_limits:
            print(f"\n🔒 OSS Limits:")
            print(f"   Execution allowed: {oss_limits.get('execution_allowed', False)}")
            print(f"   Max incidents: {oss_limits.get('max_incidents', 'unknown')}")
        
        # Test that OSS only provides advisory responses
        print("\n🔍 Testing advisory-only behavior...")
        
        request = {
            "tool": "restart_container",
            "component": "database-service",
            "parameters": {"container_id": "db-12345"},
            "justification": "Test from OSS - should be advisory only",
            "metadata": {
                "incident_id": "test_oss_001",
                "environment": "staging"
            }
        }
        
        async def make_request():
            response = await server.execute_tool(request)
            return response
        
        response = asyncio.run(make_request())
        
        print(f"📨 MCP Response:")
        print(f"   Status: {response.get('status')}")
        print(f"   Executed: {response.get('executed', False)}")
        print(f"   Message: {response.get('message', '')[:60]}...")
        
        # Verify it didn't execute
        if response.get('executed', False):
            print("❌ ERROR: OSS executed a tool! Should be advisory only.")
            return False
        
        # Check for Enterprise requirement
        result = response.get('result', {})
        if result.get('requires_enterprise'):
            print("✅ Correctly indicates Enterprise requirement")
        else:
            print("⚠️  Missing 'requires_enterprise' flag")
        
        return True
        
    except Exception as e:
        print(f"\n❌ MCP test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_healing_intent_from_mcp():
    """Test backward compatibility with existing MCP requests"""
    print("\n" + "=" * 60)
    print("Backward Compatibility Test")
    print("=" * 60)
    
    try:
        from arf_core.models.healing_intent import HealingIntent
        
        # Simulate an MCP request from existing code
        mcp_request = {
            "tool": "scale_out",
            "component": "api-service",
            "parameters": {"scale_factor": 3},
            "justification": "High traffic load detected",
            "timestamp": 1734710400.0,
            "metadata": {
                "incident_id": "inc_20241220_003",
                "environment": "production",
                "severity": "high",
                "oss_edition": "oss",
                "requires_enterprise": True,
                "execution_allowed": False
            }
        }
        
        # Convert to HealingIntent
        intent = HealingIntent.from_mcp_request(mcp_request)
        
        print(f"✅ Created HealingIntent from MCP request:")
        print(f"   Action: {intent.action}")
        print(f"   Component: {intent.component}")
        print(f"   OSS Edition: {intent.oss_edition}")
        print(f"   Execution allowed: {intent.execution_allowed}")
        
        # Verify OSS metadata was preserved
        if intent.oss_edition != "oss":
            print("❌ ERROR: OSS edition not preserved")
            return False
        
        if intent.execution_allowed:
            print("❌ ERROR: Execution should not be allowed")
            return False
        
        # Test serialization
        serialized = intent.to_dict()
        print(f"\n📄 Serialization test:")
        print(f"   Keys in dict: {len(serialized)}")
        
        required_keys = ["action", "component", "oss_edition", "requires_enterprise"]
        for key in required_keys:
            if key not in serialized:
                print(f"❌ ERROR: Missing key: {key}")
                return False
        
        print("✅ All required keys present")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_oss_factory_functions():
    """Test all OSS factory functions"""
    print("\n" + "=" * 60)
    print("OSS Factory Functions Test")
    print("=" * 60)
    
    try:
        from arf_core.models.healing_intent import (
            create_rollback_intent,
            create_restart_intent,
            create_scale_out_intent,
            create_oss_advisory_intent,
            IntentStatus
        )
        
        tests = [
            ("Rollback", lambda: create_rollback_intent("api-service", "previous")),
            ("Restart", lambda: create_restart_intent("database-service")),
            ("Scale Out", lambda: create_scale_out_intent("api-service", 3)),
            ("Generic Advisory", lambda: create_oss_advisory_intent(
                "circuit_breaker", "payment-service", {"threshold": 0.8},
                "High error rate detected"
            ))
        ]
        
        all_passed = True
        for name, factory in tests:
            intent = factory()
            
            # Check OSS properties
            if intent.oss_edition != "oss":
                print(f"❌ {name}: Wrong OSS edition: {intent.oss_edition}")
                all_passed = False
                continue
            
            if intent.execution_allowed:
                print(f"❌ {name}: Execution should not be allowed")
                all_passed = False
                continue
            
            if intent.status != IntentStatus.OSS_ADVISORY_ONLY:
                print(f"❌ {name}: Wrong status: {intent.status}")
                all_passed = False
                continue
            
            print(f"✅ {name}: OSS advisory intent created correctly")
            print(f"   Action: {intent.action}, Component: {intent.component}")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("OSS → Enterprise Integration Test Suite")
    print("=" * 60)
    print("Testing path: arf_core.models.healing_intent")
    print("=" * 60)
    
    tests = [
        ("HealingIntent Creation", test_create_healing_intent),
        ("MCP Integration", test_mcp_integration),
        ("Backward Compatibility", test_healing_intent_from_mcp),
        ("Factory Functions", test_oss_factory_functions),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n▶️  Running: {test_name}")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
        if not success:
            print(f"⏹️  Test failed: {test_name}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All OSS tests passed!")
        print("\nGenerated files in tests/test_outputs/:")
        print("  • healing_intent_for_enterprise.json - For Enterprise execution")
        print("  • healing_intent_human_readable.json - For debugging")
        print("\nNext steps:")
        print("1. Copy healing_intent_for_enterprise.json to Enterprise repo")
        print("2. Run Enterprise execution tests")
        print("3. Verify OSS→Enterprise handoff works")
    else:
        print("❌ Some tests failed. Check OSS implementation.")
    
    print("=" * 60)
    
    # Exit with appropriate code for CI
    sys.exit(0 if all_passed else 1)
