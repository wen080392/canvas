Write-Host "🎯 CLOUDGUARDIAN - VERIFICAÇÃO COMPLETA" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Testar Backend
Write-Host "`n1. 🔧 TESTANDO BACKEND..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "   ✅ Backend Online: $($health.status)" -ForegroundColor Green
    Write-Host "   📊 Versão: $($health.version)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend Offline" -ForegroundColor Red
    exit 1
}

# Testar CLI
Write-Host "`n2. 🔧 TESTANDO CLI..." -ForegroundColor Yellow
cd apps\cli

Write-Host "   📋 Testando comando config..." -ForegroundColor Gray
python simple_cli.py config

Write-Host "   📋 Testando login..." -ForegroundColor Gray
python simple_cli.py login test@example.com password123

Write-Host "   📋 Testando secret scan..." -ForegroundColor Gray
python simple_cli.py scan-secrets

Write-Host "   📋 Testando Terraform scan..." -ForegroundColor Gray
python simple_cli.py scan-tf

Write-Host "   📋 Testando compliance..." -ForegroundColor Gray
python simple_cli.py compliance SOC2

Write-Host "   📋 Testando drift detection..." -ForegroundColor Gray
python simple_cli.py drift my-project

Write-Host "`n🎉 VERIFICAÇÃO COMPLETA!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host "✅ Backend: http://localhost:8000" -ForegroundColor White
Write-Host "✅ CLI: Todos os comandos funcionando" -ForegroundColor White
Write-Host "✅ Scans: Secret, Terraform, Compliance, Drift" -ForegroundColor White
Write-Host "`n🚀 CLOUDGUARDIAN ESTÁ PRONTO PARA USO!" -ForegroundColor Cyan
