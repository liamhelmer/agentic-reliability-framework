
<p align="center">
  <img src="https://dummyimage.com/1200x260/0d1117/00d4ff&text=AGENTIC+RELIABILITY+FRAMEWORK" width="100%" alt="Agentic Reliability Framework Banner" />
</p>

<h2 align="center">Enterprise-Grade Multi-Agent AI for Autonomous System Reliability & Self-Healing</h2>

> **Production-ready AI system for mission-critical reliability monitoring**  
> Battle-tested architecture for autonomous incident detection and healing

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/agentic-reliability-framework?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/agentic-reliability-framework/)
[![Python Versions](https://img.shields.io/pypi/pyversions/agentic-reliability-framework?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/agentic-reliability-framework/)
[![Tests](https://img.shields.io/badge/tests-157%2F158%20passing-brightgreen?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/petterjuan/agentic-reliability-framework/actions)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue?style=for-the-badge&logo=apache&logoColor=white)](./LICENSE)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Live%20Demo-yellow?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/spaces/petter2025/agentic-reliability-framework)

**[🚀 Live Demo](https://huggingface.co/spaces/petter2025/agentic-reliability-framework)** • **[📚 Documentation](https://github.com/petterjuan/agentic-reliability-framework/tree/main/docs)** • **[💼 Enterprise Edition](https://github.com/petterjuan/agentic-reliability-enterprise)**

</div>

---

# Agentic Reliability Framework (ARF) v3.3.0

## What Is ARF?

Agentic Reliability Framework (ARF) is a **multi-agent AI system designed to reduce decision latency during production incidents**.

Traditional monitoring tools tell you *something is broken*.  
ARF tells you **what to do next, why, and how confident it is** — using memory, policy, and safe execution boundaries.

ARF treats incidents as **memory problems**, not alerting problems.

---

## Why This Exists

In real production systems:

- Alerts fire on time
- Humans do not decide on time
- Revenue leaks during hesitation

ARF closes the gap between **detection → decision → action**.

**Outcome:**  
- Faster MTTR  
- Lower blast radius  
- Higher system confidence  
- Auditable AI-driven decisions

---

## Core Capabilities (OSS Edition)

- Multi-agent parallel analysis (detective, diagnostician, predictive)
- RAG-powered incident correlation (FAISS-based)
- Policy-driven action recommendation
- MCP safety boundary (advisory-only)
- Deterministic HealingIntent handoff to Enterprise
- Hard OSS limits to prevent unsafe autonomy

---

## Architecture Overview

### Three-Layer Hybrid Intelligence Model

1. **Cognitive Intelligence**
   - Specialized agents analyze incidents in parallel
   - Produces structured recommendations with confidence

2. **Memory & Learning**
   - RAG Graph Memory (incident ↔ outcome graph)
   - FAISS semantic similarity for recall
   - Historical effectiveness scoring

3. **Safe Execution Boundary**
   - MCP Server enforces execution mode
   - OSS: advisory only
   - Enterprise: approval + autonomous

---

## Execution Model

| Mode | Edition | Description |
|----|----|----|
| Advisory | OSS | Analysis only, no execution |
| Approval | Enterprise | Human-in-the-loop |
| Autonomous | Enterprise | Policy-bound auto-healing |

OSS **cannot execute** actions by design.

---

## Quick Start (OSS)

```bash
pip install agentic-reliability-framework
arf --demo
```

```python
from agentic_reliability_framework import EnhancedV3ReliabilityEngine

engine = EnhancedV3ReliabilityEngine()

result = await engine.process_event_enhanced(
    component="api-service",
    latency_p99=320.0,
    error_rate=0.18,
    throughput=1250.0,
    cpu_util=0.87,
    memory_util=0.92
)

print(result["healing_actions"])
```

---

## HealingIntent: OSS → Enterprise Boundary

ARF introduces **HealingIntent** as a strict contract:

- OSS creates immutable intent objects
- Enterprise executes them safely
- Deterministic IDs prevent double execution
- Full audit trail maintained

This design is what makes ARF **enterprise-safe**.

---

## OSS vs Enterprise

| Feature | OSS | Enterprise |
|------|-----|-----------|
| Execution | ❌ | ✅ |
| MCP Modes | Advisory | Advisory / Approval / Autonomous |
| Storage | In-memory | Persistent |
| Learning Loop | ❌ | ✅ |
| Compliance | Basic logs | SOC2 / HIPAA / GDPR |
| Support | Community | 24/7 SLA |

---

## Why Graph-Based Memory Matters

Humans think in **relationships**, not metrics.

Graphs allow ARF to:

- Recall similar failures instantly
- Rank actions by past success
- Predict outcome confidence
- Explain *why* a decision is made

This is why ARF outperforms threshold-based systems.

---

## Monetization Strategy (Transparent)

OSS is intentionally constrained.

Enterprise unlocks:
- Autonomous execution
- Persistent memory
- Learning from outcomes
- Compliance reporting
- Multi-tenant support

👉 **Upgrade Path:** https://arf.dev/enterprise

---

## Who This Is For

- AI infrastructure teams
- SREs running LLM-powered systems
- Regulated industries (healthcare, fintech)
- Companies losing revenue to incident hesitation

If uptime matters, ARF fits.

---

## Roadmap

- v3.4: Outcome-weighted confidence scoring
- v3.5: Cross-service blast radius prediction
- Enterprise: Self-optimizing policies

---

## License

Apache 2.0 (OSS)  
Commercial license required for execution & learning features.

---

## Author

Juan Petter  
AI Infrastructure Engineer  
Building self-healing agentic systems

- GitHub: https://github.com/petterjuan
- LinkedIn: https://www.linkedin.com/in/petterjuan/
- Enterprise: https://arf.dev/enterprise
