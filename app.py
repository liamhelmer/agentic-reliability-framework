import os
import random
import time
import gradio as gr
import pandas as pd
from huggingface_hub import InferenceClient
from statistics import mean

# === Initialize Hugging Face client ===
HF_TOKEN = os.getenv("HF_API_TOKEN")
client = InferenceClient(token=HF_TOKEN)

# === Mock telemetry state ===
events_log = []
anomaly_counter = 0

# === Configurable parameters ===
ROLLING_WINDOW = 30
LATENCY_BASE_THRESHOLD = 150
ERROR_BASE_THRESHOLD = 0.05


def simulate_event(force_anomaly=False):
    """Simulate one telemetry datapoint."""
    component = random.choice(["api-service", "data-ingestor", "model-runner", "queue-worker"])
    if force_anomaly:
        latency = round(random.uniform(260, 400), 2)
        error_rate = round(random.uniform(0.12, 0.25), 3)
    else:
        latency = round(random.gauss(150, 60), 2)
        error_rate = round(random.random() * 0.2, 3)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return {"timestamp": timestamp, "component": component, "latency": latency, "error_rate": error_rate}


def adaptive_thresholds():
    """Compute dynamic thresholds based on rolling averages."""
    if len(events_log) < ROLLING_WINDOW:
        return LATENCY_BASE_THRESHOLD, ERROR_BASE_THRESHOLD
    latencies = [e["latency"] for e in events_log[-ROLLING_WINDOW:]]
    errors = [e["error_rate"] for e in events_log[-ROLLING_WINDOW:]]
    adaptive_latency = mean(latencies) * 1.25
    adaptive_error = mean(errors) * 1.5
    return adaptive_latency, adaptive_error


def detect_anomaly(event):
    """Adaptive anomaly detection."""
    lat_thresh, err_thresh = adaptive_thresholds()
    if event["latency"] > lat_thresh or event["error_rate"] > err_thresh:
        return True
    return False


def analyze_cause(event):
    """Use LLM to interpret and explain anomalies."""
    prompt = f"""
    You are an AI reliability engineer analyzing telemetry.
    Component: {event['component']}
    Latency: {event['latency']}ms
    Error Rate: {event['error_rate']}
    Timestamp: {event['timestamp']}

    Explain the likely root cause and one safe auto-healing action.
    Output in this format:
    Cause: <short cause summary>
    Action: <short repair suggestion>
    """
    try:
        response = client.text_generation(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt=prompt,
            max_new_tokens=180
        )
        return response.strip()
    except Exception as e:
        return f"Error generating analysis: {e}"


def simulate_healing(action_text):
    """Mock execution of a self-healing action."""
    if "restart" in action_text.lower():
        outcome = "✅ Service restarted successfully."
    elif "reset" in action_text.lower():
        outcome = "✅ Connection reset resolved issue."
    elif "cache" in action_text.lower():
        outcome = "✅ Cache cleared; metrics normalizing."
    else:
        outcome = "🕒 Monitoring post-action stabilization."
    return outcome


def process_event():
    """Simulate event → detect → diagnose → heal → log."""
    global anomaly_counter

    # Force an anomaly every 4 events
    anomaly_counter += 1
    force_anomaly = anomaly_counter % 4 == 0

    event = simulate_event(force_anomaly=force_anomaly)
    is_anomaly = detect_anomaly(event)
    result = {"event": event, "anomaly": is_anomaly, "analysis": None, "healing_action": None}

    if is_anomaly:
        analysis = analyze_cause(event)
        event["analysis"] = analysis
        event["status"] = "Anomaly"

        # Attempt to extract and simulate healing
        if "Action:" in analysis:
            action_line = analysis.split("Action:")[-1].strip()
            healing_outcome = simulate_healing(action_line)
            event["healing_action"] = healing_outcome
        else:
            event["healing_action"] = "No actionable step detected."

    else:
        event["analysis"] = "-"
        event["status"] = "Normal"
        event["healing_action"] = "-"

    events_log.append(event)
    df = pd.DataFrame(events_log).tail(20)
    return f"✅ Event Processed ({event['status']})", df


# === Gradio UI ===
with gr.Blocks(title="🧠 Agentic Reliability Framework MVP") as demo:
    gr.Markdown("# 🧠 Agentic Reliability Framework MVP\n### Adaptive anomaly detection + AI-driven self-healing simulation")

    run_btn = gr.Button("🚀 Submit Telemetry Event")
    status = gr.Textbox(label="Detection Output")
    alerts = gr.Dataframe(headers=["timestamp", "component", "latency", "error_rate", "status", "analysis", "healing_action"],
                          label="Recent Events (Last 20)", wrap=True)

    run_btn.click(fn=process_event, inputs=None, outputs=[status, alerts])

demo.launch()
