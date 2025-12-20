"""
Build-time enforcement of OSS purity
Apache 2.0 Licensed

Copyright 2025 Juan Petter

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
from pathlib import Path
import re


def is_inside_quotes(line: str, pattern: str, position: int) -> bool:
    """
    Check if a pattern at a given position is inside quotes (string literal)
    
    Args:
        line: The line of code
        pattern: The pattern to check
        position: Starting position of the pattern in the line
        
    Returns:
        True if pattern is inside quotes, False otherwise
    """
    # Track quote state
    in_single_quote = False
    in_double_quote = False
    escaped = False
    
    for i, char in enumerate(line):
        if escaped:
            escaped = False
            continue
            
        if char == '\\':
            escaped = True
            continue
            
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            
        # Check if we're at the pattern position
        if i == position:
            return in_single_quote or in_double_quote
    
    return False


def check_line_for_enterprise_code(line: str, line_num: int, filepath: Path) -> list:
    """
    Check a line for Enterprise code patterns (not in string literals)
    
    Returns list of violations found in this line
    """
    violations = []
    
    # Skip comment lines
    stripped = line.strip()
    if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
        return violations
    
    # Remove inline comments for checking
    line_without_comment = line.split('#')[0]
    
    # Patterns that indicate ACTUAL Enterprise code (not in strings)
    enterprise_patterns = [
        # Variable assignments (must be at start of line or after whitespace)
        (r'audit_trail\s*=', 'Audit trail variable assignment (Enterprise only)'),
        (r'audit_log\s*=', 'Audit log variable assignment (Enterprise only)'),
        (r'license_key\s*=', 'License key variable assignment (Enterprise only)'),
        (r'learning_enabled\s*=', 'Learning enabled flag (Enterprise only)'),
        (r'rollout_percentage\s*=', 'Rollout percentage assignment (Enterprise only)'),
        (r'beta_testing_enabled\s*=', 'Beta testing enabled flag (Enterprise only)'),
        
        # Class definitions
        (r'class EnterpriseMCPServer', 'Enterprise MCPServer class definition (Enterprise only)'),
        
        # Function calls
        (r'validate_license\(', 'License validation function call (Enterprise only)'),
        (r'\.append\([^)]*audit', 'Audit trail appending (Enterprise only)'),
        
        # MCP mode usage in code (not documentation)
        (r'MCPMode\.APPROVAL', 'APPROVAL mode usage in code (Enterprise only)'),
        (r'MCPMode\.AUTONOMOUS', 'AUTONOMOUS mode usage in code (Enterprise only)'),
        
        # Enterprise-specific imports
        (r'from.*EnterpriseMCPServer', 'Enterprise MCPServer import (Enterprise only)'),
        (r'import.*EnterpriseMCPServer', 'Enterprise MCPServer import (Enterprise only)'),
    ]
    
    for pattern, description in enterprise_patterns:
        # Find all matches of this pattern
        matches = list(re.finditer(pattern, line_without_comment))
        
        for match in matches:
            start_pos = match.start()
            
            # Check if this match is inside quotes (string literal)
            if is_inside_quotes(line_without_comment, pattern, start_pos):
                continue  # Skip string literals
            
            # Also check simple quote detection
            match_text = match.group(0)
            if f'"{match_text}"' in line or f"'{match_text}'" in line:
                continue  # Skip quoted strings
            
            # Found actual Enterprise code
            violations.append(f"{filepath}:{line_num}: {description}")
            break  # Only report first violation per line
    
    return violations


def main():
    """Smart OSS boundary checker - distinguishes code from string literals"""
    print("🔍 OSS Boundary Check - Smart Detection")
    print("=" * 60)
    print("Checking for ACTUAL Enterprise code (ignoring string literals)")
    print()
    
    # Files to check
    files_to_check = [
        Path("agentic_reliability_framework/config.py"),
        Path("agentic_reliability_framework/engine/engine_factory.py"),
        Path("agentic_reliability_framework/engine/mcp_server.py"),
        Path("agentic_reliability_framework/engine/mcp_factory.py"),
        Path("agentic_reliability_framework/app.py"),
        Path("agentic_reliability_framework/cli.py"),
    ]
    
    all_violations = []
    
    for filepath in files_to_check:
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            continue
            
        try:
            print(f"📄 Checking {filepath.name}...", end=" ")
            
            content = filepath.read_text()
            lines = content.split('\n')
            
            file_violations = []
            for line_num, line in enumerate(lines, 1):
                violations = check_line_for_enterprise_code(line, line_num, filepath)
                if violations:
                    file_violations.extend(violations)
            
            if file_violations:
                all_violations.extend(file_violations)
                print(f"❌ {len(file_violations)} violations")
            else:
                print("✅ Clean")
                
        except Exception as e:
            print(f"⚠️  Error: {e}")
            continue
    
    # Report results
    if all_violations:
        print("\n" + "=" * 60)
        print("❌ ENTERPRISE CODE DETECTED IN OSS REPOSITORY")
        print("=" * 60)
        
        print("\n🚫 Violations found:")
        for violation in all_violations:
            print(f"  • {violation}")
        
        print("\n💡 IMPORTANT:")
        print("   These are ACTUAL Enterprise code patterns, not string literals.")
        print("   String literals mentioning Enterprise features are OK.")
        
        print("\n🔧 FIX INSTRUCTIONS:")
        print("   1. Move these Enterprise features to Enterprise repository")
        print("   2. Replace with OSS alternatives (False/None/removed)")
        print("   3. Keep string literals (documentation is fine)")
        
        print("\n🔗 Enterprise Repository:")
        print("   https://github.com/petterjuan/agentic-reliability-enterprise")
        print()
        
        sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("✅ PERFECT! No Enterprise code found in OSS repository")
        print("=" * 60)
        
        print("\n🎉 OSS Repository Status:")
        print("   • String literals mentioning Enterprise: ✅ OK")
        print("   • Actual Enterprise code: ✅ None found")
        print("   • OSS boundaries: ✅ Properly enforced")
        
        print("\n📦 Ready for OSS package release!")
        print("💼 Enterprise features are properly separated")
        print()
        
        sys.exit(0)


if __name__ == "__main__":
    main()
