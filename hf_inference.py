import os
import requests

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HF_API_KEY = os.getenv("HF_API_TOKEN")  # Set in your Space's Secrets tab

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

def run_inference(prompt):
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return str(data)
    else:
        return f"Error: {response.status_code} - {response.text}"
