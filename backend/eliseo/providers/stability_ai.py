"""Stability AI provider implementation."""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
import os

from eliseo.providers.base import (
    BaseProvider,
    ProviderConfig,
    GenerationRequest,
    GenerationResponse,
    JobStatus,
    ProviderType,
)


class StabilityAIProvider(BaseProvider):
    """Stability AI provider for image generation."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        self.base_url = config.base_url or "https://api.stability.ai"
        self.model_name = config.model_name or "stable-diffusion-xl-1024-v1-0"

    async def initialize(self) -> bool:
        """Initialize Stability AI client."""
        if not self.config.api_key:
            return False
        
        try:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            )
            
            # Quick health check
            async with self._session.get(f"{self.base_url}/v1/engines/list") as resp:
                if resp.status == 200:
                    self._initialized = True
                    return True
                elif resp.status == 401:
                    raise ValueError("Invalid API key")
                else:
                    # Still initialize even if list fails (API might differ)
                    self._initialized = True
                    return True
        except Exception as e:
            print(f"Failed to initialize Stability AI: {e}")
            return False

    async def close(self):
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
            self._initialized = False

    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate image using Stability AI."""
        import uuid
        import time
        
        start_time = time.time()
        job_id = str(uuid.uuid4())
        
        if not self._initialized or not self._session:
            return GenerationResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                provider=ProviderType.STABILITY_AI,
                error_message="Provider not initialized",
            )
        
        try:
            # Stability AI text-to-image endpoint
            endpoint = f"{self.base_url}/v2beta/stable-image/generate/core"
            
            payload = {
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt or "",
                "width": request.width or 1024,
                "height": request.height or 1024,
                "steps": request.steps or 30,
                "cfg_scale": request.guidance_scale or 7.5,
                "seed": request.seed or None,
                "output_format": request.output_format or "png",
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            async with self._session.post(endpoint, json=payload) as resp:
                if resp.status == 200:
                    # Get image data
                    image_data = await resp.read()
                    
                    # In production, this would save to storage service
                    # For now, we create a mock URL
                    file_size = len(image_data)
                    
                    processing_time = int((time.time() - start_time) * 1000)
                    
                    # Cost estimate: ~$0.002-0.007 per image depending on model
                    cost = 0.005
                    
                    return GenerationResponse(
                        job_id=job_id,
                        status=JobStatus.COMPLETED,
                        provider=ProviderType.STABILITY_AI,
                        asset_urls=[f"stability://{job_id}.{request.output_format or 'png'}"],
                        thumbnail_url=f"stability://{job_id}_thumb.jpg",
                        metadata={
                            "prompt": request.prompt,
                            "width": request.width,
                            "height": request.height,
                            "model": self.model_name,
                            "seed": request.seed,
                            "file_size": file_size,
                        },
                        cost_usd=cost,
                        processing_time_ms=processing_time,
                    )
                elif resp.status == 401:
                    return GenerationResponse(
                        job_id=job_id,
                        status=JobStatus.FAILED,
                        provider=ProviderType.STABILITY_AI,
                        error_message="Invalid API key",
                    )
                elif resp.status == 429:
                    return GenerationResponse(
                        job_id=job_id,
                        status=JobStatus.FAILED,
                        provider=ProviderType.STABILITY_AI,
                        error_message="Rate limit exceeded",
                    )
                else:
                    error_text = await resp.text()
                    return GenerationResponse(
                        job_id=job_id,
                        status=JobStatus.FAILED,
                        provider=ProviderType.STABILITY_AI,
                        error_message=f"API error: {resp.status} - {error_text}",
                    )
                    
        except asyncio.TimeoutError:
            return GenerationResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                provider=ProviderType.STABILITY_AI,
                error_message="Request timed out",
            )
        except Exception as e:
            return GenerationResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                provider=ProviderType.STABILITY_AI,
                error_message=f"Generation failed: {str(e)}",
            )

    async def generate_video(self, request: GenerationRequest) -> GenerationResponse:
        """Generate video using Stability AI (if supported)."""
        # Stability AI currently focuses on images
        # This would need to use a different provider or their video API if available
        return GenerationResponse(
            job_id=str(uuid.uuid4()),
            status=JobStatus.FAILED,
            provider=ProviderType.STABILITY_AI,
            error_message="Video generation not supported by Stability AI. Use RunwayML or Replicate.",
        )

    async def check_status(self, job_id: str) -> GenerationResponse:
        """Check job status (for sync operations, always completed or failed)."""
        # Stability AI core API is synchronous
        # For async jobs, you'd need to implement polling logic
        return GenerationResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            provider=ProviderType.STABILITY_AI,
            error_message="Use generate_image for new jobs",
        )

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job (not supported for sync API)."""
        return False

    def get_cost_estimate(self, request: GenerationRequest) -> float:
        """Estimate cost for image generation."""
        # Stability AI pricing varies by model and resolution
        # Approximate: $0.002-0.007 per image
        base_cost = 0.005
        
        # Higher resolution costs more
        if request.width and request.height:
            pixels = request.width * request.height
            if pixels > 1024 * 1024:
                base_cost *= 1.5
            if pixels > 2048 * 2048:
                base_cost *= 2.0
        
        return base_cost * (request.batch_size or 1)

    def is_available(self) -> bool:
        """Check if Stability AI is available."""
        return self._initialized and self.config.api_key is not None

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Stability AI."""
        if not self._initialized or not self._session:
            return {
                "provider": ProviderType.STABILITY_AI.value,
                "available": False,
                "initialized": False,
                "error": "Not initialized",
            }
        
        try:
            async with self._session.get(f"{self.base_url}/v1/engines/list") as resp:
                return {
                    "provider": ProviderType.STABILITY_AI.value,
                    "available": resp.status == 200,
                    "initialized": True,
                    "status_code": resp.status,
                }
        except Exception as e:
            return {
                "provider": ProviderType.STABILITY_AI.value,
                "available": False,
                "initialized": True,
                "error": str(e),
            }
