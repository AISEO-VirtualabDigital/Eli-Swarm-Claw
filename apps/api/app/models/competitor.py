"""Competitor model for competitor tracking."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Competitor(Base):
    """Competitor model for tracking competitor domains and pages."""
    
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    url = Column(String(1000), nullable=False, index=True)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Competitor type
    competitor_type = Column(String(50), default="domain")  # domain, page, local
    
    # Tracking data
    is_active = Column(Boolean, default=True)
    last_analyzed_at = Column(DateTime)
    
    # Metrics (populated by analysis)
    domain_authority = Column(Integer, default=0)
    estimated_traffic = Column(Integer, default=0)
    keyword_overlap = Column(Integer, default=0)  # Shared keywords
    content_gap_count = Column(Integer, default=0)
    
    # Analysis results
    top_pages = Column(JSON, default=list)
    top_keywords = Column(JSON, default=list)
    content_themes = Column(JSON, default=list)
    
    # Additional data
    notes = Column(Text)
    extra_metadata = Column("metadata", JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="competitors")
    
    def __repr__(self) -> str:
        return f"<Competitor(id={self.id}, url={self.url})>"
