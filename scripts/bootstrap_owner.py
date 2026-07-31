#!/usr/bin/env python3
"""
Bootstrap script for creating the initial owner account and organization.

This script reads configuration from environment variables and creates:
1. Owner user account with primary email
2. Secondary email as verified alias
3. Organization with owner membership
4. Audit log entry

Security: Password comes from environment variable only, never hardcoded.
"""

import os
import sys
import re
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship
from passlib.context import CryptContext

# Define minimal models needed for bootstrap (avoid loading all models)
class Base(DeclarativeBase):
    pass

class BootstrapUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=False)
    plan_name = Column(String(50), default="enterprise")
    subscription_status = Column(String(50), default="active")
    monthly_crawl_limit = Column(Integer, default=100000)
    monthly_keyword_limit = Column(Integer, default=100000)
    monthly_ai_check_limit = Column(Integer, default=10000)
    seats_limit = Column(Integer, default=50)

class BootstrapUserEmail(Base):
    __tablename__ = "user_emails"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False)
    email_type = Column(String(50), default="secondary")
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

class BootstrapOrganization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True)
    description = Column(String(1000))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    max_workspaces = Column(Integer, default=50)
    max_projects = Column(Integer, default=500)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def hash_password(password: str) -> str:
    """Hash password securely."""
    return pwd_context.hash(password)


def bootstrap_owner():
    """Create initial owner account and organization."""
    
    # Read environment variables
    owner_email = os.getenv("BOOTSTRAP_OWNER_EMAIL")
    owner_secondary_email = os.getenv("BOOTSTRAP_OWNER_SECONDARY_EMAIL")
    owner_name = os.getenv("BOOTSTRAP_OWNER_NAME", "Owner")
    owner_password = os.getenv("BOOTSTRAP_OWNER_PASSWORD")
    org_name = os.getenv("BOOTSTRAP_ORG_NAME", "Default Organization")
    org_slug = os.getenv("BOOTSTRAP_ORG_SLUG", "default-org")
    primary_domain = os.getenv("BOOTSTRAP_PRIMARY_DOMAIN", "")
    
    # Validate required fields
    if not owner_email:
        print("❌ Error: BOOTSTRAP_OWNER_EMAIL is required")
        sys.exit(1)
    
    if not validate_email(owner_email):
        print(f"❌ Error: Invalid email format: {owner_email}")
        sys.exit(1)
    
    if not owner_password:
        print("❌ Error: BOOTSTRAP_OWNER_PASSWORD is required")
        sys.exit(1)
    
    if len(owner_password) < 8:
        print("❌ Error: Password must be at least 8 characters")
        sys.exit(1)
    
    if owner_secondary_email and not validate_email(owner_secondary_email):
        print(f"❌ Error: Invalid secondary email format: {owner_secondary_email}")
        sys.exit(1)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if owner already exists
        existing_user = db.query(User).filter(User.email == owner_email).first()
        
        if existing_user:
            print(f"⚠️  Owner account already exists: {owner_email}")
            user = existing_user
        else:
            # Create owner user
            user = User(
                email=owner_email,
                hashed_password=hash_password(owner_password),
                full_name=owner_name,
                is_active=True,
                is_verified=True,
                is_superuser=True,
                must_change_password=True,  # Require password change on first login
                plan_name="enterprise",
                subscription_status="active",
                monthly_crawl_limit=100000,
                monthly_keyword_limit=100000,
                monthly_ai_check_limit=10000,
                seats_limit=50,
            )
            db.add(user)
            db.flush()  # Get user ID
            
            print(f"✅ Created owner account: {owner_email}")
        
        # Add secondary email as verified alias if provided
        if owner_secondary_email:
            existing_email = db.query(UserEmail).filter(
                UserEmail.email == owner_secondary_email
            ).first()
            
            if not existing_email:
                secondary_email_record = UserEmail(
                    user_id=user.id,
                    email=owner_secondary_email,
                    email_type="secondary",
                    is_primary=False,
                    is_verified=True,
                )
                db.add(secondary_email_record)
                print(f"✅ Added secondary email: {owner_secondary_email}")
            else:
                print(f"⚠️  Secondary email already exists: {owner_secondary_email}")
        
        # Check if organization already exists
        existing_org = db.query(Organization).filter(
            Organization.slug == org_slug
        ).first()
        
        if existing_org:
            print(f"⚠️  Organization already exists: {org_name} ({org_slug})")
            org = existing_org
            
            # Ensure owner is linked
            if org.owner_id != user.id:
                org.owner_id = user.id
                print(f"🔗 Linked organization to owner")
        else:
            # Create organization
            org = Organization(
                name=org_name,
                slug=org_slug,
                description=f"Initial organization for {owner_name}",
                owner_id=user.id,
                is_active=True,
                max_workspaces=50,
                max_projects=500,
            )
            db.add(org)
            print(f"✅ Created organization: {org_name} ({org_slug})")
        
        db.commit()
        
        # Success message (never print password)
        print("\n" + "="*60)
        print("🎉 Bootstrap completed successfully!")
        print("="*60)
        print(f"Organization: {org_name} ({org_slug})")
        print(f"Owner: {owner_name} <{owner_email}>")
        if owner_secondary_email:
            print(f"Secondary Email: {owner_secondary_email}")
        if primary_domain:
            print(f"Primary Domain: {primary_domain}")
        print("\n⚠️  Security Notice:")
        print("   - Password must be changed on first login")
        print("   - Never share your credentials")
        print("   - Store passwords in a secure password manager")
        print("="*60 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Bootstrap failed: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    bootstrap_owner()
