#!/usr/bin/env python3
"""Database seeding script for Eli Claw."""

import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import User, Organization, Workspace, Project

# Database URL - adjust as needed
DATABASE_URL = "postgresql+asyncpg://eliclaw:eliclaw_password@localhost:5432/eliclaw"


async def seed_database():
    """Seed the database with initial data."""
    print("Starting database seeding...")
    
    # Create engine and session
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create sample organization
        org = Organization(
            name="Sample Agency",
            slug="sample-agency",
            plan_name="pro",
            subscription_status="active",
        )
        session.add(org)
        await session.commit()
        await session.refresh(org)
        print(f"Created organization: {org.name}")
        
        # Create sample user
        user = User(
            email="admin@sample.com",
            username="admin",
            organization_id=org.id,
            is_active=True,
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Created user: {user.email}")
        
        # Create sample workspace
        workspace = Workspace(
            name="Default Workspace",
            organization_id=org.id,
        )
        session.add(workspace)
        await session.commit()
        await session.refresh(workspace)
        print(f"Created workspace: {workspace.name}")
        
        # Create sample project
        project = Project(
            name="Sample SEO Project",
            description="Demo project for testing",
            organization_id=org.id,
            workspace_id=workspace.id,
            industry="Technology",
            target_location="United States",
            website_url="https://example.com",
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        print(f"Created project: {project.name}")
        
        print("\n✅ Database seeded successfully!")
        print(f"\nSample credentials:")
        print(f"  Email: admin@sample.com")
        print(f"  (Password not set - use API directly for now)")
    
    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(seed_database())
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)
