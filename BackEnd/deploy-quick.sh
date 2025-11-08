#!/bin/bash

# ========================================
# 🎹 Piano Transcription - Quick Deploy
# Versión Simplificada del Despliegue
# ========================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================="
echo "🎹 Piano Transcription - Azure Deploy"
echo "=================================="
echo ""

# Verificar prerequisitos
echo -e "${BLUE}Verificando prerequisitos...${NC}"

# 1. Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}✗ Azure CLI no instalado${NC}"
    echo "Instala con: brew install azure-cli"
    exit 1
fi
echo -e "${GREEN}✓ Azure CLI instalado${NC}"

# 2. Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker no está corriendo${NC}"
    echo "Por favor inicia Docker Desktop y vuelve a ejecutar este script"
    exit 1
fi
echo -e "${GREEN}✓ Docker corriendo${NC}"

# 3. Modelo
if [ ! -f "./modelos/modelo.keras" ]; then
    echo -e "${RED}✗ Modelo no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Modelo encontrado ($(du -h modelos/modelo.keras | cut -f1))${NC}"

echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Este proceso tomará 10-15 minutos${NC}"
echo ""

# Confirmar
read -p "¿Continuar con el despliegue? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "Despliegue cancelado"
    exit 1
fi

# Variables (genera nombres únicos)
TIMESTAMP=$(date +%s | tail -c 7)
PROJECT_NAME="pianotranscription"
RESOURCE_GROUP="${PROJECT_NAME}-rg"

# Preguntar por la región
echo ""
echo "🌎 Regiones recomendadas para Azure for Students:"
echo "  1. westus2       (West US 2)"
echo "  2. centralus     (Central US)"
echo "  3. westeurope    (West Europe)"
echo "  4. northeurope   (North Europe)"
echo "  5. southeastasia (Southeast Asia)"
echo ""
read -p "Elige una región (1-5, default: 1): " region_choice

case $region_choice in
    2) LOCATION="centralus" ;;
    3) LOCATION="westeurope" ;;
    4) LOCATION="northeurope" ;;
    5) LOCATION="southeastasia" ;;
    *) LOCATION="westus2" ;;
esac

ACR_NAME="${PROJECT_NAME}acr${TIMESTAMP}"
STORAGE_ACCOUNT="${PROJECT_NAME}st${TIMESTAMP}"
CONTAINER_APP_ENV="${PROJECT_NAME}-env"
CONTAINER_APP="${PROJECT_NAME}-api"

echo ""
echo "📊 Configuración:"
echo "  • Proyecto: $PROJECT_NAME"
echo "  • Región: $LOCATION"
echo "  • Grupo: $RESOURCE_GROUP"
echo ""

# LOGIN
echo -e "${BLUE}==> Iniciando sesión en Azure...${NC}"
az login --use-device-code

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo -e "${GREEN}✓ Suscripción: $SUBSCRIPTION_ID${NC}"

# GRUPO DE RECURSOS
echo -e "${BLUE}==> Creando grupo de recursos...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none
echo -e "${GREEN}✓ Grupo creado${NC}"

# CONTAINER REGISTRY
echo -e "${BLUE}==> Creando Container Registry (2-3 min)...${NC}"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output none
echo -e "${GREEN}✓ Registry creado${NC}"

# LOGIN A ACR
echo -e "${BLUE}==> Autenticando con Registry...${NC}"
az acr login --name $ACR_NAME
echo -e "${GREEN}✓ Autenticado${NC}"

# BUILD DOCKER
echo -e "${BLUE}==> Construyendo imagen Docker (5-7 min)...${NC}"
IMAGE_NAME="${ACR_NAME}.azurecr.io/${PROJECT_NAME}:latest"
docker build -t $IMAGE_NAME . --quiet
echo -e "${GREEN}✓ Imagen construida${NC}"

# PUSH DOCKER
echo -e "${BLUE}==> Subiendo imagen a Azure (2-3 min)...${NC}"
docker push $IMAGE_NAME --quiet
echo -e "${GREEN}✓ Imagen subida${NC}"

# STORAGE ACCOUNT
echo -e "${BLUE}==> Creando almacenamiento para modelo...${NC}"
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
echo -e "${BLUE}==> Subiendo modelo a Azure...${NC}"
az storage file upload \
    --share-name models \
    --source ./modelos/modelo.keras \
    --path modelo.keras \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    --output none
echo -e "${GREEN}✓ Modelo subido${NC}"

# CONTAINER APP ENVIRONMENT
echo -e "${BLUE}==> Creando ambiente de Container Apps...${NC}"
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none
echo -e "${GREEN}✓ Ambiente creado${NC}"

# CONFIGURAR STORAGE MOUNT
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
read -p "URL de tu frontend (Enter para localhost:3000): " FRONTEND_URL
if [ -z "$FRONTEND_URL" ]; then
    FRONTEND_URL="http://localhost:3000"
fi
echo ""

# OBTENER CREDENCIALES ACR
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# DESPLEGAR CONTAINER APP
echo -e "${BLUE}==> Desplegando Container App (2-3 min)...${NC}"
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

# RESUMEN FINAL
echo ""
echo "=================================="
echo -e "${GREEN}✓ ¡DESPLIEGUE COMPLETADO!${NC}"
echo "=================================="
echo ""
echo "🌐 URL de tu API:"
echo "   https://${APP_URL}"
echo ""
echo "📝 Endpoints:"
echo "   • Root:       https://${APP_URL}/"
echo "   • Transcribe: https://${APP_URL}/api/v1/transcribe/"
echo ""
echo "🔧 Comandos útiles:"
echo ""
echo "   # Ver logs:"
echo "   az containerapp logs show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "   # Reiniciar:"
echo "   az containerapp revision restart --name $CONTAINER_APP --resource-group $RESOURCE_GROUP"
echo ""
echo "   # Eliminar todo:"
echo "   az group delete --name $RESOURCE_GROUP --yes"
echo ""
echo "💰 Costo estimado: ~\$45-65/mes"
echo ""
echo -e "${YELLOW}⚠️  Actualiza tu frontend con la nueva URL de la API${NC}"
echo ""

# Guardar info
cat > deployment-info.txt << EOF
Piano Transcription API - Azure Deployment
==========================================

Fecha: $(date)

Recursos:
- Grupo: $RESOURCE_GROUP
- Registry: $ACR_NAME
- Storage: $STORAGE_ACCOUNT
- App: $CONTAINER_APP

URL: https://${APP_URL}

Ver logs:
az containerapp logs show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --follow

Eliminar:
az group delete --name $RESOURCE_GROUP --yes
EOF

echo -e "${GREEN}✓ Información guardada en: deployment-info.txt${NC}"
echo ""
