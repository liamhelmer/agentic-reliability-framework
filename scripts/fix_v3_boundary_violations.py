#!/usr/bin/env python3
"""
Fix V3 Boundary Violations
Automatically fixes common V3 boundary violations in OSS code.
"""

import re
from pathlib import Path
from typing import List, Tuple
import sys


class V3BoundaryFixer:
    """Fix V3 boundary violations in OSS code."""
    
    # Patterns to find and replace
    FIX_PATTERNS = [
        # License-related patterns
        {
            'pattern': r'license_key\s*=',
            'replacement': '# license_key =  # REMOVED: Enterprise-only feature',
            'description': 'License key assignment (Enterprise only)',
        },
        {
            'pattern': r'validate_license\(',
            'replacement': '# validate_license(  # REMOVED: Enterprise-only feature',
            'description': 'License validation (Enterprise only)',
        },
        
        # Execution patterns
        {
            'pattern': r'autonomous.*execute',
            'replacement': '# autonomous_execution  # REMOVED: Enterprise-only feature',
            'description': 'Autonomous execution (Enterprise only)',
        },
        {
            'pattern': r'require_admin\(',
            'replacement': 'require_operator(',  # Replace with OSS equivalent
            'description': 'Admin requirement (use require_operator in OSS)',
        },
        
        # Feature flag patterns
        {
            'pattern': r'learning_enabled\s*=',
            'replacement': 'learning_enabled = False  # OSS: Always False',
            'description': 'Learning enabled flag (False in OSS)',
        },
        {
            'pattern': r'beta_testing_enabled\s*=',
            'replacement': 'beta_testing_enabled = False  # OSS: Always False',
            'description': 'Beta testing flag (False in OSS)',
        },
        {
            'pattern': r'rollout_percentage\s*=',
            'replacement': 'rollout_percentage = 0  # OSS: Always 0',
            'description': 'Rollout percentage (0 in OSS)',
        },
        
        # MCP mode patterns
        {
            'pattern': r'MCPMode\.APPROVAL',
            'replacement': '# MCPMode.APPROVAL  # REMOVED: Enterprise-only mode',
            'description': 'MCP approval mode (Enterprise only)',
        },
        {
            'pattern': r'MCPMode\.AUTONOMOUS',
            'replacement': '# MCPMode.AUTONOMOUS  # REMOVED: Enterprise-only mode',
            'description': 'MCP autonomous mode (Enterprise only)',
        },
        {
            'pattern': r'mcp_mode.*=.*["\'](approval|autonomous)["\']',
            'replacement': "mcp_mode = 'advisory'  # OSS: Only advisory mode",
            'description': 'Non-advisory MCP modes (advisory only in OSS)',
        },
        
        # Storage patterns
        {
            'pattern': r'graph_storage.*=.*["\'](neo4j|postgres|redis)["\']',
            'replacement': "graph_storage = 'in_memory'  # OSS: Only in-memory storage",
            'description': 'Persistent storage (in-memory only in OSS)',
        },
        
        # Audit patterns
        {
            'pattern': r'audit_trail\s*=',
            'replacement': '# audit_trail =  # REMOVED: Enterprise-only feature',
            'description': 'Audit trail (Enterprise only)',
        },
        {
            'pattern': r'audit_log\s*=',
            'replacement': '# audit_log =  # REMOVED: Enterprise-only feature',
            'description': 'Audit log (Enterprise only)',
        },
    ]
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.fixes_applied = []
        self.errors = []
    
    def fix_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """Fix V3 boundary violations in a single file."""
        fixes_in_file = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply all fixes
            for fix in self.FIX_PATTERNS:
                pattern = fix['pattern']
                replacement = fix['replacement']
                
                # Check if pattern exists (case-insensitive)
                if re.search(pattern, content, re.IGNORECASE):
                    # Apply the fix
                    new_content = re.sub(
                        pattern, 
                        replacement, 
                        content, 
                        flags=re.IGNORECASE
                    )
                    
                    if new_content != content:
                        content = new_content
                        fixes_in_file.append((fix['description'], pattern))
            
            # Write back if changes were made
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return fixes_in_file
                
        except Exception as e:
            self.errors.append(f"Error fixing {file_path}: {e}")
        
        return fixes_in_file
    
    def find_oss_files(self) -> List[Path]:
        """Find all OSS Python files to check."""
        oss_files = []
        
        # Exclude test directories and enterprise code
        exclude_dirs = {'test', 'tests', '__pycache__', '.git', 'node_modules'}
        
        for py_file in self.repo_path.glob("**/*.py"):
            # Skip excluded directories
            if any(excluded in str(py_file) for excluded in exclude_dirs):
                continue
            
            # Skip if it's in an excluded directory path
            parts = py_file.parts
            if any(part in exclude_dirs for part in parts):
                continue
            
            oss_files.append(py_file)
        
        return oss_files
    
    def run_fixes(self) -> bool:
        """Run all fixes and return success status."""
        print("🔧 FIXING V3 BOUNDARY VIOLATIONS")
        print("=" * 60)
        
        oss_files = self.find_oss_files()
        print(f"Found {len(oss_files)} OSS Python files to check")
        
        total_fixes = 0
        
        for file_path in oss_files:
            fixes = self.fix_file(file_path)
            
            if fixes:
                rel_path = file_path.relative_to(self.repo_path)
                print(f"\n📝 {rel_path}:")
                for description, pattern in fixes:
                    print(f"   • {description}")
                    print(f"     Pattern: {pattern[:50]}...")
                total_fixes += len(fixes)
                self.fixes_applied.extend(fixes)
        
        # Summary
        print(f"\n" + "=" * 60)
        print("📊 FIXES APPLIED")
        print("=" * 60)
        
        if total_fixes > 0:
            print(f"✅ Applied {total_fixes} fixes across {len([f for f in oss_files if self.fix_file(f)])} files")
            
            # Show fix categories
            fix_categories = {}
            for description, _ in self.fixes_applied:
                category = description.split(':')[0] if ':' in description else description
                fix_categories[category] = fix_categories.get(category, 0) + 1
            
            print("\n📋 Fix Categories:")
            for category, count in fix_categories.items():
                print(f"   • {category}: {count} fixes")
            
            print(f"\n⚠️  {len(self.errors)} errors encountered" if self.errors else "")
            
            return True
        else:
            print("✅ No fixes needed - V3 boundaries are already enforced")
            return True if not self.errors else False


