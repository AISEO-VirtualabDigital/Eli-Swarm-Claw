# Eli Claw Production Foundation

## Overview

This document describes the production-ready foundation for Eli Claw's AI media generation system. The architecture is **VPS-first**, meaning it's designed to be self-hosted on a single VPS before scaling to cloud services.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Media Jobs   │  │ Batch Jobs   │  │ Webhooks     │      │
│  │ API          │  │ API          │  │ API          │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Redis       │  │  PostgreSQL   │  │   Storage     │
│   (Queue)     │  │  (Database)   │  │   (Local/MinIO)│
└───────────────┘  └───────────────┘  └───────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Celery Workers                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Media Gen    │  │ Batch Proc   │  │ Notifications│      │
│  │ Queue        │  │ Queue        │  │ Queue        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Provider Integrations                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Stability │ │ OpenAI   │ │ RunwayML │ │Replicate │       │
│  │ AI       │ │ DALL-E   │ │          │ │          │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Provider Abstraction Layer

Located in: `/workspace/backend/eliseo/providers/`

**Base Classes:**
- `BaseProvider` - Abstract interface for all providers
- `ProviderConfig` - Configuration model
- `GenerationRequest` - Standardized request format
- `GenerationResponse` - Standardized response format

**Implemented Providers:**
- `MockProvider` - For testing without API keys
- `StabilityAIProvider` - Stability AI image generation

**Placeholder Providers:**
- `OpenAIImageProvider` - DALL-E 3 integration
- `RunwayProvider` - Video generation
- `ReplicateProvider` - Multiple models

**Usage Example:**
```python
from eliseo.providers.base import ProviderConfig, ProviderType
from eliseo.providers.stability_ai import StabilityAIProvider

config = ProviderConfig(
    provider_type=ProviderType.STABILITY_AI,
    api_key="sk-your-key",
    model_name="stable-diffusion-xl-1024-v1-0",
)

provider = StabilityAIProvider(config)
await provider.initialize()

response = await provider.generate_image(
    GenerationRequest(prompt="A beautiful sunset")
)
```

### 2. Storage Service

Located in: `/workspace/backend/eliseo/storage/`

**Providers:**
- `LocalStorageProvider` - VPS filesystem (default)
- `MinIOStorageProvider` - S3-compatible object storage

**File Structure:**
```
/app/storage/media/
└── organizations/
    └── {org_id}/
        └── projects/
            └── {project_id}/
                └── media/
                    └── {job_id}/
                        └── {filename}
```

**Usage Example:**
```python
from eliseo.storage.service import LocalStorageProvider

storage = LocalStorageProvider("/app/storage/media")

result = await storage.upload(
    file=file_object,
    filename="image.png",
    content_type="image/png",
    organization_id=1,
    project_id=42,
    job_id="job_123",
)
```

### 3. Content Moderation

Located in `/workspace/backend/eliseo/moderation/`

**Providers:**
- `RuleBasedModerationProvider` - Blocklist/pattern matching (no API required)
- `OpenAIModerationProvider` - OpenAI Moderation API

**Categories Checked:**
- Sexual content
- Violence
- Self-harm
- Hate speech
- Illegal activity
- Copyright
- Impersonation
- Political manipulation

**Usage Example:**
```python
from eliseo.moderation.service import (
    ModerationService,
    RuleBasedModerationProvider,
)

provider = RuleBasedModerationProvider()
service = ModerationService(provider, block_unsafe=True)

result = await service.check_prompt("Generate an image of...")

if result.status == "blocked":
    print(f"Blocked: {result.flagged_categories}")
```

### 4. Celery Task Queue

Located in: `/workspace/backend/eliseo/tasks/`

**Queues:**
- `media_generation` - Image/video generation jobs
- `batch_processing` - Batch job processing
- `notifications` - Webhook and email delivery

**Tasks:**
- `generate_media_job` - Process single media generation
- `process_batch_job` - Process batch of generations
- `send_webhook_delivery` - Send webhook notifications

