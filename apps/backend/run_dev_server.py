0JSXJC#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CloudGuardian Development Server Launcher

Inicia o backend API em modo desenvolvimento
"""

import subprocess
import os
import sys
import time
from pathlib import Path

def main():
    # Obter caminho do projeto
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("=" * 70)
    print("CloudGuardian Development Server")
    print("=" * 70)
    
    # Verificar se .env existe
    if not Path(".env").exists() and not Path("../.env").exists():
        print("[AVISO] Arquivo .env nao encontrado!")
        print("        Criando .env de exemplo...")
        
        env_content = """# Database
DATABASE_URL=postgresql://cloudguardian:password@localhost:5432/cloudguardian
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# GitHub
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=owner/repo

# Encryption
ENCRYPTION_KEY=your-fernet-key-here

# Logging
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
"""
        with open(".env.local", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("[OK] Criado .env.local - edite com suas configuracoes")
    
    # Verificar dependencias
    print("\n[1/3] Verificando dependencias...")
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        print("    - FastAPI: OK")
        print("    - SQLAlchemy: OK")
        print("    - Pydantic: OK")
    except ImportError as e:
        print(f"    - ERRO: {e}")
        print("    Execute: pip install -r requirements.txt")
        sys.exit(1)
    
    # Criar banco de dados (se necesario)
    print("\n[2/3] Verificando banco de dados...")
    try:
        from app.database import engine, Base  # noqa: F401
        Base.metadata.create_all(bind=engine)
        print("    - Tabelas criadas/verificadas: OK")
    except Exception as e:
        print(f"    - AVISO: {e}")
        print("    - Certifique-se que PostgreSQL esta rodando")
    
    # Iniciar servidor
    print("\n[3/3] Iniciando servidor...\n")
    print("-" * 70)
    
    try:
        # Comando para executar uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        
        subprocess.run(cmd, check=False)

    except KeyboardInterrupt:
        print("\n\n[OK] Servidor parado pelo usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERRO] Falha ao iniciar servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
