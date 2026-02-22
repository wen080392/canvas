@echo off
chcp 65001 > nul
echo.
echo ?? CLOUDGUARDIAN - INICIANDO PLATAFORMA COMPLETA
echo ==============================================
echo.

echo [1] PARANDO SERVI?OS EXISTENTES...
taskkill /f /im python.exe > nul 2>&1
timeout /t 2 > nul

echo [2] INICIANDO BACKEND NA PORTA 8000...
cd apps\backend
start "CloudGuardian Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5 > nul

echo [3] VERIFICANDO BACKEND...
curl -s http://localhost:8000/health > nul
if %errorlevel% equ 0 (
    echo ? BACKEND RODANDO: http://localhost:8000
    echo ?? API Docs: http://localhost:8000/docs
) else (
    echo ? Backend n?o iniciou - tentando m?todo alternativo...
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    goto :end
)

echo.
echo [4] INICIANDO FRONTEND NA PORTA 5173...
cd ..\frontend
echo ?? Iniciando React...
start "CloudGuardian Frontend" cmd /k "npm run dev"
timeout /t 3 > nul

echo.
echo ? PLATAFORMA INICIADA COM SUCESSO!
echo.
echo ?? ACESSE:
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000  
echo    API Docs: http://localhost:8000/docs
echo.
echo ?? COMANDOS CLI:
echo    .\cloudguardian.bat login test@example.com password123
echo    .\cloudguardian.bat scan-secrets .
echo    .\cloudguardian.bat compliance SOC2
echo.
pause

:end
