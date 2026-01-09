#!/usr/bin/env python3
"""
V3 Validation Runner - Single command to run all V3 boundary checks

Usage:
    python run_v3_validation.py [--fast] [--certify] [--output=report.json]
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run V3 boundary validation")
    parser.add_argument("--fast", action="store_true", 
                       help="Run only essential checks")
    parser.add_argument("--certify", action="store_true",
                       help="Generate V3 compliance certification")
    parser.add_argument("--output", type=str,
                       help="Output report file path")
    
    args = parser.parse_args()
    
    print("🚀 ARF V3 Boundary Validation Suite")
    print("=" * 50)
    
    scripts_to_run = []
    
    if args.fast:
        print("⚡ Fast mode - running essential checks only")
        scripts_to_run = [
            ("Existing OSS Check", "oss_boundary_check.py"),
            ("Basic V3 Validation", "enhanced_v3_boundary_check.py"),
        ]
    else:
        print("🔍 Comprehensive mode - running all checks")
        scripts_to_run = [
            ("Existing OSS Check", "oss_boundary_check.py"),
            ("Enhanced V3 Check", "enhanced_v3_boundary_check.py"),
            ("V3 Integration", "v3_boundary_integration.py"),
        ]
    
    if args.certify:
        scripts_to_run.append(("V3 Certification", "v3_boundary_integration.py"))
    
    results = []
    all_passed = True
    
    for name, script in scripts_to_run:
        print(f"\n▶️  Running: {name}")
        print("-" * 30)
        
        script_path = Path(__file__).parent / script
        
        if not script_path.exists():
            print(f"⚠️  Script not found: {script}")
            continue
        
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            passed = result.returncode == 0
            all_passed = all_passed and passed
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   Status: {status}")
            
            # Show key output
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines[-5:]:  # Last 5 lines
                    if line.strip():
                        print(f"   {line}")
            
            results.append({
                "name": name,
                "script": script,
                "passed": passed,
                "returncode": result.returncode,
                "output": result.stdout[-500:] if result.stdout else "",
            })
            
        except subprocess.TimeoutExpired:
            print("   ⏰ TIMEOUT")
            all_passed = False
            results.append({
                "name": name,
                "script": script,
                "passed": False,
                "error": "Timeout",
            })
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            all_passed = False
            results.append({
                "name": name,
                "script": script,
                "passed": False,
                "error": str(e),
            })
    
    # Final report
    print("\n" + "=" * 50)
    print("📋 FINAL REPORT")
    print("=" * 50)
    
    passed_count = sum(1 for r in results if r.get("passed", False))
    total_count = len(results)
    
    print(f"\nTests Run: {total_count}")
    print(f"Tests Passed: {passed_count}")
    print(f"Tests Failed: {total_count - passed_count}")
    
    if all_passed:
        print("\n🎉 ALL V3 VALIDATIONS PASSED!")
        print("\nThe system is V3 compliant with:")
        print("  • Mechanical OSS/Enterprise boundaries")
        print("  • Proper execution ladder enforcement")
        print("  • License-based feature gating")
        print("  • Mandatory rollback analysis")
        
        if args.certify:
            cert_path = Path(__file__).parent.parent / "V3_COMPLIANCE_CERTIFICATION.json"
            print(f"\n📄 V3 Certification: {cert_path}")
        
        sys.exit(0)
    else:
        print("\n🚨 V3 VALIDATION FAILURES DETECTED")
        print("\nFailed tests:")
        for result in results:
            if not result.get("passed", False):
                print(f"  • {result['name']} ({result['script']})")
                if result.get("error"):
                    print(f"    Error: {result['error']}")
        
        print("\n🔧 Next steps:")
        print("  1. Check individual script outputs above")
        print("  2. Run scripts individually for detailed output")
        print("  3. Fix boundary violations before release")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
