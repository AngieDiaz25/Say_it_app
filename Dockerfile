# CAMBIO: Usamos Python 3.11 para compatibilidad con librerías modernas
FROM python:3.11-slim

# Evitamos archivos temporales
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiamos e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY . .

# Exponemos el puerto
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Comando de arranque
CMD ["python", "main.py"]
