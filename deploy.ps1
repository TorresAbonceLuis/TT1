# Script de Deployment para Piano Transcription
# Usar con PowerShell en Windows

param(
    [Parameter(Mandatory=$false)]
    [switch]$NoCache = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipPush = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipUpdate = $false
)

$ErrorActionPreference = "Stop"
$BACKEND_PATH = "d:\TT1\BackEnd"
$IMAGE_NAME = "ptacr635892.azurecr.io/piano-transcription:latest"
$APP_NAME = "pt-api"
$RESOURCE_GROUP = "pianotranscription-rg"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  PIANO TRANSCRIPTION DEPLOYMENT" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker esta corriendo
Write-Host "[*] Verificando Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "[OK] Docker esta corriendo" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker no esta corriendo. Inicia Docker Desktop primero." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Paso 1: Build
if (-not $SkipBuild) {
    Write-Host "[1] CONSTRUYENDO IMAGEN DOCKER" -ForegroundColor Cyan
    Write-Host "Directorio: $BACKEND_PATH" -ForegroundColor Gray
    Write-Host "Imagen: $IMAGE_NAME" -ForegroundColor Gray
    
    Push-Location $BACKEND_PATH
    
    try {
        if ($NoCache) {
            Write-Host "[*] Construyendo SIN CACHE (puede tardar mas)..." -ForegroundColor Yellow
            docker buildx build --platform linux/amd64 --load -t $IMAGE_NAME . --no-cache
        } else {
            Write-Host "[*] Construyendo con cache..." -ForegroundColor Yellow
            docker buildx build --platform linux/amd64 --load -t $IMAGE_NAME .
        }
        Write-Host "[OK] Imagen construida exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Fallo la construccion de la imagen: $_" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Pop-Location
} else {
    Write-Host "[1] SALTANDO BUILD (usando imagen existente)" -ForegroundColor Yellow
}

Write-Host ""

# Paso 2: Login a Azure Container Registry
Write-Host "[2] LOGIN A AZURE CONTAINER REGISTRY" -ForegroundColor Cyan

try {
    Write-Host "[*] Verificando Azure CLI..." -ForegroundColor Yellow
    $azVersion = az --version
    if (-not $?) {
        throw "Azure CLI no encontrado"
    }
    Write-Host "[OK] Azure CLI encontrado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Azure CLI no esta instalado. Instala desde: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}

try {
    Write-Host "[*] Haciendo login a Azure Container Registry..." -ForegroundColor Yellow
    az acr login --name ptacr635892
    Write-Host "[OK] Login exitoso" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Fallo el login a ACR: $_" -ForegroundColor Red
    Write-Host "[HINT] Ejecuta: az login" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Paso 3: Push
if (-not $SkipPush) {
    Write-Host "[3] SUBIENDO IMAGEN A AZURE CONTAINER REGISTRY" -ForegroundColor Cyan
    
    try {
        Write-Host "[*] Pushing imagen..." -ForegroundColor Yellow
        docker push $IMAGE_NAME
        if (-not $?) {
            throw "Fallo el push"
        }
        Write-Host "[OK] Imagen subida exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Fallo el push de la imagen: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[3] SALTANDO PUSH" -ForegroundColor Yellow
}

Write-Host ""

# Paso 4: Update Container App
if (-not $SkipUpdate) {
    Write-Host "[4] ACTUALIZANDO CONTAINER APP EN AZURE" -ForegroundColor Cyan
    
    try {
        Write-Host "[*] Actualizando container app..." -ForegroundColor Yellow
        az containerapp update `
            --name $APP_NAME `
            --resource-group $RESOURCE_GROUP `
            --image $IMAGE_NAME `
            --query "{Revision:properties.latestRevisionName, Estado:properties.runningStatus}" `
            --output table
        if (-not $?) {
            throw "Fallo la actualizacion"
        }
        Write-Host "[OK] Container app actualizado exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Fallo la actualizacion: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[4] SALTANDO ACTUALIZACION" -ForegroundColor Yellow
}

Write-Host ""

# Paso 5: Verificar logs
Write-Host "[5] VERIFICANDO LOGS" -ForegroundColor Cyan
Write-Host "[*] Ultimas 15 lineas de logs..." -ForegroundColor Yellow

try {
    az containerapp logs show `
        --name $APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --tail 15 `
        --follow false
    Write-Host "[OK] Logs obtenidos" -ForegroundColor Green
} catch {
    Write-Host "[WARN] No se pudieron obtener los logs: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "[OK] DEPLOYMENT COMPLETADO" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API URL: https://pt-api.whitewater-3f1ca299.centralus.azurecontainerapps.io" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ejecuta './test-backend-health.ps1' para verificar el backend" -ForegroundColor Gray

# Ejemplos de uso
Write-Host ""
Write-Host "EJEMPLOS DE USO:" -ForegroundColor Cyan
Write-Host "  .\deploy.ps1                    # Deployment completo normal" -ForegroundColor Gray
Write-Host "  .\deploy.ps1 -NoCache           # Rebuild sin cache (cuando cambia el modelo)" -ForegroundColor Gray
Write-Host "  .\deploy.ps1 -SkipBuild         # Solo push y update (si ya construiste)" -ForegroundColor Gray
Write-Host "  .\deploy.ps1 -SkipBuild -SkipPush  # Solo update (si ya hiciste push)" -ForegroundColor Gray
