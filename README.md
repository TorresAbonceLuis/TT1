# 🎹 Piano Transcription System

Sistema de transcripción automática de piano usando CNN-LSTM. Convierte archivos de audio WAV en partituras MIDI y PDF.

## 🎵 Características

- **Transcripción automática**: Convierte audio de piano a notación musical usando un modelo CNN-LSTM
- **Procesamiento en tiempo real**: Seguimiento del progreso mediante Server-Sent Events (SSE)
- **Múltiples formatos**: Genera archivos MIDI y PDF
- **Arquitectura chunking**: Procesa archivos grandes sin problemas de memoria
- **Interfaz moderna**: Frontend en Next.js con React

## 🏗️ Arquitectura

### Backend (FastAPI + Python)
- **Framework**: FastAPI
- **ML**: TensorFlow/Keras para CNN-LSTM
- **Audio**: Librosa para procesamiento de espectrogramas mel
- **Partituras**: music21 + MuseScore para generación de PDF

### Frontend (Next.js + React)
- **Framework**: Next.js 15
- **Estilo**: Tailwind CSS
- **Comunicación**: SSE para progreso en tiempo real

## 📋 Requisitos

### Backend
- Python 3.9+
- MuseScore 4 (para generación de PDF)
- Dependencias en `Backend/requeriment.txt`

### Frontend
- Node.js 18+
- npm o yarn

## 🚀 Instalación

### 1. Configurar Backend

```bash
cd Backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En macOS/Linux
# venv\Scripts\activate   # En Windows

# Instalar dependencias
pip install -r requeriment.txt

# Configurar MuseScore (macOS)
brew install --cask musescore

# Configurar music21
python configure_music21.py
```

### 2. Configurar Frontend

```bash
cd FrontEnd

# Instalar dependencias
npm install

# Crear archivo .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

### 3. Modelo CNN-LSTM

Coloca el archivo del modelo en:
```
Backend/modelos/modelo.keras
```

## 🎮 Uso

### Iniciar Backend
```bash
cd Backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Iniciar Frontend
```bash
cd FrontEnd
npm run dev
```

Accede a: **http://localhost:3000**

## 📡 API Endpoints

### POST `/api/v1/transcribe/`
Inicia una transcripción de piano
- **Input**: Archivo WAV
- **Output**: `task_id` para seguimiento

### GET `/api/v1/transcribe/status/{task_id}`
Obtiene el estado de una transcripción
- **Output**: JSON con estado, progreso, mensaje

### GET `/api/v1/transcribe/stream/{task_id}`
Stream SSE de progreso en tiempo real
- **Output**: Server-Sent Events con actualizaciones

### GET `/api/v1/transcribe/download/midi/{task_id}`
Descarga el archivo MIDI generado

### GET `/api/v1/transcribe/download/pdf/{task_id}`
Descarga la partitura en PDF

## 🔧 Configuración

### Backend (`Backend/config.py`)
```python
APP_NAME = "Piano Transcription API"
UPLOAD_FOLDER = "temp_uploads"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MODEL_PATH = "modelos/modelo.keras"
SAMPLE_RATE = 22050
N_MELS = 128
```

## 🎓 Modelo CNN-LSTM

- **Entrada**: Espectrogramas mel (128 bins, secuencias de 100 frames)
- **Salida**: 88 teclas de piano (MIDI 21-108, A0-C8)
- **Arquitectura**: Convoluciones + LSTM bidireccional
- **Chunking**: 10,000 frames por chunk para optimización de memoria

## 👥 Equipo

**Trabajo Terminal | ESCOM-IPN**

### Desarrolladores
- Salazar Carreón Jeshua Jonathan (2021630656)
- Torres Abonce Luis Miguel (2021630738)

### Directores
- M. en C. César Mújica Ascencio
- Tania Rodríguez Sarabia

## 📄 Licencia

Todos los derechos reservados © 2025 ESCOM-IPN

## 🐛 Troubleshooting

### MuseScore genera warnings de Qt
**Normal**. MuseScore 4 genera warnings de Qt/QML que no afectan la generación de PDF.

### Error: Modelo no encontrado
Verifica que el archivo `.keras` esté en `Backend/modelos/`

### Error: CUDA out of memory
El sistema usa chunking, pero si persiste, reduce `CHUNK_SIZE` en `services/transcription.py`

### Frontend no se conecta al backend
Verifica que `NEXT_PUBLIC_API_URL` en `.env.local` apunte a `http://localhost:8000/api/v1`

## 📚 Estructura del Proyecto

```
TT1/
├── Backend/
│   ├── main.py                 # Aplicación FastAPI
│   ├── config.py               # Configuración
│   ├── schemas.py              # Modelos Pydantic
│   ├── dependencies.py         # Dependencias FastAPI
│   ├── routers/
│   │   └── upload.py          # Endpoints de transcripción
│   ├── services/
│   │   ├── transcription.py   # Servicio de transcripción CNN-LSTM
│   │   └── sheet_music.py     # Generación de partituras PDF
│   └── utils/
│       └── file_handling.py   # Manejo de archivos
├── FrontEnd/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.js       # Página de inicio
│   │   │   └── transcription.js # Página de transcripción
│   │   └── components/
│   │       ├── NavBar.js      # Barra de navegación
│   │       └── PianoTranscription.js # Componente principal
│   └── package.json
└── README.md
```
