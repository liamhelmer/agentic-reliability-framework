# ARF Quick Start Guide (v3.3.0)

**Audience:** OSS users, engineers, pilot adopters  
**Purpose:** Run ARF locally in advisory mode with in-memory RAG graph in ~5 minutes.

---

## 1. Installation

Install the latest OSS release:

```bash
pip install agentic-reliability-framework
```
Verify installation:
```
arf --version
# Should output: Agentic Reliability Framework v3.3.0

arf doctor
# ✅ All dependencies OK!
```

2\. Launch Local Demo
---------------------

Run ARF’s Gradio UI for interactive testing:
```
arf serve
```
Open your browser at http://localhost:7860

3\. First Test Run
------------------

Simulate an incident:
```
arf simulate --event test_latency_spike
```
Expected output:
```
[INFO] Incident detected: latency spike in payment-service
[INFO] Recommended action: advisory-only
```
4\. CLI Essentials
------------------

*   **List available tools:**
```
arf tools list
```

Create an advisory HealingIntent:

```
arf intent create --tool RATE_LIMIT --incident incident_001
```
Export metrics (future Tier 2 API):
```
arf metrics export --format json
```
5\. OSS Features Summary
------------------------

| Feature           | Implementation             | Limits                     |
|------------------|---------------------------|----------------------------|
| MCP Mode          | Advisory only             | No execution               |
| RAG Memory        | In-memory graph + FAISS   | 1,000 incidents (LRU)     |
| Similarity Search | FAISS cosine similarity   | Top-K only                 |
| Learning          | Pattern stats only        | No persistence             |
| Healing           | HealingIntent creation    | Advisory only              |
| Policies          | Deterministic guardrails  | Warnings + blocks          |
| Storage           | RAM only                  | Process-lifetime           |
| Support           | GitHub Issues             | No SLA                     |


6\. Next Steps
--------------

1.  Explore /docs for detailed guides: architecture.md, api.md, configuration.md.
    
2.  Test advisory vs Enterprise MCP if available.
    
3.  Integrate with sample telemetry or monitoring tools (Prometheus, Datadog).
    

7\. Support & Resources
-----------------------

*   GitHub: [https://github.com/petterjuan/agentic-reliability-framework](https://github.com/petterjuan/agentic-reliability-framework)
    
*   Issues: [https://github.com/petterjuan/agentic-reliability-framework/issues](https://github.com/petterjuan/agentic-reliability-framework/issues)
    
*   Live Demo: [https://huggingface.co/spaces/petter2025/agentic-reliability-framework](https://huggingface.co/spaces/petter2025/agentic-reliability-framework)
