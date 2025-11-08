from pathlib import Path
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "Piano Transcription API"
    DEBUG: bool = os.getenv("ENV", "development") != "production"
    
    # Configuración de archivos
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "temp_uploads")
    ALLOWED_EXTENSIONS: set = {".wav"}
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Configuración del modelo de transcripción
    MODEL_PATH: str = os.getenv("MODEL_PATH", "modelos/modelo.keras")
    
    # Configuración de audio
    SAMPLE_RATE: int = 22050
    HOP_LENGTH: int = 512
    N_MELS: int = 128
    
    # Azure Storage (opcional para archivos persistentes)
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_STORAGE_CONTAINER: str = os.getenv("AZURE_STORAGE_CONTAINER", "models")
    
    class Config:
        env_file = ".env"

# Crear carpetas si no existen
Path(Settings().UPLOAD_FOLDER).mkdir(exist_ok=True, parents=True)
Path("modelos").mkdir(exist_ok=True, parents=True)

settings = Settings()