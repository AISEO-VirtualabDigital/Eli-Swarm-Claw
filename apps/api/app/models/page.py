"""Page and CrawlResult models for crawled pages."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Page(Base):
    """Page model representing a crawled URL."""
    
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), nullable=False, index=True)
    canonical_url = Column(String(1000))
    
    # Foreign keys
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    
    # Page metadata
    title = Column(String(500))
    meta_description = Column(Text)
    h1 = Column(String(500))
    word_count = Column(Integer, default=0)
    page_size_bytes = Column(Integer, default=0)
    
    # SEO status
    status_code = Column(Integer)
    is_indexable = Column(Boolean, default=True)
    noindex = Column(Boolean, default=False)
    nofollow = Column(Boolean, default=False)
    has_canonical = Column(Boolean, default=False)
    canonical_mismatch = Column(Boolean, default=False)
    
    # Content analysis
    language = Column(String(10))
    content_type = Column(String(100))
    
    # Links
    internal_links_count = Column(Integer, default=0)
    external_links_count = Column(Integer, default=0)
    broken_links_count = Column(Integer, default=0)
    
    # Media
    images_count = Column(Integer, default=0)
    images_missing_alt = Column(Integer, default=0)
    
    # Schema
    has_schema = Column(Boolean, default=False)
    schema_types = Column(JSON, default=list)
    
    # Open Graph / Social
    has_og_tags = Column(Boolean, default=False)
    has_twitter_card = Column(Boolean, default=False)
    
    # Issues (stored as JSON array)
    issues = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_crawled_at = Column(DateTime)
    
    # Relationships
    domain = relationship("Domain", back_populates="pages")
    crawl_results = relationship("CrawlResult", back_populates="page")
    
    def __repr__(self) -> str:
        return f"<Page(id={self.id}, url={self.url})>"


class CrawlResult(Base):
    """Detailed crawl result for a specific crawl job."""
    
    __tablename__ = "crawl_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    crawl_job_id = Column(Integer, ForeignKey("crawl_jobs.id"), nullable=False)
    
    # Crawl data snapshot
    status_code = Column(Integer)
    response_time_ms = Column(Float)
    content_hash = Column(String(64))  # For change detection
    
    # Full HTML snapshot (optional, can be large)
    html_snapshot = Column(Text)
    
    # Extracted data
    links_found = Column(JSON, default=list)
    headers = Column(JSON, default=dict)
    robots_meta = Column(String(100))
    
    # Errors
    error_message = Column(Text)
    error_type = Column(String(100))
    
    # Timestamp
    crawled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    page = relationship("Page", back_populates="crawl_results")
    crawl_job = relationship("CrawlJob", back_populates="results")
    
    def __repr__(self) -> str:
        return f"<CrawlResult(id={self.id}, page_id={self.page_id})>"
