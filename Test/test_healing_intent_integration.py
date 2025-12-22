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
        # Import from your OSS structure
        # Option 1: Try arf_core first (new structure)
        try:
            from arf_core.models.healing_intent import (
                HealingIntent,
                IntentSource,
                HealingIntentSerializer,
                create_rollback_intent
            )
            print("✅ Imported from arf_core.models.healing_intent")
        except ImportError:
            # Option 2: Try oss module (separate structure)
            from oss.healing_intent import (
                HealingIntent,
                IntentSource,
                HealingIntentSerializer,
                create_rollback_intent
            )
            print("✅ Imported from oss.healing_intent")
        
        # Create a sample healing intent for rollback
        intent = create_rollback_intent(
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
        
        print(f"\n✅ Created HealingIntent:")
        print(f"   Action: {intent.action}")
        print(f"   Component: {intent.component}")
        print(f"   Confidence: {intent.confidence:.2f}")
        print(f"   Deterministic ID: {intent.deterministic_id}")
        print(f"   Is executable: {intent.is_executable}")
        
        # Convert to Enterprise-ready JSON
        enterprise_json = HealingIntentSerializer.to_enterprise_json(intent)
        
        # Save to file for handoff
        output_dir = Path(__file__).parent / "test_outputs"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "healing_intent_for_enterprise.json"
        with open(output_file, "w") as f:
            f.write(enterprise_json)
        
        print(f"\n📤 HealingIntent ready for Enterprise handoff:")
        print(f"   File saved: {output_file}")
        print(f"   File size: {len(enterprise_json)} bytes")
        
        # Create human-readable version
        human_file = output_dir / "healing_intent_human_readable.json"
        human_readable = HealingIntentSerializer.serialize(intent)
        with open(human_file, "w") as f:
            json.dump(human_readable, f, indent=2)
        
        # Print Enterprise request summary
        print("\n📋 Enterprise Request Summary:")
        enterprise_request = intent.to_enterprise_request()
        print(f"   Action: {enterprise_request['action']}")
        print(f"   Component: {enterprise_request['component']}")
        print(f"   Requires Enterprise: {enterprise_request['requires_enterprise']}")
        print(f"   OSS Edition: {enterprise_request['oss_edition']}")
        
        if enterprise_request.get('upgrade_url'):
            print(f"   Upgrade URL: {enterprise_request['upgrade_url']}")
        
        # Print a few enterprise features for verification
        if enterprise_request.get('enterprise_features'):
            features = enterprise_request['enterprise_features']
            print(f"   Enterprise Features ({len(features)} total):")
            for i, feature in enumerate(features[:3]):  # Show first 3
                print(f"     • {feature}")
            if len(features) > 3:
                print(f"     • ... and {len(features) - 3} more")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Available modules:")
        print("  - Try: from arf_core.models.healing_intent import ...")
        print("  - Or: from oss.healing_intent import ...")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_oss_mcp_advisory_only():
    """Verify OSS MCP server only provides advisory responses"""
    print("\n" + "=" * 60)
    print("OSS MCP Server Validation (Advisory Only)")
    print("=" * 60)
    
    try:
        # Import your existing MCP server
        from agentic_reliability_framework.engine.mcp_server import MCPServer
        
        print("✅ Imported OSS MCPServer")
        
        server = MCPServer()
        stats = server.get_server_stats()
        
        print(f"\n📊 OSS MCP Server Stats:")
        print(f"   Edition: {stats.get('edition', 'unknown')}")
        print(f"   Mode: {stats.get('mode', 'unknown')}")
        print(f"   Tools: {stats.get('registered_tools', 0)}")
        
        # Verify OSS restrictions
        oss_limits = stats.get('oss_limits', {})
        print(f"\n🔒 OSS Restrictions:")
        print(f"   Execution allowed: {oss_limits.get('execution_allowed', False)}")
        print(f"   Max incidents: {oss_limits.get('max_incidents', 'unknown')}")
        
        if oss_limits.get('execution_allowed') is True:
            print("   ⚠️  WARNING: OSS should NOT allow execution!")
            return False
        
        # Test a tool request
        print("\n🔍 Testing tool request (should be advisory only)...")
        
        request = {
            "tool": "rollback",
            "component": "api-service",
            "parameters": {"revision": "previous"},
            "justification": "Test from OSS - should not execute",
            "metadata": {
                "incident_id": "test_oss_001",
                "environment": "staging"
            }
        }
        
        async def make_request():
            response = await server.execute_tool(request)
            return response
        
        response = asyncio.run(make_request())
        
        print(f"\n📨 OSS MCP Response:")
        print(f"   Status: {response.get('status')}")
        print(f"   Executed: {response.get('executed', False)}")
        print(f"   Message: {response.get('message', '')[:80]}...")
        
        # Verify it's advisory only
        if response.get('executed', False) is True:
            print("   ❌ ERROR: OSS executed a tool! Should be advisory only.")
            return False
        
        result = response.get('result', {})
        if result.get('requires_enterprise'):
            print("   ✅ Correctly indicates Enterprise requirement")
            if result.get('upgrade_url'):
                print(f"   Upgrade URL: {result.get('upgrade_url')}")
        else:
            print("   ⚠️  Missing 'requires_enterprise' flag")
        
        return True
        
    except Exception as e:
        print(f"\n❌ MCP test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_healing_intent_from_mcp_request():
    """Test creating HealingIntent from MCP request (backward compatibility)"""
    print("\n" + "=" * 60)
    print("HealingIntent from MCP Request Test")
    print("=" * 60)
    
    try:
        # Import based on your structure
        try:
            from arf_core.models.healing_intent import HealingIntent
        except ImportError:
            from oss.healing_intent import HealingIntent
        
        # Simulate an MCP request from existing code
        mcp_request = {
            "tool": "restart_container",
            "component": "database-service",
            "parameters": {"container_id": "db-12345"},
            "justification": "Database connection pool exhausted",
            "timestamp": 1734710400.0,
            "metadata": {
                "incident_id": "inc_20241220_002",
                "environment": "production",
                "severity": "high"
            }
        }
        
        # Convert MCP request to HealingIntent
        intent = HealingIntent.from_mcp_request(mcp_request)
        
        print(f"✅ Created HealingIntent from MCP request:")
        print(f"   Action: {intent.action}")
        print(f"   Component: {intent.component}")
        print(f"   Incident ID: {intent.incident_id}")
        
        # Test serialization
        import json
        serialized = intent.to_dict()
        print(f"\n📄 Serialization test:")
        print(f"   Keys: {list(serialized.keys())}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("OSS → Enterprise Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("HealingIntent Creation", test_create_healing_intent),
        ("OSS MCP Advisory Only", test_oss_mcp_advisory_only),
        ("MCP Request Compatibility", test_healing_intent_from_mcp_request),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n▶️  Running: {test_name}")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
    
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
        print("🎉 All OSS tests passed! HealingIntent ready for Enterprise.")
        print("\nNext steps:")
        print("1. Check generated files in tests/test_outputs/")
        print("2. Copy healing_intent_for_enterprise.json to Enterprise repo")
        print("3. Run Enterprise execution tests")
    else:
        print("❌ Some tests failed. Check OSS implementation.")
    
    print("=" * 60)
    
    # Exit with appropriate code for CI
    sys.exit(0 if all_passed else 1)
