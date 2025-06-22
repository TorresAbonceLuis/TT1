from fastapi import Depends, HTTPException, status
from config import settings
import os

def validate_audio_file(file: UploadFile):
    """Valida el archivo de audio antes de procesarlo"""
    # Validar extensión
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Formato no soportado. Use: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validar tamaño
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE//(1024*1024)}MB"
        )
    
    return file

# Puedes agregar más dependencias como:
# - Autenticación
# - Bases de datos
# - Clientes externos