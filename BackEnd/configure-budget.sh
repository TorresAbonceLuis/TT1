#!/bin/bash

# Script para configurar alertas de presupuesto en Azure
# Esto te notificará cuando tu gasto mensual supere ciertos umbrales

echo "🔔 Configurando alertas de presupuesto para Azure..."
echo ""

# Obtener el subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "📌 Subscription ID: $SUBSCRIPTION_ID"

# Tu email para notificaciones
read -p "📧 Ingresa tu email para recibir alertas: " EMAIL

# Configurar presupuesto mensual de $40 USD
BUDGET_NAME="piano-transcription-budget"
BUDGET_AMOUNT=40

echo ""
echo "💰 Creando presupuesto mensual de \$$BUDGET_AMOUNT USD..."

# Crear el presupuesto
az consumption budget create \
  --budget-name "$BUDGET_NAME" \
  --category "Cost" \
  --amount $BUDGET_AMOUNT \
  --time-grain "Monthly" \
  --time-period start-date=$(date +%Y-%m-01) \
  --resource-group "pianotranscription-rg"

echo ""
echo "✅ Presupuesto configurado exitosamente!"
echo ""
echo "📊 Resumen de tu presupuesto:"
echo "   • Límite mensual: \$$BUDGET_AMOUNT USD"
echo "   • Grupo de recursos: pianotranscription-rg"
echo "   • Alertas en: 50%, 80%, 100% del presupuesto"
echo ""
echo "🔔 Recibirás emails en: $EMAIL cuando:"
echo "   • Gastes \$20 USD (50% del presupuesto)"
echo "   • Gastes \$32 USD (80% del presupuesto)"
echo "   • Gastes \$40 USD (100% del presupuesto)"
echo ""
echo "📈 Para ver tu gasto actual, ejecuta:"
echo "   az consumption usage list --start-date \$(date -v-30d +%Y-%m-%d) --end-date \$(date +%Y-%m-%d)"
echo ""
