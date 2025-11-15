# 🎹 Audio a Notación | Piano Transcription System

Sistema de transcripción automática de piano usando redes neuronales CNN-LSTM. Convierte archivos de audio WAV en partituras MIDI y PDF con alta precisión.

> **Trabajo Terminal | ESCOM-IPN | 2025**

## 🎵 Características

- **🎼 Transcripción automática**: Convierte audio de piano a notación musical usando un modelo CNN-LSTM avanzado
- **📊 Procesamiento asíncrono**: Sistema de tareas con seguimiento en tiempo real
- **📝 Múltiples formatos**: Genera archivos MIDI y partituras PDF profesionales
- **🔧 Arquitectura optimizada**: Procesamiento por chunks para archivos grandes sin problemas de memoria
- **🎨 Interfaz moderna**: Frontend responsivo en Next.js 15 con React 19 y Tailwind CSS
- **🧹 Limpieza automática**: Sistema de gestión de archivos temporales
- **🐳 Docker ready**: Configuración completa para despliegue con Docker/Docker Compose

## 🏗️ Arquitectura del Sistema

### Backend (FastAPI + Python)
- **Framework**: FastAPI con uvicorn
- **Machine Learning**: TensorFlow 2.15+ / Keras 3.0+ para CNN-LSTM
- **Procesamiento de Audio**: 
  - Librosa para análisis de espectrogramas mel
  - scipy para filtros paso bajo
  - pretty_midi para generación MIDI
- **Generación de Partituras**: music21 + MuseScore 3/4 para PDF
- **Gestión de Tareas**: Sistema asíncrono con asyncio

### Frontend (Next.js + React)
- **Framework**: Next.js 15.3.4
- **UI Library**: React 19
- **Estilos**: Tailwind CSS con diseño responsivo
- **Características**: 
  - Componentes de notas musicales flotantes
  - Sistema de arrastrar y soltar archivos
  - Interfaz intuitiva y moderna

## 📋 Requisitos del Sistema

### Backend
- **Python**: 3.9 o superior
- **MuseScore**: 3 o 4 (para generación de PDF)
- **Sistema Operativo**: Linux, macOS o Windows
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB para archivos grandes)
- **Espacio en disco**: 500MB para dependencias + espacio para modelo

### Frontend
- **Node.js**: 18 o superior
- **npm** o **yarn**

## 🚀 Instalación y Configuración

### Opción 1: Instalación Local

#### 1. Configurar Backend

```powershell
# Navegar a la carpeta del backend
cd BackEnd

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requeriment.txt

# Instalar MuseScore (Windows)
# Descargar desde: https://musescore.org/es/descargar
# O usar Chocolatey:
choco install musescore
```

**Configurar music21 (opcional para Windows):**
```powershell
python -c "from music21 import *; us = environment.UserSettings(); us['musescoreDirectPNGPath'] = 'C:/Program Files/MuseScore 3/bin/MuseScore3.exe'; us['musicxmlPath'] = 'C:/Program Files/MuseScore 3/bin/MuseScore3.exe'"
```

#### 2. Configurar Frontend

```powershell
# Navegar a la carpeta del frontend
cd FrontEnd

# Instalar dependencias
npm install

# Crear archivo de variables de entorno
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

#### 3. Colocar el Modelo

Coloca el archivo del modelo CNN-LSTM entrenado en:
```
BackEnd/modelos/modelo.keras
```

### Opción 2: Instalación con Docker

```powershell
# Navegar al directorio del backend
cd BackEnd

# Construir la imagen
docker-compose build

# Iniciar el contenedor
docker-compose up -d
```

## 🎮 Uso del Sistema

### Desarrollo Local

#### Iniciar Backend
```powershell
cd BackEnd
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Iniciar Frontend
```powershell
cd FrontEnd
npm run dev
```

**Acceder a la aplicación:** http://localhost:3000

### Con Docker

```powershell
cd BackEnd
docker-compose up
```

El backend estará disponible en http://localhost:8000

## 📡 API Endpoints

### Raíz de la API
```http
GET /
```
Información general de la API y endpoints disponibles.

### Transcripción de Audio

