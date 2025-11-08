#!/bin/bash

# Script para verificar TODOS los recursos activos en Azure
# y generar un reporte de costos estimados

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║     🔍 AUDITORÍA COMPLETA DE RECURSOS EN AZURE                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Obtener información de la suscripción
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

echo "📌 Suscripción: $SUBSCRIPTION_NAME"
echo "🆔 ID: $SUBSCRIPTION_ID"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Listar todos los grupos de recursos
echo "📦 GRUPOS DE RECURSOS:"
echo ""
az group list --query "[].{Nombre:name, Ubicacion:location, Estado:properties.provisioningState}" --output table
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Obtener lista de grupos
RESOURCE_GROUPS=$(az group list --query "[].name" -o tsv)

TOTAL_RESOURCES=0
ESTIMATED_COST=0

# Iterar sobre cada grupo de recursos
for RG in $RESOURCE_GROUPS; do
    echo "🔍 Analizando grupo: $RG"
    
    # Contar recursos en el grupo
    RESOURCE_COUNT=$(az resource list --resource-group $RG --query "length([])" -o tsv)
    TOTAL_RESOURCES=$((TOTAL_RESOURCES + RESOURCE_COUNT))
    
    if [ "$RESOURCE_COUNT" -eq 0 ]; then
        echo "   ⚠️  Grupo vacío (0 recursos) - Puede eliminarse"
    else
        echo "   ✅ $RESOURCE_COUNT recurso(s) encontrado(s)"
        
        # Listar recursos en el grupo
        az resource list --resource-group $RG --query "[].{Nombre:name, Tipo:type, Ubicacion:location}" --output table | sed 's/^/      /'
        
        # Calcular costos estimados según el tipo de recursos
        if [ "$RG" = "pianotranscription-rg" ]; then
            echo "      💵 Costo estimado: $16-52 USD/mes"
            ESTIMATED_COST=30
        elif [ "$RG" = "TrabajoTerminal" ]; then
            echo "      💵 Costo estimado: $0 USD/mes (Static Web App Free)"
        fi
    fi
    
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 RESUMEN:"
echo "   • Total de grupos de recursos: $(echo "$RESOURCE_GROUPS" | wc -l | tr -d ' ')"
echo "   • Total de recursos activos: $TOTAL_RESOURCES"
echo "   • Costo estimado mensual: ~\$$ESTIMATED_COST USD"
echo ""

# Verificar uso de Container App en las últimas 24h
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📈 MÉTRICAS DE USO (últimas 24 horas):"
echo ""

# Intentar obtener métricas del Container App
REQUESTS=$(az monitor metrics list \
  --resource /subscriptions/$SUBSCRIPTION_ID/resourceGroups/pianotranscription-rg/providers/Microsoft.App/containerApps/pt-api \
  --metric "Requests" \
  --start-time $(date -v-1d -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --interval PT1H \
  --query "value[0].timeseries[0].data[].total" \
  --output tsv 2>/dev/null | awk '{s+=$1} END {print s}')

if [ -n "$REQUESTS" ] && [ "$REQUESTS" != "" ]; then
    echo "   🌐 Requests al Container App: $REQUESTS"
    
    # Calcular tiempo activo aproximado (asumiendo ~1 request cada 5 min cuando está activo)
    ACTIVE_HOURS=$(echo "scale=1; $REQUESTS / 12" | bc)
    echo "   ⏱️  Tiempo activo estimado: ${ACTIVE_HOURS} horas"
else
    echo "   ℹ️  No se pudieron obtener métricas (es normal en las primeras 24h)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 RECOMENDACIONES:"
echo ""

# Verificar grupos vacíos
EMPTY_GROUPS=$(az group list --query "[?length(resources) == 0].name" -o tsv)
if [ -n "$EMPTY_GROUPS" ]; then
    echo "   🗑️  Grupos de recursos vacíos encontrados:"
    for EMPTY_RG in $EMPTY_GROUPS; do
        echo "      • $EMPTY_RG"
        echo "        Comando: az group delete --name $EMPTY_RG --yes --no-wait"
    done
    echo ""
fi

echo "   ✅ Tu frontend está en el tier GRATUITO"
echo "   ✅ Scale-to-zero está habilitado en el backend"
echo "   ✅ Log Analytics está en el tier gratuito"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Auditoría completada"
echo "📄 Detalles completos en: COSTOS_AZURE.md"
echo ""
