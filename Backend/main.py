from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Configura CORS para tu frontend de Next.js (ajusta en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de tu frontend
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # Validar tipo de archivo
        allowed_types = ["audio/mpeg", "audio/wav", "audio/ogg"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Formato no soportado. Sube archivos MP3, WAV u OGG.")

        # Validar tamaño (10MB máximo)
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 10MB)")

        # Guardar el archivo
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return {"message": "Audio subido correctamente", "transcription": "Aquí iría la transcripción generada"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))