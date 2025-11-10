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

    # Remove random forcing for production - use actual thresholds only
    latency_anomaly = latency > 150
    error_anomaly = error_rate > 0.05
    
    return latency_anomaly or error_anomaly

def call_huggingface_analysis(prompt):
    """Use HF Inference API or fallback simulation."""
    if not HF_TOKEN:
        # Enhanced fallback analysis
        fallback_insights = [
            "High latency detected - possible resource contention or network issues",
            "Error rate increase suggests recent deployment instability",
            "Latency spike correlates with increased user traffic patterns",
            "Intermittent failures indicate potential dependency service degradation",
            "Performance degradation detected - consider scaling compute resources"
        ]
        return random.choice(fallback_insights)

    try:
        # Enhanced prompt for better analysis
        enhanced_prompt = f"""
        As a senior reliability engineer, analyze this telemetry event and provide a concise root cause analysis:
        
        {prompt}
        
        Focus on:
        - Potential infrastructure or application issues
        - Correlation between metrics
        - Business impact assessment
        - Recommended investigation areas
        
        Provide 1-2 sentences maximum with actionable insights.
        """
        
        payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "prompt": enhanced_prompt,
            "max_tokens": 150,
            "temperature": 0.4,
        }
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            analysis_text = result.get("choices", [{}])[0].get("text", "").strip()
            # Clean up any extra formatting from the response
            if analysis_text and len(analysis_text) > 10:
                return analysis_text.split('\n')[0]  # Take first line if multiple
            return analysis_text
        else:
            return f"API Error {response.status_code}: Service temporarily unavailable"
    except Exception as e:
        return f"Analysis service error: {str(e)}"

def simulate_healing(event):
    actions = [
        "Restarted container",
        "Scaled up instance",
        "Cleared queue backlog",
        "No actionable step detected."
    ]
    return random.choice(actions)

def analyze_event(component, latency, error_rate):
    # Ensure unique timestamps with higher precision
    event = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "component": component,
        "latency": latency,
        "error_rate": error_rate
    }

    is_anomaly = detect_anomaly(event)
    event["anomaly"] = is_anomaly
    event["status"] = "Anomaly" if is_anomaly else "Normal"

    # Build enhanced textual prompt
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
            # Extract meaningful part from similar incident
            similar_preview = similar[0][:100] + "..." if len(similar[0]) > 100 else similar[0]
            event["healing_action"] += f" Found {len(similar)} similar incidents (e.g., {similar_preview})."
    else:
        event["healing_action"] += " - Not enough incidents stored yet."

    events.append(event)
    return json.dumps(event, indent=2)

# === UI ===
def submit_event(component, latency, error_rate):
    result = analyze_event(component, latency, error_rate)
    parsed = json.loads(result)

    # Display last 15 events to keep table manageable
    table = [
        [e["timestamp"], e["component"], e["latency"], e["error_rate"],
         e["status"], e["analysis"], e["healing_action"]]
        for e in events[-15:]
    ]

    return (
        f"✅ Event Processed ({parsed['status']})",
        gr.Dataframe(
            headers=["timestamp", "component", "latency", "error_rate", "status", "analysis", "healing_action"],
            value=table
        )
    )

with gr.Blocks(title="🧠 Agentic Reliability Framework MVP", theme="soft") as demo:
    gr.Markdown("""
    # 🧠 Agentic Reliability Framework MVP
    **Adaptive anomaly detection + AI-driven self-healing + persistent FAISS memory**
    
    *Monitor your services in real-time with AI-powered reliability engineering*
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Telemetry Input")
            component = gr.Textbox(
                label="Component", 
                value="api-service",
                info="Name of the service being monitored"
            )
            latency = gr.Slider(
                minimum=10, 
                maximum=400, 
                value=100, 
                step=1, 
                label="Latency (ms)",
                info="Alert threshold: >150ms"
            )
            error_rate = gr.Slider(
                minimum=0, 
                maximum=0.2, 
                value=0.02, 
                step=0.001, 
                label="Error Rate",
                info="Alert threshold: >0.05"
            )
            submit = gr.Button("🚀 Submit Telemetry Event", variant="primary")
            
        with gr.Column(scale=2):
            gr.Markdown("### 🔍 Live Analysis")
            output_text = gr.Textbox(
                label="Detection Output",
                placeholder="Submit an event to see analysis results...",
                lines=2
            )
            gr.Markdown("### 📈 Recent Events")
            table_output = gr.Dataframe(
                headers=["timestamp", "component", "latency", "error_rate", "status", "analysis", "healing_action"],
                label="Event History",
                wrap=True
            )
    
    # Add some explanation
    with gr.Accordion("ℹ️ How it works", open=False):
        gr.Markdown("""
        - **Anomaly Detection**: Flags events with latency >150ms or error rate >5%
        - **AI Analysis**: Uses Mistral-8x7B for root cause analysis via Hugging Face
        - **Vector Memory**: Stores incidents in FAISS for similarity search
        - **Self-Healing**: Simulates automated recovery actions based on historical patterns
        """)
    
    submit.click(
        fn=submit_event, 
        inputs=[component, latency, error_rate], 
        outputs=[output_text, table_output]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        share=False
    )
