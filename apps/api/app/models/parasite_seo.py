"""Parasite SEO models for Eli Claw SaaS."""

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.core.database import Base


class ParasiteOpportunity(Base):
    """Model for tracking third-party publishing opportunities."""
    
    __tablename__ = "parasite_opportunities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Reddit, Medium, LinkedIn, etc.
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=True)
    topic: Mapped[str] = mapped_column(String(200), nullable=True)
    target_keyword: Mapped[str] = mapped_column(String(200), nullable=True, index=True)
    target_entity: Mapped[str] = mapped_column(String(200), nullable=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=True)  # post, article, video, etc.
    
    # Scoring
    authority_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    indexing_likelihood: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100, lower is better
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # Calculated composite score
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="identified")  # identified, planned, in_progress, published, archived
    publishing_status: Mapped[str] = mapped_column(String(50), nullable=True)  # draft, submitted, live, removed
    published_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_checked_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Content planning
    content_angle: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_ideas: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    post_outline: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_linking_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    repurposing_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Risk and compliance
    risk_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    compliance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    competitor_presence: Mapped[bool] = mapped_column(default=False)
    
    # Metadata
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="parasite_opportunities")
    creator = relationship("User", backref="parasite_opportunities")


class ParasitePlatform(Base):
    """Model for known parasite SEO platforms and their characteristics."""
    
    __tablename__ = "parasite_platforms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=True)
    platform_type: Mapped[str] = mapped_column(String(50), nullable=False)  # forum, blog, social, video, etc.
    authority_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100
    indexing_speed: Mapped[str | None] = mapped_column(String(50), nullable=True)  # fast, medium, slow
    content_formats: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    audience_types: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    compliance_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    best_practices: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
