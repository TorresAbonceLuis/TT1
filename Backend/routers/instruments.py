from fastapi import APIRouter, HTTPException
from schemas import InstrumentAnalysis
from services.audio import get_instrument_info
from utils.file_handling import cleanup_files
import os
from config import settings

router = APIRouter(
    prefix="/api/v1/instruments",
    tags=["instruments"]
)

@router.get("/detect-from-file/{filename}", response_model=InstrumentAnalysis)
async def detect_instrument(filename: str):
    try:
        filepath = os.path.join(settings.UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        analysis = await get_instrument_info(filepath)
        return {
            "instrument": analysis["instrument"],
            "confidence": analysis["confidence"],
            "features": analysis["features"],
            "original_filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'filepath' in locals():
            cleanup_files([filepath])