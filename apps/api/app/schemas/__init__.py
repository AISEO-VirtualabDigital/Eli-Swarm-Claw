"""Pydantic schemas for API validation."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

# Import AI Studio schemas
from .media import (
    MediaType,
    GenerationStatus,
    ProviderStatus,
    MediaProviderBase,
    MediaProviderCreate,
    MediaProviderUpdate,
    MediaProviderResponse,
    MediaJobBase,
    MediaJobCreate,
    MediaJobUpdate,
    MediaJobResponse,
    MediaAssetBase,
    MediaAssetCreate,
    MediaAssetUpdate,
    MediaAssetResponse,
    MediaMetricsBase,
    MediaMetricsResponse,
    GenerateImageRequest,
    GenerateVideoRequest,
    JobStatusResponse,
    GenerationMetricsResponse,
)


# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    industry: Optional[str] = None
    target_location: Optional[str] = None
    website_url: Optional[HttpUrl] = None


class ProjectCreate(ProjectBase):
    workspace_id: int
    organization_id: int


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    target_location: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    workspace_id: int
    organization_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Domain Schemas
class DomainBase(BaseModel):
    domain: str = Field(..., min_length=1, max_length=255)
    name: Optional[str] = None


class DomainCreate(DomainBase):
    project_id: int


class DomainResponse(DomainBase):
    id: int
    project_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Crawl Schemas
class CrawlStart(BaseModel):
    domain_id: int
    max_pages: int = 1000
    max_depth: int = 5
    respect_robots: bool = True
    crawl_type: str = "full"  # full, quick, custom


class CrawlResponse(BaseModel):
    id: int
    domain_id: int
    status: str
    pages_crawled: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Keyword Schemas
class KeywordResearchRequest(BaseModel):
    seed_keywords: List[str]
    industry: Optional[str] = None
    location: Optional[str] = None
    competitor_urls: Optional[List[str]] = None


class KeywordResponse(BaseModel):
    id: int
    keyword: str
    parent_topic: Optional[str]
    intent: Optional[str]
    opportunity_score: Optional[int]
    
    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationResponse(BaseModel):
    id: int
    url: str
    issue_type: str
    severity: str
    recommendation: str
    priority_score: int
    status: str
    
    class Config:
        from_attributes = True


# Task Schemas (Project Management)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    task_type: str
    project_id: int
    campaign_id: Optional[int] = None
    priority: str = "medium"
    effort_estimate: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    task_type: str
    status: str
    priority: str
    project_id: int
    assigned_to: Optional[int]
    due_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Repository Scan Schemas
class RepositoryScanRequest(BaseModel):
    repo_url: str
    project_id: Optional[int] = None


class RepositoryScanResponse(BaseModel):
    id: int
    repo_name: str
    repo_url: str
    owner: str
    license_type: str
    stars: Optional[int]
    primary_language: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Parasite SEO Schemas
class ParasiteOpportunityResponse(BaseModel):
    id: int
    platform: str
    url: str
    topic: Optional[str]
    authority_score: Optional[int]
    relevance_score: Optional[int]
    risk_level: str
    
    class Config:
        from_attributes = True


# Reddit Research Schemas
class RedditFindingResponse(BaseModel):
    id: int
    subreddit: str
    post_title: str
    post_url: str
    topic: Optional[str]
    pain_point: Optional[str]
    lead_potential_score: Optional[int]
    
    class Config:
        from_attributes = True


# YouTube SEO Schemas
class YouTubeVideoResponse(BaseModel):
    id: int
    video_url: str
    title: Optional[str]
    target_keyword: Optional[str]
    optimization_score: Optional[int]
    
    class Config:
        from_attributes = True


# Social SEO Schemas
class SocialPostResponse(BaseModel):
    id: int
    platform: str
    post_url: str
    caption: Optional[str]
    target_keyword: Optional[str]
    
    class Config:
        from_attributes = True


# API Connector Schemas
class APIConnectorCreate(BaseModel):
    provider_name: str
    api_name: str
    base_url: str
    auth_type: str
    data_type: str
    project_id: Optional[int] = None


class APIConnectorResponse(BaseModel):
    id: int
    provider_name: str
    api_name: str
    base_url: str
    auth_type: str
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
