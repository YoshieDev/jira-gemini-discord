# Imagen base de Python
FROM python:3.11-slim

# Setear directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run expone el puerto 8080 por defecto
ENV PORT=8080

# Comando de inicio con gunicorn (producción)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
