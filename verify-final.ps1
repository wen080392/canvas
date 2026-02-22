Write-Host "✅ CLOUDGUARDIAN - VERIFICAÇÃO FINAL" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# 1. Verificar Backend
Write-Host "`n1. 🔧 VERIFICANDO BACKEND..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "   ✅ Backend Online: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend Offline" -ForegroundColor Red
}

# 2. Verificar Frontend
Write-Host "`n2. �� VERIFICANDO FRONTEND..." -ForegroundColor Yellow
if (Test-Path "apps/frontend") {
    Write-Host "   ✅ Frontend React encontrado" -ForegroundColor Green
    
    # Verificar dependências
    cd apps/frontend
    if (Test-Path "node_modules") {
        Write-Host "   ✅ Dependências instaladas" -ForegroundColor Green
    } else {
        Write-Host "   📥 Instalando dependências..." -ForegroundColor Yellow
        npm install
    }
} else {
    Write-Host "   ❌ Frontend não encontrado" -ForegroundColor Red
}

# 3. Verificar CLI
Write-Host "`n3. 🔧 VERIFICANDO CLI..." -ForegroundColor Yellow
cd ..\..\apps\cli
python simple_cli.py config

Write-Host "`n🎉 VERIFICAÇÃO COMPLETA!" -ForegroundColor Green
Write-Host "💡 Próximos passos:" -ForegroundColor Cyan
Write-Host "   - Execute: .\start-cloudguardian.bat" -ForegroundColor White
Write-Host "   - Acesse: http://localhost:5173" -ForegroundColor White
Write-Host "   - Teste: http://localhost:8000/docs" -ForegroundColor White
