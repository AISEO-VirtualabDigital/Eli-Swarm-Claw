"""Domains API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models import Domain
from app.schemas import DomainCreate, DomainResponse

router = APIRouter()


@router.post("/", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def create_domain(
    domain_data: DomainCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new domain."""
    db_domain = Domain(
        domain=domain_data.domain,
        name=domain_data.name,
        project_id=domain_data.project_id,
    )
    
    db.add(db_domain)
    await db.commit()
    await db.refresh(db_domain)
    
    return db_domain


@router.get("/", response_model=List[DomainResponse])
async def list_domains(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List domains, optionally filtered by project."""
    query = select(Domain)
    if project_id:
        query = query.where(Domain.project_id == project_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    domains = result.scalars().all()
    return domains


@router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific domain by ID."""
    result = await db.execute(select(Domain).where(Domain.id == domain_id))
    domain = result.scalar_one_or_none()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    return domain


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a domain."""
    result = await db.execute(select(Domain).where(Domain.id == domain_id))
    domain = result.scalar_one_or_none()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    await db.delete(domain)
    await db.commit()
    
    return None
