"""Project model for client/campaign management."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Project(Base):
    """Project model for managing SEO campaigns."""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    slug = Column(String(100), index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    
    # Settings
    is_active = Column(Boolean, default=True)
    industry = Column(String(100))
    location = Column(String(255))
    target_audience = Column(String(500))
    
    # Configuration
    settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    workspace = relationship("Workspace", back_populates="projects")
    domains = relationship("Domain", back_populates="project", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name})>"
