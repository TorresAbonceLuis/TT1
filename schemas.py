from pydantic import BaseModel
from typing import Optional, Dict, Any

class TranscriptionStatus(BaseModel):
    """Estado de una tarea de transcripción"""
    task_id: str
    status: str  # "processing", "completed", "error"
    progress: int  # 0-100
    message: str
    midi_path: Optional[str] = None
    pdf_path: Optional[str] = None
    transcription_info: Optional[Dict[str, Any]] = None

class TranscriptionResponse(BaseModel):
    """Respuesta al iniciar una transcripción"""
    task_id: str
    message: str
    status: str