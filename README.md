# 🎹 Audio a Notación

Convierte tus interpretaciones de piano en partituras musicales automáticamente usando inteligencia artificial.

## ✨ Características

- 🎵 **Transcripción automática** - Sube un audio de piano y obtén la partitura en segundos
- 🎼 **Generación de partituras** - Descarga tus transcripciones en formato PDF y MIDI
- 🎨 **Interfaz intuitiva** - Diseño moderno y fácil de usar
- ⚡ **Procesamiento rápido** - Modelo de deep learning optimizado

## 🚀 Tecnologías

**Backend:**
- FastAPI - API REST de alto rendimiento
- TensorFlow/Keras - Modelo de transcripción
- Docker - Contenedorización

**Frontend:**
- Next.js - Framework de React
- TailwindCSS - Diseño responsive
- Animaciones fluidas

## 📦 Instalación

### Opción 1: Con Docker (Recomendado)

```powershell
.\deploy.ps1
```

### Opción 2: Manual

**Backend:**
```powershell
cd BackEnd
pip install -r requeriment.txt
uvicorn main:app --reload
```

**Frontend:**
```powershell
cd FrontEnd
npm install
npm run dev
```

## 🎯 Uso

1. Accede a `http://localhost:3000`
2. Sube un archivo de audio (WAV, MP3)
3. Espera a que el modelo procese la transcripción
4. Descarga tu partitura en PDF o MIDI

## 📝 Estructura del Proyecto

```
TT1/
├── BackEnd/          # API FastAPI + modelo de IA
│   ├── routers/      # Endpoints de la API
│   ├── services/     # Lógica de transcripción
│   └── modelos/      # Modelo entrenado
└── FrontEnd/         # Interfaz Next.js
    └── src/
        ├── components/  # Componentes React
        └── pages/       # Páginas de la app
```

## 🧪 Testing

```powershell
.\test-backend-health.ps1
```

---

Hecho con 🎵 por el equipo TT1