#### POST `/api/v1/transcribe/`
Inicia una transcripción de piano
- **Input**: Archivo WAV (multipart/form-data)
- **Output**: JSON con `task_id` único para seguimiento
- **Límite**: 100MB por archivo

**Ejemplo de respuesta:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Transcripción iniciada. Use /transcribe/status/{task_id} para ver el progreso."
}
```

#### GET `/api/v1/transcribe/status/{task_id}`
Obtiene el estado actual de una transcripción
- **Output**: JSON con estado, progreso y mensaje

**Ejemplo de respuesta:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Transcripción completada exitosamente",
  "has_midi": true,
  "has_pdf": true,
  "transcription_info": {
    "total_frames": 5280,
    "duration_seconds": 120.5,
    "total_notes": 342
  }
}
```

#### GET `/api/v1/transcribe/download/midi/{task_id}`
Descarga el archivo MIDI generado
- **Output**: Archivo MIDI (audio/midi)

#### GET `/api/v1/transcribe/download/pdf/{task_id}`
Descarga la partitura en PDF
- **Output**: Archivo PDF (application/pdf)

#### GET `/api/v1/transcribe/cleanup-status`
Monitorea el estado de archivos temporales (útil para debugging)

## 🔧 Configuración Avanzada

### Variables de Entorno (Backend)

Crear archivo `.env` en `BackEnd/`:

```env
ENV=production
FRONTEND_URL=http://localhost:3000
MODEL_PATH=modelos/modelo.keras
UPLOAD_FOLDER=temp_uploads
```

### Configuración del Modelo (`BackEnd/config.py`)

```python
APP_NAME = "Piano Transcription API"
UPLOAD_FOLDER = "temp_uploads"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MODEL_PATH = "modelos/modelo.keras"
SAMPLE_RATE = 22050
HOP_LENGTH = 512
N_MELS = 128
```

### Parámetros del Modelo CNN-LSTM

**Características del modelo:**
- **Entrada**: Espectrogramas mel (128 bins) + Delta + Delta-Delta = 384 características
- **Secuencia**: 100 frames por ventana
- **Salida**: 88 teclas de piano (MIDI 21-108, A0-C8)
- **Arquitectura**: CNN + LSTM bidireccional
- **Optimización**: Procesamiento por chunks (10,000 frames)
- **Umbrales**:
  - Detección de onsets: 0.35
  - Detección de frames activos: 0.40

**Pipeline de procesamiento:**
1. Carga y normalización de audio
2. Filtro paso bajo (6000 Hz)
3. Extracción de espectrograma mel
4. Cálculo de deltas (velocidad y aceleración)
5. Normalización de características
6. Inferencia con ventanas deslizantes
7. Decodificación a MIDI
8. Generación de partitura PDF

## 🐳 Despliegue en Producción

### Docker Compose

El archivo `docker-compose.yml` incluye:
- Configuración de puertos (8000:8000)
- Volúmenes para el modelo y archivos temporales
- Health checks
- Variables de entorno
- Política de reinicio automático

### Azure Container Apps

Información de despliegue en `deployment-info.txt`:
- Grupo de recursos: `pianotranscription-rg`
- Región: `centralus`
- Container Registry: `ptacr635892`
- App: `pt-api`

**Comandos útiles:**
```powershell
# Ver logs en tiempo real
az containerapp logs show --name pt-api --resource-group pianotranscription-rg --follow

# Reiniciar aplicación
az containerapp revision restart --name pt-api --resource-group pianotranscription-rg

# Eliminar recursos
az group delete --name pianotranscription-rg --yes
```

## 👥 Equipo de Desarrollo

**Trabajo Terminal | ESCOM-IPN**

### Desarrolladores
- **Salazar Carreón Jeshua Jonathan** (2021630656)
- **Torres Abonce Luis Miguel** (2021630738)

### Directores
- **M. en C. César Mújica Ascencio**
- **Tania Rodríguez Sarabia**

## 📄 Licencia

Todos los derechos reservados © 2025 ESCOM-IPN

## 🐛 Troubleshooting

