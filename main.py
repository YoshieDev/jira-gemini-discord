from flask import Flask, request, jsonify
import os, requests

app = Flask(__name__)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

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

    # ✅ Construir mensaje final
    message = (
        f"🔔 El ticket {key} pasó a {status}\n"
        f"📌 {summary}\n"
        f"👤 Asignado a: {data.get('assignee', 'Sin asignar')}\n"
        f"👉 [Ver en Jira]({data.get('url', '#')})"
    )

    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

    return jsonify({"status": "ok"}), 200
