#!/usr/bin/env python3
"""
Check specific files mentioned in V3 validation output
"""

from pathlib import Path
import re

def check_file_for_patterns(file_path: Path, patterns: list) -> list:
    """Check a file for specific patterns."""
    violations = []
    
    if not file_path.exists():
        return [f"File not found: {file_path}"]
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern, description in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's commented
                    stripped = line.strip()
                    if not stripped.startswith('#'):
                        violations.append({
                            'line': line_num,
                            'description': description,
                            'code': line.strip()[:100]
                        })
    
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]
    
    return violations

def main():
    """Check specific files."""
    print("🔍 CHECKING SPECIFIC FILES FOR V3 VIOLATIONS")
    print("=" * 60)
    
    # Based on validation output, these are likely problematic
    files_to_check = [
        Path("agentic_reliability_framework/config.py"),
        Path("agentic_reliability_framework/engine/mcp_server.py"),
        Path("agentic_reliability_framework/engine/mcp_factory.py"),
        Path("agentic_reliability_framework/engine/engine_factory.py"),
        Path("agentic_reliability_framework/arf_core/constants.py"),
        Path("oss/constants.py"),
        Path("agentic_reliability_framework/cli.py"),
        Path("agentic_reliability_framework/app.py"),
    ]
    
    # Common V3 violation patterns
    patterns = [
        (r'require_admin\(', 'Admin requirement (use require_operator)'),
        (r'license_key\s*=', 'License key assignment'),
        (r'learning_enabled', 'Learning enabled flag'),
        (r'beta_testing_enabled', 'Beta testing flag'),
        (r'rollout_percentage', 'Rollout percentage'),
        (r'MCPMode\.(APPROVAL|AUTONOMOUS)', 'Non-advisory MCP mode'),
        (r'mcp_mode.*=.*["\'](approval|autonomous)["\']', 'Non-advisory MCP mode'),
        (r'audit_trail', 'Audit trail'),
        (r'audit_log', 'Audit log'),
    ]
    
    all_violations = []
    
    for file_path in files_to_check:
        print(f"\n📄 Checking: {file_path}")
        
        if not file_path.exists():
            print(f"   ⚠️  File not found")
            continue
        
        violations = check_file_for_patterns(file_path, patterns)
        
        if violations:
            print(f"   ❌ Found {len(violations)} violations:")
            for violation in violations[:3]:  # Show first 3
                if isinstance(violation, dict):
                    print(f"     Line {violation['line']}: {violation['description']}")
                    print(f"       Code: {violation['code']}")
                else:
                    print(f"     {violation}")
            if len(violations) > 3:
                print(f"     ... and {len(violations) - 3} more")
            all_violations.extend(violations)
        else:
            print(f"   ✅ No violations found")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if all_violations:
        print(f"\n🚨 Found {len(all_violations)} total violations")
        print("\n🔧 Recommended fixes:")
        print("1. Open each file above and fix the violations")
        print("2. Common fixes:")
        print("   - Replace require_admin() with require_operator()")
        print("   - Set mcp_mode = 'advisory'")
        print("   - Set learning_enabled = False")
        print("   - Set beta_testing_enabled = False")
        print("   - Set rollout_percentage = 0")
        print("\n3. After fixes, run validation:")
        print("   python scripts/run_v3_validation.py --fast")
    else:
        print("\n✅ No violations found in checked files!")
        print("\nThe violations might be in other files.")
        print("Run comprehensive scan:")
        print("   python scripts/identify_v3_violations.py")

if __name__ == "__main__":
    main()
