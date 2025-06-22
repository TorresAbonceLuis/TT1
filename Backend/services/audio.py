from utils.instrument_detection import analyze_instrument
from fastapi import HTTPException
import os

async def get_instrument_info(file_path: str):
    """Obtiene información del instrumento desde el archivo de audio"""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        result = await analyze_instrument(file_path)
        
        # Asegurar que el resultado tenga los campos necesarios
        if 'predicted_instrument' in result:
            result['instrument'] = result.pop('predicted_instrument')
        
        return {
            "instrument": result.get("instrument", "desconocido"),
            "confidence": result.get("confidence", 0.0),
            "features": result.get("features", {})
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar el audio: {str(e)}"
        )

# Definir el alias después de la función principal
process_audio_file = get_instrument_info