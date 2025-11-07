import os
import json
import random
import time
import datetime
import numpy as np
import gradio as gr
import requests
from sentence_transformers import SentenceTransformer
import faiss

# === Config ===
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
if not HF_TOKEN:
    print("⚠️ No Hugging Face token found. Running in fallback/local mode.")
else:
    print("✅ Hugging Face token loaded successfully.")

HF_API_URL = "https://router.huggingface.co/hf-inference/v1/completions"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# === FAISS Setup ===
VECTOR_DIM = 384
INDEX_FILE = "incident_vectors.index"
TEXTS_FILE = "incident_texts.json"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
    with open(TEXTS_FILE, "r") as f:
        incident_texts = json.load(f)
else:
    index = faiss.IndexFlatL2(VECTOR_DIM)
    incident_texts = []

def save_index():
    faiss.write_index(index, INDEX_FILE)
    with open(TEXTS_FILE, "w") as f:
        json.dump(incident_texts, f)

# === Event Memory ===
events = []

def detect_anomaly(event):
    """Adaptive threshold-based anomaly detection."""
    latency = event["latency"]
    error_rate = event["error_rate"]

    # Force random anomaly occasionally for testing
    if random.random() < 0.25:
        return True

    return latency > 150 or error_rate > 0.05

def call_huggingface_analysis(prompt):
    """Use HF Inference API or fallback simulation."""
    if not HF_TOKEN:
        return "Offline mode: simulated analysis."

    try:
        payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "prompt": prompt,
            "max_tokens": 200,
            "temperature": 0.3,
        }
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("text", "").strip()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error generating analysis: {e}"

def simulate_healing(event):
    actions = [
        "Restarted container",
        "Scaled up instance",
        "Cleared queue backlog",
        "No actionable step detected."
    ]
    return random.choice(actions)

def analyze_event(component, latency, error_rate):
    event = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "component": component,
        "latency": latency,
        "error_rate": error_rate
    }

    is_anomaly = detect_anomaly(event)
    event["anomaly"] = is_anomaly
    event["status"] = "Anomaly" if is_anomaly else "Normal"

    # Build textual prompt
    prompt = (
        f"Component: {component}\nLatency: {latency:.2f}ms\nError Rate: {error_rate:.3f}\n"
        f"Status: {event['status']}\n\n"
        "Provide a one-line reliability insight or root cause analysis."
    )

    # Analysis
    analysis = call_huggingface_analysis(prompt)
    event["analysis"] = analysis

    # Healing simulation
    healing_action = simulate_healing(event)
    event["healing_action"] = healing_action

    # === Vector learning ===
    vector_text = f"{component} {latency} {error_rate} {analysis}"
    vec = model.encode([vector_text])
    index.add(np.array(vec, dtype=np.float32))
    incident_texts.append(vector_text)
    save_index()

    # Find similar incidents
    if len(incident_texts) > 1:
        D, I = index.search(vec, k=min(3, len(incident_texts)))
        similar = [incident_texts[i] for i in I[0] if i < len(incident_texts)]
        if similar:
            event["healing_action"] += f" Found {len(similar)} similar incidents (e.g., {similar[0][:120]}...)."
    else:
        event["healing_action"] += " - Not enough incidents stored yet."

    events.append(event)
    return json.dumps(event, indent=2)

# === UI ===
def submit_event(component, latency, error_rate):
    result = analyze_event(component, latency, error_rate)
    parsed = json.loads(result)

    table = [
        [e["timestamp"], e["component"], e["latency"], e["error_rate"],
         e["status"], e["analysis"], e["healing_action"]]
        for e in events[-20:]
    ]

    return (
        f"✅ Event Processed ({parsed['status']})",
        gr.Dataframe(
            headers=["timestamp", "component", "latency", "error_rate", "status", "analysis", "healing_action"],
            value=table
        )
    )

with gr.Blocks(title="🧠 Agentic Reliability Framework MVP") as demo:
    gr.Markdown("## 🧠 Agentic Reliability Framework MVP\nAdaptive anomaly detection + AI-driven self-healing + vector memory (FAISS persistent)")
    with gr.Row():
        component = gr.Textbox(label="Component", value="api-service")
        latency = gr.Slider(10, 400, value=100, step=1, label="Latency (ms)")
        error_rate = gr.Slider(0, 0.2, value=0.02, step=0.001, label="Error Rate")
    submit = gr.Button("🚀 Submit Telemetry Event")
    output_text = gr.Textbox(label="Detection Output")
    table_output = gr.Dataframe(headers=["timestamp", "component", "latency", "error_rate", "status", "analysis", "healing_action"])
    submit.click(fn=submit_event, inputs=[component, latency, error_rate], outputs=[output_text, table_output])

demo.launch(server_name="0.0.0.0", server_port=7860)
