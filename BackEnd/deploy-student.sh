#!/bin/bash

# 🎹 Piano Transcription - Azure Deploy (Student Edition)
# Optimizado para Azure for Students

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================="
echo "🎹 Piano Transcription - Azure Deploy"
echo "    (Azure for Students Edition)"
echo "=================================="
echo ""

# Variables
TIMESTAMP=$(date +%s | tail -c 7)
PROJECT_NAME="pianotranscription"
RESOURCE_GROUP="${PROJECT_NAME}-rg"

# IMPORTANTE: Para Azure for Students
echo -e "${YELLOW}⚠️  NOTA: Azure for Students tiene restricciones de región${NC}"
echo ""
echo "Las regiones más compatibles son:"
echo "  1. centralus     (Central US) - Recomendado"
echo "  2. westus2       (West US 2)"
echo "  3. westeurope    (West Europe)"
echo ""
read -p "Selecciona (1-3, Enter para Central US): " choice

case $choice in
    2) LOCATION="westus2" ;;
    3) LOCATION="westeurope" ;;
    *) LOCATION="centralus" ;;
esac

echo ""
echo -e "${GREEN}✓ Región seleccionada: $LOCATION${NC}"

# Generar nombres únicos (más cortos para evitar problemas)
ACR_NAME="ptacr${TIMESTAMP}"
STORAGE_ACCOUNT="ptst${TIMESTAMP}"
CONTAINER_APP_ENV="pt-env"
CONTAINER_APP="pt-api"

echo ""
echo "📊 Configuración:"
echo "  • Proyecto: $PROJECT_NAME"
echo "  • Región: $LOCATION"
echo "  • Grupo: $RESOURCE_GROUP"
echo "  • Registry: $ACR_NAME"
echo ""

read -p "¿Continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    exit 1
fi

# LOGIN (ya deberías estar logueado)
SUBSCRIPTION_ID=$(az account show --query id -o tsv 2>/dev/null)
if [ -z "$SUBSCRIPTION_ID" ]; then
    echo -e "${BLUE}==> Iniciando sesión...${NC}"
    az login
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
fi
echo -e "${GREEN}✓ Suscripción: $SUBSCRIPTION_ID${NC}"

# GRUPO DE RECURSOS
echo -e "${BLUE}==> Creando grupo de recursos en $LOCATION...${NC}"
if az group create --name $RESOURCE_GROUP --location $LOCATION --output none; then
    echo -e "${GREEN}✓ Grupo creado${NC}"
else
    echo -e "${RED}✗ Error creando grupo de recursos${NC}"
    echo ""
    echo "Posibles soluciones:"
    echo "1. Prueba otra región ejecutando de nuevo el script"
    echo "2. Verifica tu suscripción en portal.azure.com"
    echo "3. Contacta a soporte de Azure"
    exit 1
fi

# CONTAINER REGISTRY
echo -e "${BLUE}==> Creando Container Registry: $ACR_NAME${NC}"
if az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --location $LOCATION \
    --admin-enabled true \
    --output none; then
    echo -e "${GREEN}✓ Registry creado${NC}"
else
    echo -e "${RED}✗ Error creando Container Registry${NC}"
    echo "Limpiando recursos..."
    az group delete --name $RESOURCE_GROUP --yes --no-wait
    exit 1
fi

# LOGIN A ACR
echo -e "${BLUE}==> Autenticando con Registry...${NC}"
az acr login --name $ACR_NAME
echo -e "${GREEN}✓ Autenticado${NC}"

# BUILD DOCKER
echo -e "${BLUE}==> Construyendo imagen Docker (esto puede tomar 5-7 min)...${NC}"
IMAGE_NAME="${ACR_NAME}.azurecr.io/${PROJECT_NAME}:latest"
if docker build -t $IMAGE_NAME .; then
    echo -e "${GREEN}✓ Imagen construida${NC}"
else
    echo -e "${RED}✗ Error en build${NC}"
    exit 1
fi

# PUSH DOCKER
echo -e "${BLUE}==> Subiendo imagen (2-3 min)...${NC}"
if docker push $IMAGE_NAME; then
    echo -e "${GREEN}✓ Imagen subida${NC}"
else
    echo -e "${RED}✗ Error subiendo imagen${NC}"
    exit 1
fi

# STORAGE ACCOUNT
echo -e "${BLUE}==> Creando Storage Account: $STORAGE_ACCOUNT${NC}"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --output none

STORAGE_KEY=$(az storage account keys list \
    --account-name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query "[0].value" -o tsv)

az storage share create \
    --name models \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    --output none

echo -e "${GREEN}✓ Storage creado${NC}"

# SUBIR MODELO
echo -e "${BLUE}==> Subiendo modelo...${NC}"
az storage file upload \
    --share-name models \
    --source ./modelos/modelo.keras \
    --path modelo.keras \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    --output none
echo -e "${GREEN}✓ Modelo subido${NC}"

# CONTAINER APP ENVIRONMENT
echo -e "${BLUE}==> Creando Container Apps Environment...${NC}"
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none
echo -e "${GREEN}✓ Environment creado${NC}"

# STORAGE MOUNT
echo -e "${BLUE}==> Configurando storage mount...${NC}"
az containerapp env storage set \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --storage-name models \
    --azure-file-account-name $STORAGE_ACCOUNT \
    --azure-file-account-key $STORAGE_KEY \
    --azure-file-share-name models \
    --access-mode ReadOnly \
    --output none
echo -e "${GREEN}✓ Storage configurado${NC}"

# FRONTEND URL
echo ""
read -p "URL del frontend (Enter para localhost): " FRONTEND_URL
if [ -z "$FRONTEND_URL" ]; then
    FRONTEND_URL="http://localhost:3000"
fi

# OBTENER CREDENCIALES ACR
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# DESPLEGAR CONTAINER APP
echo -e "${BLUE}==> Desplegando Container App...${NC}"
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
        MODEL_PATH=/models/modelo.keras \
        UPLOAD_FOLDER=/tmp/uploads \
    --output none

echo -e "${GREEN}✓ Container App desplegado${NC}"

# OBTENER URL
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

# RESUMEN
echo ""
echo "=================================="
echo -e "${GREEN}✓ ¡DESPLIEGUE COMPLETADO!${NC}"
echo "=================================="
echo ""
echo "🌐 URL de tu API:"
echo "   https://${APP_URL}"
echo ""
echo "📝 Endpoints:"
echo "   • Root: https://${APP_URL}/"
echo "   • API:  https://${APP_URL}/api/v1/transcribe/"
echo ""
echo "🔧 Comandos útiles:"
echo ""
echo "# Ver logs:"
echo "az containerapp logs show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "# Eliminar todo:"
echo "az group delete --name $RESOURCE_GROUP --yes"
echo ""

# Guardar info
cat > deployment-info.txt << EOF
Piano Transcription API - Deployment Info
==========================================

Fecha: $(date)
Región: $LOCATION

Recursos:
- Grupo: $RESOURCE_GROUP
- Registry: $ACR_NAME
- Storage: $STORAGE_ACCOUNT
- App: $CONTAINER_APP

URL: https://${APP_URL}

Comandos:
---------
# Logs
az containerapp logs show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --follow

# Reiniciar
az containerapp revision restart --name $CONTAINER_APP --resource-group $RESOURCE_GROUP

# Eliminar todo
az group delete --name $RESOURCE_GROUP --yes
EOF

echo -e "${GREEN}✓ Info guardada en deployment-info.txt${NC}"
echo ""
