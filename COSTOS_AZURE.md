# 💰 Análisis de Costos - Piano Transcription en Azure

**Fecha:** 8 de noviembre de 2025  
**Grupos de Recursos:** `pianotranscription-rg` + `TrabajoTerminal`  
**Región:** Central US

---

## 🔍 Resumen Ejecutivo

Se encontraron **4 grupos de recursos** en total:
- ✅ **pianotranscription-rg** - 4 recursos activos (Backend)
- ✅ **TrabajoTerminal** - 1 recurso activo (Frontend)
- ⚠️ **DefaultResourceGroup-EUS** - Vacío (puede eliminarse)
- ⚠️ **DefaultResourceGroup-MXC** - Vacío (puede eliminarse)

**Costo Total Estimado:** $16-52 USD/mes (realista: $20-30 USD/mes)

---

## 📊 Recursos Activos

### GRUPO: pianotranscription-rg (Backend)

### 1. **Azure Container Registry (ACR)** - `ptacr635892`
- **Tipo:** Container Registry
- **SKU:** Basic
- **Ubicación:** Central US
- **Uso actual:** 5.28 GB / 10 GB (53% usado)
- **Imágenes almacenadas:** piano-transcription:latest

**💵 Costo Mensual:** ~$5.00 USD/mes
- Tarifa fija para SKU Basic
- Incluye 10 GB de almacenamiento

---

### 2. **Azure Container App** - `pt-api`
- **Tipo:** Container App (Consumption Plan)
- **Recursos asignados:**
  - CPU: 2.0 vCPU
  - RAM: 4 GB
  - Almacenamiento efímero: 8 GB
- **Escalado:**
  - Mínimo: 0 réplicas (scale-to-zero habilitado ✅)
  - Máximo: 3 réplicas
- **Estado:** Running

**💵 Costo Mensual (Estimado):**

#### Escenario Conservador (Bajo uso):
- **Tiempo activo:** ~50 horas/mes (uso ocasional con scale-to-zero)
- **CPU:** 2 vCPU × 50 hrs × $0.000024/vCPU/seg = ~$8.64 USD
- **Memoria:** 4 GB × 50 hrs × $0.000003/GB/seg = ~$2.16 USD
- **Requests:** ~1000 requests × $0.40/millón = ~$0.40 USD
- **Subtotal:** ~$11.20 USD/mes

#### Escenario Moderado (Uso normal):
- **Tiempo activo:** ~100 horas/mes (uso regular de estudiantes)
- **CPU:** 2 vCPU × 100 hrs × $0.000024/vCPU/seg = ~$17.28 USD
- **Memoria:** 4 GB × 100 hrs × $0.000003/GB/seg = ~$4.32 USD
- **Requests:** ~5000 requests × $0.40/millón = ~$2.00 USD
- **Subtotal:** ~$23.60 USD/mes

#### Escenario Alto (Uso intensivo):
- **Tiempo activo:** ~200 horas/mes (uso continuo para demos/pruebas)
- **CPU:** 2 vCPU × 200 hrs × $0.000024/vCPU/seg = ~$34.56 USD
- **Memoria:** 4 GB × 200 hrs × $0.000003/GB/seg = ~$8.64 USD
- **Requests:** ~10000 requests × $0.40/millón = ~$4.00 USD
- **Subtotal:** ~$47.20 USD/mes

---

### 3. **Log Analytics Workspace** - `workspace-pianotranscriptionrgncHV`
- **Tipo:** Log Analytics
- **SKU:** Pay-as-you-go (PerGB2018)
- **Retención:** 30 días
- **Ubicación:** Central US

**💵 Costo Mensual (Estimado):**
- **Ingesta de datos:** ~1-2 GB/mes (logs de aplicación)
- **Tarifa:** $2.76 USD/GB
- **Primeros 5 GB/mes:** GRATIS ✅
- **Subtotal:** ~$0.00 USD/mes (dentro del tier gratuito)

---

### 4. **Container Apps Environment** - `pt-env`
- **Tipo:** Managed Environment
- **Ubicación:** Central US
- **Estado:** Succeeded

**💵 Costo Mensual:**
- **Sin cargo adicional** - Ya incluido en el costo del Container App

---

### GRUPO: TrabajoTerminal (Frontend)

### 5. **Azure Static Web App** - `TT1-FrontEnd`
- **Tipo:** Static Web App
- **SKU:** Free
- **Ubicación:** Central US
- **URL:** https://witty-beach-0a0c32810.3.azurestaticapps.net
- **Repositorio:** https://github.com/TorresAbonceLuis/TT1
- **Estado:** Succeeded

**💵 Costo Mensual:**
- **GRATIS** ✅ - Tier gratuito incluye:
  - 100 GB de ancho de banda/mes
  - SSL gratis
  - Dominios personalizados
  - Despliegue automático desde GitHub

---

### GRUPOS VACÍOS (Sin costo pero pueden eliminarse)

