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
