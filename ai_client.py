from flask import jsonify
import requests
from config import ollama_endpoint

api_path = "/api/generate"

def send_to_model(prompt, model):
    try:
        response = requests.post(
            ollama_endpoint + api_path,
            json={"prompt": prompt, "model": model, "stream": False, "format": "json"}
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500