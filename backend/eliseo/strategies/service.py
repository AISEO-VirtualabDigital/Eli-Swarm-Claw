"""
Asymmetrical SEO Service

Implements the core logic for:
- Artifact creation strategies
- Multi-surface domination
- AI citation optimization
- Geographic scaling
- Rapid experimentation
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from .asymmetrical_seo import (
    GeoTier,
    SurfaceType,
    AssetType,
    AsymmetricalStrategy,
    AICitationTarget,
    GeographicStrategy,
    ProprietaryAsset,
    ExperimentFramework,
    MultiSurfaceDominationPlan,
    ProgrammaticSEOEngine,
    CompetitiveMoat,
    AI_CITATION_STRATEGIES,
    STANDARD_KPIS,
)

logger = logging.getLogger(__name__)


class AsymmetricalSEOService:
    """
    Service for implementing Pure Organic + Asymmetrical SEO strategies.
    
    Core capabilities:
    - Artifact Creation over generic content
    - First-Mover Exploitation
    - Multi-Surface Domination
    - Aggressive Long-Tail Programmatic SEO
    - AI Citation Optimization (Google Discover, Bing/Copilot, Brave, Claude)
    - Geographic scaling (National, International, Global)
    """
    
    def __init__(self):
        self.ai_citation_strategies = AI_CITATION_STRATEGIES
        self.standard_kpis = STANDARD_KPIS
        self.active_experiments: Dict[str, ExperimentFramework] = {}
        self.proprietary_assets: List[ProprietaryAsset] = []
        
    def create_asymmetrical_strategy(
        self,
        name: str,
        description: str,
        geo_tier: GeoTier,
        target_surfaces: List[SurfaceType],
        asset_types: List[AssetType],
        hypertargeting_criteria: Dict[str, Any],
        ideaflow_velocity: int = 20,
        experiment_window_days: int = 14
    ) -> AsymmetricalStrategy:
        """
        Create a new asymmetrical SEO strategy.
        
        Args:
            name: Strategy name
            description: Strategy description
            geo_tier: Geographic tier (national/international/global)
            target_surfaces: Surfaces to dominate
            asset_types: Types of proprietary assets to create
            hypertargeting_criteria: Criteria for keyword selection
            ideaflow_velocity: Ideas to generate/test per week
            experiment_window_days: Days to test before killing
            
        Returns:
            AsymmetricalStrategy configuration
        """
        strategy = AsymmetricalStrategy(
            name=name,
            description=description,
            geo_tier=geo_tier,
            target_surfaces=target_surfaces,
            asset_types=asset_types,
            hypertargeting_criteria=hypertargeting_criteria,
            ideaflow_velocity=ideaflow_velocity,
            experiment_window_days=experiment_window_days
        )
        
        logger.info(f"Created asymmetrical strategy: {name} targeting {len(target_surfaces)} surfaces")
        return strategy
    
    def create_geographic_strategy(
        self,
        tier: GeoTier,
        countries: List[str],
        languages: List[str],
        architecture_type: str,
        localization_depth: str = "cultural",
        local_authority_targets: Optional[List[str]] = None,
        disrespected_keywords: Optional[List[Dict[str, Any]]] = None
    ) -> GeographicStrategy:
        """
        Create geographic SEO strategy for national/international/global scaling.
        
        Args:
            tier: Geographic tier
            countries: Target countries
            languages: Target languages
            architecture_type: ccTLD, subdirectory, or subdomain
            localization_depth: Level of localization
            local_authority_targets: Local journals/associations to target
            disrespected_keywords: Keywords with low-quality competition
            
        Returns:
            GeographicStrategy configuration
        """
        strategy = GeographicStrategy(
            tier=tier,
            countries=countries,
            languages=languages,
            architecture_type=architecture_type,
            hreflang_enabled=True,
            localization_depth=localization_depth,
            local_authority_targets=local_authority_targets or [],
            disrespected_keyword_opportunities=disrespected_keywords or []
        )
        
        logger.info(f"Created {tier.value} SEO strategy for {len(countries)} countries")
        return strategy
    
    def create_proprietary_asset(
        self,
        name: str,
        asset_type: AssetType,
        data_source: str,
        update_frequency: str,
        coined_terms: Optional[List[str]] = None,
        visualization_types: Optional[List[str]] = None,
        target_entities: Optional[List[str]] = None,
        api_accessible: bool = False
    ) -> ProprietaryAsset:
        """
        Create a proprietary asset for link magnet and citation generation.
        
        Args:
            name: Asset name
            asset_type: Type of asset (calculator, dashboard, etc.)
            data_source: Source of proprietary data
            update_frequency: How often data updates
            coined_terms: Unique industry terms coined by this asset
            visualization_types: Types of visualizations included
            target_entities: Entities to associate with
            api_accessible: Whether asset has public API
            
        Returns:
            ProprietaryAsset configuration
        """
        asset = ProprietaryAsset(
            name=name,
            asset_type=asset_type,
            data_source=data_source,
            update_frequency=update_frequency,
            public_facing=True,
            api_accessible=api_accessible,
            coined_terms=coined_terms or [],
            visualization_types=visualization_types or [],
            target_entities=target_entities or []
        )
        
        self.proprietary_assets.append(asset)
        logger.info(f"Created proprietary asset: {name} ({asset_type.value})")
        return asset
    
    def get_ai_citation_optimization(self, surface: SurfaceType) -> Optional[AICitationTarget]:
        """
        Get AI citation optimization strategy for a specific surface.
        
        Args:
            surface: Target surface (Google Discover, Bing/Copilot, Brave, Claude)
            
        Returns:
            AICitationTarget configuration or None
        """
        return self.ai_citation_strategies.get(surface)
    
    def create_multi_surface_domination_plan(
        self,
        topic: str,
        primary_keyword: str,
        long_tail_keywords: List[str],
        entity_stack: List[str],
        timely_hook: Optional[str] = None
    ) -> MultiSurfaceDominationPlan:
        """
        Create a plan to dominate multiple surfaces for a single topic.
        
        Args:
            topic: Main topic
            primary_keyword: Primary keyword
            long_tail_keywords: Long-tail keyword variations
            entity_stack: Entities to associate with
            timely_hook: Current trending news to frame around
            
        Returns:
            MultiSurfaceDominationPlan
        """
        surfaces_config = {}
        
        # Configure each surface with specific tactics
        for surface in [
            SurfaceType.TEXT,
            SurfaceType.AI_OVERVIEW,
            SurfaceType.VIDEO,
            SurfaceType.IMAGE,
            SurfaceType.GOOGLE_DISCOVER,
            SurfaceType.BING_COPILOT,
            SurfaceType.BRAVE_SEARCH,
            SurfaceType.CLAUDE
        ]:
            citation_target = self.get_ai_citation_optimization(surface)
            if citation_target:
                surfaces_config[surface] = {
                    "optimization_tactics": citation_target.optimization_tactics,
                    "schema_types": citation_target.schema_types,
                    "content_requirements": citation_target.content_density_requirements
                }
            else:
                surfaces_config[surface] = {
                    "optimization_tactics": ["standard_seo"],
                    "schema_types": ["Article"],
                    "content_requirements": {}
                }
        
        artifact_assets = [
            f"{topic.replace(' ', '_')}_calculator",
            f"{topic.replace(' ', '_')}_dashboard",
            f"{topic.replace(' ', '_')}_data_report"
        ]
        
        plan = MultiSurfaceDominationPlan(
            topic=topic,
            primary_keyword=primary_keyword,
            long_tail_keywords=long_tail_keywords,
            surfaces=surfaces_config,
            entity_stack=entity_stack,
            timely_hook=timely_hook,
            artifact_assets=artifact_assets
        )
        
        logger.info(f"Created multi-surface domination plan for: {topic}")
        return plan
    
    def launch_experiment(
        self,
        hypothesis: str,
        asset_type: AssetType,
        surfaces_targeted: List[SurfaceType],
        success_metrics: List[str],
        experiment_id: Optional[str] = None
    ) -> ExperimentFramework:
        """
        Launch a rapid SEO experiment.
        
        Args:
            hypothesis: Experiment hypothesis
            asset_type: Type of asset to test
            surfaces_targeted: Surfaces to test on
            success_metrics: Metrics to measure success
            experiment_id: Optional custom ID
            
        Returns:
            ExperimentFramework
        """
        if not experiment_id:
            experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        v0_launch = datetime.now()
        kill_date = v0_launch + timedelta(days=14)  # Default 14-day window
        
        experiment = ExperimentFramework(
            experiment_id=experiment_id,
            hypothesis=hypothesis,
            asset_type=asset_type,
            surfaces_targeted=surfaces_targeted,
            v0_launch_date=v0_launch,
            success_metrics=success_metrics,
            kill_date=kill_date,
            status="running"
        )
        
        self.active_experiments[experiment_id] = experiment
        logger.info(f"Launched experiment {experiment_id}: {hypothesis}")
        return experiment
    
    def evaluate_experiment(self, experiment_id: str, results: Dict[str, Any]) -> str:
        """
        Evaluate experiment results and decide to continue or kill.
        
        Args:
            experiment_id: Experiment to evaluate
            results: Performance results
            
        Returns:
            Decision: "continue", "iterate", or "kill"
        """
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.active_experiments[experiment_id]
        
        # Simple evaluation logic (can be enhanced)
        success_count = sum(
            1 for metric in experiment.success_metrics
            if results.get(metric, {}).get("achieved", False)
        )
        
        success_rate = success_count / len(experiment.success_metrics)
        
        if success_rate >= 0.8:
            experiment.status = "successful"
            experiment.learnings.append(f"High success rate: {success_rate:.2%}")
            decision = "continue"
        elif success_rate >= 0.5:
            experiment.learnings.append(f"Moderate success: {success_rate:.2%}, needs iteration")
            decision = "iterate"
        else:
            experiment.status = "killed"
            experiment.learnings.append(f"Low success rate: {success_rate:.2%}")
            decision = "kill"
        
        logger.info(f"Experiment {experiment_id} evaluated: {decision}")
        return decision
    
    def analyze_competitive_moat(
        self,
        asset_name: str,
        moat_type: str,
        description: str
    ) -> CompetitiveMoat:
        """
        Analyze the defensibility of a competitive moat.
        
        Args:
            asset_name: Asset creating the moat
            moat_type: Type of moat (data, time, expertise, distribution, technical)
            description: Description of the moat
            
        Returns:
            CompetitiveMoat analysis
        """
        # Estimate copy cost and time based on moat type
        copy_costs = {
            "data": "prohibitive",
            "time": "high",
            "expertise": "high",
            "distribution": "medium",
            "technical": "medium"
        }
        
        time_estimates = {
            "data": "years",
            "time": "months",
            "expertise": "years",
            "distribution": "months",
            "technical": "weeks"
        }
        
        sustainability_scores = {
            "data": 9,
            "time": 7,
            "expertise": 8,
            "distribution": 6,
            "technical": 5
        }
        
        moat = CompetitiveMoat(
            moat_type=moat_type,
            description=description,
            copy_cost_estimate=copy_costs.get(moat_type, "medium"),
            time_to_copy_estimate=time_estimates.get(moat_type, "months"),
            sustainability_score=sustainability_scores.get(moat_type, 6)
        )
        
        logger.info(f"Analyzed competitive moat for {asset_name}: {moat_type} (score: {moat.sustainability_score}/10)")
        return moat
    
    def get_programmatic_seo_config(
        self,
        name: str,
        database_connection: str,
        template_path: str,
        long_tail_pattern: str,
        scale_target: int,
        canonical_strategy: str = "self_referential"
    ) -> ProgrammaticSEOEngine:
        """
        Configure a programmatic SEO engine for long-tail scale.
        
        Args:
            name: Engine name
            database_connection: Database connection string
            template_path: Path to page templates
            long_tail_pattern: Pattern for generating long-tail keywords
            scale_target: Target number of pages
            canonical_strategy: Canonical URL strategy
            
        Returns:
            ProgrammaticSEOEngine configuration
        """
        engine = ProgrammaticSEOEngine(
            name=name,
            database_connection=database_connection,
            template_path=template_path,
            generation_rules={
                "pattern": long_tail_pattern,
                "min_search_volume": 1,
                "max_competition": 0.3
            },
            scale_target=scale_target,
            long_tail_pattern=long_tail_pattern,
            quality_thresholds={
                "min_content_length": 500,
                "unique_content_ratio": 0.8,
                "internal_links_min": 3
            },
            canonical_strategy=canonical_strategy
        )
        
        logger.info(f"Configured programmatic SEO engine: {name} targeting {scale_target} pages")
        return engine
    
    def get_kpi_definitions(self) -> Dict[str, Any]:
        """
        Get all standard asymmetrical SEO KPI definitions.
        
        Returns:
            Dictionary of KPI definitions
        """
        return self.standard_kpis.model_dump()
    
    def calculate_zero_cac_ratio(
        self,
        customer_ltv: float,
        seo_team_cost: float,
        tooling_cost: float
    ) -> float:
        """
        Calculate Zero-CAC ratio.
        
        Args:
            customer_ltv: Customer lifetime value
            seo_team_cost: Monthly SEO team cost
            tooling_cost: Monthly tooling cost
            
        Returns:
            Zero-CAC ratio
        """
        total_fixed_cost = seo_team_cost + tooling_cost
        if total_fixed_cost == 0:
            return float('inf')
        
        return customer_ltv / total_fixed_cost
