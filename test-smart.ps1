Write-Host "🧪 CLOUDGUARDIAN - TESTE INTELIGENTE" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

function Test-Backend {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 3
        return $true
    } catch {
        return $false
    }
}

# Verificar backend
Write-Host "`n🔍 Verificando Backend..." -ForegroundColor Yellow
if (Test-Backend) {
    Write-Host "   ✅ Backend Online" -ForegroundColor Green
    
    # Testar endpoints
    Write-Host "`n🧪 Testando Endpoints..." -ForegroundColor Yellow
    
    try {
        # Health
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        Write-Host "   ✅ Health: $($health.status)" -ForegroundColor Green
        
        # Login
        $login = Invoke-RestMethod -Uri "http://localhost:8000/token" -Method Post -Body "username=test&password=test" -ContentType "application/x-www-form-urlencoded"
        Write-Host "   ✅ Login: Token gerado" -ForegroundColor Green
        
        # Secret Scan
        $scanBody = @{content="test"; filename="test.txt"} | ConvertTo-Json
        $scan = Invoke-RestMethod -Uri "http://localhost:8000/secrets/scan" -Method Post -Body $scanBody -ContentType "application/json"
        Write-Host "   ✅ Secret Scan: $($scan.secrets_found) segredos" -ForegroundColor Green
        
        # Compliance
        $compliance = Invoke-RestMethod -Uri "http://localhost:8000/compliance/report?framework=SOC2" -Method Get
        Write-Host "   ✅ Compliance: $($compliance.framework)" -ForegroundColor Green
        
        # Drift
        $driftBody = @{project_name="test"} | ConvertTo-Json
        $drift = Invoke-RestMethod -Uri "http://localhost:8000/drift/check" -Method Post -Body $driftBody -ContentType "application/json"
        Write-Host "   ✅ Drift: $($drift.drift_detected)" -ForegroundColor Green
        
    } catch {
        Write-Host "   ❌ Erro nos endpoints: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} else {
    Write-Host "   ❌ Backend Offline" -ForegroundColor Red
    Write-Host "`n💡 SOLUÇÃO:" -ForegroundColor Yellow
    Write-Host "   Execute em um terminal separado:" -ForegroundColor White
    Write-Host "   cd apps\backend" -ForegroundColor Gray
    Write-Host "   python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
}

# Verificar frontend
Write-Host "`n🔍 Verificando Frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3
    Write-Host "   ✅ Frontend React: http://localhost:5173" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Frontend Offline" -ForegroundColor Red
    Write-Host "`n💡 SOLUÇÃO:" -ForegroundColor Yellow
    Write-Host "   Execute em outro terminal:" -ForegroundColor White
    Write-Host "   cd apps\frontend" -ForegroundColor Gray
    Write-Host "   npm run dev" -ForegroundColor Gray
}

Write-Host "`n🎯 STATUS FINAL:" -ForegroundColor Cyan
if ((Test-Backend) -and $?) {
    Write-Host "   ✅ PLATAFORMA OPERACIONAL" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Execute os comandos acima para iniciar os serviços" -ForegroundColor Yellow
}

Write-Host "`n🚀 COMANDOS RÁPIDOS:" -ForegroundColor Magenta
Write-Host "   .\start-cloudguardian.bat  (Inicia tudo automaticamente)" -ForegroundColor White
Write-Host "   .\cloudguardian.bat config (Testa configuração)" -ForegroundColor White
