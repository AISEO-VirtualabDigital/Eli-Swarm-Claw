"""Indexing and Discovery API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.indexing import IndexingJob
from app.models.asset import Asset
from app.models.project import Project
from app.services.indexing import indexing_service
from app.schemas.indexing import (
    IndexingSubmitRequest,
    IndexingBatchSubmitRequest,
    IndexingJobResponse,
    IndexingStatusResponse,
    SitemapGenerateRequest,
    IndexabilityCheckRequest,
    IndexingReportResponse
)

router = APIRouter()


@router.post("/submit", response_model=IndexingStatusResponse)
async def submit_url(
    request: IndexingSubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a URL for indexing discovery.
    
    This creates an indexing job that will be processed by the Indexing Agent.
    The system uses compliant methods: IndexNow, sitemap updates, RSS feeds.
    
    **Important:** This does NOT guarantee indexing. It improves discovery probability.
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if URL already has pending/active job
    existing = await db.execute(
        select(IndexingJob).where(
            IndexingJob.url == request.url,
            IndexingJob.project_id == request.project_id,
            IndexingJob.status.in_(["pending", "submitted"])
        )
    )
    if existing.scalar_one_or_none():
        return IndexingStatusResponse(
            message="URL already in queue",
            status="queued",
            url=request.url,
            job_id=None
        )
    
    # Create indexing job
    job = IndexingJob(
        url=request.url,
        project_id=request.project_id,
        asset_id=request.asset_id,
        status="pending",
        method=request.method or "manual",
        content_hash=request.content_hash,
        notes=request.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return IndexingStatusResponse(
        message="URL queued for discovery workflow",
        status="submitted",
        url=request.url,
        job_id=job.id
    )


@router.post("/batch-submit", response_model=IndexingStatusResponse)
async def batch_submit(
    request: IndexingBatchSubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit multiple URLs for indexing.
    
    Efficiently queue multiple URLs for discovery processing.
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    jobs = []
    for url in request.urls:
        # Skip duplicates in batch
        if request.urls.count(url) > 1 and url != url:
            continue
            
        job = IndexingJob(
            url=url,
            project_id=request.project_id,
            status="pending",
            method="batch",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(job)
        jobs.append({"job_id": None, "url": url})  # Will get IDs after commit
    
    await db.commit()
    
    # Refresh to get IDs
    for i, job in enumerate(db.new):
        if isinstance(job, IndexingJob):
            await db.refresh(job)
            jobs[i]["job_id"] = job.id
    
    return IndexingStatusResponse(
        message=f"Batch submission queued ({len(jobs)} URLs)",
        status="submitted",
        url=f"{len(jobs)} URLs",
        job_id=None,
        details={"jobs": jobs, "submitted_count": len(jobs)}
    )


@router.get("/jobs", response_model=List[IndexingJobResponse])
async def list_indexing_jobs(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    asset_id: Optional[int] = Query(None, description="Filter by asset ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List indexing jobs with optional filters."""
    query = select(IndexingJob)
    
    if project_id:
        query = query.where(IndexingJob.project_id == project_id)
    if status:
        query = query.where(IndexingJob.status == status)
    if asset_id:
        query = query.where(IndexingJob.asset_id == asset_id)
    
    query = query.order_by(IndexingJob.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [
        IndexingJobResponse(
            id=job.id,
            url=job.url,
            project_id=job.project_id,
            asset_id=job.asset_id,
            status=job.status,
            indexing_status=job.indexing_status,
            method=job.method,
            submitted_at=job.submitted_at,
            last_checked_at=job.last_checked_at,
            retry_count=job.retry_count,
            response_code=job.response_code,
            exclusion_reason=job.exclusion_reason,
            canonical_url=job.canonical_url,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}", response_model=IndexingJobResponse)
async def get_indexing_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific indexing job."""
    result = await db.execute(select(IndexingJob).where(IndexingJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Indexing job not found")
    
    return IndexingJobResponse(
        id=job.id,
        url=job.url,
        project_id=job.project_id,
        asset_id=job.asset_id,
        status=job.status,
        indexing_status=job.indexing_status,
        method=job.method,
        submitted_at=job.submitted_at,
        last_checked_at=job.last_checked_at,
        retry_count=job.retry_count,
        response_code=job.response_code,
        response_message=job.response_message,
        exclusion_reason=job.exclusion_reason,
        canonical_url=job.canonical_url,
        content_hash=job.content_hash,
        metadata=job.metadata,
        notes=job.notes,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.post("/sitemap/generate")
async def generate_sitemap(
    request: SitemapGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate XML sitemap for a project.
    
    Creates a standards-compliant sitemap.xml following sitemaps.org protocol.
    """
    # Get all published assets for the project
    query = select(Asset).where(Asset.project_id == request.project_id)
    
    if request.include_only_indexable:
        # Filter out assets with noindex or issues
        query = query.where(Asset.indexing_status.not_in(["noindex", "excluded"]))
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    if not assets:
        return {
            "project_id": request.project_id,
            "urls_count": 0,
            "message": "No assets found for sitemap generation",
            "sitemap_xml": ""
        }
    
    # Prepare URLs for sitemap
    urls_for_sitemap = []
    for asset in assets:
        url_data = {
            "loc": asset.url,
        }
        
        if asset.updated_at:
            url_data["lastmod"] = asset.updated_at.strftime("%Y-%m-%d")
        
        if request.include_changefreq:
            # Infer change frequency from asset type
            changefreq_map = {
                "blog_post": "weekly",
                "news": "daily",
                "landing_page": "monthly",
                "product": "weekly",
            }
            url_data["changefreq"] = changefreq_map.get(asset.asset_type, "monthly")
        
        if request.include_priority:
            # Assign priority based on asset importance
            priority_map = {
                "landing_page": 1.0,
                "homepage": 1.0,
                "product": 0.8,
                "blog_post": 0.6,
                "category": 0.7,
            }
            url_data["priority"] = priority_map.get(asset.asset_type, 0.5)
        
        urls_for_sitemap.append(url_data)
    
    # Generate sitemap XML
    base_url = request.base_url or ""
    sitemap_xml = indexing_service.generate_sitemap_xml(
        urls=urls_for_sitemap,
        base_url=base_url,
        lastmod_default=datetime.utcnow().strftime("%Y-%m-%d")
    )
    
    return {
        "project_id": request.project_id,
        "urls_count": len(urls_for_sitemap),
        "sitemap_size_bytes": len(sitemap_xml.encode('utf-8')),
        "generated_at": datetime.utcnow().isoformat(),
        "sitemap_xml": sitemap_xml,
        "download_filename": f"sitemap_{request.project_id}.xml",
        "note": "Upload this file to your website root and reference in robots.txt"
    }


@router.post("/check-indexability")
async def check_indexability(
    request: IndexabilityCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Check if a URL has technical barriers to indexing.
    
    Analyzes crawl data to identify issues that would prevent indexing.
    """
    # Get crawl result if available
    crawl_result = request.crawl_data
    
    # Perform indexability check
    result = await indexing_service.check_url_indexability(
        url=request.url,
        crawl_result=crawl_result
    )
    
    return result


@router.get("/report/{project_id}")
async def generate_indexing_report(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate comprehensive indexing status report for a project.
    
    Includes statistics, health score, and prioritized recommendations.
    """
    # Get project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all indexing jobs for project
    result = await db.execute(
        select(IndexingJob).where(IndexingJob.project_id == project_id)
    )
    jobs = result.scalars().all()
    
    # Generate report
    report = indexing_service.generate_indexing_report(
        indexing_jobs=jobs,
        project_name=project.name
    )
    
    return report


@router.post("/retry-recommendation/{job_id}")
async def get_retry_recommendation(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get recommendation on whether to retry indexing submission.
    
    Uses smart logic to avoid unnecessary resubmissions.
    Only recommends retry when content changed or enough time passed.
    """
    result = await db.execute(select(IndexingJob).where(IndexingJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Indexing job not found")
    
    # Determine if content changed (compare hashes)
    content_changed = False
    if job.content_hash and request.new_content_hash:
        content_changed = job.content_hash != request.new_content_hash
    
    recommendation = indexing_service.get_retry_recommendation(
        job_status=job.status,
        retry_count=job.retry_count,
        last_submitted=job.submitted_at or job.created_at,
        content_changed=content_changed
    )
    
    return recommendation
