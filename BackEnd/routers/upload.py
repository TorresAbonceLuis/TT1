from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from services.transcription import transcribe_piano_audio
from services.sheet_music import generate_sheet_music_pdf
from utils.file_handling import save_uploaded_file, cleanup_files
import os
import json
import asyncio
import uuid

router = APIRouter(tags=["Piano Transcription"])

# Diccionario en memoria para almacenar estado de transcripciones
transcription_status = {}

@router.post("/transcribe/")
async def start_transcription(file: UploadFile = File(...)):
    """
    Endpoint para iniciar la transcripción de piano.
    Retorna un ID de tarea para hacer seguimiento del progreso.
    """
    temp_audio_path = None
    
    try:
        # Validar que es un archivo WAV o MP3
        if not (file.filename.lower().endswith('.wav') or file.filename.lower().endswith('.mp3')):
            raise HTTPException(
                status_code=400,
                detail="Formato de audio no soportado. Solo se permiten archivos WAV y MP3"
            )
        
        # Guardar archivo temporalmente
        temp_audio_path = await save_uploaded_file(file)
        
        # Generar ID único para esta transcripción
        task_id = str(uuid.uuid4())
        
        # IMPORTANTE: Inicializar estado ANTES de iniciar la tarea
        # Esto previene race conditions donde el cliente hace polling antes de que se registre la tarea
        transcription_status[task_id] = {
            "status": "pending",
            "progress": 0,
            "message": "Iniciando transcripción...",
            "audio_path": temp_audio_path,
            "filename": file.filename,
            "midi_path": None,
            "pdf_path": None,
            "error": None,
            "midi_downloaded": False,
            "pdf_downloaded": False,
            "cleanup_scheduled": False
        }
        
        # Pequeño delay para asegurar que el estado se guarde
        await asyncio.sleep(0.1)
        
        # Iniciar transcripción en background
        asyncio.create_task(run_transcription_task(task_id))
        
        return JSONResponse(content={
            "task_id": task_id,
            "message": "Transcripción iniciada. Use /transcribe/status/{task_id} para ver el progreso."
        })
        
    except Exception as e:
        if temp_audio_path and os.path.exists(temp_audio_path):
            cleanup_files([temp_audio_path])
        raise HTTPException(status_code=500, detail=str(e))


async def run_transcription_task(task_id: str):
    """
    Ejecuta la tarea de transcripción en background.
    """
    task_data = transcription_status[task_id]
    audio_path = task_data["audio_path"]
    filename = task_data["filename"]
    
    try:
        # Actualizar estado
        task_data["status"] = "processing"
        task_data["message"] = "Procesando transcripción..."
        
        # Definir rutas de salida
        output_dir = "temp_uploads"
        base_name = os.path.splitext(filename)[0]
        midi_path = os.path.join(output_dir, f"{base_name}_{task_id}.mid")
        pdf_path = os.path.join(output_dir, f"{base_name}_{task_id}_partitura.pdf")
        
        # 1. Transcribir audio a MIDI
        transcription_result = transcribe_piano_audio(audio_path, midi_path)
        task_data["midi_path"] = midi_path
        
        # 2. Generar partitura PDF
        task_data["message"] = "Generando partitura en PDF..."
        
        try:
            pdf_result = generate_sheet_music_pdf(
                midi_path,
                pdf_path,
                title=f"Transcripción: {base_name}",
                composer="Generado por IA CNN-LSTM"
            )
            task_data["pdf_path"] = pdf_result
        except Exception as pdf_error:
            # Si falla la generación del PDF, al menos tenemos el MIDI
            print(f"Error generando PDF: {pdf_error}")
            task_data["pdf_path"] = None
            task_data["message"] = f"Transcripción completada (PDF no disponible: {str(pdf_error)})"
        
        # Completar tarea
        task_data["status"] = "completed"
        task_data["progress"] = 100
        task_data["message"] = "Transcripción completada exitosamente"
        task_data["transcription_info"] = transcription_result
        
    except Exception as e:
        task_data["status"] = "failed"
        task_data["error"] = str(e)
        task_data["message"] = f"Error: {str(e)}"
    
    finally:
        # Limpiar archivo de audio temporal
        if os.path.exists(audio_path):
            cleanup_files([audio_path])


async def cleanup_task_files(task_id: str, delay: int = 300):
    """
    Limpia los archivos asociados a una tarea después de un delay.
    Se ejecuta después de que el usuario descargue los archivos.
    Por defecto espera 5 minutos para dar tiempo a múltiples descargas.
    """
    await asyncio.sleep(delay)
    
    if task_id in transcription_status:
        task_data = transcription_status[task_id]
        files_to_delete = []
        
        # Agregar MIDI si existe
        if task_data.get("midi_path") and os.path.exists(task_data["midi_path"]):
            files_to_delete.append(task_data["midi_path"])
        
        # Agregar PDF si existe
        if task_data.get("pdf_path") and os.path.exists(task_data["pdf_path"]):
            files_to_delete.append(task_data["pdf_path"])
        
        # Eliminar archivos
        if files_to_delete:
            cleanup_files(files_to_delete)
            print(f"🗑️  Archivos de tarea {task_id} eliminados: {len(files_to_delete)} archivos")
        
        # Eliminar entrada del diccionario de estado
        del transcription_status[task_id]
        print(f"✅ Tarea {task_id} limpiada completamente")


