from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "Piano Transcription API"
    DEBUG: bool = True
    
    # Configuración de archivos
    UPLOAD_FOLDER: str = "temp_uploads"
    ALLOWED_EXTENSIONS: set = {".wav"}
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Configuración del modelo de transcripción
    MODEL_PATH: str = "modelos/modelo.keras"
    
    # Configuración de audio
    SAMPLE_RATE: int = 22050
    HOP_LENGTH: int = 512
    N_MELS: int = 128
    
    class Config:
        env_file = ".env"

# Crear carpetas si no existen
Path(Settings().UPLOAD_FOLDER).mkdir(exist_ok=True)

settings = Settings()