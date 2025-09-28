from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)  # 👈 instancia de Flask

# Tu webhook de Discord se obtiene de la variable de entorno
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

@app.route("/", methods=["POST"])
def jira_webhook():
    try:
        # Intentar parsear el JSON recibido
        data = request.get_json(force=True, silent=True) or {}

        # Valores por defecto si faltan campos
        issue_key = data.get("key", "UNKNOWN")
        summary = data.get("summary", "Sin resumen")
        url = data.get("url", "#")
        status = data.get("status", "Sin estado")
        assignee = data.get("assignee") or "Sin asignar"

        # Construir mensaje para Discord
        message = {
            "content": (
                f"🔔 El ticket **{issue_key}** pasó a *{status}*\n"
                f"📌 {summary}\n"
                f"👤 Asignado a: {assignee}\n"
                f"👉 [Ver en Jira]({url})"
            )
        }

        # Enviar mensaje a Discord
        resp = requests.post(DISCORD_WEBHOOK_URL, json=message)
        if resp.status_code != 204:
            return jsonify({"error": "Error enviando a Discord", "status": resp.status_code}), 500

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
