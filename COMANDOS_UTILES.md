# ═══════════════════════════════════════════════════════════════════════
# 📝 COMANDOS RÁPIDOS - Piano Transcription Azure
# ═══════════════════════════════════════════════════════════════════════

## 📊 MONITOREO Y LOGS

### Ver logs del Container App (últimas 100 líneas)
```bash
az containerapp logs show \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --tail 100 \
  --follow false
```

### Ver logs en tiempo real (streaming)
```bash
az containerapp logs show \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --follow true
```

### Ver solo errores en los logs
```bash
az containerapp logs show \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --tail 200 \
  --follow false | grep -i "error\|exception\|failed"
```

### Ver logs de generación de PDF
```bash
az containerapp logs show \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --tail 200 \
  --follow false | grep -i "pdf\|musescore\|partitura"
```

### Ver estado de todos los recursos
```bash
az resource list \
  --resource-group pianotranscription-rg \
  --output table
```

### Ver estado del Container App
```bash
az containerapp show \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --query "{nombre:name, estado:properties.runningStatus, replicas:properties.template.scale, url:properties.configuration.ingress.fqdn}" \
  --output table
```

### Ver archivos temporales
```bash
curl -s https://pt-api.whitewater-3f1ca299.centralus.azurecontainerapps.io/api/v1/transcribe/cleanup-status | python3 -m json.tool
```

---

## ⚡ CONTROL DE RECURSOS (AHORRO DE CRÉDITOS)

### 🛑 APAGAR Container App (deja de gastar créditos)
```bash
# Deshabilitar ingress (acceso público)
az containerapp ingress disable \
  --name pt-api \
  --resource-group pianotranscription-rg

# Configurar scale a 0
az containerapp update \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --min-replicas 0
```
**💡 Esto detiene el Container App completamente. Solo pagas el Registry ($5/mes)**

### ✅ ENCENDER Container App (restaurar funcionamiento normal)
```bash
# Habilitar ingress
az containerapp ingress enable \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --type external \
  --target-port 8000 \
  --transport auto

# Configurar scale
az containerapp update \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --min-replicas 0 \
  --max-replicas 3
```
**💡 Reactiva el Container App con scale-to-zero (0-3 réplicas)**

### 🔄 Reiniciar Container App
```bash
# Obtener la revisión actual
LATEST_REVISION=$(az containerapp revision list \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --query "[0].name" \
  --output tsv)

# Reiniciar
az containerapp revision restart \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --revision $LATEST_REVISION
```

### 🔧 Reducir recursos del Container App (ahorra ~50% en costos)
```bash
az containerapp update \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --cpu 1.0 \
  --memory 2.0Gi
```

### 🔙 Restaurar recursos del Container App (rendimiento completo)
```bash
az containerapp update \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --cpu 2.0 \
  --memory 4.0Gi
```

---

## 📦 ACTUALIZAR CÓDIGO Y DESPLEGAR

### Paso 1: Construir nueva imagen
```bash
cd /Volumes/Luis/TT1/BackEnd
docker buildx build --platform linux/amd64 --load -t ptacr635892.azurecr.io/piano-transcription:latest .
```

### Paso 2: Subir imagen a Azure
```bash
docker push ptacr635892.azurecr.io/piano-transcription:latest
```

### Paso 3: Actualizar Container App
```bash
az containerapp update \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --image ptacr635892.azurecr.io/piano-transcription:latest
```

### Todo en un comando (build + push + update)
```bash
cd /Volumes/Luis/TT1/BackEnd && \
docker buildx build --platform linux/amd64 --load -t ptacr635892.azurecr.io/piano-transcription:latest . && \
docker push ptacr635892.azurecr.io/piano-transcription:latest && \
az containerapp update --name pt-api --resource-group pianotranscription-rg --image ptacr635892.azurecr.io/piano-transcription:latest
```

---

## 💰 MONITOREO DE COSTOS

### Ver resumen de costos estimados
```bash
cat COSTOS_AZURE.md
```

### Auditoría completa de recursos
```bash
bash check-all-resources.sh
```

### Ver uso del Container Registry
```bash
az acr show-usage \
  --name ptacr635892 \
  --resource-group pianotranscription-rg \
  --output table
```

