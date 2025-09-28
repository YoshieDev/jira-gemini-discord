# Imagen base ligera con Python
FROM python:3.11-slim

# Configuración de directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Exponer el puerto
EXPOSE 8080

# Comando de inicio (gunicorn ejecutando main:app)
CMD ["gunicorn", "-b", ":8080", "main:app"]
