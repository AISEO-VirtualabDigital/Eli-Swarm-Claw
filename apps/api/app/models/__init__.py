"""Database models package."""

# Import all models to register them with Base metadata
from .user import User
from .organization import Organization
from .workspace import Workspace
from .project import Project
from .domain import Domain
from .page import Page, CrawlResult
from .crawl import CrawlJob
from .keyword import Keyword, KeywordCluster
from .entity import Entity
from .asset import Asset, AssetEntity
from .indexing import IndexingJob
from .citation import AICitationCheck
from .recommendation import Recommendation
from .competitor import Competitor

# AI Studio - Generative Media Engine
from .media import MediaProvider, MediaJob, MediaAsset, MediaMetrics, MediaType, GenerationStatus, ProviderStatus

# New SaaS modules
from .project_management import Campaign, Milestone, Task, Subtask, TaskComment, TaskAttachment, TaskStatus, TaskPriority
from .parasite_seo import ParasiteOpportunity, ParasitePlatform
from .reddit import RedditFinding, SubredditProfile, RedditLeadSignal
from .youtube import YouTubeVideo, YouTubeKeyword, YouTubePlaylist
from .social import SocialPost, SocialProfile, SocialKeyword, GBPPost
from .repositories import RepositoryScan, RepurposingPlan, PublicAPIConnector, APIKeyStatus, LicenseType

__all__ = [
    # Core models
    "User",
    "Organization",
    "Workspace",
    "Project",
    "Domain",
    "Page",
    "CrawlResult",
    "CrawlJob",
    "Keyword",
    "KeywordCluster",
    "Entity",
    "Asset",
    "AssetEntity",
    "IndexingJob",
    "AICitationCheck",
    "Recommendation",
    "Competitor",
    
    # AI Studio - Generative Media
    "MediaProvider",
    "MediaJob",
    "MediaAsset",
    "MediaMetrics",
    "MediaType",
    "GenerationStatus",
    "ProviderStatus",
    
    # Project Management
    "Campaign",
    "Milestone",
    "Task",
    "Subtask",
    "TaskComment",
    "TaskAttachment",
    "TaskStatus",
    "TaskPriority",
    
    # Parasite SEO
    "ParasiteOpportunity",
    "ParasitePlatform",
    
    # Reddit Research
    "RedditFinding",
    "SubredditProfile",
    "RedditLeadSignal",
    
    # YouTube SEO
    "YouTubeVideo",
    "YouTubeKeyword",
    "YouTubePlaylist",
    
    # Social SEO
    "SocialPost",
    "SocialProfile",
    "SocialKeyword",
    "GBPPost",
    
    # Repository & API
    "RepositoryScan",
    "RepurposingPlan",
    "PublicAPIConnector",
    "APIKeyStatus",
    "LicenseType",
]
