"""AI Citation Monitoring API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models import AICitationCheck, Project

router = APIRouter()


@router.post("/check")
async def check_citation(
    brand_domain: str,
    prompt: str,
    project_id: int,
    competitor_domains: List[str] | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Check AI citation for a brand/domain."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create citation check record
    citation_check = AICitationCheck(
        project_id=project_id,
        prompt=prompt,
        target_brand=brand_domain,
        competitors=str(competitor_domains) if competitor_domains else None,
        status="pending",
    )
    
    db.add(citation_check)
    await db.commit()
    await db.refresh(citation_check)
    
    # TODO: Trigger AI Citation Agent
    return {
        "check_id": citation_check.id,
        "status": "queued",
        "message": "Citation check queued for AI analysis"
    }


@router.get("/checks")
async def list_citation_checks(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List AI citation checks."""
    query = select(AICitationCheck)
    
    if project_id:
        query = query.where(AICitationCheck.project_id == project_id)
    
    result = await db.execute(query.order_by(AICitationCheck.created_at.desc()).offset(skip).limit(limit))
    checks = result.scalars().all()
    
    return checks


@router.get("/score/{project_id}")
async def get_citation_score(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get AI citation score for a project."""
    # Calculate score from past checks
    result = await db.execute(
        select(AICitationCheck).where(AICitationCheck.project_id == project_id)
    )
    checks = result.scalars().all()
    
    total_checks = len(checks)
    mentions_found = sum(1 for c in checks if getattr(c, 'brand_mentioned', False))
    
    score = (mentions_found / total_checks * 100) if total_checks > 0 else 0
    
    return {
        "project_id": project_id,
        "total_checks": total_checks,
        "mentions_found": mentions_found,
        "citation_score": round(score, 2),
        "message": "Score based on historical citation checks"
    }
