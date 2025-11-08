# 🚀 Despliegue en Azure Container Apps

Guía completa para desplegar el backend de Piano Transcription API en Azure Container Apps.

## 📋 Prerequisitos

### 1. Instalar Herramientas

```bash
# Instalar Azure CLI (macOS)
brew install azure-cli

# Instalar Docker Desktop
# Descarga desde: https://www.docker.com/products/docker-desktop

# Verificar instalaciones
az --version
docker --version
```

### 2. Preparar el Modelo

Asegúrate de que tu modelo `modelo.keras` esté en la carpeta `modelos/`:

```bash
ls -lh modelos/modelo.keras
```

## 🎯 Opción 1: Despliegue Automático (Recomendado)

### Ejecutar el Script

```bash
cd /Volumes/Luis/TT1/BackEnd

# Dar permisos de ejecución
chmod +x deploy-azure.sh

# Ejecutar el despliegue
./deploy-azure.sh
```

El script hará TODO automáticamente:
- ✅ Login en Azure
- ✅ Crear recursos necesarios
- ✅ Construir y subir imagen Docker
- ✅ Subir modelo a Azure Files
- ✅ Desplegar Container App
- ✅ Configurar escalado automático

**Tiempo estimado**: 10-15 minutos

## 🛠️ Opción 2: Despliegue Manual (Paso a Paso)

### Paso 1: Login y Configuración Inicial

```bash
# Login en Azure
az login

# Ver suscripciones disponibles
az account list --output table

# Seleccionar suscripción (si tienes varias)
az account set --subscription "TU_SUBSCRIPTION_ID"

# Variables de configuración
RESOURCE_GROUP="piano-transcription-rg"
LOCATION="eastus"
CONTAINER_APP_ENV="piano-transcription-env"
CONTAINER_APP="piano-transcription-api"
ACR_NAME="pianotranscriptionacr$(date +%s)"
STORAGE_ACCOUNT="pianostorage$(date +%s | tail -c 7)"
```

### Paso 2: Crear Grupo de Recursos

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Paso 3: Crear Container Registry

```bash
# Crear ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Login a ACR
az acr login --name $ACR_NAME
```

### Paso 4: Construir y Subir Imagen Docker

```bash
cd /Volumes/Luis/TT1/BackEnd

# Build de la imagen
IMAGE_NAME="${ACR_NAME}.azurecr.io/piano-transcription:latest"
docker build -t $IMAGE_NAME .

# Push a ACR
docker push $IMAGE_NAME
```

### Paso 5: Crear Storage para el Modelo

```bash
# Crear Storage Account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Obtener access key
STORAGE_KEY=$(az storage account keys list \
  --account-name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query "[0].value" -o tsv)

# Crear File Share
az storage share create \
  --name models \
  --account-name $STORAGE_ACCOUNT \
  --account-key $STORAGE_KEY

# Subir modelo
az storage file upload \
  --share-name models \
  --source ./modelos/modelo.keras \
  --path modelo.keras \
  --account-name $STORAGE_ACCOUNT \
  --account-key $STORAGE_KEY
```

### Paso 6: Crear Container Apps Environment

```bash
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Configurar storage mount
az containerapp env storage set \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --storage-name models \
  --azure-file-account-name $STORAGE_ACCOUNT \
  --azure-file-account-key $STORAGE_KEY \
  --azure-file-share-name models \
  --access-mode ReadOnly
```

### Paso 7: Desplegar Container App

```bash
# Obtener credenciales de ACR
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Crear Container App
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
      FRONTEND_URL=https://tu-frontend.vercel.app \
      MODEL_PATH=/models/modelo.keras \
      UPLOAD_FOLDER=/tmp/uploads
```

### Paso 8: Obtener URL de la API

```bash
# Ver URL
az containerapp show \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv
```

## 🧪 Testing Local con Docker

Antes de desplegar a Azure, prueba localmente:

```bash
# Construir imagen
docker build -t piano-transcription-local .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -v $(pwd)/modelos:/app/modelos \
  -v $(pwd)/temp_uploads:/app/temp_uploads \
  -e ENV=development \
  -e FRONTEND_URL=http://localhost:3000 \
  piano-transcription-local

# O usar docker-compose
docker-compose up
```