### MuseScore genera warnings de Qt/QML
**Solución**: Es normal. MuseScore 4 genera warnings de Qt/QML que no afectan la generación de PDF. El sistema los filtra automáticamente.

### Error: Modelo no encontrado
**Solución**: Verifica que el archivo `modelo.keras` esté en la ruta `BackEnd/modelos/`. Confirma la variable `MODEL_PATH` en la configuración.

### Error: CUDA out of memory
**Solución**: El sistema usa chunking por defecto (10,000 frames). Si persiste, reduce `CHUNK_SIZE_FRAMES` en `services/transcription.py`.

### Frontend no se conecta al backend
**Solución**: 
1. Verifica que el backend esté corriendo en puerto 8000
2. Confirma que `NEXT_PUBLIC_API_URL` en `.env.local` apunte a `http://localhost:8000/api/v1`
3. Revisa la configuración de CORS en `main.py`

### Error: xvfb-run no encontrado (Linux/Docker)
**Solución**: El sistema usa modo offscreen como fallback. Si necesitas xvfb:
```bash
apt-get update && apt-get install -y xvfb
```

### Archivos temporales no se eliminan
**Solución**: El sistema incluye limpieza automática cada hora. Para limpieza manual, elimina archivos en `temp_uploads/` con más de 1 hora de antigüedad.

### Error al instalar dependencias de Python
**Solución**: 
```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias una por una si falla
pip install fastapi uvicorn python-multipart
pip install tensorflow keras
pip install librosa numpy scipy
pip install music21 pretty_midi
```

## 📚 Estructura Completa del Proyecto

```
TT1/
├── BackEnd/
│   ├── main.py                    # Aplicación FastAPI principal
│   ├── config.py                  # Configuración y settings
│   ├── schemas.py                 # Modelos Pydantic
│   ├── dependencies.py            # Dependencias FastAPI
│   ├── requeriment.txt            # Dependencias Python
│   ├── Dockerfile                 # Configuración Docker
│   ├── docker-compose.yml         # Orquestación de contenedores
│   ├── routers/
│   │   └── upload.py             # Endpoints de transcripción
│   ├── services/
│   │   ├── transcription.py      # Servicio de transcripción CNN-LSTM
│   │   └── sheet_music.py        # Generación de partituras PDF
│   ├── utils/
│   │   └── file_handling.py      # Manejo de archivos y limpieza
│   ├── modelos/
│   │   └── modelo.keras          # Modelo CNN-LSTM entrenado
│   └── temp_uploads/             # Archivos temporales
│
├── FrontEnd/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.js          # Página principal
│   │   │   ├── _app.js           # Configuración de la app
│   │   │   └── _document.js      # Documento HTML customizado
│   │   ├── components/
│   │   │   ├── PianoTranscription.js  # Componente principal
│   │   │   └── FloatingNotes.js       # Animación de notas
│   │   └── styles/
│   │       └── globals.css       # Estilos globales
│   ├── package.json               # Dependencias Node.js
│   ├── next.config.ts             # Configuración Next.js
│   ├── tailwind.config.ts         # Configuración Tailwind
│   ├── tsconfig.json              # Configuración TypeScript
│   └── eslint.config.mjs          # Configuración ESLint
│
├── deployment-info.txt            # Información de despliegue Azure
└── README.md                      # Este archivo
```

## 🔗 Enlaces Útiles

- **MuseScore**: https://musescore.org/es
- **TensorFlow**: https://tensorflow.org
- **FastAPI**: https://fastapi.tiangolo.com
- **Next.js**: https://nextjs.org
- **Librosa**: https://librosa.org
- **music21**: https://web.mit.edu/music21

## 📊 Estadísticas del Proyecto

- **Lenguajes**: Python, JavaScript/TypeScript
- **Frameworks**: FastAPI, Next.js, React
- **ML/AI**: TensorFlow, Keras
- **Líneas de código**: ~2000+ (Backend + Frontend)
- **Endpoints API**: 6
- **Componentes React**: 2
- **Servicios**: 2 (Transcripción + Generación de partituras)

---

**Desarrollado con ❤️ por estudiantes de ESCOM-IPN | 2025**
