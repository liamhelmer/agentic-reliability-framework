#!/usr/bin/env python3
"""
URGENT: Test script to verify ARF 3.3.4 import fix
Run this immediately after applying fixes
"""

import sys

def test_import(statement, description):
    """Test a specific import statement"""
    print(f"\n🔍 Testing: {description}")
    print(f"   Code: {statement}")
    
    try:
        exec(statement, {})
        print(f"   ✅ SUCCESS")
        return True
    except ImportError as e:
        print(f"   ❌ IMPORT FAILED: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️  OTHER ERROR: {e}")
        return False

def main():
    print("=" * 70)
    print("🚨 ARF 3.3.4 CRITICAL IMPORT FIX VERIFICATION")
    print("=" * 70)
    
    tests = [
        # CRITICAL: Basic package import
        ("import agentic_reliability_framework", "Basic package import"),
        
        # CRITICAL: The failing import from error message
        ("from agentic_reliability_framework import HealingIntent", "HealingIntent from package"),
        
        # CRITICAL: Other core imports
        ("from agentic_reliability_framework import OSSMCPClient", "OSSMCPClient from package"),
        ("from agentic_reliability_framework import create_mcp_client", "create_mcp_client factory"),
        
        # Verify OSS constants
        ("from agentic_reliability_framework import OSS_EDITION, EXECUTION_ALLOWED", "OSS constants"),
        
        # Test instantiation
        ("from agentic_reliability_framework import HealingIntent; hi = HealingIntent(action='test', component='test')", "HealingIntent instantiation"),
        
        # Test factory functions
        ("from agentic_reliability_framework import create_rollback_intent", "Factory function import"),
    ]
    
    passed = 0
    failed = 0
    
    for code, desc in tests:
        if test_import(code, desc):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/len(tests))*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL CRITICAL IMPORTS WORKING!")
        print("   Package is READY for PyPI release")
        return 0
    else:
        print(f"\n🚨 {failed} CRITICAL TESTS FAILED")
        print("   Package is STILL BROKEN")
        return 1

if __name__ == "__main__":
    sys.exit(main())
