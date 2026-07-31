"""Keyword and KeywordCluster models."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Keyword(Base):
    """Keyword model for tracking keywords and their data."""
    
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(500), nullable=False, index=True)
    
    # Foreign keys
    cluster_id = Column(Integer, ForeignKey("keyword_clusters.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Classification
    intent = Column(String(50))  # informational, navigational, commercial, transactional
    intent_score = Column(Float)  # Confidence score 0-1
    
    # Modifiers
    local_modifier = Column(String(255))  # e.g., "near me", city name
    service_type = Column(String(255))
    industry = Column(String(255))
    
    # Metrics (estimated or from APIs)
    search_volume = Column(Integer, default=0)
    difficulty = Column(Integer, default=0)  # 0-100
    cpc = Column(Float, default=0.0)
    competition = Column(Float, default=0.0)  # 0-1
    
    # Scoring
    opportunity_score = Column(Float, default=0.0)  # Calculated score
    commercial_score = Column(Float, default=0.0)  # 0-1
    
    # Content recommendations
    content_type = Column(String(100))  # blog, landing, product, category, faq
    suggested_page_type = Column(String(100))
    suggested_title = Column(String(500))
    suggested_h1 = Column(String(500))
    suggested_schema_type = Column(String(100))
    
    # AI/LLM generated
    faq_questions = Column(JSON, default=list)
    ai_prompt_variations = Column(JSON, default=list)
    related_topics = Column(JSON, default=list)
    
    # Source tracking
    source = Column(String(100))  # seed, expansion, competitor, serp, llm
    is_primary = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cluster = relationship("KeywordCluster", back_populates="keywords")
    project = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<Keyword(id={self.id}, keyword={self.keyword})>"


class KeywordCluster(Base):
    """Keyword cluster/group for topic modeling."""
    
    __tablename__ = "keyword_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"))
    parent_topic = Column(String(255))  # Parent topic name
    
    # Topic data
    main_topic = Column(String(255))
    subtopics = Column(JSON, default=list)
    
    # Metrics
    total_keywords = Column(Integer, default=0)
    avg_difficulty = Column(Float, default=0.0)
    avg_opportunity = Column(Float, default=0.0)
    total_search_volume = Column(Integer, default=0)
    
    # Content planning
    pillar_page_url = Column(String(1000))
    cluster_pages = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    keywords = relationship("Keyword", back_populates="cluster")
    project = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<KeywordCluster(id={self.id}, name={self.name})>"
