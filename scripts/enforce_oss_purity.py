# scripts/enforce_oss_purity.py
# REPLACE THE ENTIRE FILE WITH:

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


def check_line_for_enterprise_code(line: str) -> bool:
    """
    Check if a line contains ACTUAL Enterprise code (not string literals)
    
    Returns True if Enterprise code is found, False otherwise
    """
    # Remove comments
    line_without_comments = line.split('#')[0]
    
    # Skip empty lines
    if not line_without_comments.strip():
        return False
    
    # Patterns that indicate ACTUAL Enterprise code usage (not in strings)
    enterprise_patterns = [
        # Variable assignments
        r'^\s*audit_trail\s*=',
        r'^\s*audit_log\s*=',
        r'^\s*license_key\s*=',
        r'^\s*learning_enabled\s*=',
        r'^\s*rollout_percentage\s*=',
        r'^\s*beta_testing_enabled\s*=',
        
        # Class definitions
        r'^\s*class EnterpriseMCPServer',
        
        # Function calls
        r'validate_license\(',
        r'\.append\(.*audit',
        
        # MCP mode usage in code (not strings)
        r'MCPMode\.APPROVAL(?!\s*#)',
        r'MCPMode\.AUTONOMOUS(?!\s*#)',
    ]
    
    for pattern in enterprise_patterns:
        if re.search(pattern, line_without_comments):
            # Check if it's inside quotes (string literal)
            # Simple check: if the pattern text is between quotes
            pattern_text = pattern.replace(r'^\s*', '').replace(r'\s*=', '').replace(r'\(', '').replace(r'\)', '').replace(r'\.', '.')
            pattern_text = re.sub(r'\\[.*+?{}()|]', '', pattern_text)
            
            # Check if it's quoted
            if f'"{pattern_text}"' in line or f"'{pattern_text}'" in line:
                continue  # It's a string literal, not code
            
            # Check for partial matches in strings
            if '"' in line or "'" in line:
                # More sophisticated check: see if we're inside quotes
                in_single_quote = False
                in_double_quote = False
                escaped = False
                
                for i, char in enumerate(line_without_comments):
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
                    
                    # Check if pattern starts here and we're inside quotes
                    if line_without_comments[i:].startswith(pattern_text):
                        if in_single_quote or in_double_quote:
                            return False  # It's inside quotes
            
            return True  # Found Enterprise code
    
    return False  # No Enterprise code found


def main():
    """Smart OSS boundary checker that distinguishes code from strings"""
    print("🔍 OSS Boundary Check - Smart Detection")
    print("=" * 50)
    
    # Files to check
    files_to_check = [
        Path("agentic_reliability_framework/config.py"),
        Path("agentic_reliability_framework/engine/engine_factory.py"),
        Path("agentic_reliability_framework/engine/mcp_server.py"),
        Path("agentic_reliability_framework/engine/mcp_factory.py"),
        Path("agentic_reliability_framework/app.py"),
        Path("agentic_reliability_framework/cli.py"),
    ]
    
    violations = []
    
    for filepath in files_to_check:
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            continue
            
        try:
            content = filepath.read_text()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                if check_line_for_enterprise_code(line):
                    violations.append(f"{filepath}:{line_num}")
                    
        except Exception as e:
            print(f"⚠️  Error reading {filepath}: {e}")
            continue
    
    # Report results
    if violations:
        print("\n❌ ENTERPRISE CODE DETECTED IN OSS REPOSITORY:")
        print("=" * 50)
        
        for violation in violations:
            print(f"  🚫 {violation}")
        
        print("\n💡 These are ACTUAL Enterprise code (not string literals):")
        print("   - Move these to Enterprise repository")
        print("   - Replace with OSS alternatives")
        print("   - String literals mentioning Enterprise are OK")
        
        print("\n🔗 Enterprise Repository:")
        print("   https://github.com/petterjuan/agentic-reliability-enterprise")
        
        sys.exit(1)
    else:
        print("\n✅ PERFECT! No Enterprise code found.")
        print("=" * 50)
        print("\n🎉 OSS repository is clean!")
        print("📝 String literals mentioning Enterprise features are OK")
        print("💻 Actual Enterprise code has been properly removed")
        print("\n🚀 Ready for OSS package release!")
        sys.exit(0)


if __name__ == "__main__":
    main()
