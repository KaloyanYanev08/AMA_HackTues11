from flask import jsonify, Response
from ollama import Client, ResponseError
from re import search as regex
from re import DOTALL

from config import ollama_model, ollama_endpoint

def send_to_model(prompt):
    client = Client(
        host=ollama_endpoint
    )
    response = dict(client.chat(
        model=ollama_model,
        messages=[{'role': 'user', 'content': prompt}],
        stream=False
    ))

    if not response["done"] or response["done_reason"] != 'stop':
        raise ResponseError("Response stopped prematurely")
        
    end_of_reason = regex(r"\s*</think>\s*(.*)", response["message"]["content"], DOTALL)
    json_resp = ""
    if end_of_reason:
        json_resp = end_of_reason.group(1).replace("```json", "").replace("```", "").strip()
    else:
        raise ResponseError("Response format is incorrect")

    from json import loads

    return loads(json_resp)