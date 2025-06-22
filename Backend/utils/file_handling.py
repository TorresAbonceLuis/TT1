import os
from pathlib import Path
from typing import List
import shutil
from config import settings

async def save_uploaded_file(file, temp_dir: str = None) -> str:
    """Guarda el archivo subido en una ubicación temporal"""
    temp_dir = temp_dir or settings.UPLOAD_FOLDER
    Path(temp_dir).mkdir(exist_ok=True)
    
    file_path = os.path.join(temp_dir, file.filename)
    
    # Guardar el archivo en chunks
    with open(file_path, 'wb') as buffer:
        while content := await file.read(1024):
            buffer.write(content)
    
    return file_path

def cleanup_files(file_paths: List[str]):
    """Elimina archivos temporales"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error al eliminar {file_path}: {str(e)}")

def clear_temp_folder(folder_path: str = None):
    """Limpia toda la carpeta temporal"""
    folder_path = folder_path or settings.UPLOAD_FOLDER
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error al eliminar {file_path}: {str(e)}")