"""IndexingJob model for URL discovery and indexing tracking."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class IndexingJob(Base):
    """Indexing job model for tracking URL submission to discovery systems."""
    
    __tablename__ = "indexing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), nullable=False, index=True)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    submitted_by = Column(Integer, ForeignKey("users.id"))
    
    # Submission methods
    method = Column(String(50))  # indexnow, sitemap, rss, manual
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, submitted, crawled, indexed, not_indexed, excluded, duplicate, canonicalized, noindex, error, needs_improvement
    indexing_status = Column(String(50), default="unknown")
    
    # Submission data
    submitted_at = Column(DateTime)
    last_checked_at = Column(DateTime)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Results
    response_code = Column(Integer)
    response_message = Column(Text)
    exclusion_reason = Column(String(255))
    canonical_url = Column(String(1000))
    
    # Change detection (only resubmit if content changed)
    content_hash = Column(String(64))
    last_content_change = Column(DateTime)
    
    # Additional data
    metadata = Column(JSON, default=dict)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project")
    asset = relationship("Asset")
    
    def __repr__(self) -> str:
        return f"<IndexingJob(id={self.id}, url={self.url})>"
