"""AI Studio - Generative Media Engine API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import MediaProvider, MediaJob, MediaAsset, MediaMetrics, User
from app.models.media import GenerationStatus, MediaType, ProviderStatus
from app.schemas import (
    MediaProviderCreate,
    MediaProviderUpdate,
    MediaProviderResponse,
    MediaJobCreate,
    MediaJobResponse,
    MediaJobUpdate,
    MediaAssetCreate,
    MediaAssetResponse,
    MediaAssetUpdate,
    GenerateImageRequest,
    GenerateVideoRequest,
    JobStatusResponse,
    GenerationMetricsResponse,
)

router = APIRouter(prefix="/api/v1/media", tags=["AI Studio - Media Generation"])


# ============ Provider Management ============

@router.get("/providers", response_model=List[MediaProviderResponse])
def list_providers(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[ProviderStatus] = None,
    provider_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all configured media providers."""
    query = db.query(MediaProvider)
    
    if status_filter:
        query = query.filter(MediaProvider.status == status_filter)
    if provider_type:
        query = query.filter(MediaProvider.provider_type == provider_type)
    
    providers = query.order_by(MediaProvider.priority).offset(skip).limit(limit).all()
    return providers


@router.get("/providers/{provider_id}", response_model=MediaProviderResponse)
def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific provider."""
    provider = db.query(MediaProvider).filter(MediaProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.post("/providers", response_model=MediaProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(
    provider: MediaProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new media provider configuration."""
    # Check if provider name already exists
    existing = db.query(MediaProvider).filter(MediaProvider.name == provider.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Provider with this name already exists")
    
    db_provider = MediaProvider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


@router.put("/providers/{provider_id}", response_model=MediaProviderResponse)
def update_provider(
    provider_id: int,
    provider_update: MediaProviderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update provider configuration."""
    db_provider = db.query(MediaProvider).filter(MediaProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    update_data = provider_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_provider, field, value)
    
    db.commit()
    db.refresh(db_provider)
    return db_provider


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a provider configuration."""
    db_provider = db.query(MediaProvider).filter(MediaProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    db.delete(db_provider)
    db.commit()
    return None


# ============ Image Generation ============

@router.post("/generate/image", response_model=MediaJobResponse, status_code=status.HTTP_201_CREATED)
async def generate_image(
    request: GenerateImageRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI image from text prompt."""
    # Select provider
    provider_id = request.provider_id
    if not provider_id:
        # Get best available provider
        provider = db.query(MediaProvider).filter(
            MediaProvider.status == ProviderStatus.ACTIVE,
            MediaProvider.provider_type.in_(["image", "both"])
        ).order_by(MediaProvider.priority).first()
        
        if not provider:
            raise HTTPException(status_code=503, detail="No active image providers available")
        provider_id = provider.id
    
    # Create job
    job_id = f"img_{uuid.uuid4().hex[:12]}"
    job = MediaJob(
        job_id=job_id,
        media_type=MediaType.IMAGE,
        generation_type="text_to_image",
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        style_preset=request.style_preset,
        seed=request.seed,
        width=request.width,
        height=request.height,
        num_inference_steps=request.num_inference_steps,
        guidance_scale=request.guidance_scale,
        provider_id=provider_id,
        user_id=current_user.id,
        project_id=request.project_id,
        campaign_id=request.campaign_id,
        status=GenerationStatus.PENDING,
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Queue the job for processing
    background_tasks.add_task(process_media_job, job.id)
    
    return job


# ============ Video Generation ============

@router.post("/generate/video", response_model=MediaJobResponse, status_code=status.HTTP_201_CREATED)
async def generate_video(
    request: GenerateVideoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI video from text prompt."""
    # Select provider
    provider_id = request.provider_id
    if not provider_id:
        # Get best available provider
        provider = db.query(MediaProvider).filter(
            MediaProvider.status == ProviderStatus.ACTIVE,
            MediaProvider.provider_type.in_(["video", "both"])
        ).order_by(MediaProvider.priority).first()
        
        if not provider:
            raise HTTPException(status_code=503, detail="No active video providers available")
        provider_id = provider.id
    
    # Create job
    job_id = f"vid_{uuid.uuid4().hex[:12]}"
    job = MediaJob(
        job_id=job_id,
        media_type=MediaType.VIDEO,
        generation_type="text_to_video",
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        style_preset=request.style_preset,
        seed=request.seed,
        width=request.width,
        height=request.height,
        duration=request.duration,
        fps=request.fps,
        provider_id=provider_id,
        user_id=current_user.id,
        project_id=request.project_id,
        campaign_id=request.campaign_id,
        status=GenerationStatus.PENDING,
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Queue the job for processing
    background_tasks.add_task(process_media_job, job.id)
    
    return job


# ============ Job Management ============

@router.get("/jobs", response_model=List[MediaJobResponse])
def list_jobs(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[GenerationStatus] = None,
    media_type: Optional[MediaType] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List media generation jobs."""
    query = db.query(MediaJob).filter(MediaJob.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(MediaJob.status == status_filter)
    if media_type:
        query = query.filter(MediaJob.media_type == media_type)
    if project_id:
        query = query.filter(MediaJob.project_id == project_id)
    
    jobs = query.order_by(MediaJob.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/jobs/{job_id}", response_model=MediaJobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific job."""
    job = db.query(MediaJob).filter(
        MediaJob.id == job_id,
        MediaJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current status of a generation job."""
    job = db.query(MediaJob).filter(
        MediaJob.id == job_id,
        MediaJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    result_url = None
    thumbnail_url = None
    
    # If completed, get asset URLs
    if job.status == GenerationStatus.COMPLETED and job.assets:
        asset = job.assets[0]
        result_url = asset.public_url
        thumbnail_url = asset.thumbnail_url
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        media_type=job.media_type,
        result_url=result_url,
        thumbnail_url=thumbnail_url,
        error_message=job.error_message,
    )


@router.post("/jobs/{job_id}/cancel", response_model=MediaJobResponse)
def cancel_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a running or pending job."""
    job = db.query(MediaJob).filter(
        MediaJob.id == job_id,
        MediaJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status in [GenerationStatus.COMPLETED, GenerationStatus.FAILED, GenerationStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status {job.status}")
    
    job.status = GenerationStatus.CANCELLED
    db.commit()
    db.refresh(job)
    return job


# ============ Asset Management ============

@router.get("/assets", response_model=List[MediaAssetResponse])
def list_assets(
    skip: int = 0,
    limit: int = 20,
    media_type: Optional[MediaType] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List generated media assets."""
    query = db.query(MediaAsset).join(MediaJob).filter(MediaJob.user_id == current_user.id)
    
    if media_type:
        query = query.filter(MediaAsset.media_type == media_type)
    if project_id:
        query = query.filter(MediaAsset.project_id == project_id)
    
    assets = query.order_by(MediaAsset.created_at.desc()).offset(skip).limit(limit).all()
    return assets


@router.get("/assets/{asset_id}", response_model=MediaAssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific asset."""
    asset = db.query(MediaAsset).join(MediaJob).filter(
        MediaAsset.id == asset_id,
        MediaJob.user_id == current_user.id
    ).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/assets/{asset_id}", response_model=MediaAssetResponse)
def update_asset(
    asset_id: int,
    asset_update: MediaAssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update asset metadata."""
    asset = db.query(MediaAsset).join(MediaJob).filter(
        MediaAsset.id == asset_id,
        MediaJob.user_id == current_user.id
    ).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    update_data = asset_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)
    
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete an asset."""
    asset = db.query(MediaAsset).join(MediaJob).filter(
        MediaAsset.id == asset_id,
        MediaJob.user_id == current_user.id
    ).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset.is_deleted = True
    db.commit()
    return None


# ============ Metrics ============

@router.get("/metrics", response_model=List[GenerationMetricsResponse])
def get_metrics(
    days: int = Query(default=7, ge=1, le=90),
    provider_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get generation metrics for the specified period."""
    from sqlalchemy import func
    
    query = db.query(
        MediaProvider.name.label("provider_name"),
        func.sum(MediaMetrics.total_jobs).label("total_jobs"),
        func.avg(MediaMetrics.success_rate).label("success_rate"),
        func.avg(MediaMetrics.average_generation_time).label("average_generation_time"),
        func.avg(MediaMetrics.cost_per_successful_output).label("cost_per_successful_output"),
        func.avg(MediaMetrics.average_queue_time).label("queue_time"),
    ).join(MediaProvider)
    
    if provider_id:
        query = query.filter(MediaMetrics.provider_id == provider_id)
    
    metrics = query.group_by(MediaProvider.name).all()
    
    return [
        GenerationMetricsResponse(
            provider_name=m.provider_name,
            total_jobs=m.total_jobs or 0,
            success_rate=m.success_rate or 0.0,
            average_generation_time=m.average_generation_time or 0.0,
            cost_per_successful_output=m.cost_per_successful_output or 0.0,
            queue_time=m.queue_time or 0.0,
            generation_time=m.average_generation_time or 0.0,
            total_time=(m.queue_time or 0.0) + (m.average_generation_time or 0.0),
        )
        for m in metrics
    ]


# ============ Background Task Processor ============

def process_media_job(job_id: int):
    """Background task to process media generation jobs.
    
    In production, this would be handled by Celery/Redis queue.
    This is a simplified implementation for demonstration.
    """
    from app.core.database import SessionLocal
    import asyncio
    import random
    
    db = SessionLocal()
    try:
        job = db.query(MediaJob).filter(MediaJob.id == job_id).first()
        if not job:
            return
        
        # Update status to queued
        job.status = GenerationStatus.QUEUED
        job.queued_at = datetime.utcnow()
        db.commit()
        
        # Simulate provider selection and API call
        provider = db.query(MediaProvider).filter(MediaProvider.id == job.provider_id).first()
        if not provider or provider.status != ProviderStatus.ACTIVE:
            # Try fallback provider
            if provider and provider.fallback_provider_id:
                fallback = db.query(MediaProvider).filter(
                    MediaProvider.id == provider.fallback_provider_id
                ).first()
                if fallback and fallback.status == ProviderStatus.ACTIVE:
                    job.provider_id = fallback.id
                    provider = fallback
            
            if not provider or provider.status != ProviderStatus.ACTIVE:
                job.status = GenerationStatus.FAILED
                job.error_message = "No active provider available"
                db.commit()
                return
        
        # Start processing
        job.status = GenerationStatus.PROCESSING
        job.started_at = datetime.utcnow()
        job.progress = 10
        db.commit()
        
        # Simulate generation progress (in real implementation, this calls the provider API)
        for progress in range(10, 100, 10):
            job.progress = progress
            db.commit()
            asyncio.sleep(0.5)  # Simulate work
        
        # Complete the job
        job.status = GenerationStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.utcnow()
        
        # Calculate cost
        if job.media_type == MediaType.IMAGE:
            job.actual_cost = provider.cost_per_image
        else:
            job.actual_cost = provider.cost_per_video * (job.duration or 1)
        
        # Create asset record
        asset = MediaAsset(
            asset_id=f"asset_{uuid.uuid4().hex[:12]}",
            job_id=job.id,
            provider_id=job.provider_id,
            project_id=job.project_id,
            media_type=job.media_type,
            format="png" if job.media_type == MediaType.IMAGE else "mp4",
            storage_type="local",
            file_path=f"/media/{job.job_id}/output.{ 'png' if job.media_type == MediaType.IMAGE else 'mp4' }",
            public_url=f"https://cdn.example.com/media/{job.job_id}/output",
            thumbnail_url=f"https://cdn.example.com/media/{job.job_id}/thumb",
            width=job.width,
            height=job.height,
            duration=float(job.duration) if job.duration else None,
            file_size=random.randint(100000, 5000000),
            prompt_used=job.prompt,
            model_used=provider.supported_models[0] if provider.supported_models else "default",
        )
        db.add(asset)
        
        db.commit()
        
    except Exception as e:
        if job:
            job.status = GenerationStatus.FAILED
            job.error_message = str(e)
            db.commit()
    finally:
        db.close()
