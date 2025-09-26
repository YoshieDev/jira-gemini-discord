from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

# Leer variables de entorno
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Endpoint para probar que las variables de entorno funcionan
@app.get("/test-env")
async def test_env():
    return {
        "discord_webhook": bool(DISCORD_WEBHOOK),
        "gemini_api_key": bool(GEMINI_API_KEY)
    }

# Endpoint para recibir webhooks de Jira y enviar mensaje de prueba a Discord
@app.post("/jira-webhook")
async def jira_webhook(req: Request):
    data = await req.json()
    issue = data.get("issue", {})
    ticket_key = issue.get("key", "UNKNOWN")
    summary = issue.get("fields", {}).get("summary", "Sin resumen")
    description = issue.get("fields", {}).get("description", "Sin descripción")

    mensaje = {
        "content": f"Prueba: Ticket **{ticket_key}** pasó a Testing\nResumen: {summary}\nDescripción: {description}"
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=mensaje)
        response.raise_for_status()
        status = "Mensaje enviado a Discord correctamente"
    except Exception as e:
        status = f"Error enviando a Discord: {e}"

    return {"status": status, "ticket": ticket_key}
