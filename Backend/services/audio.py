from utils.instrument_detection import analyze_instrument
from fastapi import HTTPException

async def process_audio_file(file_path: str):
    """Wrapper para mantener compatibilidad con FastAPI"""
    try:
        # Usamos tu función original modificada
        result = analyze_instrument(file_path)
        
        return {
            "instrument": result["instrument"],
            "frequency": result["frequency"]  # Solo devolvemos instrumento y frecuencia
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis de audio: {str(e)}"
        )

# Alias para compatibilidad
get_instrument_info = process_audio_file