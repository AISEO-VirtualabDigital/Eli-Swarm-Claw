"""Base provider interface for AI media generation."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from enum import Enum


class ProviderType(str, Enum):
    """Supported AI media providers."""
    OPENAI_DALLE = "openai_dalle"
    OPENAI_VIDEO = "openai_video"
    STABILITY_AI = "stability_ai"
    RUNWAYML = "runwayml"
    REPLICATE = "replicate"
    ELEVENLABS = "elevenlabs"
    GOOGLE_VERTEX = "google_vertex"
    MOCK = "mock"


class JobStatus(str, Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    PARTIALLY_COMPLETED = "partially_completed"


class GenerationRequest(BaseModel):
    """Standardized generation request."""
    prompt: str
    negative_prompt: Optional[str] = None
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    steps: Optional[int] = 30
    guidance_scale: Optional[float] = 7.5
    seed: Optional[int] = None
    model: Optional[str] = None
    style_preset: Optional[str] = None
    batch_size: Optional[int] = 1
    output_format: Optional[str] = "png"
    extra_params: Optional[Dict[str, Any]] = None


class GenerationResponse(BaseModel):
    """Standardized generation response."""
    job_id: str
    status: JobStatus
    provider: ProviderType
    asset_urls: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    cost_usd: Optional[float] = None
    processing_time_ms: Optional[int] = None


class ProviderConfig(BaseModel):
    """Provider configuration."""
    provider_type: ProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    timeout_seconds: int = 300
    max_retries: int = 3
    rate_limit_requests: Optional[int] = None
    rate_limit_period_seconds: Optional[int] = None
    enabled: bool = True
    priority: int = 1  # Lower = higher priority for fallback


class BaseProvider(ABC):
    """Abstract base class for all AI media providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize provider connection and validate credentials."""
        pass

    @abstractmethod
    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate image from prompt."""
        pass

    @abstractmethod
    async def generate_video(self, request: GenerationRequest) -> GenerationResponse:
        """Generate video from prompt."""
        pass

    @abstractmethod
    async def check_status(self, job_id: str) -> GenerationResponse:
        """Check job status."""
        pass

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        pass

    @abstractmethod
    def get_cost_estimate(self, request: GenerationRequest) -> float:
        """Estimate cost for a generation request."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on provider."""
        return {
            "provider": self.config.provider_type.value,
            "available": self.is_available(),
            "initialized": self._initialized,
        }
