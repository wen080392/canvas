# Frontend HTML Pages - Atualizado

## ✅ Páginas Implementadas

### 1. Secret Scanner (`secret_scanner.html`)
- **Funcionalidade**: Detecta credenciais e secrets em código
- **Features**:
  - Input via textarea ou upload de arquivo
  - Código de exemplo com secrets
  - Resultados em tempo real
  - Status por severidade (Critical, High, Medium, Low)
  - Autenticação via JWT
  - Logout functionality

### 2. Próximas Páginas (a implementar)
- **graph.html** - Infrastructure visualization com ReactFlow
- **auto_remediation.html** - Dashboard de correções automáticas
- **compliance_report.html** - Relatórios de compliance (5 frameworks)
- **settings.html** - Configurações de usuário e AWS
- **drift_detection.html** - Detecção de drift

## 🔌 Integração com Backend

Todas as páginas usam:
- **Base URL**: `http://localhost:8000`
- **Auth**: JWT token em `Authorization: Bearer <token>`
- **Endpoints**:
  - `POST /secrets/scan` - Escanear segredos
  - `POST /graph/generate` - Gerar gráfico de infraestrutura
  - `GET /remediation/suggestions` - Sugestões de remediação
  - `GET /compliance/report` - Relatórios de compliance
  - `POST /drift/check` - Verificar drift

## 🎨 UI/UX

- **Navbar**: Navegação lateral com links para todas as páginas
- **Sidebar**: Menu com ícones e status
- **Responsive**: Mobile-first design
- **Cores**: Gradientes azul/roxo, severidade com cores padrão
- **Componentes**: Cards, badges, modals, spinners

## 📝 Exemplo de Uso

```html
<!-- Autenticação -->
<script>
  const token = localStorage.getItem('access_token');
  if (!token) window.location.href = 'login.html';
</script>

<!-- Fetch com Token -->
<script>
  const response = await fetch('http://localhost:8000/api/endpoint', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
</script>
```

## 🚀 Como Rodar

### Desenvolvimento
```bash
cd apps/frontend

# React (novo)
npm run dev

# Páginas HTML (vanilla JS)
# Abrir em http://localhost:5173 ou servidor local
```

### Build
```bash
npm run build
```

## 📊 Estrutura de Dados

### Secret Scanner Response
```json
{
  "secrets": [
    {
      "type": "AWS_KEY",
      "severity": "CRITICAL",
      "line_number": 5,
      "matched_string": "AKIAIOSFODNN7EXAMPLE",
      "description": "AWS Access Key detected"
    }
  ]
}
```

### Infrastructure Graph Response
```json
{
  "nodes": [
    {
      "id": "aws_s3_bucket.main",
      "data": {"label": "S3 Bucket", "category": "storage"},
      "position": {"x": 0, "y": 0}
    }
  ],
  "edges": [
    {
      "id": "edge1",
      "source": "aws_s3_bucket.main",
      "target": "aws_iam_role.main"
    }
  ]
}
```

## ✨ Features Principais

- ✅ Autenticação JWT
- ✅ Error handling
- ✅ Loading states
- ✅ Response parsing
- ✅ Logout functionality
- ✅ Responsive design
- ✅ Export results (JSON/CSV)
- ✅ Real-time scanning

## 🔒 Segurança

- ✅ Token validation
- ✅ CORS enabled
- ✅ XSS prevention (escapeHtml)
- ✅ No credentials in code
- ✅ Logout clears token

## 📱 Responsivo

- Mobile: Sidebar collapse, stacked layout
- Tablet: 2-column layout
- Desktop: Full layout com sidebar

