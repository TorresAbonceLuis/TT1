from pydantic import BaseModel
from typing import Optional

class AudioUpload(BaseModel):
    filename: str
    content_type: str
    size: int

class InstrumentAnalysis(BaseModel):
    instrument: str
    confidence: float
    features: dict
    original_filename: str

class PDFResponse(BaseModel):
    filename: str
    path: str
    instrument: str
    download_url: Optional[str] = None