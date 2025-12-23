# ARF v3 – MCP Tool Architecture (OSS Edition)

**Audience:** Platform Engineers, Security Teams, Buyers  
**Purpose:** Define how ARF safely crosses the boundary from *decision* to *action* using Model Context Protocol (MCP).

---

## Why MCP Exists in ARF

Automation fails when systems:

- Act implicitly without oversight
- Skip approval workflows
- Lack audit trails and traceability

ARF v3 enforces:

> **Agents reason. Policies decide. MCP executes.**

MCP is the **trust boundary** that ensures safe and auditable automation.

---

## Responsibility Split

| Layer | Responsibility |
|-------|----------------|
| Agents | Analyze & predict incidents and outcomes |
| Policy Engine | Decide what *should* happen |
| MCP Server (OSS) | Recommend what *may* happen (Advisory only) |

> **Note:** OSS Edition never executes actions, only validates and advises.

---

## MCP Server Role (OSS Edition)

The MCP server is a **governed advisory plane**. It provides:

- Explicit tool contracts
- Permission validation
- Advisory recommendations
- Audit and metrics collection

It does **not**:

- Perform analysis
- Make policy decisions
- Execute actions (Enterprise-only)

---

## Tool Taxonomy (OSS Examples)

| Category | OSS Tools |
|----------|-----------|
| Traffic Control | `circuit_breaker`, `traffic_shift`, `alert_team` |
| Compute | `scale_out` |
| Deployment | `rollback`, `restart_container` |
| Isolation / Human Intervention | `alert_team` |

---

## MCP Tool Schema (OSS-aligned)

```json
{
  "tool": "ROLLBACK",
  "component": "web-server",
  "parameters": {"revision": "v1.2.3"},
  "justification": "Rollback due to failed deployment",
  "mode": "advisory",
  "would_execute": true,
  "requires_enterprise": true,
  "oss_fallback": true
}
```

*   would\_execute: Indicates action if Enterprise edition were used
    
*   requires\_enterprise: Marks Enterprise-only execution
    
*   oss\_fallback: Advisory response when Enterprise execution unavailable
    

Execution Modes (OSS vs Enterprise)
-----------------------------------

| Mode        | OSS Edition                                | Enterprise Edition                          |
|------------|-------------------------------------------|--------------------------------------------|
| Advisory    | ✅ Recommendations only, no side effects   | ✅ Same                                     |
| Approval    | ❌ Not available                            | ✅ Human approval required, audit trail    |
| Autonomous  | ❌ Not available                            | ✅ Pre-approved actions with guardrails    |

> OSS Edition always returns advisory recommendations. Enterprise edition handles full execution workflows.

Safety Guardrails
-----------------

MCP enforces:

*   Rate limits
    
*   Cooldowns
    
*   Blast radius checks
    
*   Environment restrictions
    

Example in OSS Advisory:
```
if incident.severity != "CRITICAL":
    deny("Rollback not permitted")
```
OSS Edition validates inputs and flags risky actions but does not execute them.

Audit & Compliance (OSS Edition)
--------------------------------

Every MCP action (even advisory) records:

*   Tool and component
    
*   Validation results
    
*   Justification
    
*   Advisory notes
    

This ensures traceability for SOC2, incident reviews, and regulatory compliance.

OSS vs Enterprise Boundary
--------------------------

### OSS Edition

*   Advisory mode only (no side effects)
    
*   Tool schemas and validation
    
*   Policy → MCP handoff
    
*   Provides guidance for Enterprise execution
    

### Enterprise Edition

*   Executes actions via adapters (K8s, Cloud APIs)
    
*   Approval workflows & RBAC
    
*   Full audit exports
    
*   RAG-backed decision learning
    

Failure Modes & Design Responses
--------------------------------

RiskOSS MitigationEnterprise MitigationOver-automationAdvisory-only; no executionAutomated actions with guardrailsCascading actionsAdvisory recommendations; no changesCooldowns enforcedIncorrect actionsValidation and advisory onlyHuman approvalBlack-box decisionsRAG justification advisoryFull RAG + Learning Engine

Summary
-------

MCP in ARF v3 (OSS Edition) is a **trusted advisory plane**:

*   Validates tool actions
    
*   Provides safety checks
    
*   Generates audit-ready recommendations
    

> Automation is safe, auditable, and guided, even in OSS Advisory mode. Enterprise edition adds full execution, approval, and RAG integration.
