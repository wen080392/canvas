@echo off
REM ============================================================================
REM CloudGuardian - Development Setup Script (Windows)
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║                   CloudGuardian Development Setup                     ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Get to project root
cd /d "%~dp0\..\..\"
echo [1/5] Projeto: %cd%

REM Check Python
echo [2/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python nao encontrado!
    echo Execute: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo     - %%i

REM Check Docker
echo [3/5] Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Docker nao encontrado
    echo   Execute: https://www.docker.com/products/docker-desktop
) else (
    for /f "tokens=*" %%i in ('docker --version') do echo     - %%i
)

REM Check .env
echo [4/5] Verificando configuracao...
if not exist ".env" (
    echo     - .env nao encontrado, criando de exemplo...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo     - Copie .env.example para .env
    )
) else (
    echo     - .env: OK
)

REM Install dependencies
echo [5/5] Instalando dependencias...
cd apps\backend
if not exist "venv" (
    echo     - Criando virtualenv...
    python -m venv venv
)

echo     - Ativando virtualenv...
call venv\Scripts\activate.bat

echo     - Instalando pacotes...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                     Setup Completo!                                   ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo Proximos passos:
echo   1. Inicie o PostgreSQL (Docker): docker-compose up -d postgres
echo   2. Inicie o backend: python -m uvicorn app.main:app --reload
echo   3. Acesse a API: http://localhost:8000/docs
echo   4. Execute testes: python test_all_endpoints.py
echo.
echo. Requer Docker Compose:
echo   - docker-compose up -d          (iniciar todos servicos)
echo   - docker-compose logs -f        (ver logs)
echo   - docker-compose down           (parar servicos)
echo.
pause
