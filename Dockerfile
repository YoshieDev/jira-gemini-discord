# Usa la imagen oficial de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copia dependencias
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY main.py .

# Expone el puerto (Cloud Run lo asigna dinámicamente)
EXPOSE 8080

# Comando para iniciar la app
CMD ["python", "main.py"]
