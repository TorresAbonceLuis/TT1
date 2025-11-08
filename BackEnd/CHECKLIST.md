# ✅ Checklist de Despliegue a Azure

## 📋 Prerequisitos

- [x] Azure CLI instalado ✓
- [ ] Docker Desktop iniciado ❌ **→ INICIA DOCKER DESKTOP AHORA**
- [x] Modelo keras en `modelos/modelo.keras` ✓
- [ ] Cuenta de Azure activa
- [ ] Tarjeta de crédito/débito registrada en Azure

## 🚀 Pasos para Desplegar

### 1. Iniciar Docker Desktop
```bash
# Abre Docker Desktop desde Launchpad o:
open -a Docker
```

**Espera a que Docker esté corriendo (ícono en la barra de menú)**

### 2. Verificar que todo esté listo
```bash
cd /Volumes/Luis/TT1/BackEnd

# Verificar Docker
docker info

# Verificar Azure CLI
az --version

# Verificar modelo
ls -lh modelos/modelo.keras
```

### 3. Ejecutar el despliegue
```bash
# Opción A: Script completo con toda la info
./deploy-azure.sh

# Opción B: Script rápido (recomendado)
./deploy-quick.sh
```

### 4. Durante el despliegue

El script te pedirá:

1. **Login en Azure**: Se abrirá tu navegador
   - Inicia sesión con tu cuenta de Microsoft/Azure
   - Selecciona tu suscripción

2. **URL del Frontend** (opcional):
   - Si tienes tu frontend en Vercel, ingresa la URL
   - Si aún no lo despliegas, deja vacío (usará localhost)

### 5. Tiempos estimados

| Paso | Tiempo |
|------|--------|
| Login y crear recursos | 2-3 min |
| Build imagen Docker | 5-7 min |
| Push a Azure Registry | 2-3 min |
| Subir modelo | 1 min |
| Desplegar Container App | 2-3 min |
| **TOTAL** | **12-17 min** |

## 📊 Después del Despliegue

### 1. Obtener la URL de tu API

El script te mostrará algo como:
```
🌐 URL de tu API:
   https://pianotranscription-api-XXXXX.eastus.azurecontainerapps.io
```

### 2. Probar la API

```bash
# Prueba básica
curl https://tu-url-de-azure.azurecontainerapps.io/

# Debería retornar:
{
  "message": "Piano Transcription API",
  "version": "1.0.0",
  "status": "running",
  ...
}
```

### 3. Actualizar el Frontend

En tu proyecto de Next.js:

```bash
cd /Volumes/Luis/TT1/FrontEnd

# Crear/editar .env.local
echo "NEXT_PUBLIC_API_URL=https://tu-url-de-azure.azurecontainerapps.io/api/v1" > .env.local
```

### 4. Actualizar CORS en Azure

Si olvidaste poner la URL del frontend:

```bash
az containerapp update \
  --name pianotranscription-api \
  --resource-group pianotranscription-rg \
  --set-env-vars FRONTEND_URL=https://tu-frontend.vercel.app
```

## 🔍 Monitoreo

### Ver logs en tiempo real
```bash
az containerapp logs show \
  --name pianotranscription-api \
  --resource-group pianotranscription-rg \
  --follow
```

### Ver estado de la app
```bash
az containerapp show \
  --name pianotranscription-api \
  --resource-group pianotranscription-rg \
  --query "properties.runningStatus"
```

### Reiniciar la app
```bash
az containerapp revision restart \
  --name pianotranscription-api \
  --resource-group pianotranscription-rg
```

## 💰 Costos

### Estimación mensual:
- **Container App** (2 vCPU, 4GB, scale-to-zero): $30-50
- **Azure Files** (10GB): $2
- **Container Registry** (Basic): $5
- **Bandwidth** (100GB): $8
- **TOTAL**: ~$45-65/mes

### Reducir costos:

1. **Scale to zero**: Ya configurado (0 réplicas mínimas)
2. **Reducir recursos** si no necesitas tanto:
```bash
az containerapp update \
  --name pianotranscription-api \
  --resource-group pianotranscription-rg \
  --cpu 1 --memory 2Gi
```

## 🐛 Troubleshooting

### Error: Docker no está corriendo
```bash
# Inicia Docker Desktop
open -a Docker

# Espera 30 segundos y verifica
docker info
```

### Error: No tienes suscripción de Azure
1. Ve a https://azure.microsoft.com/free/
2. Crea una cuenta gratuita ($200 de crédito)
3. Vuelve a ejecutar el script

### Error: Modelo no se encuentra
```bash
# Verifica la ruta
ls -lh /Volumes/Luis/TT1/BackEnd/modelos/modelo.keras
```

### Error: Timeout en el build
- Tu conexión a internet puede ser lenta
- El build puede tomar hasta 10 minutos la primera vez
- Paciencia 🙂

### Error: La app no responde
```bash
# Ver logs para diagnosticar
az containerapp logs show \
  --name pianotranscription-api \
  --resource-group pianotranscription-rg \
  --tail 100
```

## 🗑️ Eliminar Todo (si quieres empezar de nuevo)

```bash
az group delete --name pianotranscription-rg --yes --no-wait
```

Esto eliminará:
- ✓ Container App
- ✓ Container Registry
- ✓ Storage Account (incluyendo el modelo)
- ✓ Container Environment
- ✓ Todo lo relacionado

**⚠️ CUIDADO: Esta acción es irreversible**

## 📝 Próximos Pasos

Una vez desplegado:

1. [ ] Actualizar frontend con nueva URL
2. [ ] Probar endpoint de transcripción
3. [ ] Configurar dominio personalizado (opcional)
4. [ ] Configurar Application Insights (monitoreo)
5. [ ] Configurar CI/CD con GitHub Actions

## 🆘 ¿Necesitas Ayuda?

Comando para ver toda la info de tu despliegue:
```bash
cat deployment-info.txt
```

---

**¿Todo listo? ¡Ejecuta el script!**

```bash
cd /Volumes/Luis/TT1/BackEnd
./deploy-quick.sh
```
