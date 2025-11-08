#!/bin/bash

# Script de despliegue automatizado para Azure Container Apps
# Autor: Luis Torres
# Proyecto: Piano Transcription API

set -e  # Detener en caso de error

# ========================
# CONFIGURACIÓN
# ========================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración (puedes modificarlas)
PROJECT_NAME="piano-transcription"
RESOURCE_GROUP="${PROJECT_NAME}-rg"
LOCATION="eastus"
CONTAINER_APP_ENV="${PROJECT_NAME}-env"
CONTAINER_APP="${PROJECT_NAME}-api"
ACR_NAME="${PROJECT_NAME}acr$(date +%s)"  # Agregar timestamp para nombre único
STORAGE_ACCOUNT="${PROJECT_NAME}storage$(date +%s | tail -c 7)"  # Max 24 chars

# Verificar que el modelo existe
MODEL_PATH="./modelos/modelo.keras"

# ========================
# FUNCIONES
# ========================

print_step() {
    echo -e "${BLUE}==> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_azure_cli() {
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI no está instalado"
        echo "Instálalo con: brew install azure-cli"
        exit 1
    fi
    print_success "Azure CLI instalado"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        echo "Instálalo desde: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    print_success "Docker instalado"
}

check_model() {
    if [ ! -f "$MODEL_PATH" ]; then
        print_error "No se encontró el modelo en: $MODEL_PATH"
        exit 1
    fi
    print_success "Modelo encontrado"
}

# ========================
# SCRIPT PRINCIPAL
# ========================

echo "=================================="
echo "🎹 Piano Transcription - Deploy Azure"
echo "=================================="
echo ""

# 1. Verificar prerequisitos
print_step "Verificando prerequisitos..."
check_azure_cli
check_docker
check_model

# 2. Login a Azure
print_step "Iniciando sesión en Azure..."
az login

# 3. Seleccionar suscripción
print_step "Seleccionando suscripción..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_success "Suscripción: $SUBSCRIPTION_ID"

# 4. Crear grupo de recursos
print_step "Creando grupo de recursos: $RESOURCE_GROUP"
if az group create --name $RESOURCE_GROUP --location $LOCATION; then
    print_success "Grupo de recursos creado"
else
    print_warning "El grupo de recursos ya existe o hubo un error"
fi

# 5. Crear Azure Container Registry
print_step "Creando Container Registry: $ACR_NAME"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

print_success "Container Registry creado"

# 6. Login a ACR
print_step "Autenticando con Container Registry..."
az acr login --name $ACR_NAME
print_success "Autenticado con ACR"

# 7. Build y push de la imagen Docker
print_step "Construyendo imagen Docker..."
IMAGE_NAME="${ACR_NAME}.azurecr.io/${PROJECT_NAME}:latest"
docker build -t $IMAGE_NAME .
print_success "Imagen construida"

print_step "Subiendo imagen a Azure Container Registry..."
docker push $IMAGE_NAME
print_success "Imagen subida"

# 8. Crear Storage Account para el modelo
print_step "Creando Storage Account: $STORAGE_ACCOUNT"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS

print_success "Storage Account creado"

# 9. Crear File Share para el modelo
print_step "Creando File Share para modelos..."
STORAGE_KEY=$(az storage account keys list \
    --account-name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query "[0].value" -o tsv)

az storage share create \
    --name models \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY

print_success "File Share creado"

# 10. Subir modelo a Azure Files
print_step "Subiendo modelo a Azure Files..."
az storage file upload \
    --share-name models \
    --source $MODEL_PATH \
    --path modelo.keras \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY

print_success "Modelo subido"

# 11. Crear Container Apps Environment
print_step "Creando Container Apps Environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

print_success "Environment creado"

# 12. Obtener credenciales de ACR
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# 13. Crear Storage Mount
print_step "Configurando storage mount..."
az containerapp env storage set \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --storage-name models \
    --azure-file-account-name $STORAGE_ACCOUNT \
    --azure-file-account-key $STORAGE_KEY \
    --azure-file-share-name models \
    --access-mode ReadOnly

print_success "Storage mount configurado"

# 14. Desplegar Container App
print_step "Desplegando Container App..."

# Pedir URL del frontend
read -p "Ingresa la URL de tu frontend (ej: https://tu-app.vercel.app): " FRONTEND_URL
if [ -z "$FRONTEND_URL" ]; then
    FRONTEND_URL="http://localhost:3000"
    print_warning "Usando URL por defecto: $FRONTEND_URL"
fi

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
        UPLOAD_FOLDER=/tmp/uploads

print_success "Container App desplegado"

# 15. Montar Azure Files en la app
print_step "Montando volumen de modelos..."
az containerapp update \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars AZURE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT

print_success "Volumen montado"

# 16. Obtener URL de la aplicación
print_step "Obteniendo URL de la aplicación..."
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

# ========================
# RESUMEN FINAL
# ========================

echo ""
echo "=================================="
echo -e "${GREEN}✓ DESPLIEGUE COMPLETADO${NC}"
echo "=================================="
echo ""
echo "📊 Información del despliegue:"
echo "  • Grupo de recursos: $RESOURCE_GROUP"
echo "  • Container Registry: $ACR_NAME"
echo "  • Storage Account: $STORAGE_ACCOUNT"
echo "  • Container App: $CONTAINER_APP"
echo ""
echo "🌐 URL de tu API:"
echo "  https://${APP_URL}"
echo ""
echo "📝 Endpoints disponibles:"
echo "  • Root: https://${APP_URL}/"
echo "  • Transcribe: https://${APP_URL}/api/v1/transcribe/"
echo "  • Status: https://${APP_URL}/api/v1/transcribe/status/{task_id}"
echo ""
echo "🔧 Comandos útiles:"
echo "  • Ver logs: az containerapp logs show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --follow"
echo "  • Restart: az containerapp revision restart --name $CONTAINER_APP --resource-group $RESOURCE_GROUP"
echo "  • Escalar: az containerapp update --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --min-replicas 1 --max-replicas 5"
echo ""
echo "💰 Costos estimados: ~\$45-65/mes"
echo ""
echo "⚠️  No olvides actualizar tu frontend con la nueva URL de la API!"
echo ""
