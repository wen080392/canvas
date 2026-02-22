Write-Host "🚀 CloudGuardian - Starting Everything..." -ForegroundColor Green

# Function to check if backend is running
function Test-Backend {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2
        return $true
    } catch {
        return $false
    }
}

# Function to start backend
function Start-Backend {
    Write-Host "🔧 Starting Backend..." -ForegroundColor Yellow
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000" -WorkingDirectory "apps\backend"
    Start-Sleep -Seconds 3
}

# Function to run CLI command
function Invoke-CLI {
    param([string]$Command)
    
    cd apps\cli
    python simple_cli.py @Command.Split(" ")
}

# Main execution
Write-Host "📦 Checking services..." -ForegroundColor Yellow

# Start backend if not running
if (-not (Test-Backend)) {
    Start-Backend
    Start-Sleep -Seconds 2
}

# Test backend
if (Test-Backend) {
    Write-Host "✅ Backend is running!" -ForegroundColor Green
} else {
    Write-Host "❌ Backend failed to start" -ForegroundColor Red
    exit 1
}

# Show available commands
Write-Host "`n🔧 Available CLI Commands:" -ForegroundColor Cyan
Write-Host "   config" -ForegroundColor White
Write-Host "   login" -ForegroundColor White  
Write-Host "   scan-secrets" -ForegroundColor White
Write-Host "   scan-tf" -ForegroundColor White
Write-Host "   compliance" -ForegroundColor White
Write-Host "   drift" -ForegroundColor White

Write-Host "`n💡 Example: .\run-cloudguardian.ps1 'scan-secrets'" -ForegroundColor Yellow

# Execute command if provided
if ($args.Count -gt 0) {
    $command = $args -join " "
    Write-Host "`n🎯 Executing: $command" -ForegroundColor Magenta
    Invoke-CLI -Command $command
} else {
    Write-Host "`n⏹️  No command provided. Backend is running." -ForegroundColor Yellow
    Write-Host "   Use CTRL+C to stop the backend" -ForegroundColor Yellow
}
