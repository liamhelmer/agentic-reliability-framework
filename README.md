---
title: Agentic Reliability Framework
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.44.1"
app_file: app.py
pinned: false
license: mit
short_description: AI-powered reliability with multi-agent anomaly detection
---

# 🧠 Agentic Reliability Framework

**AI-Powered System Reliability with Multi-Agent Anomaly Detection & Auto-Healing**

## 🚀 Live Demo

**Try it now!** Enter system telemetry data and watch specialized AI agents analyze, diagnose, and recommend healing actions in real-time.

## 🎯 What It Does

This framework transforms traditional monitoring into **autonomous reliability engineering**:

- **🤖 Multi-Agent AI Analysis**: Specialized agents work together to detect and diagnose issues
- **🔧 Automated Healing**: Policy-based auto-remediation for common failures
- **💰 Business Impact**: Real-time revenue and user impact calculations
- **📚 Learning System**: FAISS-powered memory learns from every incident
- **⚡ Production Ready**: Circuit breakers, adaptive thresholds, enterprise features

## 🛠️ Quick Start

### 1. Select a Service
Choose from: `api-service`, `auth-service`, `payment-service`, `database`, `cache-service`

### 2. Adjust Metrics
- **Latency P99**: Alert threshold >150ms (adaptive)
- **Error Rate**: Alert threshold >0.05 (5%)
- **Throughput**: Current requests per second
- **CPU/Memory**: Utilization (0.0-1.0 scale)

### 3. Submit & Analyze
Click **"Submit Telemetry Event"** to see AI agents in action!

## 📊 Example Test Cases

### 🚨 Critical Failure
Component: api-service
Latency: 800ms
Error Rate: 0.25
CPU: 0.95
Memory: 0.90

text
*Expected: CRITICAL severity, circuit_breaker + scale_out actions*

### ⚠️ Performance Issue
Component: auth-service
Latency: 350ms
Error Rate: 0.08
CPU: 0.75
Memory: 0.65

text
*Expected: HIGH severity, traffic_shift action*

### ✅ Normal Operation
Component: payment-service
Latency: 120ms
Error Rate: 0.02
CPU: 0.45
Memory: 0.35

text
*Expected: NORMAL status, no actions needed*

## 🔧 Technical Features

### Multi-Agent Architecture
- **🕵️ Detective Agent**: Anomaly detection & pattern recognition
- **🔍 Diagnostician Agent**: Root cause analysis & investigation
- **🤖 Orchestration Manager**: Coordinates all agents in parallel

### Smart Detection
- Adaptive thresholds that learn from your environment
- Multi-dimensional anomaly scoring (0-100% confidence)
- Correlation analysis across metrics
- FAISS vector memory for incident similarity

### Business Intelligence
- Real-time revenue impact calculations
- User impact estimation  
- Severity classification (LOW, MEDIUM, HIGH, CRITICAL)

## 🎮 Try These Scenarios

### Test 1: Resource Exhaustion
Set CPU to 0.95 and Memory to 0.95 - watch scale_out actions trigger

### Test 2: High Latency + Errors  
Set Latency to 500ms and Error Rate to 0.15 - see circuit breaker activation

### Test 3: Gradual Degradation
Start with normal values and slowly increase latency/errors to see adaptive thresholds

## 🚨 Default Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Latency P99 | >150ms | >300ms |
| Error Rate | >0.05 | >0.15 |
| CPU Utilization | >0.8 | >0.9 |
| Memory Utilization | >0.8 | >0.9 |

## 🔮 Roadmap

- [ ] Predictive anomaly detection
- [ ] Multi-cloud coordination  
- [ ] Advanced root cause analysis
- [ ] Automated runbook execution
- [ ] Team learning and knowledge transfer

## 💡 Why This Matters

> "The most reliable system is the one that fixes itself before anyone notices there was a problem."

This framework represents the evolution from **reactive monitoring** to **proactive, autonomous reliability engineering**.

## 🛠️ Technical Stack

- **Backend**: Python, FastAPI, Sentence Transformers
- **AI/ML**: FAISS, Hugging Face, Custom Agents
- **Frontend**: Gradio
- **Storage**: FAISS vector database, JSON metadata

---

**Built with ❤️ by [Juan Petter](https://huggingface.co/petter2025)**

*AI Infrastructure Engineer | Building Self-Healing Agentic Systems*