#!/usr/bin/env python3
"""
Quick V3 Status Checker

Provides a quick overview of V3 validation status without running full tests.
"""

import json
from pathlib import Path
from datetime import datetime
import sys


def check_v3_status():
    """Check current V3 validation status."""
    print("🔍 Quick V3 Status Check")
    print("=" * 50)
    
    # Check for certification files
    cert_path = Path("V3_COMPLIANCE_CERTIFICATION.json")
    issues_path = Path("V3_COMPLIANCE_ISSUES.json")
    
    if cert_path.exists():
        try:
            with open(cert_path, 'r') as f:
                cert = json.load(f)
            
            print(f"✅ V3 CERTIFICATION FOUND")
            print(f"   Version: {cert.get('version', 'Unknown')}")
            print(f"   Timestamp: {cert.get('timestamp', 'Unknown')}")
            
            # Check key compliance levels
            v3_0_status = cert.get('compliance_levels', {}).get('v3_0_advisory_intelligence', 'UNKNOWN')
            if v3_0_status == 'VERIFIED':
                print(f"   🎉 V3.0 Advisory Intelligence: {v3_0_status}")
                return True
            else:
                print(f"   ⚠️  V3.0 Advisory Intelligence: {v3_0_status}")
                return False
                
        except Exception as e:
            print(f"⚠️  Error reading certification: {e}")
            return False
    
    elif issues_path.exists():
        print(f"⚠️  V3 COMPLIANCE ISSUES FOUND")
        print(f"   See: {issues_path.name}")
        print(f"   Run: python scripts/run_v3_validation.py --certify")
        return False
    
    else:
        print(f"📝 NO V3 CERTIFICATION FOUND")
        print(f"   Run: python scripts/run_v3_validation.py --certify")
        return False


def check_validation_scripts():
    """Check if validation scripts exist and are runnable."""
    print("\n🔧 Validation Scripts Check")
    print("-" * 30)
    
    scripts = [
        "oss_boundary_check.py",
        "enforce_oss_purity.py", 
        "enhanced_v3_boundary_check.py",
        "v3_boundary_integration.py",
        "run_v3_validation.py",
    ]
    
    all_exist = True
    for script in scripts:
        path = Path("scripts") / script
        if path.exists():
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script} (missing)")
            all_exist = False
    
    return all_exist


def check_workflow_status():
    """Check GitHub Actions workflow status."""
    print("\n🚀 GitHub Actions Status")
    print("-" * 30)
    
    workflows = [
        "OSS Boundary Tests",
        "OSS Comprehensive Tests", 
        "Test Built Package",
    ]
    
    print("   Recent runs should show:")
    for workflow in workflows:
        print(f"   • {workflow}")
    
    print("\n   Check: https://github.com/petterjuan/agentic-reliability-framework/actions")
    print("   Look for green checkmarks ✅")
    
    return True  # Assume passes since we can't check API


def main():
    """Main status check."""
    print("\n" + "=" * 50)
    print("🚀 ARF V3 VALIDATION STATUS")
    print("=" * 50)
    
    # Check current status
    v3_certified = check_v3_status()
    
    # Check scripts
    scripts_ok = check_validation_scripts()
    
    # Check workflow status
    workflow_ok = check_workflow_status()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if v3_certified and scripts_ok:
        print("\n🎉 V3 VALIDATION READY")
        print("\nNext steps:")
        print("1. Review V3_COMPLIANCE_CERTIFICATION.json")
        print("2. Check GitHub Actions for all green tests")
        print("3. Proceed with V3.0 release")
        sys.exit(0)
    else:
        print("\n🚨 ACTION REQUIRED")
        print("\nRequired actions:")
        if not v3_certified:
            print("• Run: python scripts/run_v3_validation.py --certify")
        if not scripts_ok:
            print("• Ensure all validation scripts exist in scripts/ directory")
        print("\nThen re-run this check.")
        sys.exit(1)


if __name__ == "__main__":
    main()