@router.get("/transcribe/status/{task_id}")
async def get_transcription_status(task_id: str):
    """
    Obtiene el estado actual de una transcripción.
    """
    if task_id not in transcription_status:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task_data = transcription_status[task_id]
    
    return JSONResponse(content={
        "task_id": task_id,
        "status": task_data["status"],
        "progress": task_data["progress"],
        "message": task_data["message"],
        "error": task_data.get("error"),
        "has_midi": task_data.get("midi_path") is not None,
        "has_pdf": task_data.get("pdf_path") is not None,
        "transcription_info": task_data.get("transcription_info")
    })


@router.get("/transcribe/download/midi/{task_id}")
async def download_midi(task_id: str):
    """
    Descarga el archivo MIDI generado.
    Los archivos se mantienen disponibles por 5 minutos después de completarse.
    """
    if task_id not in transcription_status:
        raise HTTPException(status_code=404, detail="Tarea no encontrada o archivos ya eliminados")
    
    task_data = transcription_status[task_id]
    
    if task_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="La transcripción aún no ha finalizado")
    
    if not task_data.get("midi_path") or not os.path.exists(task_data["midi_path"]):
        raise HTTPException(status_code=404, detail="Archivo MIDI no encontrado o ya eliminado")
    
    filename = os.path.splitext(task_data["filename"])[0] + ".mid"
    
    # Marcar que el MIDI fue descargado
    task_data["midi_downloaded"] = True
    
    # Programar limpieza automática solo la primera vez que se descarga algo
    if not task_data.get("cleanup_scheduled"):
        task_data["cleanup_scheduled"] = True
        asyncio.create_task(cleanup_task_files(task_id, delay=300))  # 5 minutos
        print(f"⏰ Limpieza programada para tarea {task_id} en 5 minutos")
    
    return FileResponse(
        task_data["midi_path"],
        media_type="audio/midi",
        filename=filename
    )


@router.get("/transcribe/download/pdf/{task_id}")
async def download_pdf_sheet(task_id: str):
    """
    Descarga la partitura en PDF.
    Los archivos se mantienen disponibles por 5 minutos después de completarse.
    """
    if task_id not in transcription_status:
        raise HTTPException(status_code=404, detail="Tarea no encontrada o archivos ya eliminados")
    
    task_data = transcription_status[task_id]
    
    if task_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="La transcripción aún no ha finalizado")
    
    if not task_data.get("pdf_path") or not os.path.exists(task_data["pdf_path"]):
        raise HTTPException(status_code=404, detail="Partitura PDF no disponible o ya eliminada")
    
    filename = os.path.splitext(task_data["filename"])[0] + "_partitura.pdf"
    
    # Marcar que el PDF fue descargado
    task_data["pdf_downloaded"] = True
    
    # Programar limpieza automática solo la primera vez que se descarga algo
    if not task_data.get("cleanup_scheduled"):
        task_data["cleanup_scheduled"] = True
        asyncio.create_task(cleanup_task_files(task_id, delay=300))  # 5 minutos
        print(f"⏰ Limpieza programada para tarea {task_id} en 5 minutos")
    
    return FileResponse(
        task_data["pdf_path"],
        media_type="application/pdf",
        filename=filename
    )


@router.get("/transcribe/cleanup-status")
async def get_cleanup_status():
    """
    Endpoint para monitorear el estado de los archivos temporales.
    Útil para debugging y verificar que la limpieza funcione.
    """
    from config import settings
    import time
    
    temp_dir = settings.UPLOAD_FOLDER
    
    if not os.path.exists(temp_dir):
        return JSONResponse(content={
            "temp_folder": temp_dir,
            "exists": False,
            "message": "Carpeta temporal no existe"
        })
    
    files_info = []
    total_size = 0
    
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path):
            file_stat = os.stat(file_path)
            file_age_hours = (time.time() - file_stat.st_mtime) / 3600
            file_size_kb = file_stat.st_size / 1024
            
            files_info.append({
                "filename": filename,
                "size_kb": round(file_size_kb, 2),
                "age_hours": round(file_age_hours, 2),
                "will_be_deleted": file_age_hours > 1
            })
            total_size += file_size_kb
    
    return JSONResponse(content={
        "temp_folder": temp_dir,
        "total_files": len(files_info),
        "total_size_mb": round(total_size / 1024, 2),
        "active_tasks": len(transcription_status),
        "files": files_info
    })