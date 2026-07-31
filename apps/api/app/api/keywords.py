"""Keyword Research API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models import Keyword, KeywordCluster, Project
from app.schemas import KeywordResearchRequest, KeywordResponse

router = APIRouter()


@router.post("/research", response_model=List[KeywordResponse])
async def research_keywords(
    request: KeywordResearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Research and expand keywords."""
    # TODO: Trigger Keyword Agent for expansion
    # For now, return placeholder with seed keywords
    
    results = []
    for seed in request.seed_keywords:
        keyword = Keyword(
            keyword=seed,
            intent="unknown",
            opportunity_score=50,
        )
        results.append(keyword)
    
    return results


@router.post("/cluster")
async def cluster_keywords(
    project_id: int,
    keyword_ids: List[int] | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Cluster keywords into topic groups."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # TODO: Trigger Keyword Agent for clustering
    return {
        "project_id": project_id,
        "status": "clustering_queued",
        "message": "Keywords will be clustered by Keyword Agent"
    }


@router.get("/", response_model=List[KeywordResponse])
async def list_keywords(
    project_id: int | None = None,
    cluster_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List keywords."""
    query = select(Keyword)
    
    if project_id:
        query = query.where(Keyword.project_id == project_id)
    if cluster_id:
        query = query.where(Keyword.cluster_id == cluster_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    keywords = result.scalars().all()
    
    return keywords


@router.get("/clusters")
async def list_clusters(
    project_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List keyword clusters."""
    query = select(KeywordCluster)
    
    if project_id:
        query = query.where(KeywordCluster.project_id == project_id)
    
    result = await db.execute(query)
    clusters = result.scalars().all()
    
    return clusters
