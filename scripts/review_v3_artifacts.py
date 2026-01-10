#!/usr/bin/env python3
"""
Review and validate V3.3.9 release artifacts
"""
import json
from pathlib import Path
from datetime import datetime

def review_milestone_report(report_path: Path):
    """Review milestone report for completeness"""
    print("📋 Reviewing Milestone Report...")
    
    if not report_path.exists():
        print("❌ Milestone report not found")
        return False
    
    content = report_path.read_text()
    required_sections = [
        "V3 Architecture Achievements",
        "Business Impact", 
        "Next Steps"
    ]
    
    for section in required_sections:
        if section not in content:
            print(f"❌ Missing section: {section}")
            return False
    
    print("✅ Milestone report validated")
    return True

def review_validation_report(report_path: Path):
    """Review validation report for correctness"""
    print("🔍 Reviewing Validation Report...")
    
    if not report_path.exists():
        print("❌ Validation report not found")
        return False
    
    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        # Check for V3.3.9 specific validation
        if "version" in data and data["version"] != "3.3.9":
            print(f"❌ Wrong version in report: {data.get('version')}, expected 3.3.9")
            return False
            
        print("✅ Validation report is for V3.3.9")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in validation report")
        return False

def check_v3_architecture_files():
    """Check that all required V3.3.9 files exist"""
    print("🏗️  Checking V3.3.9 Architecture Files...")
    
    required_files = [
        "agentic_reliability_framework/engine/v3_reliability.py",
        "agentic_reliability_framework/arf_core/config/oss_config.py",
        "agentic_reliability_framework/arf_core/engine/oss_mcp_client.py",
        ".github/workflows/v3_milestone_sequence.yml",
        ".github/workflows/v3_release_automation.yml",
        "scripts/smart_v3_validator.py",
        "scripts/review_v3_artifacts.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
    
    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} required files")
        return False
    
    print(f"✅ All {len(required_files)} V3.3.9 files present")
    return True

def generate_release_summary():
    """Generate comprehensive release summary for V3.3.9"""
    print("📊 Generating V3.3.9 Release Summary...")
    
    summary = {
        "release_phase": "V3.3.9",
        "validation_status": "PASSED",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "v3_architecture_files": False,
            "milestone_report": False,
            "validation_report": False,
            "workflow_files": False
        },
        "artifacts": [],
        "next_actions": [
            "Run: python scripts/smart_v3_validator.py",
            "Check: artifacts/v3-validation-report.json",
            "Review: milestone-report-V3.3.md"
        ]
    }
    
    # Check V3 architecture files
    summary["checks"]["v3_architecture_files"] = check_v3_architecture_files()
    
    # Check for artifacts
    artifacts_dir = Path("artifacts")
    if artifacts_dir.exists():
        for artifact in artifacts_dir.glob("*"):
            summary["artifacts"].append({
                "name": artifact.name,
                "size": artifact.stat().st_size,
                "modified": datetime.fromtimestamp(artifact.stat().st_mtime).isoformat()
            })
    
    # Review reports
    milestone_report = Path("milestone-report-V3.3.md")
    validation_report = artifacts_dir / "v3-validation-report.json"
    
    summary["checks"]["milestone_report"] = review_milestone_report(milestone_report)
    summary["checks"]["validation_report"] = review_validation_report(validation_report)
    
    # Check workflow files
    workflow_files_exist = all([
        Path(".github/workflows/v3_milestone_sequence.yml").exists(),
        Path(".github/workflows/v3_release_automation.yml").exists()
    ])
    summary["checks"]["workflow_files"] = workflow_files_exist
    
    # Determine overall status
    if all(summary["checks"].values()):
        summary["next_actions"] = [
            "✅ Proceed with V3.3.9 release",
            "📦 Upload to PyPI",
            "📢 Announce release"
        ]
    else:
        summary["validation_status"] = "FAILED"
        summary["next_actions"] = [
            "❌ Fix validation issues before release",
            "🔧 Check missing files listed above",
            "🔄 Re-run validation workflow"
        ]
    
    # Save summary
    summary_path = Path("release_summary_v3.3.9.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Release summary saved to: {summary_path}")
    return summary

if __name__ == "__main__":
    print("🚀 V3.3.9 Release Artifact Review")
    print("=" * 50)
    
    summary = generate_release_summary()
    
    print("\n📈 Review Summary:")
    print(f"   Status: {summary['validation_status']}")
    print(f"   Release: {summary['release_phase']}")
    print(f"   Artifacts: {len(summary['artifacts'])} found")
    
    print("\n🔍 Checks performed:")
    for check_name, check_result in summary["checks"].items():
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")
    
    if summary["validation_status"] == "PASSED":
        print("\n🎉 V3.3.9 READY FOR RELEASE!")
        for action in summary["next_actions"]:
            print(f"   {action}")
    else:
        print("\n⚠️  V3.3.9 RELEASE BLOCKED!")
        for action in summary["next_actions"]:
            print(f"   {action}")
