"""Pydantic schemas for AI Studio - Generative Media Engine."""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MediaType(str, Enum):
    """Types of media that can be generated."""
    IMAGE = "image"
    VIDEO = "video"


class GenerationStatus(str, Enum):
    """Status of a generation job."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProviderStatus(str, Enum):
    """Status of a provider configuration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


# ============ Provider Schemas ============

class MediaProviderBase(BaseModel):
    """Base schema for media provider."""
    name: str = Field(..., description="Provider identifier")
    display_name: Optional[str] = None
    provider_type: str = Field(..., description="image, video, or both")
    base_url: Optional[HttpUrl] = None
    api_version: Optional[str] = None
    supported_models: List[str] = []
    max_image_resolution: Optional[str] = None
    max_video_duration: Optional[int] = None
    supports_upscaling: bool = False
    supports_inpainting: bool = False
    cost_per_image: float = 0.0
    cost_per_video: float = 0.0
    currency: str = "USD"
    requests_per_minute: int = 60
    concurrent_jobs: int = 5
    priority: int = 1


class MediaProviderCreate(MediaProviderBase):
    """Schema for creating a media provider."""
    api_key: str = Field(..., description="API key for the provider")


class MediaProviderUpdate(BaseModel):
    """Schema for updating a media provider."""
    display_name: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    supported_models: Optional[List[str]] = None
    max_image_resolution: Optional[str] = None
    max_video_duration: Optional[int] = None
    supports_upscaling: Optional[bool] = None
    supports_inpainting: Optional[bool] = None
    cost_per_image: Optional[float] = None
    cost_per_video: Optional[float] = None
    requests_per_minute: Optional[int] = None
    concurrent_jobs: Optional[int] = None
    priority: Optional[int] = None
    status: Optional[ProviderStatus] = None
    fallback_provider_id: Optional[int] = None


class MediaProviderResponse(MediaProviderBase):
    """Schema for media provider response."""
    id: int
    status: ProviderStatus
    success_rate: float
    average_latency: float
    last_health_check: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Job Schemas ============

class MediaJobBase(BaseModel):
    """Base schema for media job."""
    media_type: MediaType
    generation_type: str = Field(..., description="text_to_image, text_to_video, etc.")
    prompt: str = Field(..., min_length=1, max_length=5000)
    negative_prompt: Optional[str] = None
    style_preset: Optional[str] = None
    seed: Optional[int] = None
    width: int = 1024
    height: int = 1024
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    duration: Optional[int] = None  # For video
    fps: int = 24


class MediaJobCreate(MediaJobBase):
    """Schema for creating a media job."""
    project_id: Optional[int] = None
    campaign_id: Optional[int] = None
    provider_id: Optional[int] = None
    metadata: Dict[str, Any] = {}


class MediaJobUpdate(BaseModel):
    """Schema for updating a media job."""
    status: Optional[GenerationStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    retry_count: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None


class MediaJobResponse(MediaJobBase):
    """Schema for media job response."""
    id: int
    job_id: str
    status: GenerationStatus
    progress: int
    retry_count: int
    max_retries: int
    provider_id: Optional[int] = None
    project_id: Optional[int] = None
    user_id: Optional[int] = None
    campaign_id: Optional[int] = None
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    estimated_cost: float
    actual_cost: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Asset Schemas ============

class MediaAssetBase(BaseModel):
    """Base schema for media asset."""
    media_type: MediaType
    format: str
    storage_type: str = "local"
    file_path: Optional[str] = None
    public_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    quality: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    tags: List[str] = []
    is_public: bool = False


class MediaAssetCreate(MediaAssetBase):
    """Schema for creating a media asset."""
    job_id: int
    provider_id: Optional[int] = None
    project_id: Optional[int] = None
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    generation_params: Dict[str, Any] = {}


class MediaAssetUpdate(BaseModel):
    """Schema for updating a media asset."""
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    download_count: Optional[int] = None
    view_count: Optional[int] = None
    share_count: Optional[int] = None


class MediaAssetResponse(MediaAssetBase):
    """Schema for media asset response."""
    id: int
    asset_id: str
    job_id: int
    provider_id: Optional[int] = None
    project_id: Optional[int] = None
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    generation_params: Dict[str, Any] = {}
    download_count: int
    view_count: int
    share_count: int
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Metrics Schemas ============

class MediaMetricsBase(BaseModel):
    """Base schema for media metrics."""
    date: datetime
    period_type: str = "daily"
    provider_id: Optional[int] = None
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0
    image_jobs: int = 0
    video_jobs: int = 0
    average_queue_time: float = 0.0
    average_generation_time: float = 0.0
    average_total_time: float = 0.0
    p95_generation_time: float = 0.0
    p99_generation_time: float = 0.0
    success_rate: float = 100.0
    retry_rate: float = 0.0
    average_retries: float = 0.0
    total_cost: float = 0.0
    average_cost_per_image: float = 0.0
    average_cost_per_video: float = 0.0
    cost_per_successful_output: float = 0.0
    rate_limit_hits: int = 0
    timeout_errors: int = 0
    api_errors: int = 0


class MediaMetricsResponse(MediaMetricsBase):
    """Schema for media metrics response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Request/Response Schemas ============

class GenerateImageRequest(BaseModel):
    """Request schema for generating an image."""
    prompt: str = Field(..., min_length=1, max_length=5000)
    negative_prompt: Optional[str] = None
    style_preset: Optional[str] = None
    width: int = 1024
    height: int = 1024
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    project_id: Optional[int] = None
    campaign_id: Optional[int] = None
    provider_id: Optional[int] = None


class GenerateVideoRequest(BaseModel):
    """Request schema for generating a video."""
    prompt: str = Field(..., min_length=1, max_length=5000)
    negative_prompt: Optional[str] = None
    style_preset: Optional[str] = None
    duration: int = Field(default=5, ge=1, le=60)
    fps: int = 24
    width: int = 1024
    height: int = 1024
    seed: Optional[int] = None
    project_id: Optional[int] = None
    campaign_id: Optional[int] = None
    provider_id: Optional[int] = None


class JobStatusResponse(BaseModel):
    """Response schema for job status check."""
    job_id: str
    status: GenerationStatus
    progress: int
    media_type: MediaType
    result_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds


class GenerationMetricsResponse(BaseModel):
    """Response schema for generation metrics."""
    provider_name: str
    total_jobs: int
    success_rate: float
    average_generation_time: float
    cost_per_successful_output: float
    queue_time: float
    generation_time: float
    total_time: float
