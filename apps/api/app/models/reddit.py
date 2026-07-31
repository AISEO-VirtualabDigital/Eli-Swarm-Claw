"""Reddit Research models for Eli Claw SaaS."""

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.core.database import Base


class RedditFinding(Base):
    """Model for storing Reddit research findings."""
    
    __tablename__ = "reddit_findings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    subreddit: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    post_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    post_title: Mapped[str] = mapped_column(String(300), nullable=False)
    author_handle: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Public handle only
    post_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Content analysis
    topic: Mapped[str] = mapped_column(String(200), nullable=True, index=True)
    keyword: Mapped[str] = mapped_column(String(200), nullable=True)
    intent: Mapped[str] = mapped_column(String(50), nullable=True)  # informational, commercial, transactional, navigational
    pain_point: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_signal: Mapped[str | None] = mapped_column(String(200), nullable=True)
    service_signal: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    # Scoring
    client_relevance: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10
    lead_potential_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    engagement_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # upvotes + comments
    comment_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    upvote_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Action planning
    suggested_response_angle: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_opportunity: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_content_asset: Mapped[str | None] = mapped_column(String(200), nullable=True)
    recommended_client_page: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Compliance
    compliance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    spam_risk: Mapped[str] = mapped_column(String(20), default="low")  # low, medium, high
    outreach_appropriate: Mapped[bool] = mapped_column(default=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="identified")  # identified, reviewed, acted_on, archived
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="reddit_findings")


class SubredditProfile(Base):
    """Model for tracking subreddit characteristics and relevance."""
    
    __tablename__ = "subreddit_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    subreddit_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    subscriber_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_users: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Relevance
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    
    # Rules and compliance
    posting_rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    self_promotion_allowed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    link_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Activity metrics
    avg_posts_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_comments_per_post: Mapped[float | None] = mapped_column(Float, nullable=True)
    engagement_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Tracking
    last_checked: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="subreddit_profiles")


class RedditLeadSignal(Base):
    """Model for high-intent lead signals from Reddit."""
    
    __tablename__ = "reddit_lead_signals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    finding_id: Mapped[int] = mapped_column(Integer, ForeignKey("reddit_findings.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Signal details
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)  # question, complaint, recommendation_request, etc.
    intent_level: Mapped[str] = mapped_column(String(20), nullable=False)  # low, medium, high, urgent
    budget_signal: Mapped[str | None] = mapped_column(String(50), nullable=True)  # mentioned budget range
    timeline_signal: Mapped[str | None] = mapped_column(String(50), nullable=True)  # urgency indicator
    location_specific: Mapped[bool] = mapped_column(default=False)
    
    # Response planning
    response_recommended: Mapped[bool] = mapped_column(default=True)
    response_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # helpful_comment, dm_if_allowed, content_creation
    response_draft: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_to_share: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Ethical guidelines
    no_spam_warning: Mapped[bool] = mapped_column(default=True)
    value_first_approach: Mapped[bool] = mapped_column(default=True)
    disclosure_required: Mapped[bool] = mapped_column(default=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="new")  # new, reviewing, responded, converted, disqualified
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    converted: Mapped[bool] = mapped_column(default=False)
    conversion_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    finding = relationship("RedditFinding", backref="lead_signals")
    project = relationship("Project", backref="reddit_lead_signals")
