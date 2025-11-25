# Script para probar la salud del backend en Azure
# Ejecutar con: .\test-backend-health.ps1

$API_URL = "https://pt-api.whitewater-3f1ca299.centralus.azurecontainerapps.io"

Write-Host "[*] Probando Backend de Piano Transcription" -ForegroundColor Cyan
Write-Host "URL: $API_URL" -ForegroundColor Yellow
Write-Host ""

# Test 1: Root endpoint
Write-Host "[1] Probando endpoint root (/)..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$API_URL/" -Method Get -TimeoutSec 10
    Write-Host "[OK] Root endpoint funciona correctamente" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "[ERROR] Error en root endpoint: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: CORS Headers
Write-Host "[2] Verificando headers CORS..." -ForegroundColor Cyan
try {
    $headers = @{
        "Origin" = "https://elpianista.me"
    }
    $response = Invoke-WebRequest -Uri "$API_URL/" -Method Options -Headers $headers -TimeoutSec 10
    Write-Host "[OK] Headers CORS:" -ForegroundColor Green
    $response.Headers | Format-Table -AutoSize
} catch {
    Write-Host "[ERROR] Error verificando CORS: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Health check del cleanup status
Write-Host "[3] Verificando estado de archivos temporales..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/transcribe/cleanup-status" -Method Get -TimeoutSec 10
    Write-Host "[OK] Estado de limpieza:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "[ERROR] Error obteniendo cleanup status: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Verificar si el servidor responde correctamente a status
Write-Host "[4] Probando endpoint de status (debe fallar con 404, es normal)..." -ForegroundColor Cyan
try {
    $testTaskId = "test-id-12345"
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/transcribe/status/$testTaskId" -Method Get -TimeoutSec 10
    Write-Host "[WARN] Status endpoint respondio (inesperado): $response" -ForegroundColor Yellow
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 404) {
        Write-Host "[OK] Status endpoint funciona correctamente (404 esperado para ID inexistente)" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Error inesperado: $statusCode" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[OK] Pruebas completadas" -ForegroundColor Green
