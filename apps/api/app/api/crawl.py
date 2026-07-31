"""Crawl API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models import CrawlJob, Domain
from app.schemas import CrawlStart, CrawlResponse

router = APIRouter()


@router.post("/start", response_model=CrawlResponse, status_code=status.HTTP_201_CREATED)
async def start_crawl(
    crawl_data: CrawlStart,
    db: AsyncSession = Depends(get_db),
):
    """Start a new crawl job."""
    # Verify domain exists
    result = await db.execute(select(Domain).where(Domain.id == crawl_data.domain_id))
    domain = result.scalar_one_or_none()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # Create crawl job
    db_crawl = CrawlJob(
        domain_id=crawl_data.domain_id,
        max_pages=crawl_data.max_pages,
        max_depth=crawl_data.max_depth,
        respect_robots_txt=crawl_data.respect_robots,
        crawl_type=crawl_data.crawl_type,
        status="pending",
    )
    
    db.add(db_crawl)
    await db.commit()
    await db.refresh(db_crawl)
    
    # TODO: Trigger background crawl worker
    # For now, just return the created job
    
    return db_crawl


@router.get("/jobs", response_model=List[CrawlResponse])
async def list_crawl_jobs(
    domain_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List crawl jobs."""
    query = select(CrawlJob)
    if domain_id:
        query = query.where(CrawlJob.domain_id == domain_id)
    
    result = await db.execute(query.order_by(CrawlJob.created_at.desc()).offset(skip).limit(limit))
    crawls = result.scalars().all()
    return crawls


@router.get("/jobs/{crawl_id}", response_model=CrawlResponse)
async def get_crawl_job(
    crawl_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific crawl job by ID."""
    result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_id))
    crawl = result.scalar_one_or_none()
    
    if not crawl:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    
    return crawl


@router.post("/jobs/{crawl_id}/cancel", response_model=CrawlResponse)
async def cancel_crawl(
    crawl_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running crawl job."""
    result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_id))
    crawl = result.scalar_one_or_none()
    
    if not crawl:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    
    if crawl.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Crawl job is not running")
    
    crawl.status = "cancelled"
    await db.commit()
    await db.refresh(crawl)
    
    return crawl