### Ver imágenes en el Container Registry
```bash
az acr repository list \
  --name ptacr635892 \
  --output table
```

### Ver métricas de requests (últimas 24h)
```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
az monitor metrics list \
  --resource /subscriptions/$SUBSCRIPTION_ID/resourceGroups/pianotranscription-rg/providers/Microsoft.App/containerApps/pt-api \
  --metric "Requests" \
  --start-time $(date -v-1d -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --interval PT1H \
  --query "value[0].timeseries[0].data[].total" \
  --output tsv | awk '{s+=$1} END {print "Total requests últimas 24h:", s}'
```

---

## 🧪 TESTING Y DEBUGGING

### Probar el API (health check)
```bash
curl -s https://pt-api.whitewater-3f1ca299.centralus.azurecontainerapps.io/ | python3 -m json.tool
```

### Probar transcripción (necesitas un archivo WAV)
```bash
curl -X POST \
  -F "file=@tu_archivo.wav" \
  https://pt-api.whitewater-3f1ca299.centralus.azurecontainerapps.io/api/v1/transcribe/
```

### Ver revisiones del Container App
```bash
az containerapp revision list \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --output table
```

---

## 🗑️ LIMPIEZA Y MANTENIMIENTO

### Limpiar imágenes antiguas del registro (libera espacio)
```bash
# Ver todas las imágenes
az acr repository show-tags \
  --name ptacr635892 \
  --repository piano-transcription \
  --output table

# Eliminar una imagen específica (opcional)
# az acr repository delete \
#   --name ptacr635892 \
#   --image piano-transcription:tag_viejo \
#   --yes
```

### Ver grupos de recursos
```bash
az group list --output table
```

### Eliminar un grupo de recursos (¡CUIDADO! Esto elimina TODO)
```bash
# NO EJECUTAR A MENOS QUE QUIERAS ELIMINAR TODO EL PROYECTO
# az group delete --name pianotranscription-rg --yes --no-wait
```

---

## 📋 SCRIPT INTERACTIVO

Para un menú interactivo con todas estas opciones, ejecuta:
```bash
bash gestionar-recursos.sh
```

---

## 💡 TIPS IMPORTANTES

### 🛑 Cuando NO uses el proyecto (ahorrar créditos):
1. Apaga el Container App: `az containerapp update --name pt-api --resource-group pianotranscription-rg --min-replicas 0 --max-replicas 0`
2. Solo pagarás el Registry: $5/mes
3. Total ahorro: ~$20-25/mes

### ✅ Cuando USES el proyecto:
1. Enciende el Container App: `az containerapp update --name pt-api --resource-group pianotranscription-rg --min-replicas 0 --max-replicas 3`
2. El scale-to-zero se encargará de optimizar costos automáticamente

### 📊 Monitoreo regular:
```bash
# Ejecutar semanalmente
bash check-all-resources.sh
```

### 🔄 Actualizaciones de código:
```bash
# Después de hacer cambios en el código
cd /Volumes/Luis/TT1/BackEnd
docker buildx build --platform linux/amd64 --load -t ptacr635892.azurecr.io/piano-transcription:latest .
docker push ptacr635892.azurecr.io/piano-transcription:latest
az containerapp update --name pt-api --resource-group pianotranscription-rg --image ptacr635892.azurecr.io/piano-transcription:latest
```

---

## 🆘 TROUBLESHOOTING

### Si el Container App no responde:
```bash
# 1. Ver logs
az containerapp logs show --name pt-api --resource-group pianotranscription-rg --tail 50 --follow false

# 2. Reiniciar
LATEST_REVISION=$(az containerapp revision list --name pt-api --resource-group pianotranscription-rg --query "[0].name" --output tsv)
az containerapp revision restart --name pt-api --resource-group pianotranscription-rg --revision $LATEST_REVISION

# 3. Verificar estado
az containerapp show --name pt-api --resource-group pianotranscription-rg --query "properties.runningStatus"
```

### Si Docker falla:
```bash
# Reiniciar Docker Desktop
pkill -9 -f Docker && open -a Docker

# Esperar 30 segundos y verificar
docker ps
```

### Si Azure CLI da errores:
```bash
# Re-login
az logout
az login
```

---

**Última actualización:** 8 de noviembre de 2025
