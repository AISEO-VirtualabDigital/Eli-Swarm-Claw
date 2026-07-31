"""Domain model for tracked websites."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Domain(Base):
    """Domain model for tracked websites."""
    
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False, index=True)
    name = Column(String(255))
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Crawl settings
    crawl_enabled = Column(Boolean, default=True)
    crawl_frequency = Column(String(50), default="weekly")  # daily, weekly, monthly
    respect_robots_txt = Column(Boolean, default=True)
    max_pages = Column(Integer, default=1000)
    max_depth = Column(Integer, default=5)
    
    # Status tracking
    is_active = Column(Boolean, default=True)
    last_crawled_at = Column(DateTime)
    next_crawl_at = Column(DateTime)
    crawl_status = Column(String(50), default="pending")  # pending, crawling, completed, failed
    
    # SEO metrics (populated by crawls)
    total_pages = Column(Integer, default=0)
    indexed_pages = Column(Integer, default=0)
    health_score = Column(Integer, default=0)  # 0-100
    
    # Additional data
    notes = Column(Text)
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="domains")
    pages = relationship("Page", back_populates="domain", cascade="all, delete-orphan")
    crawls = relationship("CrawlJob", back_populates="domain", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Domain(id={self.id}, url={self.url})>"
