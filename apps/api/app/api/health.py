"""Health check endpoint."""

from fastapi import APIRouter, status
from datetime import datetime

from app.core.config import settings

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    
    Returns application status and basic information.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    
    Indicates whether the service is ready to accept traffic.
    """
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
    }
