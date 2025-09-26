from fastapi import FastAPI, Request
import os
import requests
import json

app = FastAPI()

# Variables de entorno
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Función para llamar a Google Gemini
def consultar_gemini(texto):
    url = "https://api.gemini.google.com/v1/models/generateContent"  # Ajusta según la documentación de Gemini
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gemini-2.5-flash",  # Ajusta según tu modelo
        "contents": texto
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        resultado = response.json()
        try:
            return resultado["choices"][0]["text"]
        except KeyError:
            return "No se pudo obtener respuesta de Gemini"
    else:
        return f"Error en Gemini: {response.status_code}"

# Endpoint que Jira llamará
@app.post("/jira-webhook")
async def jira_webhook(req: Request):
    data = await req.json()
    issue = data.get("issue", {})
    ticket_key = issue.get("key", "UNKNOWN")
    fields = issue.get("fields", {})
    summary = fields.get("summary", "Sin resumen")
    description = fields.get("description", "Sin descripción")

    # Preparar prompt para Gemini
    prompt = f"""
    Analiza este ticket de Jira:
    - Resumen: {summary}
    - Descripción: {description}

    Devuelve:
    1. Un resumen breve en una frase.
    2. Nivel de riesgo (Bajo, Medio, Alto).
    3. Tres casos de prueba recomendados.
    """

    resumen_ia = consultar_gemini(prompt)

    # Construir mensaje para Discord
    mensaje = {
        "content": f"🚀 Ticket **{ticket_key}** pasó a *Testing*\n"
                   f"📋 Resumen: {summary}\n"
                   f"🤖 Análisis IA:\n{resumen_ia}\n"
                   f"🔗 Ver en Jira: {issue.get('self', 'URL no disponible')}"
    }

    # Enviar mensaje a Discord
    try:
        requests.post(DISCORD_WEBHOOK, json=mensaje)
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

    return {"status": "ok"}
