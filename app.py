import gradio as gr
import time
import random
import requests
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# --- CONFIG ---
HF_TOKEN = (open(".env", "r").read().strip() if ".env" else None) or ""
HF_TOKEN = HF_TOKEN.strip() if HF_TOKEN else ""
if not HF_TOKEN:
    print("⚠️ No Hugging Face token found. Running in fallback mode (local inference).")

API_URL = "https://router.huggingface.co/hf-inference"

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
incident_embeddings = []
incident_texts = []

recent_events = []

# --- SIMULATION HELPERS ---
def simulate_healing_action(component: str) -> str:
    actions = [
        "Restarted container",
        "Cleared queue backlog",
        "Rebalanced load",
        "No actionable step detected.",
    ]
    return random.choice(actions)

def detect_anomaly(latency: float, error_rate: float) -> bool:
    # Simple adaptive anomaly threshold
    score = latency * error_rate
    threshold = random.uniform(5, 25)
    return score > threshold

def embed_incident(text: str):
    emb = model.encode([text], normalize_embeddings=True)
    return np.array(emb).astype("float32")

def find_similar_incidents(new_text: str, top_k=3):
    if not incident_embeddings:
        return "Not enough incidents stored yet."
    new_emb = embed_incident(new_text)
    index = faiss.IndexFlatIP(len(new_emb[0]))
    index.add(np.vstack(incident_embeddings))
    scores, ids = index.search(new_emb, top_k)
    similar = [
        f"Component: {incident_texts[i]['component']} | Latency: {incident_texts[i]['latency']} | ErrorRate: {incident_texts[i]['error_rate']} | Analysis: {incident_texts[i]['analysis'][:60]}..."
        for i in ids[0] if i < len(incident_texts)
    ]
    return f"Found {len(similar)} similar incidents ({'; '.join(similar)})."

# --- MAIN PROCESS ---
def process_event(component, latency, error_rate):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    anomaly = detect_anomaly(latency, error_rate)

    # --- Analysis step ---
    payload = {
        "inputs": f"Component {component} showing latency {latency} and error rate {error_rate}.",
    }

    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN.strip()}"}
        response = requests.post(f"{API_URL}/facebook/bart-large-mnli", headers=headers, json=payload)
        if response.status_code == 200:
            analysis = response.json().get("generated_text", "No analysis output.")
        else:
            analysis = f"Error {response.status_code}: {response.text}"
    except Exception as e:
        analysis = f"Error generating analysis: {str(e)}"

    status = "Anomaly" if anomaly else "Normal"
    healing_action = simulate_healing_action(component) if anomaly else "-"
    similar_info = find_similar_incidents(analysis)

    event = {
        "timestamp": timestamp,
        "component": component,
        "latency": latency,
        "error_rate": error_rate,
        "status": status,
        "analysis": analysis,
        "healing_action": f"{healing_action} {similar_info}" if anomaly else f"- {similar_info}",
    }

    recent_events.append(event)
    if len(recent_events) > 20:
        recent_events.pop(0)

    # --- Store vector memory ---
    incident_embeddings.append(embed_incident(analysis))
    incident_texts.append(event)

    return f"✅ Event Processed", pd.DataFrame(recent_events)

# --- GRADIO UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 🧠 Agentic Reliability Framework MVP")
    gr.Markdown("Adaptive anomaly detection + AI-driven self-healing + vector memory")

    with gr.Row():
        component = gr.Textbox(label="Component", value="api-service")
        latency = gr.Number(label="Latency (ms)", value=random.uniform(50, 200))
        error_rate = gr.Number(label="Error Rate", value=random.uniform(0.01, 0.2))

    submit = gr.Button("🚀 Submit Telemetry Event")
    output_text = gr.Textbox(label="Detection Output")
    output_table = gr.Dataframe(headers=["timestamp", "component", "latency", "error_rate", "status", "analysis", "healing_action"], label="Recent Events (Last 20)")

    submit.click(process_event, inputs=[component, latency, error_rate], outputs=[output_text, output_table])

demo.launch()
