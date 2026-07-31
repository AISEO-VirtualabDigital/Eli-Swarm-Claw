"""Recommendation model for prioritized SEO recommendations."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Recommendation(Base):
    """Recommendation model for actionable SEO recommendations."""
    
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"))
    url = Column(String(1000), index=True)
    
    # Recommendation data
    type = Column(String(100), nullable=False)  # technical_seo, content_quality, internal_linking, schema, indexing, keyword_opportunity, entity_coverage, ai_citation_readiness, competitor_gap, local_seo, performance
    category = Column(String(100))
    
    # Issue and fix
    issue = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    explanation = Column(Text)
    
    # Prioritization
    severity = Column(String(50))  # critical, high, medium, low, info
    impact = Column(Integer, default=0)  # 1-10
    effort = Column(Integer, default=0)  # 1-10
    priority_score = Column(Float, default=0.0)  # Calculated: impact/effort
    
    # Status tracking
    status = Column(String(50), default="open")  # open, in_progress, completed, dismissed, deferred
    
    # Implementation
    implementation_notes = Column(Text)
    code_snippet = Column(Text)
    
    # Tracking
    assigned_to = Column(Integer, ForeignKey("users.id"))
    completed_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Additional data
    metadata = Column(JSON, default=dict)
    related_issues = Column(JSON, default=list)
    
    def __repr__(self) -> str:
        return f"<Recommendation(id={self.id}, type={self.type}, status={self.status})>"
