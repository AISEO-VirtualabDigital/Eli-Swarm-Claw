"""YouTube SEO models for Eli Claw SaaS."""

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.core.database import Base


class YouTubeVideo(Base):
    """Model for tracking YouTube video assets and optimization."""
    
    __tablename__ = "youtube_videos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    video_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # YouTube video ID
    channel_name: Mapped[str] = mapped_column(String(200), nullable=True)
    channel_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Video metadata
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # SEO targeting
    target_keyword: Mapped[str] = mapped_column(String(200), nullable=True, index=True)
    topic_cluster: Mapped[str | None] = mapped_column(String(100), nullable=True)
    search_intent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Content structure
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    chapters: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Thumbnail
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    thumbnail_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Publishing
    publish_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    visibility: Mapped[str | None] = mapped_column(String(20), nullable=True)  # public, unlisted, private
    
    # Performance metrics
    view_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    like_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    engagement_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Optimization scoring
    optimization_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    title_optimization_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    description_optimization_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    tag_optimization_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Recommendations
    suggested_improvements: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    shorts_ideas: Mapped[str | None] = mapped_column(Text, nullable=True)
    playlist_recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Website integration
    related_website_page: Mapped[str | None] = mapped_column(String(500), nullable=True)
    embedded_on_site: Mapped[bool] = mapped_column(default=False)
    internal_linking_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Repurposing
    repurposing_status: Mapped[str] = mapped_column(String(50), default="not_started")
    repurposed_assets: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")
    last_checked: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="youtube_videos")


class YouTubeKeyword(Base):
    """Model for YouTube-specific keyword research."""
    
    __tablename__ = "youtube_keywords"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    parent_topic: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Search characteristics
    search_volume_estimate: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    competition_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    search_intent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Video type recommendations
    recommended_video_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # tutorial, review, comparison, etc.
    recommended_length: Mapped[str | None] = mapped_column(String(20), nullable=True)  # short, medium, long
    
    # Content suggestions
    suggested_title_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_hooks: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_ctas: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="youtube_keywords")


class YouTubePlaylist(Base):
    """Model for YouTube playlist strategy."""
    
    __tablename__ = "youtube_playlists"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    playlist_url: Mapped[str] = mapped_column(String(500), nullable=True, unique=True)
    playlist_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic_cluster: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    video_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    video_ids: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of video IDs
    optimization_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="youtube_playlists")
