#!/bin/bash

# Script para verificar regiones disponibles en Azure for Students

echo "🌎 Verificando regiones disponibles para tu suscripción..."
echo ""

# Regiones a probar (comunes para estudiantes)
REGIONS=("westus2" "centralus" "westeurope" "northeurope" "southeastasia" "eastus")

echo "Probando regiones..."
echo ""

AVAILABLE_REGIONS=()

for region in "${REGIONS[@]}"; do
    echo -n "  Probando $region... "
    
    # Intentar crear un grupo de recursos temporal
    TEMP_RG="temp-test-rg-$(date +%s)"
    
    if az group create --name $TEMP_RG --location $region --output none 2>/dev/null; then
        echo "✓ DISPONIBLE"
        AVAILABLE_REGIONS+=("$region")
        
        # Eliminar el grupo temporal
        az group delete --name $TEMP_RG --yes --no-wait 2>/dev/null
    else
        echo "✗ No disponible"
    fi
    
    sleep 1
done

echo ""
echo "=================================="
echo "Regiones disponibles:"
echo "=================================="

if [ ${#AVAILABLE_REGIONS[@]} -eq 0 ]; then
    echo "❌ No se encontraron regiones disponibles"
    echo ""
    echo "Posibles soluciones:"
    echo "1. Contacta a soporte de Azure"
    echo "2. Verifica tu suscripción en portal.azure.com"
    echo "3. Intenta con una región diferente manualmente"
else
    for i in "${!AVAILABLE_REGIONS[@]}"; do
        echo "$((i+1)). ${AVAILABLE_REGIONS[$i]}"
    done
    
    echo ""
    echo "✅ Usa alguna de estas regiones en el script de despliegue"
fi

echo ""
