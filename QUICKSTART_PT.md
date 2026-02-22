# 🚀 CloudGuardian - Guia Rápido (Português)

## ⚡ Setup em 5 Minutos (Windows/PowerShell)

### 1. Clonar & Configurar
```powershell
cd C:\Users\USER\CloudGuardian
cp .env.example .env  # Copiar arquivo de configuração

# Editar .env com configurações locais (opcional)
notepad .env
```

### 2. Iniciar Banco de Dados (Docker)
```powershell
docker-compose up -d postgres

# Verificar se está rodando
docker-compose ps
```

### 3. Ativar Ambiente Python
```powershell
cd apps\backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 4. Rodar Backend
```powershell
# Terminal 1: Backend API
cd C:\Users\USER\CloudGuardian\apps\backend
python -m uvicorn app.main:app --reload

# Você verá:
# Uvicorn running on http://127.0.0.1:8000
```

### 5. Testar API (Em outro terminal PowerShell)
```powershell
# Terminal 2: Rodar testes
cd C:\Users\USER\CloudGuardian\apps\backend
$env:PYTHONIOENCODING='utf-8'
python test_all_endpoints.py
```

### 6. Acessar Interface Web
```
# No navegador:
http://localhost:8000/docs          # Swagger UI (teste interativo)
http://localhost:8000/redoc         # ReDoc (documentação)
```

---

## 📋 Arquivos Importantes

| Arquivo | Propósito |
|---------|-----------|
| `.env.example` | Variáveis de ambiente (copiar para `.env`) |
| `docker-compose.yml` | Configuração Docker |
| `apps/backend/requirements.txt` | Dependências Python |
| `apps/backend/app/main.py` | FastAPI principal |
| `apps/backend/test_all_endpoints.py` | Testes E2E |

---

## 🧪 Testes

### Rodar Todos os Testes
```powershell
cd C:\Users\USER\CloudGuardian\apps\backend
$env:PYTHONIOENCODING='utf-8'
python test_all_endpoints.py
```

**Resultado esperado:**
```
✅ User registration
✅ User login
✅ Dashboard stats
✅ Secret patterns
✅ Secret scan
✅ Batch scan
✅ Infrastructure graph
✅ Remediation suggestions
✅ Remediation history
✅ Compliance frameworks
✅ Compliance reports
✅ Drift alerts

📈 Results: 12/12 tests passed (100%)
```

### Testes Específicos
```powershell
# Teste de scan de secrets
pytest tests/test_secret_scanner.py -v

# Teste de detecção de drift
pytest tests/test_drift_detection.py -v

# Todos com cobertura
pytest --cov=app tests/ --cov-report=html
```

---

## 🔧 Resolução de Problemas

### "Connection refused" no teste
**Problema**: Backend não está rodando
**Solução**:
```powershell
# Verificar se servidor está rodando
netstat -ano | findstr :8000

# Se não estiver:
cd C:\Users\USER\CloudGuardian\apps\backend
python -m uvicorn app.main:app --reload
```

### "Module not found" - sqlalchemy, fastapi
**Problema**: Dependências não instaladas
**Solução**:
```powershell
cd C:\Users\USER\CloudGuardian\apps\backend
pip install -r requirements.txt
```

### "PostgreSQL connection error"
**Problema**: Banco de dados não está rodando
**Solução**:
```powershell
# Iniciar PostgreSQL via Docker
docker-compose up -d postgres

# Verificar status
docker-compose logs postgres
```

### "UnicodeEncodeError" nos testes
**Problema**: Encoding de emojis
**Solução**:
```powershell
$env:PYTHONIOENCODING='utf-8'
python test_all_endpoints.py
```

---

## 📚 Documentação

- **API Docs**: http://localhost:8000/docs (quando servidor estiver rodando)
- **DEPLOYMENT.md**: Guia completo de produção
- **README.md**: Visão geral do projeto
- **.github/copilot-instructions.md**: Guia para AI agents

---

## 🎯 Endpoints Principais

### Autenticação
```
POST /users              # Registrar usuário
POST /token              # Login
GET /users/me            # Dados do usuário
```

### Scanning
```
POST /secrets/scan              # Scan de secrets
POST /graph/generate            # Gerar grafo
POST /compliance/scan           # Scan de compliance
```

### Dados
```
GET /dashboard/stats            # Estatísticas
GET /remediation/suggestions    # Remediações
GET /drift/alerts               # Alertas de drift
```

---

## 🚀 Próximos Passos

1. **Explorar API**: Abrir http://localhost:8000/docs
2. **Entender Endpoints**: Testar cada um via Swagger
3. **Ler Documentação**: Ver DEPLOYMENT.md para produção
4. **AI Agent Guide**: Ver .github/copilot-instructions.md

---

## 💡 Dicas

**Para desenvolvimento rápido:**
```powershell
# Watch automático de código
python -m uvicorn app.main:app --reload

# Recarrega automaticamente quando você muda arquivos Python
```

**Logs detalhados:**
```powershell
# Ver logs completos
$env:LOG_LEVEL='DEBUG'
python -m uvicorn app.main:app --reload
```

**Banco de dados:**
```powershell
# Conectar ao PostgreSQL
psql -U cloudguardian -d cloudguardian

# Ver tabelas
\dt

# Consultar usuários
SELECT * FROM users;
```

---

## ❓ Dúvidas?

- **API não responde?** → Verificar se `http://localhost:8000/health` retorna OK
- **Testes falhando?** → Ver `.github/copilot-instructions.md` seção de troubleshooting
- **Erro de setup?** → Executar `python -m pip install --upgrade pip`

---

**Pronto para começar! 🎉**

```powershell
# Tudo em um comando:
cd C:\Users\USER\CloudGuardian\apps\backend; python -m uvicorn app.main:app --reload
```
