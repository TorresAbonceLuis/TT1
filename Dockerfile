    # Usa una imagen base de Python oficial, que ya incluye pip
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos para aprovechar el caché
COPY requeriment.txt .

# Instala todas las dependencias (uvicorn estará disponible globalmente en este entorno)
RUN pip install --no-cache-dir -r requeriment.txt

# Copia el resto de tu código (main.py, modelos, etc.)
COPY . .

# Comando de inicio
# NOTA: En este entorno Docker, 'uvicorn' sí estará en el PATH.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]