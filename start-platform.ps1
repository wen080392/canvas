Write-Host "🚀 CLOUDGUARDIAN - INICIANDO PLATAFORMA COMPLETA" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Configurar política de execução
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Função para testar backend
function Test-Backend {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2
        return $true
    } catch {
        return $false
    }
}

# Função para iniciar backend
function Start-Backend {
    Write-Host "`n🔧 INICIANDO BACKEND API..." -ForegroundColor Yellow
    $backendJob = Start-Job -ScriptBlock {
        cd "C:\Users\USER\CloudGuardian\apps\backend"
        python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000
    }
    return $backendJob
}

# Função para iniciar frontend React
function Start-Frontend {
    Write-Host "`n🎨 INICIANDO FRONTEND REACT..." -ForegroundColor Yellow
    cd "C:\Users\USER\CloudGuardian\apps\frontend"
    
    # Verificar se node_modules existe
    if (-not (Test-Path "node_modules")) {
        Write-Host "   📥 Instalando dependências..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host "   🚀 Iniciando servidor de desenvolvimento Vite..." -ForegroundColor Yellow
    Write-Host "   💡 O frontend será aberto em http://localhost:5173" -ForegroundColor Green
    npm run dev
}

# MAIN EXECUTION
Write-Host "`n📦 VERIFICANDO SERVIÇOS..." -ForegroundColor Cyan

# Iniciar backend se não estiver rodando
if (-not (Test-Backend)) {
    $backendJob = Start-Backend
    Write-Host "   ✅ Backend iniciado em background" -ForegroundColor Green
} else {
    Write-Host "   ✅ Backend já está rodando" -ForegroundColor Green
}

# Aguardar backend ficar pronto
Write-Host "`n⏳ Aguardando backend ficar pronto..." -ForegroundColor Yellow
$attempts = 0
while ($attempts -lt 10) {
    if (Test-Backend) {
        Write-Host "   ✅ Backend pronto!" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 1
    $attempts++
}

if ($attempts -eq 10) {
    Write-Host "   ❌ Backend não iniciou corretamente" -ForegroundColor Red
}

# Iniciar frontend
Write-Host "`n🎨 INICIANDO FRONTEND REACT..." -ForegroundColor Cyan
Start-Frontend

Write-Host "`n🎉 PLATAFORMA CLOUDGUARDIAN ESTÁ RODANDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "🔧 Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "🎨 Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n💡 Use Ctrl+C para parar o servidor frontend" -ForegroundColor Yellow
