#!/usr/bin/env python3
"""
Quick fix for specific V3 violations found in the validation.
"""

from pathlib import Path
import sys

def fix_config_py():
    """Fix agentic_reliability_framework/config.py."""
    config_path = Path("agentic_reliability_framework/config.py")
    
    if not config_path.exists():
        print(f"❌ {config_path} not found")
        return False
    
    try:
        content = config_path.read_text(encoding='utf-8')
        
        # Fix autonomous execution references
        if 'autonomous_execution' in content:
            content = content.replace(
                'autonomous_execution',
                '# autonomous_execution  # REMOVED: Enterprise-only feature'
            )
        
        # Fix rollout_percentage
        if 'rollout_percentage' in content and '= 0' not in content:
            # Find and replace rollout_percentage assignments
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if 'rollout_percentage' in line and '=' in line:
                    # Check if it's already set to 0
                    if '0' not in line:
                        new_lines.append('rollout_percentage = 0  # OSS: Always 0')
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        
        config_path.write_text(content, encoding='utf-8')
        print(f"✅ Fixed {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {config_path}: {e}")
        return False

def fix_oss_constants():
    """Fix oss/constants.py if it exists."""
    # Check if oss/constants.py exists
    oss_constants_path = Path("oss/constants.py")
    
    if not oss_constants_path.exists():
        print(f"⚠️  {oss_constants_path} not found (may not exist)")
        return True  # Not an error if file doesn't exist
    
    try:
        content = oss_constants_path.read_text(encoding='utf-8')
        
        # Fix license_key references
        if 'license_key' in content:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if 'license_key' in line and '=' in line:
                    # Comment out the line
                    new_lines.append(f'# {line}  # REMOVED: Enterprise-only feature')
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        
        oss_constants_path.write_text(content, encoding='utf-8')
        print(f"✅ Fixed {oss_constants_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {oss_constants_path}: {e}")
        return False

def main():
    """Run quick fixes."""
    print("🔧 QUICK FIX FOR V3 VIOLATIONS")
    print("=" * 50)
    print("\nFixing specific violations found in validation:")
    print("1. config.py - autonomous_execution and rollout_percentage")
    print("2. oss/constants.py - license_key references")
    print()
    
    success = True
    
    # Fix config.py
    if not fix_config_py():
        success = False
    
    # Fix oss/constants.py
    if not fix_oss_constants():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ QUICK FIXES APPLIED")
        print("\nNext steps:")
        print("1. Run: python scripts/run_v3_validation.py --fast")
        print("2. Check if violations are resolved")
        print("3. Run: python scripts/run_v3_validation.py --certify")
        return 0
    else:
        print("❌ SOME FIXES FAILED")
        print("\nManual intervention may be required.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
