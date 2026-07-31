"""AI Studio - Generative Media Engine models."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class MediaType(str, enum.Enum):
    """Types of media that can be generated."""
    IMAGE = "image"
    VIDEO = "video"


class GenerationStatus(str, enum.Enum):
    """Status of a generation job."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProviderStatus(str, enum.Enum):
    """Status of a provider configuration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class MediaProvider(Base):
    """Provider configuration for AI media generation services."""
    
    __tablename__ = "media_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "stable_diffusion", "dalle3", "runwayml"
    display_name = Column(String(255))
    provider_type = Column(String(50), nullable=False)  # "image", "video", "both"
    
    # API configuration
    base_url = Column(String(500))
    api_key = Column(String(500))
    api_version = Column(String(50))
    
    # Capabilities
    supported_models = Column(JSON, default=list)  # List of model names
    max_image_resolution = Column(String(20))  # e.g., "1024x1024"
    max_video_duration = Column(Integer)  # seconds
    supports_upscaling = Column(Boolean, default=False)
    supports_inpainting = Column(Boolean, default=False)
    
    # Cost tracking
    cost_per_image = Column(Float, default=0.0)  # USD
    cost_per_video = Column(Float, default=0.0)  # USD per second
    currency = Column(String(10), default="USD")
    
    # Rate limiting
    requests_per_minute = Column(Integer, default=60)
    concurrent_jobs = Column(Integer, default=5)
    
    # Status and fallback
    status = Column(SQLEnum(ProviderStatus), default=ProviderStatus.ACTIVE)
    priority = Column(Integer, default=1)  # Lower = higher priority
    fallback_provider_id = Column(Integer, ForeignKey("media_providers.id"))
    
    # Health monitoring
    success_rate = Column(Float, default=100.0)
    average_latency = Column(Float, default=0.0)  # seconds
    last_health_check = Column(DateTime)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("MediaJob", back_populates="provider")
    assets = relationship("MediaAsset", back_populates="provider")
    
    def __repr__(self) -> str:
        return f"<MediaProvider(id={self.id}, name={self.name})>"


class MediaJob(Base):
    """Job tracking for async media generation tasks."""
    
    __tablename__ = "media_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, nullable=False, index=True)  # External provider job ID
    
    # Job type
    media_type = Column(SQLEnum(MediaType), nullable=False)
    generation_type = Column(String(100), nullable=False)  # "text_to_image", "text_to_video", "image_to_image", "upscale"
    
    # Input data
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text)
    style_preset = Column(String(100))
    seed = Column(Integer)
    
    # Parameters
    width = Column(Integer, default=1024)
    height = Column(Integer, default=1024)
    num_inference_steps = Column(Integer, default=50)
    guidance_scale = Column(Float, default=7.5)
    duration = Column(Integer)  # For video, in seconds
    fps = Column(Integer, default=24)
    
    # Foreign keys
    provider_id = Column(Integer, ForeignKey("media_providers.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    
    # Status tracking
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timing
    queued_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Cost tracking
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Metadata
    extra_metadata = Column("metadata", JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("MediaProvider", back_populates="jobs")
    project = relationship("Project")
    user = relationship("User")
    campaign = relationship("Campaign")
    assets = relationship("MediaAsset", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<MediaJob(id={self.id}, job_id={self.job_id}, status={self.status})>"


class MediaAsset(Base):
    """Generated media asset storage and metadata."""
    
    __tablename__ = "media_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    job_id = Column(Integer, ForeignKey("media_jobs.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("media_providers.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Asset type
    media_type = Column(SQLEnum(MediaType), nullable=False)
    format = Column(String(50))  # png, jpg, webp, mp4, webm, gif
    
    # Storage
    storage_type = Column(String(50), default="local")  # local, s3, gcs, azure
    file_path = Column(String(1000))  # Local path or object key
    public_url = Column(String(1000))  # Public accessible URL
    thumbnail_url = Column(String(1000))
    
    # Dimensions and quality
    width = Column(Integer)
    height = Column(Integer)
    duration = Column(Float)  # For video, in seconds
    file_size = Column(Integer)  # bytes
    quality = Column(String(50))
    
    # Generation parameters used
    prompt_used = Column(Text)
    model_used = Column(String(100))
    generation_params = Column(JSON, default=dict)
    
    # SEO integration
    title = Column(String(500))
    description = Column(Text)
    alt_text = Column(String(1000))
    tags = Column(JSON, default=list)
    
    # Usage tracking
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Status
    is_public = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("MediaJob", back_populates="assets")
    provider = relationship("MediaProvider", back_populates="assets")
    project = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<MediaAsset(id={self.id}, asset_id={self.asset_id}, type={self.media_type})>"


class MediaMetrics(Base):
    """Aggregated metrics for media generation performance tracking."""
    
    __tablename__ = "media_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(20), default="daily")  # hourly, daily, weekly, monthly
    
    # Provider breakdown
    provider_id = Column(Integer, ForeignKey("media_providers.id"))
    
    # Volume metrics
    total_jobs = Column(Integer, default=0)
    completed_jobs = Column(Integer, default=0)
    failed_jobs = Column(Integer, default=0)
    cancelled_jobs = Column(Integer, default=0)
    
    # By media type
    image_jobs = Column(Integer, default=0)
    video_jobs = Column(Integer, default=0)
    
    # Performance metrics
    average_queue_time = Column(Float, default=0.0)  # seconds
    average_generation_time = Column(Float, default=0.0)  # seconds
    average_total_time = Column(Float, default=0.0)  # seconds
    p95_generation_time = Column(Float, default=0.0)
    p99_generation_time = Column(Float, default=0.0)
    
    # Quality metrics
    success_rate = Column(Float, default=100.0)
    retry_rate = Column(Float, default=0.0)
    average_retries = Column(Float, default=0.0)
    
    # Cost metrics
    total_cost = Column(Float, default=0.0)
    average_cost_per_image = Column(Float, default=0.0)
    average_cost_per_video = Column(Float, default=0.0)
    cost_per_successful_output = Column(Float, default=0.0)
    
    # Provider-specific
    rate_limit_hits = Column(Integer, default=0)
    timeout_errors = Column(Integer, default=0)
    api_errors = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("MediaProvider")
    
    def __repr__(self) -> str:
        return f"<MediaMetrics(id={self.id}, date={self.date}, provider_id={self.provider_id})>"
