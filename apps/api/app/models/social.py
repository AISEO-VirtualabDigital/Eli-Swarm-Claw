"""Social Media SEO models for Eli Claw SaaS."""

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.core.database import Base


class SocialPost(Base):
    """Model for tracking social media posts and optimization."""
    
    __tablename__ = "social_posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # facebook, instagram, linkedin, tiktok, twitter, pinterest, reddit
    post_url: Mapped[str] = mapped_column(String(500), nullable=True, unique=True)
    post_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Content
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # text, image, video, carousel, story, reel, short
    media_urls: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # SEO targeting
    target_keyword: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    target_entity: Mapped[str | None] = mapped_column(String(200), nullable=True)
    hashtags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # Optimization
    cta: Mapped[str | None] = mapped_column(String(300), nullable=True)
    link_to_website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    related_campaign: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Publishing
    publish_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    visibility: Mapped[str | None] = mapped_column(String(20), nullable=True)  # public, followers, etc.
    
    # Performance metrics
    impressions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    engagement_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    clicks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    engagement_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # SEO value
    seo_value_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    search_visibility_impact: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    
    # Repurposing
    repurposing_status: Mapped[str] = mapped_column(String(50), default="original")  # original, repurposed_from, repurposed_to
    source_post_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("social_posts.id"), nullable=True)
    repurposed_to_platforms: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="published")  # draft, scheduled, published, archived
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="social_posts")


class SocialProfile(Base):
    """Model for tracking social media profile optimization."""
    
    __tablename__ = "social_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    profile_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=True)
    
    # Profile content
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # SEO optimization
    target_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    brand_entities: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Optimization scoring
    optimization_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    bio_optimization_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    keyword_presence: Mapped[bool] = mapped_column(default=False)
    entity_consistency: Mapped[bool] = mapped_column(default=False)
    
    # Recommendations
    suggested_improvements: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metrics
    follower_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    following_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verified: Mapped[bool] = mapped_column(default=False)
    
    # Metadata
    last_checked: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="social_profiles")


class SocialKeyword(Base):
    """Model for social media keyword and hashtag research."""
    
    __tablename__ = "social_keywords"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    keyword_type: Mapped[str] = mapped_column(String(20), default="keyword")  # keyword, hashtag, topic
    
    # Characteristics
    usage_volume: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    competition_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    trending: Mapped[bool] = mapped_column(default=False)
    seasonal: Mapped[bool] = mapped_column(default=False)
    
    # Recommendations
    recommended_for: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of content types
    related_hashtags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    best_practices: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="social_keywords")


class GBPPost(Base):
    """Model for Google Business Profile posts."""
    
    __tablename__ = "gbp_posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    domain_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("domains.id"), nullable=True)
    
    # Post content
    post_type: Mapped[str] = mapped_column(String(50), nullable=False)  # update, offer, event, product
    title: Mapped[str] = mapped_column(String(200), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cta_text: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cta_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_urls: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # Event-specific
    event_start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    event_end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Offer-specific
    offer_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    offer_expiration: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # SEO
    target_keyword: Mapped[str | None] = mapped_column(String(200), nullable=True)
    local_keyword: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    # Publishing
    published_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, scheduled, published, expired, archived
    
    # Performance
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    clicks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="gbp_posts")
    domain = relationship("Domain", backref="gbp_posts")
