from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from services.audio import process_audio_file
from services.pdf import generate_pdf_report
from utils.file_handling import save_uploaded_file, cleanup_files
import os

router = APIRouter()

@router.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    temp_audio_path = None
    try:
        # 1. Guardar archivo temporalmente
        temp_audio_path = await save_uploaded_file(file)
        
        # 2. Procesar audio con tu código original modificado
        analysis_result = await process_audio_file(temp_audio_path)
        
        # 3. Generar PDF con frecuencia
        pdf_path = generate_pdf_report(
            original_filename=file.filename,
            instrument=analysis_result["instrument"],
            frequency=analysis_result["frequency"]  # Pasamos la frecuencia
        )
        
        # 4. Devolver PDF
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{os.path.splitext(file.filename)[0]}_{analysis_result['instrument']}.pdf"
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            cleanup_files([temp_audio_path])