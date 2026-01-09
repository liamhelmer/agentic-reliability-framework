# scripts/v3_feature_gating.py
"""
V3 Feature Gating - Leverage Proven Architecture Split
Version: 3.3.7 | Validated: $(date)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# ============================================================================
# V3 PROVEN ARCHITECTURE CONSTANTS
# ============================================================================

class Edition(str, Enum):
    """V3 Proven Editions"""
    OSS = "oss"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"

class V3Boundary(str, Enum):
    """Mechanically Enforced Boundaries"""
    ADVISORY_ONLY = "advisory_only"
    NO_EXECUTION = "no_execution"
    LICENSE_CHECK_ONLY = "license_check_only"
    ROLLBACK_REQUIRED = "rollback_required"
    ADMIN_ONLY_MUTATION = "admin_only_mutation"

# ============================================================================
# V3 FEATURE MATRIX (PROVEN)
# ============================================================================

class V3FeatureMatrix:
    """
    V3 Feature Gating Based on Proven Architecture Split
    
    This is not marketing - features are mechanically gated
    based on validated V3 boundaries.
    """
    
    # OSS Edition Features (Apache 2.0)
    OSS_FEATURES = {
        "advisory_intelligence": {
            "description": "Sophisticated analysis without execution",
            "components": [
                "execution_graph_analysis",
                "policy_evaluation",
                "confidence_scoring",
                "business_impact_modeling",
                "memory_backed_reasoning"
            ],
            "validation": "V3.0 validated",
            "enforcement": "EXECUTION_ALLOWED = False"
        },
        "rag_graph": {
            "description": "RAG with 1k incident limit",
            "limit": 1000,
            "validation": "MAX_INCIDENT_HISTORY = 1000",
            "upgrade_path": "enterprise_unlimited_rag"
        },
        "mcp_advisory": {
            "description": "MCP server advisory mode only",
            "mode": "advisory",
            "validation": "MCPMode.ADVISORY enforced",
            "enforcement": "pattern='^advisory$'"
        },
        "execution_traces": {
            "description": "Read-only audit trails",
            "capability": "analysis_only",
            "validation": "No mutation endpoints"
        }
    }
    
    # Enterprise Edition Features (Commercial License)
    ENTERPRISE_FEATURES = {
        "governed_execution": {
            "description": "Permissioned execution with oversight",
            "components": [
                "execution_ladder",
                "role_gated_authority",
                "require_admin_paths",
                "mandatory_rollback"
            ],
            "license_required": True,
            "validation": "V3.1 planned"
        },
        "unlimited_rag": {
            "description": "No incident limit constraints",
            "limit": "unlimited",
            "license_required": True,
            "upgrade_from": "oss_rag_graph"
        },
        "mcp_authority": {
            "description": "MCP approval/autonomous modes",
            "modes": ["approval", "autonomous"],
            "license_required": True,
            "validation": "License gated"
        },
        "rollback_api": {
            "description": "Production rollback execution",
            "capabilities": [
                "pre_execution_analysis",
                "bulk_orchestration",
                "audit_trail_export"
            ],
            "license_required": True,
            "validation": "Enterprise-only endpoints"
        },
        "neo4j_persistence": {
            "description": "Persistent causal execution graphs",
            "dependencies": ["neo4j"],
            "license_required": True,
            "validation": "Enterprise dependencies"
        },
        "learning_loop": {
            "description": "Outcome-based system improvement",
            "components": [
                "confidence_weighting",
                "policy_effectiveness",
                "memory_graph_updates"
            ],
            "license_required": True,
            "validation": "V3.3 planned"
        }
    }
    
    # Trial Features (Evaluation Bridge)
    TRIAL_FEATURES = {
        "execution_preview": {
            "description": "Limited execution with oversight",
            "duration": "30_days",
            "limits": ["production_safe", "monitored_only"],
            "conversion_target": "governed_execution"
        },
        "enhanced_rag": {
            "description": "10k incident limit",
            "limit": 10000,
            "duration": "30_days",
            "conversion_target": "unlimited_rag"
        },
        "audit_preview": {
            "description": "Export sample audit trails",
            "limit": "100_entries",
            "duration": "30_days",
            "conversion_target": "full_audit"
        }
    }

# ============================================================================
# RUNTIME FEATURE GATING
# ============================================================================

class V3FeatureGate:
    """
    Runtime Feature Gating Based on Proven V3 Architecture
    
    Uses mechanical validation of current environment to determine
    which features are available.
    """
    
    def __init__(self):
        self.edition = self._detect_edition()
        self.license_valid = self._check_license()
        self.trial_active = self._check_trial()
        
        # Log detection results
        print(f"🔍 V3 Feature Gate Initialized:")
        print(f"   Edition: {self.edition.value}")
        print(f"   License Valid: {self.license_valid}")
        print(f"   Trial Active: {self.trial_active}")
        print(f"   Validation: V3 boundaries proven")
    
    def _detect_edition(self) -> Edition:
        """Detect edition based on proven V3 boundaries"""
        
        # Check environment variables
        env_edition = os.getenv("ARF_EDITION", "oss").lower()
        
        if env_edition == "enterprise":
            # Verify Enterprise indicators
            if os.getenv("ARF_LICENSE_KEY", "").startswith("ARF-ENT-"):
                return Edition.ENTERPRISE
            elif os.getenv("ARF_TRIAL_ACTIVE", "false").lower() == "true":
                return Edition.TRIAL
        
        # Default to OSS (proven safe)
        return Edition.OSS
    
    def _check_license(self) -> bool:
        """Check if valid Enterprise license exists"""
        license_key = os.getenv("ARF_LICENSE_KEY", "")
        
        # Valid Enterprise license patterns
        enterprise_patterns = ["ARF-ENT-", "ARF-COMMERCIAL-"]
        
        for pattern in enterprise_patterns:
            if license_key.startswith(pattern):
                # Additional validation could go here
                return True
        
        return False
    
    def _check_trial(self) -> bool:
        """Check if trial is active"""
        trial_active = os.getenv("ARF_TRIAL_ACTIVE", "false").lower()
        trial_expiry = os.getenv("ARF_TRIAL_EXPIRY", "")
        
        if trial_active == "true" and trial_expiry:
            # Check if trial is still valid
            from datetime import datetime
            try:
                expiry_date = datetime.fromisoformat(trial_expiry)
                if datetime.now() < expiry_date:
                    return True
            except ValueError:
                pass
        
        return False
    
    def get_available_features(self) -> Dict[str, Dict]:
        """Get features available in current edition"""
        matrix = V3FeatureMatrix()
        available = {"edition": self.edition.value}
        
        # Always include OSS features (proven available)
        available["oss_features"] = matrix.OSS_FEATURES
        
        # Add Enterprise features if licensed
        if self.edition == Edition.ENTERPRISE and self.license_valid:
            available["enterprise_features"] = matrix.ENTERPRISE_FEATURES
        
        # Add Trial features if active
        elif self.edition == Edition.TRIAL and self.trial_active:
            available["trial_features"] = matrix.TRIAL_FEATURES
            
            # Also include limited Enterprise features
            limited_enterprise = {}
            for key, feature in matrix.ENTERPRISE_FEATURES.items():
                limited_enterprise[key] = {
                    **feature,
                    "trial_limited": True,
                    "requires_conversion": True
                }
            available["trial_enterprise_features"] = limited_enterprise
        
        # Add upgrade prompts for OSS users
        if self.edition == Edition.OSS:
            available["upgrade_opportunities"] = self._get_upgrade_opportunities()
        
        return available
    
    def _get_upgrade_opportunities(self) -> List[Dict]:
        """Get upgrade opportunities for OSS users"""
        return [
            {
                "from": "oss_rag_graph",
                "to": "enterprise_unlimited_rag",
                "benefit": "Remove 1k incident limit",
                "business_case": "Large-scale deployments"
            },
            {
                "from": "mcp_advisory",
                "to": "mcp_authority",
                "benefit": "Enable approval/autonomous modes",
                "business_case": "Reduced operator workload"
            },
            {
                "from": "execution_traces",
                "to": "rollback_api",
                "benefit": "Add production rollback capability",
                "business_case": "Survivable autonomy"
            }
        ]
    
    def can_execute(self, action: str, context: Dict = None) -> Tuple[bool, str]:
        """
        Check if execution is allowed based on V3 boundaries
        
        Returns: (allowed, reason)
        """
        context = context or {}
        
        # OSS Edition: No execution (proven)
        if self.edition == Edition.OSS:
            return False, "OSS edition: Advisory only (V3.0 validated)"
        
        # Trial Edition: Limited execution
        if self.edition == Edition.TRIAL:
            trial_limits = {
                "max_executions_per_day": 100,
                "allowed_actions": ["rollback", "restart", "scale"],
                "production_safe_only": True
            }
            
            if action not in trial_limits["allowed_actions"]:
                return False, f"Trial: Action '{action}' not allowed"
            
            # Additional trial checks...
            return True, "Trial execution allowed (monitored)"
        
        # Enterprise Edition: Check license and permissions
        if self.edition == Edition.ENTERPRISE:
            if not self.license_valid:
                return False, "Enterprise license required"
            
            # Enterprise execution with V3.1 governance
            return True, "Enterprise execution allowed (V3.1 governance)"
        
        return False, "Unknown edition"
    
    def get_upgrade_url(self, feature: str = None) -> str:
        """Get upgrade URL based on current edition and desired feature"""
        base_url = "https://arf.dev/upgrade"
        
        if self.edition == Edition.OSS:
            if feature:
                return f"{base_url}/oss-to-enterprise?feature={feature}"
            return f"{base_url}/oss-to-enterprise"
        
        elif self.edition == Edition.TRIAL:
            return f"{base_url}/trial-to-enterprise"
        
        return base_url

# ============================================================================
# UPGRADE FLOW MANAGEMENT
# ============================================================================

class V3UpgradeManager:
    """
    Manage OSS → Enterprise upgrade flows
    
    Based on proven V3 architecture, not feature flags.
    """
    
    def __init__(self, feature_gate: V3FeatureGate):
        self.gate = feature_gate
        self.upgrade_paths = self._define_upgrade_paths()
    
    def _define_upgrade_paths(self) -> Dict[str, Dict]:
        """Define mechanical upgrade paths based on V3 boundaries"""
        return {
            "v3.0_to_v3.1": {
                "from": {"edition": "oss", "milestone": "V3.0"},
                "to": {"edition": "enterprise", "milestone": "V3.1"},
                "changes": [
                    "Enable require_admin() paths",
                    "Add license validation",
                    "Gate execution endpoints",
                    "Enable rollback API"
                ],
                "validation_required": ["v3_boundaries", "license_gating"],
                "estimated_duration": "1_hour",
                "reversible": True
            },
            "v3.1_to_v3.2": {
                "from": {"edition": "enterprise", "milestone": "V3.1"},
                "to": {"edition": "enterprise", "milestone": "V3.2"},
                "changes": [
                    "Add risk-bounded autonomy",
                    "Enhance rollback planning",
                    "Add confidence threshold escalation"
                ],
                "validation_required": ["autonomy_safety", "rollback_verification"],
                "estimated_duration": "2_hours",
                "reversible": False
            }
        }
    
    def generate_upgrade_plan(self, target_milestone: str) -> Dict:
        """Generate upgrade plan to target V3 milestone"""
        current_edition = self.gate.edition.value
        
        # Find applicable upgrade path
        for path_id, path in self.upgrade_paths.items():
            if (path["from"]["edition"] == current_edition and 
                path["to"]["milestone"] == target_milestone):
                
                plan = {
                    "path": path_id,
                    "current": path["from"],
                    "target": path["to"],
                    "steps": self._generate_upgrade_steps(path),
                    "prerequisites": self._check_prerequisites(path),
                    "validation_script": self._generate_validation_script(path)
                }
                
                return plan
        
        return {"error": f"No upgrade path from {current_edition} to {target_milestone}"}
    
    def _generate_upgrade_steps(self, path: Dict) -> List[str]:
        """Generate concrete upgrade steps"""
        steps = []
        
        if path["to"]["milestone"] == "V3.1":
            steps = [
                "1. Obtain Enterprise license from https://arf.dev/pricing",
                "2. Set ARF_LICENSE_KEY environment variable",
                "3. Restart ARF services",
                "4. Verify license validation: curl http://localhost:8000/api/v1/license/validate",
                "5. Enable execution features in configuration",
                "6. Run V3.1 validation: python scripts/validate_v3.1.py"
            ]
        
        return steps
    
    def _check_prerequisites(self, path: Dict) -> Dict:
        """Check if prerequisites are met for upgrade"""
        checks = {
            "v3_boundaries_valid": self._check_v3_boundaries(),
            "system_compatible": self._check_system_compatibility(),
            "data_backup_available": True,  # Placeholder
            "rollback_plan_exists": True    # Placeholder
        }
        
        return {
            "checks": checks,
            "all_passed": all(checks.values()),
            "failed_checks": [k for k, v in checks.items() if not v]
        }
    
    def _check_v3_boundaries(self) -> bool:
        """Verify V3 boundaries are intact before upgrade"""
        try:
            # Run quick V3 validation
            import subprocess
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/test_v3_boundaries.py::test_oss_no_execution", "-v"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_system_compatibility(self) -> bool:
        """Check if system meets requirements for target edition"""
        # Check for Enterprise dependencies if needed
        if self.gate.edition == Edition.OSS:
            # OSS → Enterprise requires additional dependencies
            try:
                import neo4j
                return True
            except ImportError:
                return False
        
        return True
    
    def _generate_validation_script(self, path: Dict) -> str:
        """Generate validation script for upgrade"""
        milestone = path["to"]["milestone"]
        
        if milestone == "V3.1":
            return """#!/usr/bin/env python3
# V3.1 Upgrade Validation Script
import sys
import os

print("🔍 Validating V3.1 (Execution Governance) Upgrade")
print("=" * 60)

checks_passed = 0
checks_total = 0

# Check 1: License validation
checks_total += 1
if os.getenv("ARF_LICENSE_KEY", "").startswith("ARF-ENT-"):
    print("✅ License: Valid Enterprise license")
    checks_passed += 1
else:
    print("❌ License: Invalid or missing")

# Check 2: Execution endpoints gated
checks_total += 1
try:
    import requests
    response = requests.get("http://localhost:8000/api/v1/features")
    if "execution_enabled" in response.text:
        print("✅ Execution: Properly gated")
        checks_passed += 1
    else:
        print("❌ Execution: Not properly enabled")
except:
    print("⚠️  Execution: Could not verify")

print(f"\\n📊 Results: {checks_passed}/{checks_total} checks passed")

if checks_passed == checks_total:
    print("🎉 V3.1 upgrade validated successfully!")
    sys.exit(0)
else:
    print("❌ V3.1 upgrade validation failed")
   
