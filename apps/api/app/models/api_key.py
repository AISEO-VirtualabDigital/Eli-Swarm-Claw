"""API Key model for programmatic access."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ApiKeyScope(str, enum.Enum):
    """Scopes for API key permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class ApiKey(Base):
    """API Key for programmatic access to the API."""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Key metadata (never store full key)
    name = Column(String(255), nullable=False)
    key_prefix = Column(String(16), nullable=False, index=True)  # First 8-16 chars for lookup
    key_hash = Column(String(255), nullable=False)  # Hashed full key
    
    # Scopes/Permissions
    scopes = Column(ARRAY(String), default=[ApiKeyScope.READ.value])  # List of scope strings
    
    # Status
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime)
    revoked_by = Column(Integer, ForeignKey("users.id"))
    
    # Usage tracking
    last_used_at = Column(DateTime)
    request_count = Column(Integer, default=0)
    
    # Rate limiting (optional per-key limits)
    rate_limit_per_minute = Column(Integer)
    rate_limit_per_hour = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="api_keys")
    user = relationship("User", back_populates="api_keys")
    revoker = relationship("User", foreign_keys=[revoked_by])
    
    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name={self.name}, prefix={self.key_prefix})>"