def verify_fixes(repo_path: Path) -> bool:
    """Verify that fixes were applied correctly."""
    print("\n" + "=" * 60)
    print("🔍 VERIFYING FIXES")
    print("=" * 60)
    
    # Patterns that should NOT exist in OSS code
    prohibited_patterns = [
        r'license_key\s*=',
        r'validate_license\(',
        r'require_admin\(',
        r'MCPMode\.(APPROVAL|AUTONOMOUS)',
        r'mcp_mode.*=.*["\'](approval|autonomous)["\']',
        r'graph_storage.*=.*["\'](neo4j|postgres|redis)["\']',
    ]
    
    violations_found = []
    
    for py_file in repo_path.glob("**/*.py"):
        # Skip test files
        if 'test' in str(py_file).lower():
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            
            for pattern in prohibited_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if it's commented out or in a string
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            # Check if line is a comment or contains comment
                            stripped = line.strip()
                            if not stripped.startswith('#') and '#' not in line[:line.find(pattern)]:
                                rel_path = py_file.relative_to(repo_path)
                                violations_found.append(
                                    f"{rel_path}:{line_num}: {pattern[:30]}..."
                                )
        except Exception:
            continue
    
    if violations_found:
        print(f"❌ Found {len(violations_found)} remaining violations:")
        for violation in violations_found[:10]:  # Show first 10
            print(f"   • {violation}")
        if len(violations_found) > 10:
            print(f"   ... and {len(violations_found) - 10} more")
        return False
    else:
        print("✅ No remaining V3 boundary violations found!")
        return True


def main():
    """Main entry point."""
    repo_path = Path.cwd()
    
    print("=" * 70)
    print("🚀 V3 BOUNDARY VIOLATION FIXER")
    print("=" * 70)
    print("\nThis script fixes common V3 boundary violations in OSS code.")
    print("It will:")
    print("  1. Find Enterprise patterns in OSS code")
    print("  2. Replace them with OSS-compliant alternatives")
    print("  3. Verify fixes were applied correctly")
    print()
    
    # Ask for confirmation
    response = input("⚠️  Proceed with fixing V3 boundary violations? (y/N): ")
    if response.lower() != 'y':
        print("Aborted.")
        return 1
    
    # Run fixes
    fixer = V3BoundaryFixer(repo_path)
    fixes_applied = fixer.run_fixes()
    
    if not fixes_applied:
        print("❌ Failed to apply fixes")
        return 1
    
    # Verify fixes
    verification_passed = verify_fixes(repo_path)
    
    print("\n" + "=" * 70)
    if verification_passed:
        print("🎉 V3 BOUNDARY FIXES COMPLETED SUCCESSFULLY!")
        print("\nNext steps:")
        print("  1. Run V3 validation: python scripts/run_v3_validation.py --fast")
        print("  2. Get certification: python scripts/run_v3_validation.py --certify")
        print("  3. Check GitHub Actions: Run V3 Comprehensive Validation workflow")
        return 0
    else:
        print("🚨 V3 BOUNDARY FIXES INCOMPLETE")
        print("\nRequired actions:")
        print("  1. Manually fix remaining violations shown above")
        print("  2. Re-run this script: python scripts/fix_v3_boundary_violations.py")
        print("  3. Run V3 validation after fixes")
        return 1


if __name__ == "__main__":
    sys.exit(main())
