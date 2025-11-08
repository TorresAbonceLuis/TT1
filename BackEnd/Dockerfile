# Usar imagen base de Python optimizada
FROM python:3.9-slim

# Instalar dependencias del sistema necesarias para audio y ML
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    musescore3 \
    lilypond \
    xvfb \
    build-essential \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Nota: MuseScore y Lilypond se instalarán solo si son necesarios
# Para reducir tamaño de imagen y tiempo de build

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de requerimientos primero (para aprovechar cache de Docker)
COPY requeriment.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requeriment.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p temp_uploads modelos

# Exponer el puerto 8000
EXPOSE 8000

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
