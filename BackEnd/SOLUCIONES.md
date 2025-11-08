
# 🔧 Problemas Solucionados Durante el Despliegue

## Problemas Encontrados y Soluciones

### 1. ❌ Región no permitida (eastus)
**Error:** `RequestDisallowedByAzure` - eastus no disponible para Azure for Students

**Solución:** ✅ Cambiamos a `centralus` que es compatible con suscripciones de estudiantes

---

### 2. ❌ Grupo de recursos ya existía
**Error:** `InvalidResourceGroupLocation` - El grupo ya existía en eastus

**Solución:** ✅ Eliminamos el grupo anterior con:
```bash
az group delete --name pianotranscription-rg --yes --no-wait
```

---

### 3. ❌ Proveedores no registrados
**Error:** `MissingSubscriptionRegistration` - Namespace 'Microsoft.ContainerRegistry' no registrado

**Solución:** ✅ Registramos los proveedores necesarios:
```bash
az provider register --namespace Microsoft.ContainerRegistry --wait
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
```

---

## ✅ Estado Actual

El script `deploy-student.sh` está corriendo correctamente.

### Pasos del Despliegue (en progreso):

1. ✅ Login a Azure
2. ⏳ Esperando tu input para región y confirmación
3. ⏸️ Crear grupo de recursos
4. ⏸️ Crear Container Registry (~3 min)
5. ⏸️ Build imagen Docker (~5-7 min)
6. ⏸️ Push imagen a Azure (~2-3 min)
7. ⏸️ Crear Storage y subir modelo (~1 min)
8. ⏸️ Desplegar Container App (~2-3 min)

**Tiempo estimado total:** 12-17 minutos

---

## 📝 Inputs Requeridos

Cuando el script te pregunte:

1. **Región:**
   ```
   Selecciona (1-3, Enter para Central US): 
   ```
   → Presiona `Enter` o escribe `1`

2. **Confirmar:**
   ```
   ¿Continuar? (s/n): 
   ```
   → Escribe `s` y presiona `Enter`

3. **URL del Frontend:**
   ```
   URL del frontend (Enter para localhost): 
   ```
   → Presiona `Enter` (usaremos localhost por ahora)

---

## 🎯 Próximos Pasos (Después del Despliegue)

1. **Obtener URL de la API** - El script te mostrará la URL
2. **Probar la API** - Hacer un curl a la URL
3. **Actualizar Frontend** - Configurar la URL en Next.js
4. **Desplegar Frontend** - Subir a Vercel con la nueva API URL

---

## 💰 Costos Estimados

Con Azure for Students:
- **Crédito inicial:** $100 USD gratis
- **Costo mensual estimado:** $45-65 USD
- **Duración del crédito:** ~1.5-2 meses

Para reducir costos:
- Scale-to-zero está habilitado (0 réplicas cuando no hay tráfico)
- Puedes detener la app cuando no la uses
- Eliminar recursos cuando no los necesites

---

## 🗑️ Cómo Eliminar Todo

Si necesitas empezar de nuevo o eliminar recursos:

```bash
az group delete --name pianotranscription-rg --yes
```

Esto eliminará:
- Container App
- Container Registry + Imagen Docker
- Storage Account + Modelo
- Container Environment
- Todos los recursos relacionados

---

## 📞 Comandos Útiles

### Ver estado del despliegue
```bash
az group deployment list --resource-group pianotranscription-rg
```

### Ver recursos creados
```bash
az resource list --resource-group pianotranscription-rg --output table
```

### Ver logs de la app
```bash
az containerapp logs show --name pt-api --resource-group pianotranscription-rg --follow
```

### Reiniciar la app
```bash
az containerapp revision restart --name pt-api --resource-group pianotranscription-rg
```

---

**Creado:** 8 de noviembre de 2025
**Última actualización:** Durante el despliegue
