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

client = OpenAI(api_key=GEMINI_API_KEY)

app = Flask(__name__)

@app.route("/", methods=["POST"])
def jira_to_discord():
    data = request.json or {}

    key = data.get("key")
    status = (data.get("status") or "").strip()
    summary = data.get("summary")
    description = data.get("description", "")

    # 🚫 Ignorar payloads sin datos básicos
    if not key or not summary or not status:
        return jsonify({"status": "ignored", "reason": "faltan campos"}), 200

    # 🚫 Ignorar si NO es exactamente "Testing / QA"
    if status.lower() not in ["testing / qa", "testing/qa"]:
        return jsonify({"status": "ignored", "reason": f"status={status}"}), 200

    # ✅ Preparar campo Ambientado QA
    ambientado_qa = data.get("ambientado_qa")
    if isinstance(ambientado_qa, list):
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

    # ✅ Generar Excel con texto plano usando Gemini
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
        # Notificar error en Discord
        requests.post(DISCORD_WEBHOOK_URL, json={"content": f"❌ Error generando Excel para {key}: {str(e)}"})

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(port=5000)

