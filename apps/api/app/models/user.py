"""User model for authentication and account management."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class Role(str, enum.Enum):
    """User roles within an organization."""
    VIEWER = "viewer"
    WRITER = "writer"
    ADMIN = "admin"
    OWNER = "owner"


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
    
    # First login password change requirement
    must_change_password = Column(Boolean, default=False)
    
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
    emails = relationship("UserEmail", back_populates="user", cascade="all, delete-orphan")
    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class UserEmail(Base):
    """User email addresses (primary and secondary/alias)."""
    
    __tablename__ = "user_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    email_type = Column(String(50), default="secondary")  # primary, secondary, alias, notification
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emails")
    
    def __repr__(self) -> str:
        return f"<UserEmail(id={self.id}, email={self.email}, type={self.email_type})>"


class Membership(Base):
    """User membership in an organization with role-based access."""
    
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Roles (can have multiple, stored as array in Postgres or comma-separated)
    # For simplicity, we store primary role here
    role = Column(SQLEnum(Role), nullable=False, default=Role.VIEWER)
    
    # Additional permissions can be added as needed
    invited_by = Column(Integer, ForeignKey("users.id"))
    accepted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - specify foreign_keys to avoid ambiguity
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])
    organization = relationship("Organization", back_populates="memberships")
    inviter = relationship("User", foreign_keys=[invited_by], overlaps="user,memberships,organization")
    
    def __repr__(self) -> str:
        return f"<Membership(user_id={self.user_id}, org_id={self.organization_id}, role={self.role})>"
