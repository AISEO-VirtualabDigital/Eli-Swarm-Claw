"""Entity model for entity-based SEO."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Entity(Base):
    """Entity model for tracking business, topic, and semantic entities."""
    
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    
    # Entity type
    entity_type = Column(String(100), nullable=False)  # business, service, location, product, person, organization, industry, problem, solution, audience, competitor
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"))
    parent_entity_id = Column(Integer, ForeignKey("entities.id"))
    
    # Entity data
    wikipedia_url = Column(String(1000))
    wikidata_id = Column(String(100))
    schema_org_type = Column(String(200))
    
    # Attributes
    attributes = Column(JSON, default=dict)  # Flexible key-value store
    related_entities = Column(JSON, default=list)  # IDs of related entities
    synonyms = Column(JSON, default=list)
    
    # Coverage tracking
    mention_count = Column(Integer, default=0)
    coverage_score = Column(Float, default=0.0)  # How well covered in content
    relevance_score = Column(Float, default=0.0)  # Relevance to topic
    authority_score = Column(Float, default=0.0)  # Entity authority
    
    # AI/LLM extracted
    extracted_from = Column(JSON, default=list)  # URLs where entity was found
    confidence = Column(Float, default=1.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project")
    parent_entity = relationship("Entity", remote_side=[id], backref="child_entities")
    assets = relationship("AssetEntity", back_populates="entity", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, name={self.name}, type={self.entity_type})>"
