# 🚀 Quick Start Guide

## Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/CloudGuardian.git
cd CloudGuardian

# 2. Create .env file
cp apps/backend/.env.example apps/backend/.env
# Edit .env and add your GITHUB_TOKEN

# 3. Start with Docker Compose
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## Option 2: Manual Setup

### Backend

```bash
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env

# Run server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
# Simply open in browser:
file:///C:/Users/USER/CloudGuardian/apps/frontend/login.html

# Or use local server:
cd apps/frontend
python -m http.server 3000
# Visit: http://localhost:3000/login.html
```

## 🎯 First Steps After Login

1. **Dashboard** - View security metrics
2. **Infrastructure Graph** - Click "Load Sample Infrastructure"
3. **Compliance** - Navigate to see audit report
4. **API Docs** - Visit http://localhost:8000/docs

## 🔐 Default Credentials

- **Email**: admin@company.com
- **Password**: demo123

*(These are for demo purposes only - no actual authentication)*

## 📝 Testing API

```bash
# Scan for secrets
curl -X POST http://localhost:8000/api/v1/secrets/scan \
  -H "Content-Type: application/json" \
  -d '{"content": "aws_key = \"AKIAIOSFODNN7EXAMPLE\""}'

# Generate infrastructure graph
curl -X POST http://localhost:8000/api/v1/graph/generate \
  -H "Content-Type: application/json" \
  -d @sample_terraform.json
```

## 🛑 Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (needs 3.10+)
- Install Terraform CLI: Required for validation

**Graph won't load:**
- Ensure backend is running on port 8000
- Check browser console for CORS errors

**PDF generation fails:**
- WeasyPrint requires GTK libraries
- Fallback: Reports save as HTML automatically

## 🎨 Customization

Edit these files to customize:
- `apps/frontend/login.html` - Login page branding
- `apps/backend/app/services/compliance_service.py` - Add compliance controls
- `apps/backend/app/remediation/strategies/` - Add new fix strategies

---

Need help? Open an issue or contact: support@cloudguardian.io
