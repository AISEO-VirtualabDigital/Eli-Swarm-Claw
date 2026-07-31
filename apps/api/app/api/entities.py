"""Entity and Topic Graph API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models import Entity, Page

router = APIRouter()


@router.post("/extract")
async def extract_entities(
    page_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Extract entities from a page."""
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # TODO: Trigger Entity Agent for extraction
    return {
        "page_id": page_id,
        "status": "extraction_queued",
        "message": "Entities will be extracted by Entity Agent"
    }


@router.get("/", response_model=List[dict])
async def list_entities(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List entities."""
    query = select(Entity)
    
    if project_id:
        query = query.where(Entity.project_id == project_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    entities = result.scalars().all()
    
    return entities


@router.get("/map")
async def get_entity_map(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get entity-topic map for a project."""
    # TODO: Build entity graph
    return {
        "project_id": project_id,
        "entities": [],
        "topics": [],
        "connections": []
    }
