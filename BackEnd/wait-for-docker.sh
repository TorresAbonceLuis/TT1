#!/bin/bash

# Script para verificar que Docker esté listo

echo "🐳 Esperando a que Docker esté listo..."
echo ""

for i in {1..30}; do
    if docker info > /dev/null 2>&1; then
        echo "✅ Docker está listo!"
        echo ""
        echo "Ahora puedes ejecutar el despliegue:"
        echo "  cd /Volumes/Luis/TT1/BackEnd"
        echo "  ./deploy-quick.sh"
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "❌ Docker tardó mucho en iniciar"
echo "Por favor verifica que Docker Desktop esté corriendo"
