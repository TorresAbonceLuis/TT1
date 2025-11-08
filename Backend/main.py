from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Piano Transcription API",
    description="API para transcripción automática de piano usando CNN-LSTM",
    version="1.0.0"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "endpoints": {
            "transcribe": "/api/v1/transcribe/",
            "status": "/api/v1/transcribe/status/{task_id}",
            "stream": "/api/v1/transcribe/stream/{task_id}",
            "download_midi": "/api/v1/transcribe/download/midi/{task_id}",
            "download_pdf": "/api/v1/transcribe/download/pdf/{task_id}"
        }
    }