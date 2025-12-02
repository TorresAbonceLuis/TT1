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
    
    # Configuración de audio (Magenta Specs - High Resolution)
    SAMPLE_RATE: int = 16000  # Sample rate optimizado para piano
    HOP_LENGTH: int = 512
    N_FFT: int = 2048
    N_MELS: int = 229  # High resolution para mayor precisión
    F_MIN: float = 30.0  # Frecuencia mínima (piano más bajo)
    F_MAX: float = 8000.0  # Frecuencia máxima
    
    # Configuración del filtro de banda
    FILTER_ORDER: int = 5
    LOW_CUT: float = 30.0
    HIGH_CUT: float = 8000.0
    
    # Umbrales de transcripción (optimizados por Grid Search)
    UMBRAL_ONSETS: float = 0.30  # Umbral para detección de inicio de notas
    UMBRAL_FRAMES: float = 0.45  # Umbral para detección de frames activos
    DURACION_MINIMA_S: float = 0.030  # Duración mínima de nota (30ms) para filtrar ruido
    
    # Configuración de inferencia
    INFER_BATCH_SIZE: int = 32  # Batch size para procesamiento de ventanas
    
    # MIDI
    LOW_MIDI: int = 21  # Nota MIDI más baja del piano (A0)
    
    class Config:
        env_file = ".env"

# Crear carpetas si no existen
Path(Settings().UPLOAD_FOLDER).mkdir(exist_ok=True, parents=True)
Path("modelos").mkdir(exist_ok=True, parents=True)

settings = Settings()