### 6. **DefaultResourceGroup-EUS**
- **Ubicación:** East US
- **Recursos:** 0 (vacío)
- **Nota:** Creado automáticamente por Azure, puede eliminarse

### 7. **DefaultResourceGroup-MXC**
- **Ubicación:** Mexico Central
- **Recursos:** 0 (vacío)
- **Nota:** Creado automáticamente por Azure, puede eliminarse

---

## 💰 RESUMEN DE COSTOS TOTALES

| Recurso | Grupo | Escenario Bajo | Escenario Normal | Escenario Alto |
|---------|-------|----------------|------------------|----------------|
| Container Registry | pianotranscription-rg | $5.00 | $5.00 | $5.00 |
| Container App | pianotranscription-rg | $11.20 | $23.60 | $47.20 |
| Log Analytics | pianotranscription-rg | $0.00 | $0.00 | $0.00 |
| Static Web App | TrabajoTerminal | $0.00 ✅ | $0.00 ✅ | $0.00 ✅ |
| **TOTAL MENSUAL** | | **~$16.20 USD** | **~$28.60 USD** | **~$52.20 USD** |

### Notas:
- **Escenario Bajo:** 50 horas activo/mes (uso ocasional)
- **Escenario Normal:** 100 horas activo/mes (uso regular de estudiantes)
- **Escenario Alto:** 200 horas activo/mes (demos y pruebas continuas)

---

## 🎯 Costo Actual Proyectado

Basándose en que es un proyecto académico con uso intermitente:

### **Estimación Realista: $20-30 USD/mes**

---

## 💡 Recomendaciones para Optimizar Costos

### ✅ Ya Implementadas:
1. **Scale-to-zero habilitado** - El Container App se detiene cuando no hay tráfico
2. **Container Registry Basic SKU** - La opción más económica
3. **Limpieza automática de archivos** - Evita uso excesivo de almacenamiento
4. **Log Analytics tier gratuito** - Primeros 5 GB gratis

### 🔧 Optimizaciones Adicionales:

#### 1. Eliminar grupos de recursos vacíos (recomendado):
```bash
# Eliminar grupos vacíos que no generan costo pero mantienen orden
az group delete --name DefaultResourceGroup-EUS --yes --no-wait
az group delete --name DefaultResourceGroup-MXC --yes --no-wait
```
**Ahorro:** $0.00 (no generan costo, pero mejora organización)

#### 2. Reducir recursos del Container App (si es aceptable el rendimiento):
```bash
az containerapp update \
  --name pt-api \
  --resource-group pianotranscription-rg \
  --cpu 1.0 \
  --memory 2.0Gi
```
**Ahorro potencial:** ~50% en costos de compute

#### 2. Reducir retención de logs (si no necesitas 30 días):
```bash
az monitor log-analytics workspace update \
  --workspace-name workspace-pianotranscriptionrgncHV \
  --resource-group pianotranscription-rg \
  --retention-time 7
```
**Ahorro potencial:** Mínimo, pero reduce riesgo de exceder tier gratuito

#### 3. Configurar alertas de costo:
- Configurar alertas cuando el gasto mensual supere $30 USD
- Revisar métricas de uso semanalmente

#### 4. Considerar apagar recursos fuera de horario de uso:
Si solo usas la app durante horario de clases/demos:
```bash
# Detener Container App
az containerapp update --name pt-api --resource-group pianotranscription-rg --min-replicas 0 --max-replicas 0

# Reiniciar cuando sea necesario
az containerapp update --name pt-api --resource-group pianotranscription-rg --min-replicas 0 --max-replicas 3
```

---

## 📈 Monitoreo de Costos en Tiempo Real

### Ver costos acumulados del mes actual:
```bash
az consumption usage list \
  --resource-group pianotranscription-rg \
  --start-date $(date -v-30d +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  --query "[].{Service:meterName, Cost:pretaxCost, Unit:unit}" \
  --output table
```

### Verificar uso de recursos:
```bash
# Ver métricas del Container App
az monitor metrics list \
  --resource /subscriptions/c1f40849-db79-43f1-9817-4401f9c1ad8a/resourceGroups/pianotranscription-rg/providers/Microsoft.App/containerApps/pt-api \
  --metric "Requests" \
  --start-time $(date -v-7d -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --interval PT1H
```

---

## 🎓 Nota para Azure for Students

Con tu suscripción de **Azure for Students**, tienes:
- ✅ $100 USD en créditos
- ✅ Servicios gratuitos limitados
- ⚠️ Los créditos expiran después de 12 meses

**Tu proyecto actual usaría aproximadamente $20-30 USD/mes**, lo que significa que los $100 de crédito te durarían **~3-4 meses** con uso normal.

---

## 🚨 Alertas Importantes

1. **Scale-to-zero es CRÍTICO**: Sin esto, el Container App corre 24/7 y el costo sería ~$350-400 USD/mes
2. **Limpieza de archivos**: Ya implementada, evita llenar el almacenamiento
3. **Monitorear uso mensual**: Revisar cada semana para evitar sorpresas

---

**Última actualización:** 8 de noviembre de 2025
