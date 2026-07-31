# Eli Claw - Environment Variables Loading Guide

## Overview
Eli Claw uses a **separated environment file strategy** for better security, organization, and deployment flexibility. Each configuration category has its own `.env.*` file.

## Environment Files

### 1. `.env.app` - Application Configuration
- Application name and version
- API prefix settings
- Debug mode
- Security keys (SECRET_KEY)
- CORS settings
- Allowed hosts

### 2. `.env.database` - Database Configuration
- PostgreSQL connection URL
- Connection pool settings
- Alembic migration config

### 3. `.env.queue` - Queue & Cache Configuration
- Redis connection URL
- Celery broker/backend settings
- Worker concurrency settings
- Task serialization options

### 4. `.env.storage` - Storage Configuration
- Storage provider type (local, minio, s3, gcs, etc.)
- Provider-specific credentials
- File size limits
- Allowed extensions

### 5. `.env.providers` - AI Provider Configuration
- **SENSITIVE**: API keys for AI providers
- OpenAI, Stability AI, RunwayML, Replicate
- ElevenLabs, Google Vertex AI
- Rate limits
- Fallback order

### 6. `.env.moderation` - Content Moderation Configuration
- Moderation enabled/disabled
- Provider selection
- Sensitivity thresholds
- Custom blocklists/allowlists
- Audit logging settings

### 7. `.env.notifications` - Webhooks & Notifications
- Webhook timeout and retry settings
- Email provider configuration
- Slack/Discord integrations

## Loading Strategy

### Development
```bash
# Load all environment files
set -a
source .env.app
source .env.database
source .env.queue
source .env.storage
source .env.providers
source .env.moderation
source .env.notifications
set +a

# Start application
python -m uvicorn apps.api.app.api.main:app --reload
```

### Production (Docker)
```dockerfile
# In docker-compose.yml
environment:
  - APP_NAME=${APP_NAME}
  - DATABASE_URL=${DATABASE_URL}
  - REDIS_URL=${REDIS_URL}
  # ... load each variable as needed
```

### Production (VPS)
```bash
# Use systemd service with EnvironmentFile
# /etc/systemd/system/eliclaw.service
[Service]
EnvironmentFile=/etc/eliclaw/.env.app
EnvironmentFile=/etc/eliclaw/.env.database
EnvironmentFile=/etc/eliclaw/.env.queue
# ... etc
```

## Security Best Practices

1. **Never commit `.env.providers`** - Contains API keys
2. **Set restrictive permissions**:
   ```bash
   chmod 600 .env.providers
   chmod 600 .env.storage
   chmod 640 .env.*
   ```
3. **Use secrets management in production**:
   - Docker secrets
   - HashiCorp Vault
   - AWS Secrets Manager
   - Kubernetes Secrets

4. **Rotate keys regularly**
5. **Use different keys per environment** (dev, staging, prod)

## Required vs Optional Files

### Required (Must configure):
- `.env.app` - Core application settings
- `.env.database` - Database connection
- `.env.queue` - Redis/Celery (can use defaults for dev)

### Optional (Can use defaults):
- `.env.storage` - Defaults to local storage
- `.env.providers` - Uses mock provider if empty
- `.env.moderation` - Has safe defaults
- `.env.notifications` - Not required for core functionality

## Example Quick Start

```bash
# Copy example files
cp .env.app.example .env.app
cp .env.database.example .env.database
cp .env.queue.example .env.queue

# Edit with your values
nano .env.app
nano .env.database

# Start services
docker-compose up -d postgres redis
python -m pytest backend/tests/  # Verify setup
```

## Troubleshooting

### Module not found errors
Ensure PYTHONPATH includes backend directory:
```bash
export PYTHONPATH=/workspace/backend:$PYTHONPATH
```

### Redis connection errors
Check Redis is running:
```bash
redis-cli ping  # Should return PONG
```

### Database connection errors
Verify PostgreSQL is running and accessible:
```bash
psql $DATABASE_URL -c "SELECT 1"
```
