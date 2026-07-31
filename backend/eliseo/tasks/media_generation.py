"""Celery tasks for AI media generation."""

import asyncio
import time
from typing import Optional, Dict, Any
from datetime import datetime

from eliseo.celery_config import celery_app
from eliseo.providers.base import (
    ProviderType,
    ProviderConfig,
    GenerationRequest,
    JobStatus,
)
from eliseo.providers.mock_provider import MockProvider


@celery_app.task(bind=True, max_retries=3)
def generate_image_task(
    self,
    job_id: str,
    prompt: str,
    provider_type: str = "mock",
    width: int = 1024,
    height: int = 1024,
    model: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    steps: int = 30,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    style_preset: Optional[str] = None,
    output_format: str = "png",
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate image using Celery worker."""
    
    start_time = time.time()
    
    try:
        # Create provider config
        config = ProviderConfig(
            provider_type=ProviderType(provider_type),
            timeout_seconds=300,
            max_retries=3,
        )
        
        # Initialize provider (using mock for now)
        provider = MockProvider(config)
        asyncio.run(provider.initialize())
        
        # Create generation request
        request = GenerationRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=guidance_scale,
            seed=seed,
            model=model,
            style_preset=style_preset,
            output_format=output_format,
        )
        
        # Generate image
        response = asyncio.run(provider.generate_image(request))
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "job_id": job_id,
            "status": response.status.value,
            "asset_urls": response.asset_urls,
            "thumbnail_url": response.thumbnail_url,
            "metadata": response.metadata,
            "cost_usd": response.cost_usd,
            "processing_time_ms": processing_time_ms,
            "completed_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        # Retry logic
        retry_in = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_in)


@celery_app.task(bind=True, max_retries=3)
def generate_video_task(
    self,
    job_id: str,
    prompt: str,
    provider_type: str = "mock",
    width: int = 1024,
    height: int = 1024,
    duration_seconds: int = 5,
    fps: int = 24,
    model: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    output_format: str = "mp4",
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate video using Celery worker."""
    
    start_time = time.time()
    
    try:
        # Create provider config
        config = ProviderConfig(
            provider_type=ProviderType(provider_type),
            timeout_seconds=600,  # Videos take longer
            max_retries=3,
        )
        
        # Initialize provider (using mock for now)
        provider = MockProvider(config)
        asyncio.run(provider.initialize())
        
        # Create generation request
        request = GenerationRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            seed=seed,
            model=model,
            output_format=output_format,
            extra_params={
                "duration_seconds": duration_seconds,
                "fps": fps,
            },
        )
        
        # Generate video
        response = asyncio.run(provider.generate_video(request))
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "job_id": job_id,
            "status": response.status.value,
            "asset_urls": response.asset_urls,
            "thumbnail_url": response.thumbnail_url,
            "metadata": response.metadata,
            "cost_usd": response.cost_usd,
            "processing_time_ms": processing_time_ms,
            "completed_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        # Retry logic
        retry_in = 120 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_in)


@celery_app.task
def check_job_status_task(job_id: str, provider_type: str = "mock") -> Dict[str, Any]:
    """Check status of a generation job."""
    
    config = ProviderConfig(provider_type=ProviderType(provider_type))
    provider = MockProvider(config)
    asyncio.run(provider.initialize())
    
    response = asyncio.run(provider.check_status(job_id))
    
    return {
        "job_id": job_id,
        "status": response.status.value,
        "asset_urls": response.asset_urls,
        "error_message": response.error_message,
    }


@celery_app.task
def cancel_job_task(job_id: str, provider_type: str = "mock") -> bool:
    """Cancel a running job."""
    
    config = ProviderConfig(provider_type=ProviderType(provider_type))
    provider = MockProvider(config)
    asyncio.run(provider.initialize())
    
    return asyncio.run(provider.cancel_job(job_id))
