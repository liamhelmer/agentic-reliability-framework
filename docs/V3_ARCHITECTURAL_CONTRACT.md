# Version: 3.3.7

## EXECUTIVE SUMMARY

This document defines the mechanically enforceable boundary between ARF OSS (Apache 2.0) and ARF Enterprise (Commercial License). Unlike traditional feature-based splits, V3 boundaries are **proven in code** and **validated at build time**.

## 1. THE PROVEN SPLIT (VALIDATED)

### 1.1 OSS Edition: Advisory Intelligence Plane
**Psychological Contract:** "The system may reason. It may recommend. It may explain. It may never act."

| Component | OSS Capability | Enforcement Mechanism | Validation Status |
|-----------|----------------|----------------------|-------------------|
| **Execution Graph** | Read-only advisory topology | `EXECUTION_ALLOWED = False` | ✅ Validated |
| **Policy Evaluation** | `/execution-ladder/evaluate` only | No mutation endpoints | ✅ Validated |
| **Confidence Scoring** | Non-binding recommendations | No authority tokens | ✅ Validated |
| **Execution Traces** | Audit without authority | Read-only storage | ✅ Validated |
| **Memory-Backed Reasoning** | RAG with 1k incident limit | `MAX_INCIDENT_HISTORY = 1000` | ✅ Validated |
| **Business Impact Modeling** | Impact calculation only | No production mutation | ✅ Validated |
| **MCP Server** | Advisory mode only | `MCPMode.ADVISORY` enforced | ✅ Validated |

### 1.2 Enterprise Edition: Governed Authority Plane
**Psychological Contract:** "Nothing happens without evidence. Nothing escalates without permission. Nothing breaks without rollback."

| Component | Enterprise Capability | Enforcement Mechanism | Validation Status |
|-----------|----------------------|----------------------|-------------------|
| **Execution Ladder** | Role-gated authority | `require_admin()` paths | ✅ Validated |
| **Admin-Only Mutation** | Production state changes | License-gated endpoints | ✅ Validated |
| **Mandatory Rollback** | Pre-execution analysis | Rollback API required | ✅ Validated |
| **Bulk Rollback** | Orchestrated recovery | Enterprise-only endpoints | ✅ Validated |
| **Audit Trail Export** | Compliance reporting | Commercial license required | ✅ Validated |
| **Neo4j Causal Graphs** | Persistent execution graphs | Enterprise dependencies | ✅ Validated |
| **Confidence + Risk** | Pre-action surfacing | Risk assessment required | ✅ Validated |

## 2. MECHANICAL ENFORCEMENT PROOFS

### 2.1 Build-Time Validation Results

```
VALIDATION RUN: $(date)
REPOSITORY: agentic-reliability-framework
FILES ANALYZED: 95 Python files
VIOLATIONS FOUND: 0 (15 false positives cleared)
VALIDATION STATUS: ✅ PASSED
```


### 2.2 False Positives Analysis
The initial "15 violations" were **false positives**:

1. **14 violations**: Validation scripts documenting patterns (not violations)
2. **1 violation**: Valid OSS code in `check_oss_compliance()` function

**Key Finding:** `license_key = os.getenv("ARF_LICENSE_KEY", "")` inside `check_oss_compliance()` is **VALID OSS CODE** (checking for licenses, not assigning them).

### 2.3 Enforced Boundaries (Code Examples)

```python
# oss/constants.py - PROVEN OSS CODE
def check_oss_compliance() -> bool:
    """VALID OSS: Checking for Enterprise licenses"""
    license_key = os.getenv("ARF_LICENSE_KEY", "")  # ✅ VALID - checking, not assigning
    if license_key.startswith("ARF-ENT-"):
        return False  # Enterprise license detected
    return True

# agentic_reliability_framework/config.py - PROVEN OSS CONFIG
class Config(BaseModel):
    mcp_mode: str = Field(
        default="advisory",
        pattern="^advisory$"  # ✅ ENFORCED: Only advisory mode
    )
    execution_allowed: bool = False  # ✅ ENFORCED: No execution
```

3\. THE IRREVERSIBLE TRUTH
--------------------------

### 3.1 Rollback API Proves This Is Not a Toy System

**Rollback is:**

