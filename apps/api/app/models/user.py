"""User model for authentication and account management."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Subscription & billing
    plan_name = Column(String(50), default="free")  # free, starter, pro, agency, enterprise
    subscription_status = Column(String(50), default="inactive")  # inactive, active, cancelled, past_due
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    
    # Plan limits (for tracking)
    monthly_crawl_limit = Column(Integer, default=100)
    monthly_keyword_limit = Column(Integer, default=100)
    monthly_ai_check_limit = Column(Integer, default=10)
    seats_limit = Column(Integer, default=1)
    
    # API access
    api_key = Column(String(255), unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # Relationships
    organizations = relationship("Organization", back_populates="owner", foreign_keys="Organization.owner_id")
    workspaces = relationship("Workspace", back_populates="user")
    projects = relationship("Project", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
