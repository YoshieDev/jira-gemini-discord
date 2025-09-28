from flask import Flask, request, jsonify
import os, requests
import pandas as pd
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

client = OpenAI(api_key=GEMINI_API_KEY)

app = Flask(__name__)

STATUS_CONFIG = {
    "testing / qa": {"color": 0xE74C3C, "emoji": "🔴"},
    "done": {"color": 0x2ECC71, "emoji": "🟢"}
}

@app.route("/", methods=["POST"])
def jira_to_discord():
    data = request.json or {}

    key = data.get("key")
    status = (data.get("status") or "").strip()
    summary = data.get("summary")
    description = data.get("description", "")

    if not key or not summary or not status:
        return jsonify({"status": "ignored", "reason": "faltan campos"}), 200

    # Configuración de color y emoji
    config = STATUS_CONFIG.get(status.lower(), {"color": 0x3498DB, "emoji": "🔵"})
    color = config["color"]
    emoji = config["emoji"]

    # Campo Ambientado QA
    ambientado_qa = data.get("ambientado_qa")
    if isinstance(ambientado_qa, list):
        ambientado_qa = ", ".join(ambientado_qa)
    ambientado_qa = ambientado_qa or "No definido"

    # Embed de Discord
    embed = {
        "title": f"{emoji} Ticket {key} pasó a {status}",
        "url": data.get("url", "#"),
        "color": color,
        "fields": [
            {"name": "📌 Resumen", "value": summary, "inline": False},
            {"name": "👤 Asignado a", "value": data.get("assignee", "Sin asignar"), "inline": True},
            {"name": "🛠 Ambientado QA", "value": ambientado_qa, "inline": True}
        ]
    }
    requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})

    # Solo generar Excel si Testing / QA
    if status.lower() in ["testing / qa", "testing/qa"]:
        try:
            prompt = f"""
            Genera 10 casos de prueba para este ticket de Jira.
            Título: {summary}
            Descripción: {description}
            Devuelve la información como texto plano.
            """

            response = client.chat.completions.create(
                model="gemini-1.5",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            text = response.choices[0].message.content

            # Crear Excel con texto plano
            df = pd.DataFrame([text.splitlines()], columns=[f"Casos de prueba para {key}"])

            # Guardar Excel en memoria
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)

            # Subir archivo a Discord
            files = {"file": (f"{key}_casos_de_prueba.xlsx", excel_buffer)}
            requests.post(DISCORD_WEBHOOK_URL, files=files, data={"content": f"📄 Casos de prueba generados para {key}"})

        except Exception as e:
            # Enviar error a Discord
            requests.post(DISCORD_WEBHOOK_URL, json={"content": f"❌ Error generando casos de prueba para {key}: {str(e)}"})

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(port=5000)
