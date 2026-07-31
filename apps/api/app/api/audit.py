"""Technical SEO Audit API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models import CrawlJob, Page, Recommendation

router = APIRouter()


@router.post("/analyze/{crawl_id}")
async def analyze_crawl(
    crawl_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Run technical SEO audit on crawl results."""
    # Verify crawl exists and is completed
    result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_id))
    crawl = result.scalar_one_or_none()
    
    if not crawl:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    
    if crawl.status != "completed":
        raise HTTPException(status_code=400, detail="Crawl must be completed before analysis")
    
    # TODO: Trigger SEO Auditor Agent to analyze crawl results
    # For now, return placeholder response
    
    return {
        "crawl_id": crawl_id,
        "status": "analysis_queued",
        "message": "Audit analysis will be performed by SEO Auditor Agent"
    }


@router.get("/results/{crawl_id}")
async def get_audit_results(
    crawl_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get audit results for a crawl."""
    # Get pages from this crawl
    result = await db.execute(
        select(Page).where(Page.crawl_job_id == crawl_id)
    )
    pages = result.scalars().all()
    
    # Get recommendations from this crawl
    rec_result = await db.execute(
        select(Recommendation).where(Recommendation.crawl_job_id == crawl_id)
    )
    recommendations = rec_result.scalars().all()
    
    # Calculate summary stats
    total_pages = len(pages)
    pages_with_issues = sum(1 for p in pages if p.has_issues)
    
    critical_issues = sum(
        1 for r in recommendations 
        if hasattr(r, 'severity') and r.severity == "critical"
    )
    
    return {
        "crawl_id": crawl_id,
        "total_pages": total_pages,
        "pages_with_issues": pages_with_issues,
        "critical_issues": critical_issues,
        "recommendations_count": len(recommendations),
        "health_score": calculate_health_score(pages, recommendations),
    }


@router.get("/issues")
async def list_issues(
    crawl_id: int | None = None,
    severity: str | None = None,
    issue_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List SEO issues from audits."""
    query = select(Recommendation)
    
    if crawl_id:
        query = query.where(Recommendation.crawl_job_id == crawl_id)
    if severity:
        query = query.where(Recommendation.severity == severity)
    if issue_type:
        query = query.where(Recommendation.issue_type == issue_type)
    
    result = await db.execute(query.offset(skip).limit(limit))
    issues = result.scalars().all()
    
    return issues


def calculate_health_score(pages: List[Page], recommendations: List[Recommendation]) -> float:
    """Calculate overall SEO health score (0-100)."""
    if not pages:
        return 0.0
    
    # Base score starts at 100
    score = 100.0
    
    # Deduct points for issues
    critical_deduction = sum(1 for r in recommendations if getattr(r, 'severity', None) == "critical") * 5
    warning_deduction = sum(1 for r in recommendations if getattr(r, 'severity', None) == "warning") * 2
    info_deduction = sum(1 for r in recommendations if getattr(r, 'severity', None) == "info") * 0.5
    
    score -= (critical_deduction + warning_deduction + info_deduction)
    
    # Ensure score stays in valid range
    return max(0.0, min(100.0, score))
