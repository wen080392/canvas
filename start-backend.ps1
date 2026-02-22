Write-Host "🚀 INICIANDO BACKEND CLOUDGUARDIAN" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Parar backends existentes
Write-Host "🛑 Parando serviços Python existentes..." -ForegroundColor Yellow
taskkill /f /im python.exe 2>$null

# Iniciar backend
Write-Host "🔧 Iniciando API na porta 8000..." -ForegroundColor Yellow
cd apps\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Write-Host "`n💡 Quando quiser parar: Pressione CTRL+C" -ForegroundColor Cyan
