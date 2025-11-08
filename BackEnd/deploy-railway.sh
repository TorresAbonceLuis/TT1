#!/bin/bash

# Despliegue rápido a Railway
# Mucho más simple que Azure

echo "🚂 Piano Transcription - Railway Deploy"
echo "========================================"
echo ""

# Verificar que Railway CLI esté instalado
if ! command -v railway &> /dev/null; then
    echo "📦 Instalando Railway CLI..."
    npm i -g @railway/cli
fi

echo "✓ Railway CLI listo"
echo ""

# Login
echo "🔐 Iniciando sesión en Railway..."
railway login

# Crear proyecto
echo "📁 Creando proyecto..."
railway init

# Configurar variables de entorno
echo "⚙️  Configurando variables..."
railway variables set PORT=8000
railway variables set ENV=production

# Desplegar
echo "🚀 Desplegando..."
railway up

# Obtener URL
URL=$(railway domain)

echo ""
echo "=================================="
echo "✓ ¡DESPLEGADO!"
echo "=================================="
echo ""
echo "🌐 URL: $URL"
echo ""
