#!/usr/bin/env python3
"""
Simple OSS boundary check - No external dependencies
"""

import os
import sys
from pathlib import Path

def check_oss_constants():
    """Check that OSS constants are properly defined"""
    print("🔍 Checking OSS constants...")
    
    # Look for arf_core directory
    arf_core_path = Path("agentic_reliability_framework/arf_core")
    
    if not arf_core_path.exists():
        print(f"❌ arf_core directory not found at: {arf_core_path}")
        return False
    
    # Look for constants.py
    constants_path = arf_core_path / "constants.py"
    if not constants_path.exists():
        print(f"❌ constants.py not found at: {constants_path}")
        return False
    
    # Try to check the constants
    try:
        # Simple regex-based check instead of import
        with open(constants_path, 'r') as f:
            content = f.read()
        
        checks = [
            ("MAX_INCIDENT_HISTORY", "1000"),
            ("MCP_MODES_ALLOWED", "advisory"),
            ("EXECUTION_ALLOWED", "False"),
            ("GRAPH_STORAGE", "in_memory"),
        ]
        
        for const_name, expected_value in checks:
            if const_name not in content:
                print(f"❌ Constant {const_name} not found")
                return False
            
            # Check if it's set to the right value
            lines = content.split('\n')
            for line in lines:
                if const_name in line and "=" in line:
                    if expected_value not in line:
                        print(f"❌ {const_name} has wrong value: {line.strip()}")
                        return False
                    else:
                        print(f"✅ {const_name} = {expected_value}")
        
        print("✅ All OSS constants are correct")
        return True
        
    except Exception as e:
        print(f"❌ Error checking constants: {e}")
        return False

def check_no_enterprise_imports():
    """Check that OSS code doesn't import Enterprise modules"""
    print("\n🔍 Checking for Enterprise imports...")
    
    oss_dirs = [
        Path("agentic_reliability_framework/arf_core"),
        Path("agentic_reliability_framework/engine"),
    ]
    
    forbidden_patterns = [
        "arf_enterprise",
        "EnterpriseMCPServer", 
        "LicenseManager",
        "license_key",
        "audit_trail",
        "validate_license",
    ]
    
    violations = []
    
    for oss_dir in oss_dirs:
        if not oss_dir.exists():
            continue
            
        for py_file in oss_dir.rglob("*.py"):
            # Skip test files
            if "test_" in py_file.name or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                for pattern in forbidden_patterns:
                    if pattern in content:
                        violations.append(f"{py_file.relative_to(Path('.'))}: Contains '{pattern}'")
                        
            except Exception as e:
                print(f"⚠️  Error reading {py_file}: {e}")
    
    if violations:
        print("❌ Enterprise imports found in OSS code:")
        for violation in violations:
            print(f"  - {violation}")
        return False
    else:
        print("✅ No Enterprise imports found in OSS code")
        return True

def check_oss_file_structure():
    """Check that OSS package structure is correct"""
    print("\n🔍 Checking OSS file structure...")
    
    required_files = [
        Path("agentic_reliability_framework/arf_core/__init__.py"),
        Path("agentic_reliability_framework/arf_core/constants.py"),
        Path("agentic_reliability_framework/arf_core/models/healing_intent.py"),
        Path("agentic_reliability_framework/arf_core/engine/oss_mcp_client.py"),
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print("❌ Missing required OSS files:")
        for missing in missing_files:
            print(f"  - {missing}")
        return False
    else:
        print("✅ All required OSS files exist")
        return True

def main():
    """Main boundary check"""
    print("🔐 OSS BOUNDARY CHECK")
    print("=" * 50)
    
    # Run all checks
    results = []
    
    results.append(("File Structure", check_oss_file_structure()))
    results.append(("Constants", check_oss_constants()))
    results.append(("Enterprise Imports", check_no_enterprise_imports()))
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All OSS boundary checks passed!")
        return 0
    else:
        print("\n🚨 OSS boundary violations detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())
