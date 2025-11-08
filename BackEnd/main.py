from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from contextlib import asynccontextmanager

# Tarea de limpieza de fondo
cleanup_task = None

async def periodic_cleanup():
    """
    Tarea que se ejecuta periódicamente para limpiar archivos antiguos.
    Elimina archivos en temp_uploads que tengan más de 1 hora.
    """
    from utils.file_handling import cleanup_files
    from config import settings
    import time
    
    while True:
        try:
            await asyncio.sleep(3600)  # Ejecutar cada hora
            
            temp_dir = settings.UPLOAD_FOLDER
            if not os.path.exists(temp_dir):
                continue
            
            current_time = time.time()
            files_deleted = 0
            
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                
                if os.path.isfile(file_path):
                    # Verificar si el archivo tiene más de 1 hora
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > 3600:  # 1 hora en segundos
                        cleanup_files([file_path])
                        files_deleted += 1
            
            if files_deleted > 0:
                print(f"🗑️  Limpieza automática: {files_deleted} archivos antiguos eliminados")
                
        except Exception as e:
            print(f"❌ Error en limpieza automática: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    Inicia y detiene tareas de fondo.
    """
    global cleanup_task
    
    # Inicio: Crear tarea de limpieza
    cleanup_task = asyncio.create_task(periodic_cleanup())
    print("✅ Tarea de limpieza automática iniciada")
    
    yield
    
    # Cierre: Cancelar tarea de limpieza
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
    print("🛑 Tarea de limpieza automática detenida")

app = FastAPI(
    title="Piano Transcription API",
    description="API para transcripción automática de piano usando CNN-LSTM",
    version="1.0.0",
    lifespan=lifespan
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