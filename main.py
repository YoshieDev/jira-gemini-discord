from flask import Flask, request, jsonify
import os, requests
import pandas as pd
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)

@app.route("/", methods=["POST"])
def jira_to_discord():
    data = request.json or {}

    key = data.get("key")
    status = (data.get("status") or "").strip()
    summary = data.get("summary")

    # 🚫 Ignorar payloads sin datos básicos
    if not key or not summary or not status:
        return jsonify({"status": "ignored", "reason": "faltan campos"}), 200

    # 🚫 Ignorar si NO es exactamente "Testing / QA"
    if status.lower() not in ["testing / qa", "testing/qa"]:
        return jsonify({"status": "ignored", "reason": f"status={status}"}), 200

    # ✅ Preparar campo Ambientado QA
    ambientado_qa = data.get("ambientado_qa")
    if isinstance(ambientado_qa, list):
        # Si Jira envía una lista de valores
        ambientado_qa = ", ".join(ambientado_qa)
    ambientado_qa = ambientado_qa or "No definido"

    # ✅ Construir mensaje final
    message = (
        f"🔔 El ticket {key} pasó a {status}\n"
        f"📌 {summary}\n"
        f"👤 Asignado a: {data.get('assignee', 'Sin asignar')}\n"
        f"🛠 Ambientado QA: {ambientado_qa}\n"
        f"👉 [Ver en Jira]({data.get('url', '#')})"
    )

    # Enviar a Discord
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(port=5000)
