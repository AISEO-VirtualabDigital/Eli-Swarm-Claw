"""Workspace model for organizing projects."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Workspace(Base):
    """Workspace model for grouping related projects."""
    
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    slug = Column(String(100), index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="workspaces")
    organization = relationship("Organization", back_populates="workspaces")
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name={self.name})>"
