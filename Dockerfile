# Imagen base
FROM python:3.11-slim

# Carpeta de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Ejecutar la app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
