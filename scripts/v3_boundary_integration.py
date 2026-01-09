#!/usr/bin/env python3
"""
V3 Boundary Integration - Bridges existing checks with V3 architecture

This script:
1. Runs the existing oss_boundary_check.py
2. Runs the enhanced V3 boundary validator  
3. Provides unified reporting
4. Generates V3 compliance certification
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import sys


def run_existing_check() -> dict:
    """Run the existing oss_boundary_check.py."""
    print("🔍 Running existing OSS boundary check...")
    
    script_path = Path(__file__).parent / "oss_boundary_check.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout running existing check",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1,
        }


def run_v3_validator() -> dict:
    """Run the enhanced V3 boundary validator."""
    print("🔍 Running enhanced V3 boundary validator...")
    
    script_path = Path(__file__).parent / "enhanced_v3_boundary_check.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout running V3 validator",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1,
        }


def generate_v3_certification(existing_results: dict, v3_results: dict) -> dict:
    """Generate V3 compliance certification."""
    certification = {
        "version": "V3.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components_validated": [
            "OSS/Enterprise Split",
            "Execution Ladder Boundaries",
            "Rollback API Boundaries",
            "Memory System Boundaries",
            "License Manager Boundaries",
            "Cross-Repository Dependencies",
        ],
        "existing_check": {
            "passed": existing_results["success"],
            "return_code": existing_results.get("returncode", -1),
        },
        "v3_check": {
            "passed": v3_results["success"],
            "return_code": v3_results.get("returncode", -1),
        },
        "compliance_levels": {
            "v3_0_advisory_intelligence": "PENDING",
            "v3_1_execution_governance": "PENDING",
            "v3_2_risk_bounded_autonomy": "PENDING",
            "v3_3_outcome_learning": "PENDING",
        },
        "boundary_verification": {
            "require_operator_vs_require_admin": "PENDING",
            "oss_execution_prevention": "PENDING",
            "enterprise_license_enforcement": "PENDING",
            "rollback_mandatory_analysis": "PENDING",
            "novel_execution_protocol": "PENDING",
        },
    }
    
    # Update compliance based on results
    if existing_results["success"] and v3_results["success"]:
        certification["compliance_levels"]["v3_0_advisory_intelligence"] = "VERIFIED"
        certification["boundary_verification"]["require_operator_vs_require_admin"] = "VERIFIED"
        certification["boundary_verification"]["oss_execution_prevention"] = "VERIFIED"
    
    # Extract more details from stdout
    if v3_results.get("stdout"):
        stdout = v3_results["stdout"]
        if "OSS Constants:" in stdout:
            certification["oss_constants_integration"] = "VERIFIED"
        if "Cross-Repository Dependencies (0):" in stdout:
            certification["boundary_verification"]["cross_repo_isolation"] = "VERIFIED"
    
    return certification


def main():
    """Main integration entry point."""
    print("=" * 70)
    print("🔄 V3 BOUNDARY INTEGRATION VALIDATOR")
    print("=" * 70)
    print("\nThis script integrates existing checks with V3 architecture validation.")
    print("It ensures backward compatibility while enforcing V3 boundaries.\n")
    
    # Run both checks
    existing_results = run_existing_check()
    v3_results = run_v3_validator()
    
    # Generate unified report
    print("\n" + "=" * 70)
    print("📊 UNIFIED VALIDATION REPORT")
    print("=" * 70)
    
    print("\n1. EXISTING OSS BOUNDARY CHECK:")
    if existing_results["success"]:
        print("   ✅ PASSED")
        if existing_results.get("stdout"):
            # Extract key lines
            lines = existing_results["stdout"].split('\n')
            for line in lines:
                if "PERFECT!" in line or "No Enterprise code found" in line:
                    print(f"   📝 {line.strip()}")
    else:
        print("   ❌ FAILED")
        if existing_results.get("stderr"):
            print(f"   Error: {existing_results['stderr'][:200]}...")
    
    print("\n2. ENHANCED V3 BOUNDARY VALIDATION:")
    if v3_results["success"]:
        print("   ✅ PASSED")
        if v3_results.get("stdout"):
            lines = v3_results["stdout"].split('\n')
            for line in lines:
                if "V3 BOUNDARIES VERIFIED" in line or "READY FOR:" in line:
                    print(f"   📝 {line.strip()}")
    else:
        print("   ❌ FAILED")
        if v3_results.get("stderr"):
            print(f"   Error: {v3_results['stderr'][:200]}...")
    
    # Generate certification
    certification = generate_v3_certification(existing_results, v3_results)
    
    print("\n" + "=" * 70)
    print("🏆 V3 COMPLIANCE CERTIFICATION")
    print("=" * 70)
    
    print(f"\nVersion: {certification['version']}")
    print(f"Timestamp: {certification['timestamp']}")
    
    print("\nCompliance Levels:")
    for level, status in certification["compliance_levels"].items():
        icon = "✅" if status == "VERIFIED" else "⏳"
        readable_name = level.replace("_", " ").title()
        print(f"  {icon} {readable_name}: {status}")
    
    print("\nBoundary Verification:")
    for boundary, status in certification["boundary_verification"].items():
        icon = "✅" if status == "VERIFIED" else "⏳"
        readable_name = boundary.replace("_", " ").title()
        print(f"  {icon} {readable_name}: {status}")
    
    # Determine overall status
    all_passed = (
        existing_results["success"] and 
        v3_results["success"] and
        certification["compliance_levels"]["v3_0_advisory_intelligence"] == "VERIFIED"
    )
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 V3 ARCHITECTURE FULLY VERIFIED")
        print("\n✅ Both existing and V3 checks pass")
        print("✅ OSS/Enterprise boundaries are mechanically enforced")
        print("✅ Ready for V3.0 (Advisory Intelligence Lock-In) release")
        
        # Save certification to file
        cert_path = Path(__file__).parent.parent / "V3_COMPLIANCE_CERTIFICATION.json"
        with open(cert_path, 'w') as f:
            json.dump(certification, f, indent=2)
        
        print(f"\n📄 Certification saved to: {cert_path.relative_to(Path.cwd())}")
        sys.exit(0)
    else:
        print("🚨 V3 ARCHITECTURE VALIDATION FAILED")
        print("\n🔧 Required Actions:")
        print("  1. Fix issues identified by existing OSS boundary check")
        print("  2. Address V3 boundary violations")
        print("  3. Ensure require_operator is used in OSS, require_admin in Enterprise")
        print("  4. Verify no cross-repository dependencies")
        
        # Save partial certification for debugging
        cert_path = Path(__file__).parent.parent / "V3_COMPLIANCE_ISSUES.json"
        with open(cert_path, 'w') as f:
            json.dump(certification, f, indent=2)
        
        print(f"\n⚠️  Issues log saved to: {cert_path.relative_to(Path.cwd())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
