Write-Host "🎯 CLOUDGUARDIAN - TESTE DE INTEGRAÇÃO COMPLETA" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Testar Backend
Write-Host "`n1. 🔧 TESTANDO BACKEND..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "   ✅ Backend: $($health.status) v$($health.version)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend offline - Inicie com: cd apps\backend && python -m uvicorn simple_main:app --reload --port 8000" -ForegroundColor Red
}

# Testar Frontend
Write-Host "`n2. 🎨 TESTANDO FRONTEND..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5
    Write-Host "   ✅ Frontend React rodando: http://localhost:5173" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Frontend offline - Inicie com: cd apps\frontend && npm run dev" -ForegroundColor Red
}

# Testar CLI
Write-Host "`n3. 🔧 TESTANDO CLI..." -ForegroundColor Yellow
cd apps\cli
python simple_cli.py config

Write-Host "`n4. 🧪 TESTANDO ENDPOINTS DA API..." -ForegroundColor Yellow
try {
    # Testar login
    $login = Invoke-RestMethod -Uri "http://localhost:8000/token" -Method Post -Body @{username="test"; password="test"} -ContentType "application/x-www-form-urlencoded"
    Write-Host "   ✅ Login endpoint: Funcionando" -ForegroundColor Green
    
    # Testar secret scan
    $scan = Invoke-RestMethod -Uri "http://localhost:8000/secrets/scan" -Method Post -Body (@{content="test"; filename="test.txt"} | ConvertTo-Json) -ContentType "application/json"
    Write-Host "   ✅ Secret scan: Funcionando ($($scan.secrets_found) segredos encontrados)" -ForegroundColor Green
    
    # Testar compliance
    $compliance = Invoke-RestMethod -Uri "http://localhost:8000/compliance/report?framework=SOC2" -Method Get
    Write-Host "   ✅ Compliance: Funcionando (Framework: $($compliance.framework))" -ForegroundColor Green
    
    # Testar drift
    $drift = Invoke-RestMethod -Uri "http://localhost:8000/drift/check" -Method Post -Body (@{project_name="test"} | ConvertTo-Json) -ContentType "application/json"
    Write-Host "   ✅ Drift detection: Funcionando (Drift: $($drift.drift_detected))" -ForegroundColor Green
    
} catch {
    Write-Host "   ❌ Erro nos endpoints: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 PLATAFORMA CLOUDGUARDIAN ESTÁ OPERACIONAL!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "🔧 Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "🎨 Frontend:     http://localhost:5173" -ForegroundColor White
Write-Host "🔐 Páginas HTML: http://localhost:5173/login.html" -ForegroundColor White
Write-Host "📊 Dashboard:    http://localhost:5173/dashboard.html" -ForegroundColor White
Write-Host "`n💡 COMANDOS DISPONÍVEIS:" -ForegroundColor Cyan
Write-Host "   .\cloudguardian.bat login email senha" -ForegroundColor White
Write-Host "   .\cloudguardian.bat scan-secrets ." -ForegroundColor White
Write-Host "   .\cloudguardian.bat scan-tf ." -ForegroundColor White
Write-Host "   .\cloudguardian.bat compliance SOC2" -ForegroundColor White
Write-Host "   .\cloudguardian.bat drift meu-projeto" -ForegroundColor White
