from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Endpoint principal para recibir Jira
@app.route("/jira-webhook", methods=["POST"])
def jira_webhook():
    try:
        data = request.get_json(force=True)
    except Exception:
        raw_body = request.data.decode('utf-8')
        safe_body = raw_body.replace('\n', '\\n').replace('\t', '\\t')
        try:
            data = json.loads(safe_body)
        except json.JSONDecodeError:
            print(f"Error parseando JSON de Jira: {raw_body}")
            return jsonify({"error": "Invalid JSON"}), 400

    # Log para debug
    print("Webhook recibido de Jira:")
    print(json.dumps(data, indent=2))

    issue = data.get("issue")
    if not issue:
        return jsonify({"error": "No issue data found"}), 400

    fields = issue.get("fields", {})
    key = issue.get("key", "No key")
    summary = fields.get("summary", "No summary")
    team = fields.get("customfield_team", "No definido")
    ambiente_qa = fields.get("customfield_ambienteQA", "No definido")
    assignee = fields.get("assignee", {}).get("displayName", "Sin asignar")
    status = fields.get("status", {}).get("name", "No definido")

    if status == "Testing / QA":
        embed = {
            "title": f"🟢 Ticket en Testing / QA: {key}",
            "url": issue.get('self').replace('/rest/api/2/issue/', '/browse/'),
            "color": 3066993,
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
            requests.post(DISCORD_WEBHOOK_URL, json=payload).raise_for_status()
            print(f"Mensaje enviado a Discord: {key}")
        except Exception as e:
            print(f"Error enviando a Discord: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"}), 200

# Endpoint para probar conexión a Discord
@app.route("/test-discord", methods=["GET"])
def test_discord():
    payload = {"content": "Prueba de conexión desde Cloud Run"}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload).raise_for_status()
        print("Mensaje de prueba enviado a Discord ✅")
        return "Mensaje enviado a Discord ✅", 200
    except Exception as e:
        print(f"Error enviando a Discord ❌: {e}")
        return f"Error enviando a Discord ❌: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
