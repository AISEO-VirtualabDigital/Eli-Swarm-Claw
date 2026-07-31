"""Repository Scanner and Repurposing models for Eli Claw SaaS."""

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import enum

from app.core.database import Base


class LicenseType(str, enum.Enum):
    """Open source license types."""
    MIT = "mit"
    APACHE_2 = "apache_2"
    GPL_3 = "gpl_3"
    GPL_2 = "gpl_2"
    BSD_3 = "bsd_3"
    BSD_2 = "bsd_2"
    ISC = "isc"
    UNLICENSE = "unlicense"
    CC0 = "cc0"
    PROPRIETARY = "proprietary"
    OTHER = "other"
    UNKNOWN = "unknown"


class RepositoryScan(Base):
    """Model for tracking public repository scans."""
    
    __tablename__ = "repository_scans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    # Repository identification
    repo_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)  # owner/repo
    repo_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    owner: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metrics
    stars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    forks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    watchers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    open_issues: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Language and topics
    primary_language: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    languages: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON object as text
    topics: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # License
    license_type: Mapped[str] = mapped_column(SQLEnum(LicenseType), default=LicenseType.UNKNOWN)
    license_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    license_compatible: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    attribution_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    
    # Activity
    created_at_repo: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at_repo: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    pushed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_scanned: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Architecture analysis
    architecture_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_files: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    dependencies: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    tech_stack: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # Reusability assessment
    reusable_ideas: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    reusable_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    reusable_packages: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # Compliance
    compliance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")  # low, medium, high
    requires_attribution: Mapped[bool] = mapped_column(default=False)
    copyleft_license: Mapped[bool] = mapped_column(default=False)
    
    # Repurpose recommendation
    repurpose_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    implementation_complexity: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    recommended_action: Mapped[str | None] = mapped_column(String(50), nullable=True)  # adopt, adapt, ignore, study_only
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="scanned")  # scanned, analyzed, recommended, implemented, archived
    scan_status: Mapped[str] = mapped_column(String(50), default="success")  # success, failed, rate_limited, not_found
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="repository_scans")


class RepurposingPlan(Base):
    """Model for tracking repurposing implementation plans."""
    
    __tablename__ = "repurposing_plans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    repository_scan_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("repository_scans.id"), nullable=True)
    
    # Plan details
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    feature_category: Mapped[str] = mapped_column(String(100), nullable=False)  # crawler, keyword_research, etc.
    
    # Source attribution
    source_repository: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_license: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attribution_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Implementation approach
    implementation_approach: Mapped[str] = mapped_column(String(50), nullable=False)  # adopt, adapt, inspired_by, reference_only
    what_to_build: Mapped[str | None] = mapped_column(Text, nullable=True)
    what_to_adapt: Mapped[str | None] = mapped_column(Text, nullable=True)
    what_to_ignore: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Technical mapping
    eli_claw_module: Mapped[str] = mapped_column(String(100), nullable=False)
    required_changes: Mapped[str | None] = mapped_column(Text, nullable=True)
    compatibility_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Tasks
    implementation_tasks: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of task IDs
    estimated_effort: Mapped[int | None] = mapped_column(Integer, nullable=True)  # hours
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, critical
    
    # Legal compliance
    legal_review_required: Mapped[bool] = mapped_column(default=False)
    legal_reviewed: Mapped[bool] = mapped_column(default=False)
    legal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="proposed")  # proposed, approved, in_progress, completed, rejected
    approved_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="repurposing_plans")
    repository_scan = relationship("RepositoryScan", backref="repurposing_plans")
    approver = relationship("User", backref="approved_repurposing_plans")


class PublicAPIConnector(Base):
    """Model for tracking public API connectors and data sources."""
    
    __tablename__ = "public_api_connectors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    # API identification
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    documentation_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Authentication
    auth_type: Mapped[str] = mapped_column(String(50), nullable=False)  # none, api_key, oauth2, bearer, basic
    required_scopes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # Rate limiting
    rate_limit_requests: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rate_limit_period: Mapped[str | None] = mapped_column(String(20), nullable=True)  # second, minute, hour, day
    
    # Endpoints
    allowed_endpoints: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    endpoint_templates: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON object as text
    
    # Data tracking
    data_type: Mapped[str] = mapped_column(String(100), nullable=False)
    data_format: Mapped[str] = mapped_column(String(50), default="json")  # json, xml, csv
    
    # Status tracking
    last_successful_request: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_failed_request: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_count: Mapped[int] = mapped_column(default=0)
    consecutive_failures: Mapped[int] = mapped_column(default=0)
    
    # Compliance
    compliance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    terms_of_service_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data_usage_restrictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Configuration
    active: Mapped[bool] = mapped_column(default=True)
    timeout_seconds: Mapped[int] = mapped_column(default=30)
    retry_attempts: Mapped[int] = mapped_column(default=3)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="api_connectors")


class APIKeyStatus(Base):
    """Model for tracking API key health without storing actual keys."""
    
    __tablename__ = "api_key_statuses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    connector_id: Mapped[int] = mapped_column(Integer, ForeignKey("public_api_connectors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Key identification (never store actual key)
    key_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Descriptive name
    key_prefix: Mapped[str | None] = mapped_column(String(10), nullable=True)  # First few chars for identification
    key_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Hash for comparison
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="unknown")  # unknown, active, inactive, expired, revoked, error
    last_validated: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    validation_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Expiration tracking
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expiration_warning_sent: Mapped[bool] = mapped_column(default=False)
    
    # Rotation
    rotation_scheduled: Mapped[bool] = mapped_column(default=False)
    rotation_reminder_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_rotated: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Fallback configuration
    is_fallback: Mapped[bool] = mapped_column(default=False)
    fallback_for_key_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("api_key_statuses.id"), nullable=True)
    
    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_count: Mapped[int] = mapped_column(default=0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    connector = relationship("PublicAPIConnector", backref="key_statuses")
    fallback_key = relationship("APIKeyStatus", remote_side=[id], backref="primary_keys")
