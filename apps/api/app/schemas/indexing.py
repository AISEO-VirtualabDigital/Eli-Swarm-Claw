"""Pydantic schemas for Indexing and Discovery module."""

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class IndexingSubmitRequest(BaseModel):
    """Request to submit a single URL for indexing."""
    
    url: HttpUrl = Field(..., description="URL to submit for indexing")
    project_id: int = Field(..., description="Project ID")
    asset_id: Optional[int] = Field(None, description="Associated asset ID if exists")
    method: Optional[str] = Field("manual", description="Submission method: manual, indexnow, sitemap, rss")
    content_hash: Optional[str] = Field(None, description="SHA-256 hash of content for change detection")
    notes: Optional[str] = Field(None, description="Optional notes about this submission")
    
    model_config = ConfigDict(from_attributes=True)


class IndexingBatchSubmitRequest(BaseModel):
    """Request to submit multiple URLs for indexing."""
    
    urls: List[HttpUrl] = Field(..., description="List of URLs to submit", min_length=1, max_length=1000)
    project_id: int = Field(..., description="Project ID")
    
    model_config = ConfigDict(from_attributes=True)


class IndexingJobResponse(BaseModel):
    """Response containing indexing job details."""
    
    id: int
    url: str
    project_id: Optional[int]
    asset_id: Optional[int]
    status: str
    indexing_status: Optional[str]
    method: Optional[str]
    submitted_at: Optional[datetime]
    last_checked_at: Optional[datetime]
    retry_count: int
    response_code: Optional[int]
    response_message: Optional[str]
    exclusion_reason: Optional[str]
    canonical_url: Optional[str]
    content_hash: Optional[str]
    metadata: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class IndexingStatusResponse(BaseModel):
    """Response for indexing submission status."""
    
    message: str
    status: str
    url: str
    job_id: Optional[int]
    details: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class SitemapGenerateRequest(BaseModel):
    """Request to generate XML sitemap."""
    
    project_id: int = Field(..., description="Project ID")
    base_url: Optional[str] = Field(None, description="Base URL for the sitemap")
    include_only_indexable: bool = Field(True, description="Only include indexable assets")
    include_changefreq: bool = Field(False, description="Include changefreq tags")
    include_priority: bool = Field(False, description="Include priority tags")
    
    model_config = ConfigDict(from_attributes=True)


class IndexabilityCheckRequest(BaseModel):
    """Request to check URL indexability."""
    
    url: HttpUrl = Field(..., description="URL to check")
    crawl_data: Optional[Dict[str, Any]] = Field(None, description="Existing crawl data if available")
    
    model_config = ConfigDict(from_attributes=True)


class IndexabilityIssue(BaseModel):
    """Single indexability issue."""
    
    type: str
    severity: str  # critical, high, medium, warning, low
    message: str
    impact: str
    
    model_config = ConfigDict(from_attributes=True)


class IndexabilityRecommendation(BaseModel):
    """Single recommendation to improve indexability."""
    
    action: str
    message: str
    
    model_config = ConfigDict(from_attributes=True)


class IndexabilityCheckResponse(BaseModel):
    """Response from indexability check."""
    
    url: str
    is_indexable: bool
    indexability_score: int = Field(ge=0, le=100)
    status: str  # ready_for_submission, needs_improvement, blocked
    message: str
    checked_at: datetime
    issues: List[IndexabilityIssue]
    recommendations: List[IndexabilityRecommendation]
    
    model_config = ConfigDict(from_attributes=True)


class RetryRecommendationResponse(BaseModel):
    """Response with retry recommendation."""
    
    should_retry: bool
    reason: str
    suggested_action: str
    current_retry_count: int
    max_retries: int
    job_status: str
    content_changed: bool
    
    model_config = ConfigDict(from_attributes=True)


class IndexingReportSummary(BaseModel):
    """Summary statistics for indexing report."""
    
    total_submissions: int
    indexed: int
    crawled_not_indexed: int
    submitted_pending: int
    errors: int
    excluded: int
    success_rate: float
    
    model_config = ConfigDict(from_attributes=True)


class IndexingRecommendation(BaseModel):
    """Single recommendation from indexing report."""
    
    priority: str  # critical, high, medium, low
    category: str
    issue: str
    action: str
    message: str
    
    model_config = ConfigDict(from_attributes=True)


class NextAction(BaseModel):
    """Next action item from report."""
    
    priority: int
    action: str
    description: str
    endpoint: str
    
    model_config = ConfigDict(from_attributes=True)


class IndexingReportResponse(BaseModel):
    """Comprehensive indexing report."""
    
    project: str
    generated_at: datetime
    summary: IndexingReportSummary
    status_breakdown: Dict[str, int]
    health_score: int = Field(ge=0, le=100)
    recommendations: List[IndexingRecommendation]
    next_actions: List[NextAction]
    
    model_config = ConfigDict(from_attributes=True)


class IndexNowSubmissionResult(BaseModel):
    """Result from IndexNow submission."""
    
    success: bool
    method: str
    url: str
    status_code: Optional[int]
    message: str
    error: Optional[str]
    suggestion: Optional[str]
    submitted_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)
