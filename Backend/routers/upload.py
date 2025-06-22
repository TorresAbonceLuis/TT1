from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from services.audio import process_audio_file
from services.pdf import generate_pdf_report
from utils.file_handling import save_uploaded_file, cleanup_files  # Importación corregida
import os
from fastapi import HTTPException

router = APIRouter()

@router.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    temp_audio_path = None
    try:
        # 1. Guardar archivo temporalmente
        temp_audio_path = await save_uploaded_file(file)
        
        # 2. Procesar audio
        instrument_info = await process_audio_file(temp_audio_path)
        
        # Validar campos requeridos
        if not all(key in instrument_info for key in ['instrument', 'confidence']):
            raise HTTPException(
                status_code=500,
                detail="El análisis no devolvió los campos requeridos"
            )
        
        # 3. Generar PDF
        pdf_path = generate_pdf_report(
            original_filename=file.filename,
            instrument=instrument_info['instrument'],
            confidence=instrument_info['confidence']
        )
        
        # 4. Devolver PDF
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{os.path.splitext(file.filename)[0]}_{instrument_info['instrument']}.pdf"
        )
        
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"error": str(he.detail)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error en el servidor: {str(e)}"}
        )
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            cleanup_files([temp_audio_path])