"""Reports API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.models import Project, CrawlJob, Recommendation, Keyword

router = APIRouter()


@router.get("/dashboard/{project_id}")
async def get_project_dashboard(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get project dashboard summary."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get crawl stats
    crawls_result = await db.execute(
        select(CrawlJob).where(CrawlJob.domain_id.in_(
            select(Project.id).where(Project.id == project_id)  # Simplified
        ))
    )
    crawls = crawls_result.scalars().all()
    
    # Get recommendation stats
    recs_result = await db.execute(
        select(Recommendation).where(Recommendation.project_id == project_id)
    )
    recommendations = recs_result.scalars().all()
    
    # Get keyword count
    keywords_result = await db.execute(
        select(Keyword).where(Keyword.project_id == project_id)
    )
    keywords = keywords_result.scalars().all()
    
    critical_issues = sum(1 for r in recommendations if getattr(r, 'severity', None) == 'critical')
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "total_crawls": len(crawls),
        "total_keywords": len(keywords),
        "total_recommendations": len(recommendations),
        "critical_issues": critical_issues,
        "health_score": calculate_health_score(recommendations),
        "last_updated": datetime.utcnow().isoformat(),
    }


@router.get("/export/{project_id}")
async def export_report(
    project_id: int,
    format: str = "json",
    db: AsyncSession = Depends(get_db),
):
    """Export project report."""
    # TODO: Generate comprehensive PDF/JSON report
    return {
        "project_id": project_id,
        "format": format,
        "status": "generated",
        "message": "Report export placeholder - full implementation pending",
        "generated_at": datetime.utcnow().isoformat(),
    }


def calculate_health_score(recommendations: List[Recommendation]) -> float:
    """Calculate project health score."""
    if not recommendations:
        return 100.0
    
    score = 100.0
    for rec in recommendations:
        severity = getattr(rec, 'severity', 'info')
        if severity == 'critical':
            score -= 5
        elif severity == 'warning':
            score -= 2
        elif severity == 'info':
            score -= 0.5
    
    return max(0.0, min(100.0, score))
