Write-Host "🔍 CLOUDGUARDIAN - ENCONTRANDO FRONTEND..." -ForegroundColor Cyan

# Testar portas comuns do Vite
$ports = @(5173, 5174, 5175, 5176, 5177, 5178, 5179, 5180)
$frontendUrl = $null

foreach ($port in $ports) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port" -TimeoutSec 2
        $frontendUrl = "http://localhost:$port"
        Write-Host "✅ Frontend encontrado: $frontendUrl" -ForegroundColor Green
        break
    } catch {
        # Continue tentando
    }
}

if ($frontendUrl) {
    Write-Host "`n🎯 ACESSE A PLATAFORMA:" -ForegroundColor Yellow
    Write-Host "   Frontend: $frontendUrl" -ForegroundColor White
    Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
    
    # Abrir no navegador
    Write-Host "`n🌐 Abrindo no navegador..." -ForegroundColor Green
    Start-Process $frontendUrl
} else {
    Write-Host "❌ Frontend não encontrado em nenhuma porta comum." -ForegroundColor Red
    Write-Host "💡 Inicie manualmente: cd apps\frontend && npm run dev" -ForegroundColor Yellow
}

# Testar backend
Write-Host "`n🔧 Verificando Backend..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✅ Backend: $($health.status) v$($health.version)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend offline" -ForegroundColor Red
}
