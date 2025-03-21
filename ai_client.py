from flask import jsonify
from ollama import Client, ResponseError

from config import ollama_model, ollama_endpoint

def send_to_model(prompt):
    try:
        client = Client(
            host=ollama_endpoint
        )
        response = client.chat(
            model=ollama_model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=False
        )
        
        if response["done"] and response["done"]["done_reason"] != 'stop':
            raise ResponseError("Response stopped prematurely")
        return jsonify(dict(response))
    except Exception as e:
        return jsonify({"error": str(e)}), 500