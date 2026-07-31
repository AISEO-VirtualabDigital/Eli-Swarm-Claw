"""
Eli Claw - Additional Database Models
Includes: Batches, Webhooks, Reports, Writer, Storage, Usage
(Models not yet in existing model files)
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Index, Column
from sqlalchemy.orm import relationship
from app.core.database import Base


# --- Enums ---

class BatchStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partially_completed"


class WebhookEventType(str, Enum):
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    BATCH_COMPLETED = "batch.completed"
    CRAWL_COMPLETED = "crawl.completed"
    REPORT_READY = "report.ready"
    ASSET_CREATED = "asset.created"


class ReportType(str, Enum):
    TECHNICAL_AUDIT = "technical_audit"
    KEYWORD_OPPORTUNITY = "keyword_opportunity"
    CONTENT_PLAN = "content_plan"
    AI_READINESS = "ai_readiness"
    MONTHLY_PROGRESS = "monthly_progress"


class ContentType(str, Enum):
    SERVICE_PAGE = "service_page"
    BLOG_ARTICLE = "blog_article"
    LOCAL_SEO_PAGE = "local_seo_page"
    GBP_POST = "gbp_post"
    LINKEDIN_POST = "linkedin_post"
    REDDIT_POST = "reddit_post"
    YOUTUBE_DESC = "youtube_description"
    FAQ_SECTION = "faq_section"
    META_TAGS = "meta_tags"


# --- Batch Job Models ---

class BatchJob(Base):
    """Batch job for processing multiple media generation requests together."""
    
    __tablename__ = "batch_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_uuid = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Batch configuration
    batch_type = Column(String(100), nullable=False)  # e.g., "social_set", "blog_thumbnails"
    provider = Column(String(100), nullable=False)
    
    # Status tracking
    status = Column(String(50), default="draft")  # draft, queued, processing, completed, failed, cancelled, partial
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    cancelled_items = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    
    # Payloads
    input_payload = Column(JSON, default=dict)
    result_summary = Column(JSON, default=dict)
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    failed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("BatchJobItem", back_populates="batch", cascade="all, delete-orphan")
    organization = relationship("Organization", foreign_keys=[organization_id])


class BatchJobItem(Base):
    """Individual item within a batch job."""
    
    __tablename__ = "batch_job_items"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_job_id = Column(Integer, ForeignKey("batch_jobs.id"), nullable=False, index=True)
    media_job_id = Column(Integer, ForeignKey("media_jobs.id"), nullable=True)
    
    # Status
    status = Column(String(50), default="draft")
    input_payload = Column(JSON, default=dict)
    result_payload = Column(JSON, default=dict)
    error_message = Column(Text)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    batch = relationship("BatchJob", back_populates="items")
    media_job = relationship("MediaJob", foreign_keys=[media_job_id])


# --- Webhook Models ---

class Webhook(Base):
    """Webhook configuration for event notifications."""
    
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_uuid = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Configuration
    name = Column(String(255), nullable=False)
    target_url = Column(String(1000), nullable=False)
    event_types = Column(JSON, default=list)  # List of WebhookEventType values
    signing_secret = Column(String(500))  # Encrypted secret for HMAC signature
    is_active = Column(Boolean, default=True)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")
    organization = relationship("Organization", foreign_keys=[organization_id])


class WebhookDelivery(Base):
    """Record of webhook delivery attempts."""
    
    __tablename__ = "webhook_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Event data
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, default=dict)
    
    # Delivery status
    status = Column(String(50), default="pending")  # pending, success, failed
    response_code = Column(Integer)
    response_body_preview = Column(Text)
    attempt_count = Column(Integer, default=0)
    
    # Retry logic
    last_attempt_at = Column(DateTime)
    next_retry_at = Column(DateTime)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")
    organization = relationship("Organization", foreign_keys=[organization_id])


# --- Report Models ---

class Report(Base):
    """SEO report generation."""
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_uuid = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Report configuration
    report_type = Column(String(100), nullable=False)  # ReportType value
    title = Column(String(500), nullable=False)
    
    # Status
    status = Column(String(50), default="draft")  # draft, processing, completed, failed
    progress_percentage = Column(Float, default=0.0)
    
    # Content
    summary = Column(Text)
    data_payload = Column(JSON, default=dict)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exports = relationship("ReportExport", back_populates="report", cascade="all, delete-orphan")
    organization = relationship("Organization", foreign_keys=[organization_id])


class ReportExport(Base):
    """Exported report file."""
    
    __tablename__ = "report_exports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    storage_file_id = Column(Integer, ForeignKey("storage_files.id"), nullable=True)
    
    # Export details
    format = Column(String(50), nullable=False)  # html, pdf, csv, json
    file_name = Column(String(500), nullable=False)
    public_url = Column(String(1000))
    size_bytes = Column(Integer, default=0)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    report = relationship("Report", back_populates="exports")
    storage_file = relationship("StorageFile", foreign_keys=[storage_file_id])


# --- Writer Models ---

class WriterJob(Base):
    """SEO content writer job."""
    
    __tablename__ = "writer_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_uuid = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Content configuration
    content_type = Column(String(100), nullable=False)  # ContentType value
    topic = Column(String(1000), nullable=False)
    target_keyword = Column(String(500))
    search_intent = Column(String(200))
    tone = Column(String(200))
    brand_voice = Column(String(200))
    
    # Status
    status = Column(String(50), default="draft")
    progress_percentage = Column(Float, default=0.0)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    drafts = relationship("WriterDraft", back_populates="job", cascade="all, delete-orphan")
    organization = relationship("Organization", foreign_keys=[organization_id])


class WriterDraft(Base):
    """Generated content draft from a writer job."""
    
    __tablename__ = "writer_drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    writer_job_id = Column(Integer, ForeignKey("writer_jobs.id"), nullable=False, index=True)
    
    # Content
    title = Column(String(500), nullable=False)
    h1 = Column(String(500))
    meta_title = Column(String(500))
    meta_description = Column(Text)
    body_content = Column(Text, nullable=False)
    
    # SEO analysis
    seo_score = Column(Integer, default=0)
    entities_detected = Column(JSON, default=list)
    internal_links_suggested = Column(JSON, default=list)
    faq_ideas = Column(JSON, default=list)
    schema_suggestion = Column(JSON, default=dict)
    repurposing_suggestions = Column(JSON, default=list)
    
    # Versioning
    version = Column(Integer, default=1)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("WriterJob", back_populates="drafts")


# --- Storage & Usage Models ---

class StorageFile(Base):
    """File storage tracking."""
    
    __tablename__ = "storage_files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_uuid = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # File details
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False, unique=True)
    provider = Column(String(50), nullable=False)  # local, minio, s3, gcs
    bucket = Column(String(255))
    mime_type = Column(String(255), nullable=False)
    size_bytes = Column(Integer, default=0)
    checksum = Column(String(100))
    
    # Access control
    is_public = Column(Boolean, default=False)
    public_url = Column(String(1000))
    
    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    assets = relationship("MediaAsset", back_populates="storage_file")
    report_exports = relationship("ReportExport", back_populates="storage_file")
    organization = relationship("Organization", foreign_keys=[organization_id])


class UsageEvent(Base):
    """Usage tracking for billing and analytics."""
    
    __tablename__ = "usage_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100))  # media_job, crawl, report, writer
    resource_id = Column(Integer)
    
    # Metrics
    quantity = Column(Integer, default=1)
    cost_estimate = Column(Float, default=0.0)
    provider = Column(String(100))
    
    # Metadata (renamed from 'metadata' which is reserved)
    event_metadata = Column(JSON, default=dict)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Index for fast monthly aggregation
    __table_args__ = (
        Index('idx_usage_org_month', 'organization_id', 'created_at'),
    )
    
    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id])
