"""CrawlJob model for tracking crawl operations."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class CrawlJob(Base):
    """Crawl job model for tracking website crawl operations."""
    
    __tablename__ = "crawl_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    started_by = Column(Integer, ForeignKey("users.id"))
    
    # Job configuration
    max_pages = Column(Integer, default=1000)
    max_depth = Column(Integer, default=5)
    respect_robots_txt = Column(Boolean, default=True)
    user_agent = Column(String(255))
    
    # Status
    status = Column(String(50), default="pending")  # pending, running, completed, failed, cancelled
    progress_percentage = Column(Float, default=0.0)
    
    # Statistics
    pages_found = Column(Integer, default=0)
    pages_crawled = Column(Integer, default=0)
    pages_successful = Column(Integer, default=0)
    pages_failed = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Results summary
    summary = Column(JSON, default=dict)
    issues_found = Column(JSON, default=list)
    
    # Errors
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="crawls")
    results = relationship("CrawlResult", back_populates="crawl_job", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<CrawlJob(id={self.id}, domain_id={self.domain_id}, status={self.status})>"
