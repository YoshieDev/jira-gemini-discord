# Instrucciones Copilot para `jira-gemini-discord`

## Descripción del Proyecto

Este servicio en Python con Flask actúa como puente entre Jira y Discord. Recibe eventos webhook de Jira, los procesa y publica notificaciones formateadas en un canal de Discord usando un webhook. Está pensado para desplegarse en plataformas como Cloud Run usando Docker.

## Arquitectura

- **Aplicación de un solo archivo:** Toda la lógica principal está en `main.py`.
- **Endpoints:**
  - `/jira-webhook` (o `/` en algunas ramas): Recibe payloads POST de Jira.
  - `/test-discord`: Envía un mensaje de prueba a Discord (solo en algunas ramas).
- **Integración Discord:** Usa la variable de entorno `DISCORD_WEBHOOK_URL` para publicar mensajes.
- **Integración Jira:** Espera campos específicos en el JSON recibido (por ejemplo, `issue`, `fields`, `status`, `summary`, `assignee`).

## Patrones Clave

- **Filtrado por estado:** Solo los tickets con estado "Testing / QA" (insensible a mayúsculas/minúsculas) disparan notificaciones a Discord.
- **Extracción de campos:** Maneja campos faltantes o malformados con valores por defecto y logs de error.
- **Formato de mensajes:** Los mensajes a Discord usan embeds (formato enriquecido) o texto plano, según la rama.
- **Variables de entorno:** Se deben definir `DISCORD_WEBHOOK_URL` y opcionalmente `PORT`.

## Build & Run

- **Dependencias:** Ver `requirements.txt`. Instalar con `pip install -r requirements.txt`.
- **Docker:** Hay dos variantes:
  - Ejecución directa con Python: `CMD ["python", "main.py"]`
  - Ejecución con Gunicorn: `CMD ["gunicorn", "-b", ":8080", "main:app"]`
- **Puerto:** Expone `8080` para Cloud Run; en local puede usar `5000`.

## Pruebas y Debug

- Usa el endpoint `/test-discord` para verificar la conexión con Discord.
- Los logs de depuración se imprimen en stdout para payloads recibidos y resultados de envío a Discord.
- El manejo de errores es robusto para JSON malformado y fallos al enviar a Discord.

## Convenciones

- **Nombres de campos en español:** Algunos campos personalizados de Jira usan español (ejemplo: `customfield_team`, `customfield_ambienteQA`).
- **Diferencias entre ramas:** Hay conflictos de merge en `main.py` y `Dockerfile`. Resolver antes de hacer cambios grandes.
- **Sin módulos externos:** Toda la lógica está en `main.py`.

## Ejemplo: Lógica de notificación a Discord

```python
if status == "Testing / QA":
    # Construir embed/mensaje para Discord
    # Publicar en DISCORD_WEBHOOK_URL
```

## Dependencias externas

- Flask, requests, gunicorn, python-dotenv, pandas, openpyxl, openai (ver `requirements.txt`).

## Puntos de integración

- **Jira:** Espera payloads webhook con campos específicos.
- **Discord:** Publica notificaciones vía webhook.

---

**Solicito feedback:**
- ¿Hay endpoints, scripts o flujos de trabajo adicionales que no estén cubiertos aquí?
- ¿Debo aclarar instrucciones de despliegue para plataformas específicas (Cloud Run vs local)?
- ¿Existen convenciones para campos personalizados de Jira o formato de Discord que deban detallarse más?

Avísame si alguna sección es poco clara o incompleta para poder mejorarla.