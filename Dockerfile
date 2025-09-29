<<<<<<< HEAD
# Usa la imagen oficial de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copia dependencias
=======
FROM python:3.11-slim
WORKDIR /app
>>>>>>> a52c7ca3cdcdbb41ae803c0ed57a1b7771097596
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt
<<<<<<< HEAD

# Copia el código fuente
COPY main.py .

# Expone el puerto (Cloud Run lo asigna dinámicamente)
EXPOSE 8080

# Comando para iniciar la app
CMD ["python", "main.py"]
=======
COPY . .
EXPOSE 8080
CMD ["gunicorn", "-b", ":8080", "main:app"]
>>>>>>> a52c7ca3cdcdbb41ae803c0ed57a1b7771097596