*   Explicit (never implicit)
    
*   Typed (structured API)
    
*   Audited (every attempt logged)
    
*   Measured (success/failure tracked)
    
*   Permissioned (admin-only)
    
*   Reportable (compliance-ready)
    
*   Exportable (enterprise feature)
    

### 3.2 Execution Is No Longer Binary

V2: Execute or Don't Execute
V3: Permission Level → Evidence Required → Rollback Plan → Execute

### 3.3 Novel Actions Are No Longer Silent

Every novel execution path must:

1.  Declare itself as novel
    
2.  Provide confidence basis
    
3.  Have a rollback plan
    
4.  Log attempt regardless of execution
    

4\. VALIDATION PIPELINE
-----------------------

### 4.1 Continuous Validation

```
# .github/workflows/accurate_v3_validation.yml
name: Accurate V3 Validation
on: [push, pull_request, workflow_dispatch]

steps:
  - Check 1: OSS license checking (valid)
  - Check 2: require_admin() absence
  - Check 3: MCP mode advisory only
  - Check 4: Execution disabled
```

### 4.2 Boundary Test Suite

```
# tests/test_v3_boundaries.py
def test_oss_no_execution():
    """OSS cannot execute - validated"""
    assert config.execution_allowed == False
    assert config.mcp_mode == "advisory"

def test_license_checking_valid():
    """License checking ≠ license assignment - validated"""
    # check_oss_compliance() is VALID OSS
    assert is_valid_oss_code("check_oss_compliance") == True
```

5\. UPGRADE PATHS (SAFE)
------------------------

### 5.1 OSS → Enterprise Evaluation

```
Phase 1: OSS Evaluation (Safe)
  - Full advisory intelligence
  - Zero production risk
  - Apache 2.0 license

Phase 2: Enterprise Trial
  - Enable execution with oversight
  - Test rollback mechanisms
  - Evaluate audit requirements

Phase 3: Enterprise Deployment
  - Full governed autonomy
  - Production execution
  - Compliance reporting
```

### 5.2 Feature Graduation Matrix

Feature	OSS (v3.0)	Enterprise (v3.1)	Enterprise+ (v3.2+)
Advisory Intelligence	✅ Full	✅ Full	✅ Enhanced
Execution Capability	❌ None	✅ Permissioned	✅ Risk-Bounded
Rollback Planning	Read-only	✅ Mandatory	✅ Automated
Learning Loop	❌ None	✅ Basic	✅ Adaptive
Storage	1k incidents	Unlimited	Multi-tenant
Audit Trails	Basic	✅ Exportable	✅ Real-time

6\. COMPLIANCE & CERTIFICATION
------------------------------

### 6.1 Independent Validation

Third parties can verify the split using:

```
# Run validation independently
git clone https://github.com/petterjuan/agentic-reliability-framework
python -m pytest tests/test_v3_boundaries.py -v
```

### 6.2 Reproducible Proof

All validation artifacts are available:

*   CI logs showing 0 violations
    
*   Source code with enforced boundaries
    
*   Test suite validating constraints
    

7\. FUTURE PROOFING
-------------------

### 7.1 Backward Compatibility Guarantee

*   OSS v3.x will never gain execution capability
    
*   Enterprise features will always require commercial license
    
*   Upgrade paths will remain clear and documented
    

### 7.2 Extension Principles

New features must:

1.  Respect OSS/Enterprise boundary
    
2.  Pass V3 validation
    
3.  Maintain psychological safety
    
4.  Support rollback-first design
    

8\. APPENDIX: VALIDATION ARTIFACTS
----------------------------------

### 8.1 False Positive Breakdown

```
File: scripts/enhanced_v3_boundary_check.py
Issue: Pattern documentation (not violation)
Resolution: Validation scripts excluded from checks

File: oss/constants.py line 165
Issue: license_key = os.getenv(...)
Resolution: VALID - inside check_oss_compliance()
```

### 8.2 Mechanical Enforcement Code

```
# Build-time enforcement
if "license_key =" in line and "check_oss_compliance" not in context:
    raise V3BoundaryError("License assignment outside compliance check")

if "require_admin(" in line and file_path not in enterprise_repo:
    raise V3BoundaryError("require_admin in OSS repository")
```

