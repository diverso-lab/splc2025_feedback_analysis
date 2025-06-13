FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar el contenido del proyecto
COPY . .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Configurar entorno (si se usa .env)
ENV PYTHONUNBUFFERED=1

# Por defecto no hacemos nada, el usuario invoca manualmente los scripts
CMD ["bash"]
