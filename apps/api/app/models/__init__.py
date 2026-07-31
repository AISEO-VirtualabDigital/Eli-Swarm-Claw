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

__all__ = [
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
]