**Configuration:**
```python
# .env
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### 5. Database Models

Key models for media generation:

**MediaJob:**
- Tracks individual generation requests
- Status: queued, processing, completed, failed, cancelled
- Stores prompt, parameters, provider info

**MediaAsset:**
- Stores generated media metadata
- Links to storage location
- Includes SEO fields (alt text, caption, etc.)

**BatchJob:**
- Groups multiple generation jobs
- Tracks overall progress
- Aggregates results

**Webhook:**
- Configures external notifications
- Supports signing secrets
- Tracks delivery attempts

## Environment Variables

See `.env.example` for complete list. Key variables:

```bash
# Provider Keys
STABILITY_API_KEY=sk-...
OPENAI_API_KEY=sk-...

# Storage
MEDIA_STORAGE_PROVIDER=local
MINIO_ENDPOINT=localhost:9000

# Queue
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Moderation
MODERATION_ENABLED=true
BLOCK_UNSAFE_PROMPTS=true
```

## Deployment

### Local Development

```bash
# Start infrastructure
cd infra
docker-compose up -d postgres redis

# Run API
cd ../apps/api
uvicorn app.main:app --reload

# Run Celery worker (separate terminal)
cd ../../backend
celery -A eliseo.celery_config:celery_app worker -l info -Q media_generation,batch_processing,notifications
```

### VPS Production

1. **Prerequisites:**
   - Ubuntu 22.04+ VPS with 4GB+ RAM
   - Docker & Docker Compose installed
   - Domain configured

2. **Setup:**
```bash
# Clone repository
git clone <repo> /opt/eliclaw
cd /opt/eliclaw

# Copy environment files
cp .env.example .env
# Edit .env with your values

# Start all services
docker-compose -f infra/docker-compose.prod.yml up -d

# Run migrations
docker-compose exec api alembic upgrade head
```

3. **Services:**
   - API: Port 8000 (behind nginx)
   - PostgreSQL: Internal
   - Redis: Internal
   - MinIO: Port 9000 (optional)
   - Celery Workers: Background

## API Endpoints

### Media Jobs
```
POST   /api/v1/media/jobs           # Create generation job
GET    /api/v1/media/jobs           # List jobs
GET    /api/v1/media/jobs/{id}      # Get job details
POST   /api/v1/media/jobs/{id}/cancel
POST   /api/v1/media/jobs/{id}/retry
```

### Media Assets
```
GET    /api/v1/media/assets         # List assets
GET    /api/v1/media/assets/{id}    # Get asset
PATCH  /api/v1/media/assets/{id}    # Update metadata
DELETE /api/v1/media/assets/{id}    # Delete asset
```

### Batch Jobs
```
POST   /api/v1/media/batches        # Create batch
GET    /api/v1/media/batches        # List batches
GET    /api/v1/media/batches/{id}   # Get batch status
POST   /api/v1/media/batches/{id}/cancel
POST   /api/v1/media/batches/{id}/retry-failed
```

### Webhooks
```
POST   /api/v1/webhooks             # Create webhook
GET    /api/v1/webhooks             # List webhooks
PATCH  /api/v1/webhooks/{id}        # Update webhook
DELETE /api/v1/webhooks/{id}        # Delete webhook
POST   /api/v1/webhooks/{id}/test   # Test webhook
GET    /api/v1/webhooks/{id}/deliveries
```

## Testing

All tests use mock providers - no API keys required:

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test categories
pytest backend/tests/providers/ -v
pytest backend/tests/services/ -v
```

## Security Considerations

1. **API Keys:** Never commit to version control. Use environment variables only.
2. **Moderation:** Always enable in production (`MODERATION_ENABLED=true`)
3. **Tenant Isolation:** All queries filtered by organization_id
4. **Rate Limiting:** Implement at API gateway level
5. **Storage:** Use signed URLs for private assets

## Next Steps

1. Add real API keys to `.env` (not committed)
2. Configure Stability AI as first provider
3. Test single image generation end-to-end
4. Build frontend UI components
5. Deploy to VPS

## Troubleshooting

**Provider initialization fails:**
- Check API key is set correctly
- Verify network connectivity
- Check provider status page

**Celery tasks not processing:**
- Ensure Redis is running
- Check worker logs: `celery -A eliseo.celery_config:celery_app worker -l debug`
- Verify queue names match

**Storage errors:**
- Check directory permissions for local storage
- Verify MinIO credentials if using object storage
- Ensure disk space available
