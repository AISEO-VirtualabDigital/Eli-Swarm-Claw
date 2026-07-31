"""Mock provider for testing and development."""

import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from eliseo.providers.base import (
    BaseProvider,
    ProviderConfig,
    GenerationRequest,
    GenerationResponse,
    JobStatus,
    ProviderType,
)


class MockProvider(BaseProvider):
    """Mock provider for testing without real API calls."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._jobs: Dict[str, GenerationResponse] = {}
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize mock provider."""
        self._initialized = True
        return True

    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate mock image."""
        job_id = str(uuid.uuid4())
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        response = GenerationResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            provider=ProviderType.MOCK,
            asset_urls=[f"https://mock-storage.example.com/images/{job_id}.png"],
            thumbnail_url=f"https://mock-storage.example.com/thumbnails/{job_id}_thumb.png",
            metadata={
                "prompt": request.prompt,
                "width": request.width,
                "height": request.height,
                "model": request.model or "mock-model-v1",
                "seed": request.seed or 42,
            },
            cost_usd=0.0,
            processing_time_ms=500,
        )
        
        self._jobs[job_id] = response
        return response

    async def generate_video(self, request: GenerationRequest) -> GenerationResponse:
        """Generate mock video."""
        job_id = str(uuid.uuid4())
        
        # Simulate longer processing delay for video
        await asyncio.sleep(1.0)
        
        response = GenerationResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            provider=ProviderType.MOCK,
            asset_urls=[f"https://mock-storage.example.com/videos/{job_id}.mp4"],
            thumbnail_url=f"https://mock-storage.example.com/thumbnails/{job_id}_thumb.jpg",
            metadata={
                "prompt": request.prompt,
                "duration_seconds": 5,
                "fps": 24,
                "resolution": f"{request.width}x{request.height}",
                "model": request.model or "mock-video-v1",
            },
            cost_usd=0.0,
            processing_time_ms=1000,
        )
        
        self._jobs[job_id] = response
        return response

    async def check_status(self, job_id: str) -> GenerationResponse:
        """Check job status."""
        if job_id in self._jobs:
            return self._jobs[job_id]
        
        return GenerationResponse(
            job_id=job_id,
            status=JobStatus.FAILED,
            provider=ProviderType.MOCK,
            error_message="Job not found",
        )

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        if job_id in self._jobs:
            self._jobs[job_id].status = JobStatus.CANCELLED
            return True
        return False

    def get_cost_estimate(self, request: GenerationRequest) -> float:
        """Get cost estimate (always 0 for mock)."""
        return 0.0

    def is_available(self) -> bool:
        """Check if mock provider is available."""
        return self._initialized

    def clear_jobs(self):
        """Clear all mock jobs (for testing)."""
        self._jobs.clear()
