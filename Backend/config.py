from pathlib import Path
from pydantic_settings import BaseSettings  # Cambiado aquí

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "Music Instrument Detector"
    DEBUG: bool = True
    
    # Configuración de archivos
    UPLOAD_FOLDER: str = "temp_uploads"
    PDF_OUTPUT_FOLDER: str = "pdf_reports"
    ALLOWED_EXTENSIONS: set = {".mp3", ".wav", ".ogg"}
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Configuración del modelo
    MODEL_PATH: str = "models/instrument_classifier.pkl"
    
    class Config:
        env_file = ".env"

# Crear carpetas si no existen
Path(Settings().UPLOAD_FOLDER).mkdir(exist_ok=True)  # Corregido aquí
Path(Settings().PDF_OUTPUT_FOLDER).mkdir(exist_ok=True)  # Corregido aquí

settings = Settings()