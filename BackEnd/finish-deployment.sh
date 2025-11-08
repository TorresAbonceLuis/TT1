#!/bin/bash

# Script para finalizar el despliegue sin Storage
# Como Azure CLI tiene problemas, desplegamos sin el modelo montado
# El modelo puede agregarse después manualmente

echo "🎹 Finalizando despliegue de Piano Transcription"
echo "==============================================="
echo ""

# Variables
RESOURCE_GROUP="pianotranscription-rg"
LOCATION="centralus"
ACR_NAME="ptacr635892"  # El último registry que creamos
CONTAINER_APP_ENV="pt-env"
CONTAINER_APP="pt-api"
IMAGE_NAME="${ACR_NAME}.azurecr.io/pianotranscription:latest"

# Obtener credenciales del ACR
echo "Obteniendo credenciales del registry..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

echo "✓ Credenciales obtenidas"
echo ""

# Crear Container Apps Environment
echo "Creando Container Apps Environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none

echo "✓ Environment creado"
echo ""

# Preguntar URL del frontend
read -p "URL del frontend (Enter para localhost): " FRONTEND_URL
if [ -z "$FRONTEND_URL" ]; then
    FRONTEND_URL="http://localhost:3000"
fi

# Desplegar Container App (sin storage mount por ahora)
echo "Desplegando Container App..."
az containerapp create \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image $IMAGE_NAME \
    --target-port 8000 \
    --ingress external \
    --registry-server ${ACR_NAME}.azurecr.io \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 2 --memory 4Gi \
    --min-replicas 0 --max-replicas 3 \
    --env-vars \
        ENV=production \
        FRONTEND_URL=$FRONTEND_URL \
        MODEL_PATH=modelos/modelo.keras \
        UPLOAD_FOLDER=/tmp/uploads \
    --output none

echo "✓ Container App desplegado"
echo ""

# Obtener URL
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

echo "=================================="
echo "✓ ¡DESPLIEGUE COMPLETADO!"
echo "=================================="
echo ""
echo "🌐 URL de tu API:"
echo "   https://${APP_URL}"
echo ""
echo "⚠️  NOTA: El modelo está incluido en la imagen Docker"
echo "   La app debería funcionar correctamente."
echo ""
echo "📝 Para ver logs:"
echo "   az containerapp logs show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "🗑️  Para eliminar todo:"
echo "   az group delete --name $RESOURCE_GROUP --yes"
echo ""

# Guardar info
cat > deployment-info.txt << EOF
Piano Transcription API - Azure Deployment
==========================================

Fecha: $(date)
Región: $LOCATION

Recursos:
- Grupo: $RESOURCE_GROUP
- Registry: $ACR_NAME
- App: $CONTAINER_APP

URL: https://${APP_URL}

El modelo está incluido en la imagen Docker (14MB).

Comandos útiles:
----------------
# Ver logs
az containerapp logs show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --follow

# Reiniciar
az containerapp revision restart --name $CONTAINER_APP --resource-group $RESOURCE_GROUP

# Eliminar
az group delete --name $RESOURCE_GROUP --yes
EOF

echo "✓ Info guardada en deployment-info.txt"
echo ""
