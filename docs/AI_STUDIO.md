# AI Studio - Generative Media Engine

## Overview

AI Studio is a powerful generative media engine integrated into Eli Claw that enables users to generate AI-powered images and videos directly within the platform for SEO assets, content briefs, and social media content.

## Features

### Core Capabilities
- **Text-to-Image Generation**: Generate high-quality images from text prompts
- **Text-to-Video Generation**: Create short video clips from text descriptions
- **Multi-Provider Support**: Configure multiple AI providers with automatic fallback
- **Cost Tracking**: Monitor costs per generation across providers
- **Metrics & Analytics**: Track success rates, latency, and queue times
- **SEO Integration**: Link generated assets to projects and campaigns

### Provider Management
- Support for multiple AI backends (Stable Diffusion, DALL-E 3, RunwayML, etc.)
- Automatic provider selection based on priority and availability
- Fallback configuration for reliability
- Rate limiting and concurrent job management
- Health monitoring and status tracking

### Job Processing
- Async job queue for long-running generation tasks
- Real-time progress tracking (0-100%)
- Retry logic with configurable max retries
- Job cancellation support
- Cost estimation and actual cost tracking

### Asset Management
- Centralized storage for generated media
- Metadata editing (title, description, alt text, tags)
- Usage tracking (downloads, views, shares)
- Soft delete capability
- Public/private visibility control

## Database Models

### MediaProvider
Configuration for AI media generation services.
- `name`: Provider identifier (e.g., "stable_diffusion", "dalle3")
- `provider_type`: "image", "video", or "both"
- `base_url`, `api_key`: API configuration
- `supported_models`: List of available models
- `cost_per_image`, `cost_per_video`: Pricing information
- `priority`: Selection priority (lower = higher priority)
- `fallback_provider_id`: Backup provider
- `status`: ACTIVE, INACTIVE, or ERROR

### MediaJob
Tracking for async media generation tasks.
- `job_id`: Unique external job identifier
- `media_type`: IMAGE or VIDEO
- `generation_type`: "text_to_image", "text_to_video", etc.
- `prompt`, `negative_prompt`: Generation parameters
- `width`, `height`, `duration`, `fps`: Output specifications
- `status`: PENDING, QUEUED, PROCESSING, COMPLETED, FAILED, CANCELLED
- `progress`: 0-100 completion percentage
- `estimated_cost`, `actual_cost`: Cost tracking

### MediaAsset
Generated media asset storage and metadata.
- `asset_id`: Unique asset identifier
- `job_id`: Reference to generation job
- `media_type`, `format`: File type information
- `storage_type`, `file_path`, `public_url`: Storage locations
- `width`, `height`, `duration`, `file_size`: Technical specs
- `title`, `description`, `alt_text`, `tags`: SEO metadata
- `download_count`, `view_count`, `share_count`: Usage metrics

### MediaMetrics
Aggregated performance metrics.
- Time-based aggregation (hourly, daily, weekly, monthly)
- Success/failure rates
- Average and percentile generation times
- Cost metrics per successful output
- Error breakdown (rate limits, timeouts, API errors)

## API Endpoints

### Provider Management
```
GET    /api/v1/media/providers          # List all providers
GET    /api/v1/media/providers/{id}     # Get provider details
POST   /api/v1/media/providers          # Create provider
PUT    /api/v1/media/providers/{id}     # Update provider
DELETE /api/v1/media/providers/{id}     # Delete provider
```

### Image Generation
```
POST   /api/v1/media/generate/image     # Generate image from prompt
```

### Video Generation
```
POST   /api/v1/media/generate/video     # Generate video from prompt
```

### Job Management
```
GET    /api/v1/media/jobs               # List jobs
GET    /api/v1/media/jobs/{id}          # Get job details
GET    /api/v1/media/jobs/{id}/status   # Get job status
POST   /api/v1/media/jobs/{id}/cancel   # Cancel job
```

### Asset Management
```
GET    /api/v1/media/assets             # List assets
GET    /api/v1/media/assets/{id}        # Get asset details
PUT    /api/v1/media/assets/{id}        # Update asset metadata
DELETE /api/v1/media/assets/{id}        # Soft delete asset
```

### Metrics
```
GET    /api/v1/media/metrics            # Get generation metrics
```

## Key Metrics to Track

Following community feedback, the system tracks these important metrics:

1. **Cost Metrics**
   - Cost per successful image/video
   - Average cost per provider
   - Total cost by time period

2. **Reliability Metrics**
   - Failed generation / retry rate
   - Success rate by provider
   - Fallback usage frequency

3. **Performance Metrics**
   - Queue time before generation starts
   - Total time to final asset
   - P95/P99 generation times

4. **Quality Metrics**
   - Prompt adherence tracking (via user feedback)
   - Image consistency across variations

5. **Operational Metrics**
   - Provider rate limit hits
   - Timeout errors
   - API error breakdown

## Provider Layer Architecture

The provider abstraction layer enables easy comparison and switching between AI models:

```python
class MediaProvider(Base):
    name: str              # Provider identifier
    base_url: str          # API endpoint
    api_key: str           # Authentication
    provider_type: str     # image/video/both
    supported_models: list # Available models
    cost_per_image: float  # Pricing
    cost_per_video: float
    priority: int          # Selection order
    fallback_provider_id: int  # Backup
```

This design allows:
- Comparing providers by output quality, latency, and cost
- Automatic failover when providers are unavailable
- Easy addition of new AI backends
- A/B testing different providers

## Implementation Files

### Backend (FastAPI)
- `apps/api/app/models/media.py` - Database models
- `apps/api/app/schemas/media.py` - Pydantic schemas
- `apps/api/app/api/media.py` - API routes
- `apps/api/app/models/__init__.py` - Model imports updated
- `apps/api/app/schemas/__init__.py` - Schema imports updated
- `apps/api/app/api/main.py` - Router registration

### Frontend (to be implemented)
- React components for media generation UI
- Job status polling and progress display
- Asset gallery and management
- Provider configuration interface

## Usage Example

### Generate an Image
```bash
curl -X POST http://localhost:8000/api/v1/media/generate/image \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A professional SEO dashboard with charts and graphs",
    "width": 1024,
    "height": 1024,
    "project_id": 1
  }'
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/media/jobs/123/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Generated Assets
```bash
curl http://localhost:8000/api/v1/media/assets?project_id=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Future Enhancements

- [ ] Real provider integrations (Stable Diffusion, DALL-E 3, RunwayML)
- [ ] Celery/Redis integration for production job queue
- [ ] Image enhancement and upscaling
- [ ] Style presets and templates
- [ ] Batch generation support
- [ ] Advanced editing (inpainting, outpainting)
- [ ] User feedback collection for quality improvement
- [ ] A/B testing framework for providers
- [ ] Custom model fine-tuning support

## License

MIT License - Part of Eli Claw AI Search Intelligence Platform
