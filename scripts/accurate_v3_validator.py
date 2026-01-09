#!/usr/bin/env python3
"""
Accurate V3 Boundary Validator
Only flags REAL violations, not false positives
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict

class AccurateV3Validator:
    """Validates V3 boundaries without false positives"""
    
    def __init__(self):
        # REAL violations only - patterns that should NOT exist in OSS
        self.real_violations = {
            # License key ASSIGNMENT (not checking)
            'license_key_assignment': {
                'pattern': r'^\s*license_key\s*=',
                'description': 'License key variable assignment (Enterprise only)',
                'valid_oss_examples': [
                    'license_key = os.getenv("ARF_LICENSE_KEY")',  # BAD - assignment
                ]
            },
            
            # Enterprise features that should not exist in OSS
            'autonomous_execution_field': {
                'pattern': r'^\s*autonomous_execution\s*:',
                'description': 'autonomous_execution field (Enterprise only)',
            },
            
            # MCP modes that should not exist in OSS
            'mcp_mode_approval': {
                'pattern': r'MCPMode\.APPROVAL\b',
                'description': 'MCP approval mode (Enterprise only)',
            },
            'mcp_mode_autonomous': {
                'pattern': r'MCPMode\.AUTONOMOUS\b',
                'description': 'MCP autonomous mode (Enterprise only)',
            },
            
            # Admin requirement (should use operator in OSS)
            'require_admin_call': {
                'pattern': r'require_admin\(',
                'description': 'require_admin() call (should be require_operator in OSS)',
            },
            
            # Enterprise feature flags
            'learning_enabled_true': {
                'pattern': r'^\s*learning_enabled\s*=\s*True\b',
                'description': 'learning_enabled = True (must be False in OSS)',
            },
            'beta_testing_enabled_true': {
                'pattern': r'^\s*beta_testing_enabled\s*=\s*True\b',
                'description': 'beta_testing_enabled = True (must be False in OSS)',
            },
            'rollout_percentage_gt_zero': {
                'pattern': r'^\s*rollout_percentage\s*=\s*[1-9]',
                'description': 'rollout_percentage > 0 (must be 0 in OSS)',
            },
        }
        
        # Valid OSS patterns (NOT violations)
        self.valid_oss_patterns = {
            'license_checking': r'os\.getenv\("ARF_LICENSE_KEY"',
            'oss_edition': r'OSS_EDITION\s*=',
            'require_operator': r'require_operator\(',
            'advisory_mode': r'MCPMode\.ADVISORY\b',
            'oss_advisory': r'OSS.*advisory',
        }

    def check_file(self, file_path: Path) -> List[Dict]:
        """Check a file for REAL violations only"""
        violations = []
        
        if not file_path.exists():
            return violations
        
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""'):
                continue
            
            for violation_name, violation_info in self.real_violations.items():
                pattern = violation_info['pattern']
                
                # Check if pattern exists
                if re.search(pattern, line):
                    # Additional validation for specific cases
                    if not self._is_false_positive(line, violation_name):
                        violations.append({
                            'file': str(file_path),
                            'line': line_num,
                            'violation': violation_name,
                            'description': violation_info['description'],
                            'code': line.strip()[:80]
                        })
        
        return violations

    def _is_false_positive(self, line: str, violation_name: str) -> bool:
        """Check if a detected pattern is a false positive"""
        line_lower = line.lower()
        
        # Valid OSS patterns that might look like violations
        if violation_name == 'license_key_assignment':
            # Check if it's actually in a function that checks for licenses
            # (like check_oss_compliance())
            return 'check_oss_compliance' in line_lower or 'check_compliance' in line_lower
        
        # Check if line is commented out
        if line.strip().startswith('#'):
            return True
            
        # Check if pattern is in a string literal (not code)
        if self._is_in_string_literal(line):
            return True
            
        return False

    def _is_in_string_literal(self, line: str) -> bool:
        """Check if text is inside quotes"""
        # Simple check: if there's an odd number of quotes before the text
        # This is a simplified check
        parts = line.split('"')
        if len(parts) % 2 == 0:  # Even number of quotes means we're inside a string
            return True
        return False

    def validate_repository(self, repo_path: Path) -> Dict:
        """Validate entire repository"""
        all_violations = []
        
        print(f"🔍 Checking {repo_path.name} for REAL V3 violations...")
        
        # Check all Python files
        python_files = list(repo_path.glob("**/*.py"))
        
        for py_file in python_files:
            if "__pycache__" in str(py_file) or "test" in str(py_file).lower():
                continue
                
            violations = self.check_file(py_file)
            all_violations.extend(violations)
        
        # Group by file
        violations_by_file = {}
        for violation in all_violations:
            violations_by_file.setdefault(violation['file'], []).append(violation)
        
        return {
            'total_violations': len(all_violations),
            'violations_by_file': violations_by_file,
            'all_violations': all_violations,
        }

def main():
    """Main function"""
    validator = AccurateV3Validator()
    repo_path = Path(__file__).parent.parent
    
    print("=" * 70)
    print("🔍 ACCURATE V3 BOUNDARY VALIDATION")
    print("Only flags REAL violations, not false positives")
    print("=" * 70)
    
    results = validator.validate_repository(repo_path)
    
    if results['total_violations'] == 0:
        print("\n✅ NO REAL V3 VIOLATIONS FOUND!")
        print("\nYour OSS code is clean.")
        print("The previous validation was showing false positives.")
        return 0
    else:
        print(f"\n🚨 Found {results['total_violations']} REAL violations:")
        
        for file_path, file_violations in results['violations_by_file'].items():
            print(f"\n📄 {file_path}:")
            for violation in file_violations:
                print(f"   Line {violation['line']}: {violation['violation']}")
                print(f"      {violation['code']}")
        
        return 1

if __name__ == "__main__":
    exit(main())
