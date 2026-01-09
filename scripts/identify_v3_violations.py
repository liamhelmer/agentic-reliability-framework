#!/usr/bin/env python3
"""
Identify V3 Violations - Shows exactly which files and lines are causing V3 boundary violations
"""

import re
from pathlib import Path
import sys
from typing import List, Dict, Any

class V3ViolationFinder:
    def __init__(self):
        self.repo_path = Path.cwd()
        self.violations = []
        
        # V3 Boundary Patterns (Enterprise-only in OSS)
        self.boundary_patterns = [
            # Execution patterns
            (r'require_admin\(', 'Admin requirement (use require_operator in OSS)'),
            (r'autonomous.*execute', 'Autonomous execution (Enterprise only)'),
            (r'autonomous.*mode', 'Autonomous mode (Enterprise only)'),
            (r'AUTONOMOUS.*MODE', 'Autonomous mode constant (Enterprise only)'),
            
            # License patterns
            (r'license_key\s*=', 'License key assignment (Enterprise only)'),
            (r'validate_license\(', 'License validation call (Enterprise only)'),
            (r'has_enterprise_license\(', 'Enterprise license check (Enterprise only)'),
            (r'has_autonomy_license\(', 'Autonomy license check (Enterprise only)'),
            
            # MCP Mode patterns
            (r'MCPMode\.APPROVAL', 'MCP approval mode (Enterprise only)'),
            (r'MCPMode\.AUTONOMOUS', 'MCP autonomous mode (Enterprise only)'),
            (r'mcp_mode\s*=\s*["\'](approval|autonomous)["\']', 'Non-advisory MCP mode (advisory only in OSS)'),
            
            # Feature flags
            (r'learning_enabled\s*=\s*(True|\d+)', 'Learning enabled (must be False in OSS)'),
            (r'beta_testing_enabled\s*=\s*(True|\d+)', 'Beta testing enabled (must be False in OSS)'),
            (r'rollout_percentage\s*=\s*[1-9]\d*', 'Rollout percentage > 0 (must be 0 in OSS)'),
            
            # Audit patterns
            (r'audit_trail\s*=', 'Audit trail (Enterprise only)'),
            (r'audit_log\s*=', 'Audit log (Enterprise only)'),
            (r'export_audit\(', 'Audit export (Enterprise only)'),
            
            # Storage patterns
            (r'graph_storage\s*=\s*["\'](neo4j|postgres|redis|mysql)["\']', 'Persistent storage (in-memory only in OSS)'),
            
            # Learning patterns
            (r'learning_engine', 'Learning engine (Enterprise only)'),
            (r'LearningEngine', 'LearningEngine class (Enterprise only)'),
            
            # Novel execution
            (r'novel_execution', 'Novel execution (Enterprise only)'),
            (r'validate_novel_execution', 'Novel execution validation (Enterprise only)'),
            
            # Rollback execution
            (r'execute_rollback', 'Rollback execution (OSS can only analyze)'),
            
            # Enterprise imports
            (r'from arf_enterprise', 'Enterprise import (not allowed in OSS)'),
            (r'import arf_enterprise', 'Enterprise import (not allowed in OSS)'),
            
            # Advanced FAISS
            (r'IndexIVF', 'Advanced FAISS IndexIVF (Enterprise only)'),
            (r'IndexHNSW', 'Advanced FAISS IndexHNSW (Enterprise only)'),
            (r'IndexPQ', 'Advanced FAISS IndexPQ (Enterprise only)'),
        ]
    
    def should_scan_file(self, file_path: Path) -> bool:
        """Check if we should scan this file."""
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', '.github', 'node_modules', 'dist', 'build'}
        
        for part in file_path.parts:
            if part in skip_dirs:
                return False
        
        # Only scan Python files
        if file_path.suffix != '.py':
            return False
        
        # Skip our own scripts to avoid false positives
        if file_path.name.startswith(('identify_v3', 'fix_v3', 'diagnose_v3')):
            return False
        
        return True
    
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a single file for V3 violations."""
        file_violations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern, description in self.boundary_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        # Check if it's commented out or in a string
                        if not self._is_excluded(line, match.start()):
                            file_violations.append({
                                'file': str(file_path),
                                'line': line_num,
                                'pattern': pattern,
                                'description': description,
                                'code': line.strip(),
                                'match': match.group(0)
                            })
                            
        except Exception as e:
            file_violations.append({
                'file': str(file_path),
                'error': f"Error scanning file: {e}"
            })
        
        return file_violations
    
    def _is_excluded(self, line: str, match_pos: int) -> bool:
        """Check if match is in comment or string."""
        # Check if line is commented
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            return True
        
        # Check if match is after a comment
        if '#' in line and line.find('#') < match_pos:
            return True
        
        # Check if match is inside quotes (crude check)
        before_match = line[:match_pos]
        after_match = line[match_pos:]
        
        # Count quotes before and after
        quotes_before = before_match.count('"') + before_match.count("'")
        quotes_after = after_match.count('"') + after_match.count("'")
        
        # If odd number of quotes before and after, it's inside string
        if quotes_before % 2 == 1 and quotes_after % 2 == 1:
            return True
        
        return False
    
    def scan_repository(self) -> None:
        """Scan entire repository for V3 violations."""
        print("🔍 SCANNING FOR V3 BOUNDARY VIOLATIONS")
        print("=" * 70)
        
        python_files = list(self.repo_path.glob("**/*.py"))
        print(f"Found {len(python_files)} Python files in repository")
        
        for i, file_path in enumerate(python_files):
            if not self.should_scan_file(file_path):
                continue
            
            file_violations = self.scan_file(file_path)
            if file_violations:
                self.violations.extend(file_violations)
            
            # Show progress
            if (i + 1) % 50 == 0:
                print(f"  Scanned {i + 1}/{len(python_files)} files...")
    
    def generate_report(self) -> str:
        """Generate a detailed violation report."""
        if not self.violations:
            return "✅ No V3 boundary violations found!"
        
        report = []
        report.append("=" * 70)
        report.append("🚨 V3 BOUNDARY VIOLATIONS REPORT")
        report.append("=" * 70)
        report.append(f"\nTotal violations found: {len(self.violations)}")
        
        # Group by file
        violations_by_file = {}
        for violation in self.violations:
            if 'error' not in violation:
                file = violation['file']
                violations_by_file[file] = violations_by_file.get(file, []) + [violation]
        
        report.append(f"Files with violations: {len(violations_by_file)}")
        
        # Report by file
        for file, file_violations in violations_by_file.items():
            rel_path = Path(file).relative_to(self.repo_path)
            report.append(f"\n📄 {rel_path} ({len(file_violations)} violations):")
            
            for violation in file_violations[:5]:  # Show first 5 per file
                report.append(f"  Line {violation['line']}: {violation['description']}")
                report.append(f"     Code: {violation['code'][:80]}...")
                report.append(f"     Match: {violation['match']}")
            
            if len(file_violations) > 5:
                report.append(f"  ... and {len(file_violations) - 5} more violations")
        
        # Summary by violation type
        violation_types = {}
        for violation in self.violations:
            if 'error' not in violation:
                desc = violation['description']
                violation_types[desc] = violation_types.get(desc, 0) + 1
        
        report.append("\n" + "=" * 70)
        report.append("📊 VIOLATIONS BY TYPE")
        report.append("=" * 70)
        
        for desc, count in sorted(violation_types.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {desc}: {count}")
        
        # Recommendations
        report.append("\n" + "=" * 70)
        report.append("🚀 RECOMMENDED ACTIONS")
        report.append("=" * 70)
        report.append("\n1. Review the violations above")
        report.append("2. For each violation:")
        report.append("   - Replace require_admin() with require_operator()")
        report.append("   - Set learning_enabled = False")
        report.append("   - Set beta_testing_enabled = False") 
        report.append("   - Set rollout_percentage = 0")
        report.append("   - Change mcp_mode to 'advisory'")
        report.append("   - Comment out or remove Enterprise-only features")
        report.append("\n3. Run validation after fixes:")
        report.append("   python scripts/run_v3_validation.py --fast")
        report.append("\n4. If many violations, use fix script:")
        report.append("   python scripts/fix_v3_boundary_violations.py")
        
        return "\n".join(report)
    
    def save_report(self, output_path: Path = None) -> Path:
        """Save report to file."""
        if output_path is None:
            output_path = self.repo_path / "V3_VIOLATIONS_DETAILED_REPORT.txt"
        
        report = self.generate_report()
        output_path.write_text(report, encoding='utf-8')
        return output_path

def main():
    """Main function."""
    print("=" * 70)
    print("🔍 V3 BOUNDARY VIOLATION IDENTIFIER")
    print("=" * 70)
    print("\nThis script scans the entire repository to identify")
    print("exactly which files and lines violate V3 boundaries.")
    print("\nIt will show you the violations BEFORE any fixes are made.")
    print()
    
    finder = V3ViolationFinder()
    
    # Scan repository
    print("Scanning... This may take a moment...")
    finder.scan_repository()
    
    # Generate and display report
    report = finder.generate_report()
    print("\n" + report)
    
    # Save detailed report
    report_path = finder.save_report()
    print(f"\n📄 Detailed report saved to: {report_path.relative_to(Path.cwd())}")
    
    # Show next steps
    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS")
    print("=" * 70)
    
    if finder.violations:
        print("\n🚨 ACTION REQUIRED:")
        print("1. Review the violations in the report above")
        print("2. Decide whether to:")
        print("   a) Fix manually (recommended for review)")
        print("   b) Use automatic fix script")
        print("3. Run validation after fixes")
        print("\nTo use automatic fix (after review):")
        print("   python scripts/fix_v3_boundary_violations.py")
        return 1
    else:
        print("\n✅ NO ACTION NEEDED:")
        print("The repository is already V3 compliant!")
        print("\nRun validation to confirm:")
        print("   python scripts/run_v3_validation.py --certify")
        return 0

if __name__ == "__main__":
    sys.exit(main())
