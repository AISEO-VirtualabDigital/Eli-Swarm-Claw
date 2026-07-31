"""AICitationCheck model for AI citation monitoring."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class AICitationCheck(Base):
    """AI Citation check model for tracking brand/domain mentions in AI answers."""
    
    __tablename__ = "ai_citation_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Query data
    prompt_question = Column(Text, nullable=False)
    target_brand = Column(String(255))
    target_domain = Column(String(500))
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # AI system checked
    ai_system = Column(String(100))  # chatgpt, gemini, perplexity, claude, copilot, google_ai_overview, google_ai_mode
    
    # Results
    answer_text = Column(Text)
    sources_cited = Column(JSON, default=list)  # URLs cited in the answer
    
    # Mention tracking
    brand_mentioned = Column(Boolean, default=False)
    competitor_mentioned = Column(Boolean, default=False)
    url_cited = Column(Boolean, default=False)
    citation_position = Column(Integer)  # Position in source list
    
    # Competitor data
    competitors_checked = Column(JSON, default=list)
    competitor_mentions = Column(JSON, default=list)
    
    # Scoring
    citation_score = Column(Float, default=0.0)  # Overall AI citation score
    relevance_score = Column(Float, default=0.0)
    entity_completeness = Column(Float, default=0.0)
    
    # Change tracking
    previous_check_id = Column(Integer, ForeignKey("ai_citation_checks.id"))
    changed_from_previous = Column(Boolean, default=False)
    
    # Timestamps
    checked_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project")
    previous_check = relationship("AICitationCheck", remote_side=[id])
    
    def __repr__(self) -> str:
        return f"<AICitationCheck(id={self.id}, prompt={self.prompt_question[:50]}...)>"
