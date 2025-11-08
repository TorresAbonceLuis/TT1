from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Piano Transcription API",
    description="API para transcripción automática de piano usando CNN-LSTM",
    version="1.0.0"
)

# Obtener origen permitido desde variable de entorno
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "https://*.vercel.app",  # Permite todos los subdominios de Vercel
        "https://*.railway.app"  # Para testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importa el router de transcripción
from routers import upload

app.include_router(upload.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Piano Transcription API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "transcribe": "/api/v1/transcribe/",
            "status": "/api/v1/transcribe/status/{task_id}",
            "stream": "/api/v1/transcribe/stream/{task_id}",
            "download_midi": "/api/v1/transcribe/download/midi/{task_id}",
            "download_pdf": "/api/v1/transcribe/download/pdf/{task_id}"
        }
    }