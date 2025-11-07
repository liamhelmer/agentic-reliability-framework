import gradio as gr
import sqlite3
import time
from datetime import datetime

DB_PATH = "reliability.db"

# --- Setup database (first run only) ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        component TEXT,
        latency REAL,
        error_rate REAL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        alert_type TEXT,
        threshold REAL,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Core functions ---
def log_event(component, latency, error_rate):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO telemetry (timestamp, component, latency, error_rate) VALUES (?, ?, ?, ?)",
              (datetime.now().isoformat(), component, latency, error_rate))
    conn.commit()
    conn.close()
    return detect_anomaly()

def detect_anomaly(threshold_latency=200, threshold_error=0.3):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        id, ts, component, latency, error_rate = row
        if latency > threshold_latency or error_rate > threshold_error:
            alert_msg = f"⚠️ Anomaly detected in {component} — latency {latency}ms, error rate {error_rate}"
            save_alert(id, "anomaly", max(latency, error_rate))
            return alert_msg
    return "✅ No anomaly detected."

def save_alert(event_id, alert_type, threshold):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO alerts (event_id, alert_type, threshold, timestamp) VALUES (?, ?, ?, ?)",
              (event_id, alert_type, threshold, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def show_recent_alerts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    if not rows:
        return "No alerts yet."
    return "\n".join([f"[{r[4]}] {r[2]} (threshold: {r[3]})" for r in rows])

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 Agentic Reliability Framework MVP")
    gr.Markdown("Simulate telemetry events and detect anomalies automatically.")
    
    with gr.Row():
        component = gr.Textbox(label="Component", value="api-service")
        latency = gr.Number(label="Latency (ms)", value=150)
        error_rate = gr.Number(label="Error rate", value=0.05)
    btn = gr.Button("Submit Event")
    output = gr.Textbox(label="Detection Output")
    
    btn.click(fn=log_event, inputs=[component, latency, error_rate], outputs=output)
    
    gr.Markdown("### Recent Alerts")
    alert_box = gr.Textbox(label="", interactive=False)
    refresh_btn = gr.Button("Refresh Alerts")
    refresh_btn.click(fn=show_recent_alerts, outputs=alert_box)

demo.launch()
