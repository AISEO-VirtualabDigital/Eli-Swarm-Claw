"""
Asymmetrical SEO Strategy Engine

Implements the Pure Organic + Asymmetrical SEO philosophy:
- Artifact Creation over generic content
- First-Mover Exploitation via automated monitoring
- Multi-Surface Domination (Text, AI Overviews, Video, Images)
- Aggressive Long-Tail Programmatic SEO
- Hypertargeting and Rapid Experimentation
- Geographic scaling (National, International, Global)
- AI Citation Optimization (Google Discover, Bing/Copilot, Brave, Claude)
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class GeoTier(str, Enum):
    NATIONAL = "national"
    INTERNATIONAL = "international"
    GLOBAL = "global"


class SurfaceType(str, Enum):
    TEXT = "text"
    AI_OVERVIEW = "ai_overview"  # SGE
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENTATION = "documentation"
    FORUM = "forum"  # Reddit, specialized communities
    GOOGLE_DISCOVER = "google_discover"
    BING_COPILOT = "bing_copilot"
    BRAVE_SEARCH = "brave_search"
    CLAUDE = "claude"


class AssetType(str, Enum):
    CALCULATOR = "calculator"
    DASHBOARD = "dashboard"
    TEMPLATE = "template"
    DATA_REPORT = "data_report"
    PROGRAMMATIC_PAGE = "programmatic_page"
    INTERACTIVE_TOOL = "interactive_tool"
    FRAMEWORK = "framework"


class AsymmetricalStrategy(BaseModel):
    """Core asymmetrical strategy configuration"""
    name: str
    description: str
    geo_tier: GeoTier
    target_surfaces: List[SurfaceType]
    asset_types: List[AssetType]
    hypertargeting_criteria: Dict[str, Any] = Field(
        default_factory=dict,
        description="Criteria for ruthlessly selecting winnable keywords"
    )
    ideaflow_velocity: int = Field(
        ge=1,
        description="Number of ideas to generate/test per week"
    )
    experiment_window_days: int = Field(
        ge=1,
        description="Days to test before killing non-performing tactics"
    )


class AICitationTarget(BaseModel):
    """Configuration for optimizing AI/Alternative Search citations"""
    surface: SurfaceType
    optimization_tactics: List[str]
    schema_types: List[str] = Field(
        default_factory=list,
        description="JSON-LD schema types to implement"
    )
    content_density_requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Requirements for LLM parsing density"
    )
    social_signal_channels: List[str] = Field(
        default_factory=list,
        description="Channels for amplifying social signals"
    )


class GeographicStrategy(BaseModel):
    """Geographic tier strategy configuration"""
    tier: GeoTier
    countries: List[str]
    languages: List[str]
    architecture_type: str = Field(
        description="ccTLD, subdirectory, or subdomain"
    )
    hreflang_enabled: bool = True
    localization_depth: str = Field(
        description="translation, cultural, or full_localization"
    )
    local_authority_targets: List[str] = Field(
        default_factory=list,
        description="Local journals, associations, authorities to target"
    )
    disrespected_keyword_opportunities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Keywords with low-quality local competition"
    )


class ProprietaryAsset(BaseModel):
    """Proprietary SaaS asset for link magnet and citation generation"""
    name: str
    asset_type: AssetType
    data_source: str
    update_frequency: str  # real-time, daily, weekly, monthly
    public_facing: bool = True
    api_accessible: bool = False
    coined_terms: List[str] = Field(
        default_factory=list,
        description="Unique industry terms/frameworks coined by this asset"
    )
    visualization_types: List[str] = Field(
        default_factory=list,
        description="Types of data visualizations included"
    )
    target_entities: List[str] = Field(
        default_factory=list,
        description="Entities to stack/associate with"
    )


class KPIDefinition(BaseModel):
    """Asymmetrical SEO KPI definition"""
    name: str
    description: str
    calculation_method: str
    target_value: Optional[float] = None
    measurement_frequency: str  # daily, weekly, monthly
    surfaces: List[SurfaceType] = Field(default_factory=list)


class AsymmetricalSEOKPIs(BaseModel):
    """Key Performance Indicators for Pure Organic Growth"""
    non_branded_organic_share: KPIDefinition
    proprietary_asset_attribution: KPIDefinition
    ai_citation_rate: KPIDefinition
    link_velocity: KPIDefinition
    zero_cac_ratio: KPIDefinition
    discover_impression_click_ratio: KPIDefinition
    independent_index_share: KPIDefinition
    proprietary_framework_adoption: KPIDefinition
    international_revenue_by_region: KPIDefinition


class ExperimentFramework(BaseModel):
    """Rapid experimentation framework configuration"""
    experiment_id: str
    hypothesis: str
    asset_type: AssetType
    surfaces_targeted: List[SurfaceType]
    v0_launch_date: datetime
    success_metrics: List[str]
    kill_date: datetime
    status: str = Field(
        default="planned",
        description="planned, running, successful, killed"
    )
    learnings: List[str] = Field(default_factory=list)


class MultiSurfaceDominationPlan(BaseModel):
    """Plan for dominating multiple surfaces for a single topic"""
    topic: str
    primary_keyword: str
    long_tail_keywords: List[str]
    surfaces: Dict[SurfaceType, Dict[str, Any]] = Field(
        description="Surface-specific content and optimization plans"
    )
    entity_stack: List[str]
    timely_hook: Optional[str] = Field(
        description="Current trending news cycle to frame around"
    )
    artifact_assets: List[str]


class ProgrammaticSEOEngine(BaseModel):
    """Custom programmatic SEO engine configuration"""
    name: str
    database_connection: str
    template_path: str
    generation_rules: Dict[str, Any]
    scale_target: int = Field(
        description="Target number of pages to generate"
    )
    long_tail_pattern: str
    quality_thresholds: Dict[str, Any]
    canonical_strategy: str


class CompetitiveMoat(BaseModel):
    """Defensible moat analysis"""
    moat_type: str  # data, time, expertise, distribution, technical
    description: str
    copy_cost_estimate: str  # low, medium, high, prohibitive
    time_to_copy_estimate: str  # weeks, months, years
    sustainability_score: int = Field(ge=1, le=10)


# Pre-configured AI Citation Optimization Strategies
AI_CITATION_STRATEGIES = {
    SurfaceType.GOOGLE_DISCOVER: AICitationTarget(
        surface=SurfaceType.GOOGLE_DISCOVER,
        optimization_tactics=[
            "proprietary_data_visualizations",
            "entity_stacking",
            "timely_evergreen_hooks",
            "high_res_visual_assets",
            "curiosity_gap_headlines"
        ],
        schema_types=["Article", "Dataset", "ImageObject"],
        content_density_requirements={
            "visual_to_text_ratio": 0.4,
            "dwell_time_target_seconds": 120,
            "eeat_signals_required": True
        }
    ),
    SurfaceType.BING_COPILOT: AICitationTarget(
        surface=SurfaceType.BING_COPILOT,
        optimization_tactics=[
            "aggressive_schema_dominance",
            "social_signal_amplification",
            "exact_match_optimization",
            "nested_json_ld"
        ],
        schema_types=[
            "Dataset", "SoftwareApplication", "FAQPage", 
            "HowTo", "Organization", "Person"
        ],
        social_signal_channels=["LinkedIn", "Twitter/X"],
        content_density_requirements={
            "schema_completeness_score": 0.95,
            "social_mentions_target": 50
        }
    ),
    SurfaceType.BRAVE_SEARCH: AICitationTarget(
        surface=SurfaceType.BRAVE_SEARCH,
        optimization_tactics=[
            "goggles_exploitation",
            "independent_index_gap_analysis",
            "privacy_focused_content",
            "community_driven_ranking"
        ],
        schema_types=["Dataset", "Article", "WebSite"],
        content_density_requirements={
            "privacy_compliance": True,
            "no_tracking_scripts": True
        }
    ),
    SurfaceType.CLAUDE: AICitationTarget(
        surface=SurfaceType.CLAUDE,
        optimization_tactics=[
            "llm_parsing_density",
            "primary_source_strategy",
            "clean_markdown_formatting",
            "hierarchical_headings",
            "coined_framework_terms"
        ],
        schema_types=["Article", "ScholarlyArticle", "Dataset"],
        content_density_requirements={
            "signal_to_noise_ratio": 0.9,
            "markdown_cleanliness": True,
            "hierarchical_depth": 4,
            "bullet_point_density": 0.3
        }
    )
}


# Standard Asymmetrical KPIs
STANDARD_KPIS = AsymmetricalSEOKPIs(
    non_branded_organic_share=KPIDefinition(
        name="Non-Branded Organic Market Share",
        description="Growth in traffic from users who did not know the brand",
        calculation_method="(Non-branded organic sessions / Total organic sessions) * 100",
        target_value=75.0,
        measurement_frequency="weekly"
    ),
    proprietary_asset_attribution=KPIDefinition(
        name="Proprietary Asset Attribution",
        description="Backlinks and conversions from custom tools/data reports",
        calculation_method="Count of backlinks referencing proprietary assets + conversions attributed",
        target_value=100.0,
        measurement_frequency="monthly",
        surfaces=[SurfaceType.TEXT, SurfaceType.AI_OVERVIEW]
    ),
    ai_citation_rate=KPIDefinition(
        name="AI Citation Rate",
        description="Times domain is named/quoted by Copilot, Claude, Brave",
        calculation_method="Count of AI platform citations per month",
        target_value=50.0,
        measurement_frequency="weekly",
        surfaces=[SurfaceType.BING_COPILOT, SurfaceType.CLAUDE, SurfaceType.BRAVE_SEARCH]
    ),
    link_velocity=KPIDefinition(
        name="Link Velocity",
        description="Rate of new organic editorial backlinks per month",
        calculation_method="New editorial backlinks acquired / month",
        target_value=30.0,
        measurement_frequency="monthly"
    ),
    zero_cac_ratio=KPIDefinition(
        name="Zero-CAC Ratio",
        description="LTV divided by fixed SEO/content team and tooling costs",
        calculation_method="Customer LTV / (SEO team cost + tooling cost)",
        target_value=10.0,
        measurement_frequency="monthly"
    ),
    discover_impression_click_ratio=KPIDefinition(
        name="Discover Impression-to-Click Ratio",
        description="Viral coefficient of content in Google Discover",
        calculation_method="(Clicks from Discover / Impressions in Discover) * 100",
        target_value=5.0,
        measurement_frequency="weekly",
        surfaces=[SurfaceType.GOOGLE_DISCOVER]
    ),
    independent_index_share=KPIDefinition(
        name="Independent Index Market Share",
        description="Percentage of traffic from non-Google sources",
        calculation_method="(Traffic from Brave+Bing+DuckDuckGo / Total organic traffic) * 100",
        target_value=15.0,
        measurement_frequency="monthly",
        surfaces=[SurfaceType.BRAVE_SEARCH, SurfaceType.BING_COPILOT]
    ),
    proprietary_framework_adoption=KPIDefinition(
        name="Proprietary Framework Adoption",
        description="Usage of coined terms in third-party content and AI outputs",
        calculation_method="Count of external mentions of coined framework terms",
        target_value=25.0,
        measurement_frequency="monthly"
    ),
    international_revenue_by_region=KPIDefinition(
        name="International Organic Revenue by Region",
        description="Regional conversions from localized SEO efforts",
        calculation_method="Revenue by region from organic search",
        measurement_frequency="monthly"
    )
)
