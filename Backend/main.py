from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse  # Nuevo: Para devolver archivos
import os

app = FastAPI()

# Configura CORS para tu frontend de Next.js (ajusta en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL frontend
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

        # Validar tamaño (10MB máximo) se puede ajustar segun las necesidades
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 10MB)")

        # Guardar el archivo
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Devuelve el PDF estático (ruta relativa a tu backend)
        pdf_path = "pdf/reporte1.pdf"
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF no encontrado")
        #borrar el archivo de audio después de procesarlo
        os.remove(file_path)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=partitura.pdf"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))