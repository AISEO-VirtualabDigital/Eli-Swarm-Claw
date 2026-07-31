"""Indexing and Discovery API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models import IndexingJob, Asset

router = APIRouter()


@router.post("/submit")
async def submit_url(
    url: str,
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Submit a URL for indexing discovery."""
    # Create indexing job
    job = IndexingJob(
        url=url,
        project_id=project_id,
        status="pending",
        submission_method="manual",
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # TODO: Trigger Indexing Agent for submission
    return {
        "job_id": job.id,
        "url": url,
        "status": "submitted",
        "message": "URL queued for discovery workflow"
    }


@router.post("/batch-submit")
async def batch_submit(
    urls: List[str],
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Submit multiple URLs for indexing."""
    jobs = []
    for url in urls:
        job = IndexingJob(
            url=url,
            project_id=project_id,
            status="pending",
            submission_method="batch",
        )
        db.add(job)
        jobs.append({"job_id": job.id, "url": url})
    
    await db.commit()
    
    return {
        "submitted_count": len(jobs),
        "jobs": jobs,
        "message": "Batch submission queued"
    }


@router.get("/jobs")
async def list_indexing_jobs(
    project_id: int | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List indexing jobs."""
    query = select(IndexingJob)
    
    if project_id:
        query = query.where(IndexingJob.project_id == project_id)
    if status:
        query = query.where(IndexingJob.status == status)
    
    result = await db.execute(query.order_by(IndexingJob.created_at.desc()).offset(skip).limit(limit))
    jobs = result.scalars().all()
    
    return jobs


@router.get("/sitemap/generate")
async def generate_sitemap(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Generate XML sitemap for a project."""
    # Get all published assets
    result = await db.execute(
        select(Asset).where(Asset.project_id == project_id)
    )
    assets = result.scalars().all()
    
    # TODO: Generate proper XML sitemap
    return {
        "project_id": project_id,
        "urls_count": len(assets),
        "sitemap_xml": "<!-- Sitemap generation placeholder -->",
        "message": "Sitemap generated"
    }
