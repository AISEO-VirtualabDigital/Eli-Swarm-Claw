"""Asset and AssetEntity models for content asset registry."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Asset(Base):
    """Asset model for tracking all content assets across channels."""
    
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), nullable=False, index=True)
    canonical_url = Column(String(1000))
    title = Column(String(500))
    
    # Asset type
    asset_type = Column(String(100), nullable=False)  # webpage, blog_post, landing_page, local_seo_page, programmatic_seo, pdf, image, video, youtube, reddit, linkedin, medium, gbp_post, github, press_release, external_citation
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"))
    domain_id = Column(Integer, ForeignKey("domains.id"))
    
    # Content metadata
    topic = Column(String(255))
    primary_keyword = Column(String(500))
    secondary_keywords = Column(JSON, default=list)
    
    # Entity tags
    entity_tags = Column(JSON, default=list)
    
    # Status tracking
    indexing_status = Column(String(50), default="unknown")  # draft, published, submitted, crawled, indexed, not_indexed, excluded, duplicate, canonicalized, noindex, error, needs_improvement
    crawl_status = Column(String(50), default="pending")
    ai_citation_status = Column(String(50), default="unknown")
    
    # Link data
    internal_links_in = Column(Integer, default=0)
    internal_links_out = Column(Integer, default=0)
    external_links = Column(JSON, default=list)
    
    # Schema data
    schema_found = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_crawled_at = Column(DateTime)
    
    # Additional data
    recommendations = Column(JSON, default=list)
    extra_metadata = Column("metadata", JSON, default=dict)
    
    # Relationships
    project = relationship("Project")
    domain = relationship("Domain")
    entities = relationship("AssetEntity", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, url={self.url})>"


class AssetEntity(Base):
    """Junction table for assets and entities."""
    
    __tablename__ = "asset_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    
    # Relationship data
    relevance_score = Column(Float, default=1.0)
    mention_count = Column(Integer, default=0)
    context = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="entities")
    entity = relationship("Entity", back_populates="assets")
    
    def __repr__(self) -> str:
        return f"<AssetEntity(asset_id={self.asset_id}, entity_id={self.entity_id})>"