Visita: http://localhost:8000

## 📊 Comandos de Administración

### Ver Logs en Tiempo Real

```bash
az containerapp logs show \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --follow
```

### Reiniciar la Aplicación

```bash
az containerapp revision restart \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg
```

### Actualizar Variables de Entorno

```bash
az containerapp update \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --set-env-vars FRONTEND_URL=https://nueva-url.vercel.app
```

### Escalar la Aplicación

```bash
# Escalar manualmente
az containerapp update \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --min-replicas 1 \
  --max-replicas 5 \
  --cpu 2 --memory 4Gi
```

### Ver Métricas

```bash
az containerapp show \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --query "properties.{URL:configuration.ingress.fqdn,Replicas:template.scale,CPU:template.containers[0].resources.cpu,Memory:template.containers[0].resources.memory}"
```

### Actualizar Imagen Docker

```bash
# Build nueva versión
docker build -t ${ACR_NAME}.azurecr.io/piano-transcription:v2 .
docker push ${ACR_NAME}.azurecr.io/piano-transcription:v2

# Actualizar Container App
az containerapp update \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --image ${ACR_NAME}.azurecr.io/piano-transcription:v2
```

## 🔐 Configurar CORS en el Frontend

Una vez desplegado, actualiza tu frontend con la URL de la API:

```typescript
// En tu archivo .env.local del frontend
NEXT_PUBLIC_API_URL=https://piano-transcription-api.XXXXXX.eastus.azurecontainerapps.io/api/v1
```

## 💰 Costos Estimados

| Recurso | Especificación | Costo Mensual |
|---------|---------------|---------------|
| Container App | 2 vCPU, 4GB RAM, scale-to-zero | $30-50 |
| Azure Files | 10GB | $2 |
| Container Registry | Basic | $5 |
| Bandwidth | 100GB salida | $8 |
| **TOTAL** | | **~$45-65/mes** |

## 🛡️ Mejores Prácticas

### 1. Configurar Custom Domain (Opcional)

```bash
# Agregar dominio personalizado
az containerapp hostname add \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --hostname api.tudominio.com
```

### 2. Configurar Application Insights (Monitoreo)

```bash
# Crear Application Insights
az monitor app-insights component create \
  --app piano-transcription-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP

# Obtener instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app piano-transcription-insights \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)

# Agregar a Container App
az containerapp update \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --set-env-vars APPLICATIONINSIGHTS_CONNECTION_STRING=$INSTRUMENTATION_KEY
```

### 3. Configurar Backups del Modelo

```bash
# Habilitar backups automáticos de Azure Files
az backup vault create \
  --name piano-backup-vault \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

## 🐛 Troubleshooting

### El contenedor no inicia

```bash
# Ver logs detallados
az containerapp logs show \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --tail 100

# Verificar estado
az containerapp show \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --query "properties.runningStatus"
```

### Error de memoria

```bash
# Aumentar memoria
az containerapp update \
  --name piano-transcription-api \
  --resource-group piano-transcription-rg \
  --cpu 4 --memory 8Gi
```

### Modelo no se encuentra

```bash
# Verificar que el archivo existe en Azure Files
az storage file list \
  --share-name models \
  --account-name $STORAGE_ACCOUNT \
  --account-key $STORAGE_KEY
```

## 🗑️ Limpiar Recursos (Eliminar Todo)

```bash
# CUIDADO: Esto elimina TODOS los recursos
az group delete --name piano-transcription-rg --yes --no-wait
```

## 📚 Recursos Adicionales

- [Azure Container Apps Docs](https://learn.microsoft.com/azure/container-apps/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Azure CLI Reference](https://learn.microsoft.com/cli/azure/)

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs con `az containerapp logs show`
2. Verifica que el modelo esté en Azure Files
3. Confirma que las variables de entorno sean correctas
4. Asegúrate de que el CORS esté configurado con la URL del frontend

---

**✨ ¡Listo para producción!**
