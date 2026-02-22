# 🐳 CloudGuardian Docker Setup

## Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Start All Services
```bash
docker-compose up -d
```

### Services Running
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Nginx**: http://localhost

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## 🔧 Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Important variables**:
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - JWT secret (min 32 chars)
- `GITHUB_TOKEN` - GitHub API access (optional)
- `ENCRYPTION_KEY` - Fernet encryption key (optional)

### Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 📊 Database

### Access PostgreSQL
```bash
docker-compose exec postgres psql -U cloudguardian -d cloudguardian
```

### Reset Database
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Restart
```

### Backup Database
```bash
docker-compose exec postgres pg_dump -U cloudguardian cloudguardian > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U cloudguardian cloudguardian < backup.sql
```

## 🚀 Development

### Hot Reload
- **Backend**: Automatically reloads on file changes (Uvicorn --reload)
- **Frontend**: Vite hot module replacement

### Access Backend Shell
```bash
docker-compose exec backend bash
```

### Run Backend Tests
```bash
docker-compose exec backend pytest tests/
```

### Backend Logs
```bash
docker-compose logs -f backend
```

## 📦 Production Deployment

### Build Production Images
```bash
docker-compose -f docker-compose.yml build
```

### Environment Variables
Set these in production:
- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRET_KEY=` (strong random string)
- `GITHUB_TOKEN=` (GitHub app token)
- `ENCRYPTION_KEY=` (Fernet key)
- Update `DATABASE_URL` for production DB

### SSL/TLS
Place certificates in `./ssl/`:
- `ssl/cert.pem`
- `ssl/key.pem`

### Scale Services
```bash
docker-compose up -d --scale backend=3
```

## 🔒 Security

### Default Credentials (Change in Production!)
- **DB User**: cloudguardian
- **DB Password**: password
- **Admin User**: admin@company.com (create via API)

### Network
- Services communicate via `cloudguardian-net` bridge
- Only expose ports 80, 443, and dev ports (5173, 8000)

### Firewall Rules
```bash
# Allow HTTP/HTTPS only
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 8000  # Backend internal
ufw deny 5173  # Frontend internal
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Or use different port
docker-compose -f docker-compose.yml -e "BACKEND_PORT=8001" up
```

### Database Connection Error
```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### Frontend Can't Connect to Backend
1. Check backend is running: `docker-compose logs backend`
2. Verify API URL in frontend: check `VITE_API_URL` in `.env`
3. Check CORS enabled in backend

### Redis Connection Error
```bash
# Check Redis is running
docker-compose logs redis

# Test connection
docker-compose exec redis redis-cli ping
```

## 📚 Useful Commands

```bash
# View all containers
docker-compose ps

# Build specific service
docker-compose build backend

# Run one-off command
docker-compose run backend python -m pytest

# Remove volumes and start fresh
docker-compose down -v && docker-compose up -d

# View resource usage
docker stats

# Clean up everything
docker-compose down
docker system prune -a
```

## 🔗 API Endpoints

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📝 Example Workflows

### Development Setup
```bash
# 1. Start services
docker-compose up -d

# 2. Create admin user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Admin@1234"}'

# 3. Login and get token
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@test.com&password=Admin@1234"

# 4. Use token in requests
curl -X GET http://localhost:8000/dashboard/stats \
  -H "Authorization: Bearer <your_token>"
```

## 📖 Documentation

- API Docs: http://localhost:8000/docs
- Deployment Guide: See `DEPLOYMENT.md`
- Architecture: See `.github/copilot-instructions.md`

