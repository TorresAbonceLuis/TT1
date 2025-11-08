from fastapi import HTTPException, status
from fastapi import UploadFile
import os

def validate_wav_file(file: UploadFile):
    """Valida que el archivo sea WAV antes de procesarlo"""
    # Validar extensión
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != '.wav':
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se permiten archivos WAV (.wav)"
        )
    
    # Validar tamaño (máximo 100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande. Tamaño máximo: 100MB"
        )
    
    return file