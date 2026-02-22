# 🚀 CloudGuardian - Production Deployment Guide

**Last Updated**: November 2025  
**Version**: 1.0.0  
**Status**: Production Ready

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Security Hardening](#security-hardening)
6. [Scaling & Performance](#scaling--performance)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Disaster Recovery](#disaster-recovery)

---

## Quick Start

**5-minute production deployment**:

```bash
# 1. Clone and setup
git clone https://github.com/cloudguardian/cloudguardian.git
cd cloudguardian
cp .env.example .env
nano .env  # Edit with your settings

# 2. Start services (Production)
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Verify
curl http://localhost/health
echo "✅ CloudGuardian is ready at http://localhost (Port 80)"
```

---

## System Requirements

### Minimum (Development)
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB
- Docker: 20.10+

### Recommended (Production)
- CPU: 8+ cores
- RAM: 16GB+
- Disk: 100GB+ (SSD)
- Docker: 20.10+, Docker Compose: 2.0+

### Software Dependencies
- PostgreSQL 13+
- Terraform 1.5+
- Python 3.10+
- Node.js 16+ (for frontend)

---

## Installation Methods

### Method 1: Docker Compose (Recommended)

**Supports**: Single node or cluster

```bash
# Full stack deployment (API + DB + Frontend)
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3

# Stop services
docker-compose down

# Clean state (remove volumes)
docker-compose down -v
```

**Services started**:
- **backend**: FastAPI on port 8000
- **postgres**: PostgreSQL on port 5432
- **frontend**: Nginx on port 3000
- **nginx**: Reverse proxy on port 80/443

### Method 2: Kubernetes

**Supports**: Multi-node, auto-scaling

```bash
# 1. Create namespace
kubectl create namespace cloudguardian

# 2. Create secrets
kubectl create secret generic cloudguardian-secrets \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=encryption-key=$ENCRYPTION_KEY \
  --from-literal=github-token=$GITHUB_TOKEN \
  -n cloudguardian

# 3. Deploy
kubectl apply -f k8s/deployment.yaml -n cloudguardian

# 4. Verify
kubectl get pods -n cloudguardian
kubectl logs -f deployment/cloudguardian-backend -n cloudguardian

# 5. Port forward (for testing)
kubectl port-forward svc/cloudguardian-api 8000:8000 -n cloudguardian
```

**Kubernetes manifests** (in `k8s/`):
- `deployment.yaml`: API backend deployment
- `service.yaml`: Kubernetes service
- `ingress.yaml`: Ingress controller
- `configmap.yaml`: Configuration
- `secrets.yaml`: Encrypted secrets

### Method 3: Manual Installation

**Supports**: Custom environments

```bash
# 1. Install dependencies
apt-get install -y python3.10 python3-pip postgresql terraform

# 2. Clone repo
git clone https://github.com/cloudguardian/cloudguardian.git
cd cloudguardian/apps/backend

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Database setup
export DATABASE_URL="postgresql://user:password@localhost:5432/cloudguardian"
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# 5. Run API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 6. Run frontend (separate terminal)
cd ../frontend
npm install && npm run build
python -m http.server 3000
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# ============== DATABASE ==============
DATABASE_URL=postgresql://cloudguardian:password@db.example.com:5432/cloudguardian_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600

# ============== AUTHENTICATION ==============
SECRET_KEY=your-super-secret-key-min-32-chars-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============== GITHUB INTEGRATION ==============
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=owner/repo  # Target repo for auto-fix PRs
GITHUB_API_VERSION=2022-11-28

# ============== ENCRYPTION ==============
ENCRYPTION_KEY=<output-from: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

# ============== AWS (Optional for Drift Detection) ==============
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============== TERRAFORM ==============
TERRAFORM_BIN=/usr/bin/terraform

# ============== LOGGING ==============
LOG_LEVEL=INFO
LOG_FORMAT=json  # json for CloudWatch/ELK
LOG_OUTPUT=stdout  # stdout or file

# ============== API ==============
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false  # Must be false in production

# ============== CORS ==============
CORS_ORIGINS=["https://app.yourdomain.com", "https://yourdomain.com"]

# ============== FEATURES ==============
ENABLE_AUTO_REMEDIATION=true
ENABLE_DRIFT_DETECTION=true
ENABLE_COMPLIANCE_REPORTING=true
MAX_FILE_SIZE_MB=50

# ============== RATE LIMITING ==============
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

### Database Setup

```bash
# Create database
createdb cloudguardian_prod

# Run migrations (automatic on startup)
docker-compose exec backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Create backup
pg_dump cloudguardian_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql cloudguardian_prod < backup_20240101_120000.sql
```

---

## Security Hardening

### 1. HTTPS/TLS Configuration

```nginx
# /etc/nginx/conf.d/cloudguardian.conf
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    
    server_name api.yourdomain.com;
    
    # SSL Certificate (LetsEncrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. Database Security

```bash
# Create restricted database user
psql -U postgres <<EOF
CREATE USER cloudguardian_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE cloudguardian_prod TO cloudguardian_readonly;
GRANT USAGE ON SCHEMA public TO cloudguardian_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cloudguardian_readonly;
EOF

# Enable SSL for connections
echo "hostssl all all 0.0.0.0/0 md5" >> /etc/postgresql/13/main/pg_hba.conf

# Backup database regularly
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
```

### 3. API Authentication

```python
# All endpoints require JWT token (except /users, /token)
@app.get("/sensitive-endpoint")
async def protected_endpoint(current_user: User = Depends(get_current_active_user)):
    # Only authenticated users can access
    return {"data": "sensitive"}
```

### 4. Secrets Management

```bash
# Use environment variables (not hardcoded)
export GITHUB_TOKEN=$(aws secretsmanager get-secret-value --secret-id github/token --query SecretString --output text)

# Rotate encryption key safely
# 1. Generate new key
# 2. Re-encrypt all secrets with new key
# 3. Update ENCRYPTION_KEY in .env
# 4. Deploy
```

### 5. Network Security

```bash
# Use private subnet for database
# Use security groups to restrict traffic
# Allow only backend -> database
# Allow only frontend -> API
# Block public internet access to database
```

---

## Scaling & Performance

### Horizontal Scaling

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Auto-scale based on CPU (Kubernetes)
kubectl autoscale deployment cloudguardian-backend \
  --min=2 --max=10 --cpu-percent=80 -n cloudguardian
```

### Caching Layer (Redis)

```bash
# Add Redis to docker-compose.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data

# Use in application
from redis import Redis
cache = Redis(host='redis', port=6379)
cache.set('key', 'value', ex=3600)  # 1 hour TTL
```

### Database Optimization

```bash
# Add indexes for frequently queried fields
CREATE INDEX idx_user_id ON scans(user_id);
CREATE INDEX idx_created_at ON scans(created_at DESC);

# Monitor slow queries
ALTER DATABASE cloudguardian_prod SET log_min_duration_statement = 1000;  # 1 second
```

### Load Testing

```bash
# Using locust
pip install locust

# Run load test
locust -f tests/locustfile.py -u 100 -r 10 --run-time 1m --headless
```

---

## Monitoring & Maintenance

### Logging

```bash
# Centralized logging (ELK stack)
# Logs automatically sent to Elasticsearch

# View logs
docker-compose logs -f backend --tail 100

# Export logs
docker-compose logs backend > backend_$(date +%Y%m%d_%H%M%S).log
```

### Metrics & Observability

```bash
# Prometheus metrics at /metrics
curl http://localhost:8000/metrics

# Grafana dashboard (included in docker-compose)
# Access at http://localhost:3001
```

### Health Checks

```bash
# Liveness probe (container health)
GET /health
Response: {"status": "healthy"}

# Readiness probe (service readiness)
GET /ready
Response: {"status": "ready", "database": "connected"}

# Detailed diagnostics
GET /system/status
Response: {
  "api": "ok",
  "database": "ok",
  "encryption": "ok",
  "terraform": "ok"
}
```

### Maintenance Tasks

```bash
# Daily: Verify backups
ls -lh /backups/ | tail -5

# Weekly: Check disk space
df -h / | grep cloudguardian

# Monthly: Vacuum database
docker-compose exec postgres vacuumdb -U cloudguardian cloudguardian_prod

# Quarterly: Update dependencies
cd apps/backend
pip list --outdated
pip install --upgrade pip -r requirements.txt
```

---

## Troubleshooting

### Issue: "Failed to connect to database"

```bash
# Check database service
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection directly
psql $DATABASE_URL

# Check PostgreSQL logs
docker-compose logs postgres
```

### Issue: "Terraform binary not found"

```bash
# Install Terraform
apt-get install terraform

# Verify installation
terraform --version

# Check PATH
which terraform
echo $PATH

# Update .env
TERRAFORM_BIN=/usr/bin/terraform
```

### Issue: "Secret scan timeout"

```bash
# Increase timeout in main.py
# Adjust scanner for large files
# Consider async processing with Celery
```

### Issue: "Out of memory"

```bash
# Check memory usage
docker stats

# Increase container memory limit
# docker-compose.yml:
  backend:
    mem_limit: 2g
```

---

## Disaster Recovery

### Backup Strategy

```bash
# Automated daily backups
0 2 * * * /scripts/backup.sh

# Backup script
#!/bin/bash
DB_NAME=cloudguardian_prod
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

### Recovery Process

```bash
# 1. Stop services
docker-compose down

# 2. Restore database from backup
gunzip < /backups/db_20240101_020000.sql.gz | psql cloudguardian_prod

# 3. Restart services
docker-compose up -d

# 4. Verify
curl http://localhost:8000/health
```

### Replication Setup (High Availability)

```bash
# PostgreSQL streaming replication
# Primary: main database
# Standby: read-only replica

# In primary's postgresql.conf:
wal_level = replica
max_wal_senders = 5

# In standby's postgresql.conf:
standby_mode = 'on'
primary_conninfo = 'host=primary_ip port=5432 user=replication password=xxx'
```

---

## Support & Resources

- **Documentation**: [docs/](../docs/)
- **API Reference**: http://localhost:8000/docs
- **Issues**: https://github.com/cloudguardian/cloudguardian/issues
- **Discussions**: https://github.com/cloudguardian/cloudguardian/discussions

---

## Changelog

**v1.0.0** (Nov 2025)
- ✅ Production-ready API
- ✅ Auto-remediation engine
- ✅ Compliance reporting (SOC2, ISO27001, HIPAA, GDPR, PCI-DSS)
- ✅ Secret scanning (regex + entropy)
- ✅ Infrastructure graph visualization
- ✅ Drift detection

---

**Last Updated**: 2025-11-23  
**Maintained by**: CloudGuardian Team
