from flask import Flask, request, jsonify
import os, requests
import json
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv   # 👈 nuevo

# --- Cargar variables desde .env ---
load_dotenv()

# --- CONFIGURACIÓN DE LA API DE GEMINI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
# ----------------------------------------

app = Flask(__name__)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# -------------------------------
# Guardar casos en Excel
# -------------------------------
def save_test_cases_to_excel(test_cases_list, ticket_key):
    rows = []
    for i, tc in enumerate(test_cases_list, 1):
        rows.append({
            "ID": f"TC{i:03d}",
            "Descripción": tc.get("caseTitle", ""),
            "Pasos": " -> ".join(tc.get("steps", [])),
            "Datos de prueba": tc.get("testData", "No definido"),
            "Resultado esperado": tc.get("expectedResult", "")
        })
    
    df = pd.DataFrame(rows, columns=["ID", "Descripción", "Pasos", "Datos de prueba", "Resultado esperado"])
    filename = f"casos_prueba_{ticket_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(filename, index=False)
    return filename

# -------------------------------
# Generación de casos con Gemini
# -------------------------------
def generate_test_cases(summary: str, ambient_info: str):
    response_schema = {
        "type": "ARRAY",
        "description": "Lista de 5 casos de prueba de aceptación funcionales.",
        "items": {
            "type": "OBJECT",
            "properties": {
                "caseTitle": {"type": "STRING"},
                "steps": {"type": "ARRAY", "items": {"type": "STRING"}},
                "testData": {"type": "STRING"},
                "expectedResult": {"type": "STRING"}
            },
            "required": ["caseTitle", "steps", "testData", "expectedResult"],
            "propertyOrdering": ["caseTitle", "steps", "testData", "expectedResult"]
        }
    }

    system_prompt = (
        "Eres un experto en QA. Genera exactamente 5 casos de prueba de aceptación "
        "en español para la funcionalidad descrita. Incluye escenarios positivos, negativos y de borde. "
        "Cada caso debe tener: título, pasos claros, datos de prueba realistas y resultado esperado. "
        "Responde únicamente en un JSON estricto que cumpla el esquema."
    )

    user_query = (
        f"Genera casos de prueba basados en este ticket:\n"
        f"RESUMEN: '{summary}'\n"
        f"AMBIENTE: '{ambient_info}'"
    )

    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        },
    }

    headers = {'Content-Type': 'application/json'}
    url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    max_retries = 3
    base_delay = 1

    for attempt in range(max_retries):
        try:
            response = requests.post(url_with_key, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()

            json_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
            if json_text:
                return json.loads(json_text)  # devolvemos lista cruda
            else:
                return []
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
            else:
                print(f"[ERROR GEMINI] {e}")
                return []

    return []

# -------------------------------
# Flujo principal del Webhook
# -------------------------------
@app.route("/", methods=["POST"])
def jira_to_discord():
    data = request.json or {}

    key = data.get("key")
    status = (data.get("status") or "").strip()
    summary = data.get("summary")

    if not key or not summary or not status:
        return jsonify({"status": "ignored", "reason": "faltan campos"}), 200

    if status.lower().strip().replace(' ', '') not in ["testing/qa", "testingqa"]:
        return jsonify({"status": "ignored", "reason": f"status='{status}' no coincide con Testing/QA"}), 200

    ambientado_qa = data.get("ambientado_qa")
    if isinstance(ambientado_qa, list):
        ambientado_qa = ", ".join(ambientado_qa)
    ambientado_qa = ambientado_qa or "No definido"

    # 1. Generar casos
    test_cases_list = generate_test_cases(summary, ambientado_qa)

    # 2. Guardar en Excel
    excel_file = None
    if test_cases_list:
        excel_file = save_test_cases_to_excel(test_cases_list, key)

        # 3. Mensaje principal de notificación
    message = (
        f"🔔 El ticket {key} pasó a **{status}**\n"
        f"📌 **Resumen:** {summary}\n"
        f"👤 Asignado a: {data.get('assignee', 'Sin asignar')}\n"
        f"🛠 **Ambientado QA:** {ambientado_qa}\n"
        f"👉 [Ver en Jira]({data.get('url', '#' )})"
    )

    # 4. Casos de prueba generados
    if test_cases_list:
        message += "\n\n---\n\n## 🤖 Casos de Prueba Generados (QA)\n"
        for i, tc in enumerate(test_cases_list, 1):
            message += (
                f"### 🧪 Caso {i}: {tc.get('caseTitle', '')}\n"
                f"**Datos de prueba:** {tc.get('testData','No definido')}\n"
                f"**Resultado Esperado:** {tc.get('expectedResult','')}\n"
                f"**Pasos:**\n"
            )
            for j, step in enumerate(tc.get('steps', []), 1):
                message += f"{j}. {step}\n"
            message += "\n---\n"


    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Error al enviar a Discord: {e}")
        return jsonify({"status": "error", "reason": "fallo Discord"}), 500

    return jsonify({"status": "ok", "excel_file": excel_file}), 200


if __name__ == "__main__":
    app.run(port=5000)
