from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Usa variables de entorno para mayor seguridad
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

@app.route("/", methods=["POST"])
def jira_webhook():
    data = request.json

    if not data or "issue" not in data:
        return jsonify({"error": "No issue data found"}), 400

    issue = data["issue"]
    fields = issue.get("fields", {})

    key = issue.get("key", "No key")
    summary = fields.get("summary", "No summary")
    # Ajusta según los custom fields de tu Jira
    team = fields.get("customfield_team", "No definido")
    ambiente_qa = fields.get("customfield_ambienteQA", "No definido")
    assignee = fields.get("assignee", {}).get("displayName", "Sin asignar")
    status = fields.get("status", {}).get("name", "No definido")

    # Solo enviar notificación si el estado es Testing / QA
    if status == "Testing / QA":
        embed = {
            "title": f"🟢 Ticket en Testing / QA: {key}",
            "url": issue.get('self').replace('/rest/api/2/issue/', '/browse/'),
            "color": 3066993,  # Verde
            "fields": [
                {"name": "Resumen", "value": summary, "inline": False},
                {"name": "Team Responsable", "value": team, "inline": True},
                {"name": "Ambientado QA", "value": ambiente_qa, "inline": True},
                {"name": "Persona Asignada", "value": assignee, "inline": True},
                {"name": "Estado", "value": status, "inline": True}
            ]
        }

        payload = {"embeds": [embed]}

        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error enviando a Discord: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
