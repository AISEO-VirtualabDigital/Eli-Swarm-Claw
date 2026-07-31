"""Content moderation service for AI generation prompts and outputs."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from enum import Enum
import re


class ModerationSeverity(str, Enum):
    """Moderation severity levels."""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


class ModerationCategory(str, Enum):
    """Moderation categories."""
    SEXUAL = "sexual"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    HATE = "hate"
    HARASSMENT = "harassment"
    ILLEGAL = "illegal"
    COPYRIGHT = "copyright"
    IMPERSONATION = "impersonation"
    POLITICAL = "political"
    SPAM = "spam"


class ModerationResult(BaseModel):
    """Result of content moderation check."""
    is_safe: bool
    severity: ModerationSeverity
    flagged_categories: List[ModerationCategory]
    confidence_scores: Dict[str, float]
    requires_review: bool
    block_reason: Optional[str] = None
    suggestions: Optional[List[str]] = None


class ModerationConfig(BaseModel):
    """Moderation configuration."""
    enabled: bool = True
    provider: str = "local"  # local, openai, perspective
    api_key: Optional[str] = None
    block_unsafe_prompts: bool = True
    require_admin_review: bool = False
    allow_political_content: bool = False
    custom_blocklist: List[str] = []
    custom_allowlist: List[str] = []
    sensitivity_threshold: float = 0.7  # 0.0 to 1.0


class BaseModerationProvider:
    """Base class for moderation providers."""

    def __init__(self, config: ModerationConfig):
        self.config = config
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize moderation provider."""
        self._initialized = True
        return True

    async def moderate_prompt(self, prompt: str) -> ModerationResult:
        """Moderate a text prompt."""
        raise NotImplementedError

    async def moderate_output(self, output_data: Any) -> ModerationResult:
        """Moderate generated output (if supported)."""
        raise NotImplementedError


class LocalModerationProvider(BaseModerationProvider):
    """Local rule-based moderation provider."""

    def __init__(self, config: ModerationConfig):
        super().__init__(config)
        self._compiled_blocklist = []
        self._compiled_allowlist = []

    async def initialize(self) -> bool:
        """Initialize local moderation with compiled patterns."""
        # Compile blocklist patterns
        self._compiled_blocklist = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.config.custom_blocklist
        ]
        
        # Compile allowlist patterns
        self._compiled_allowlist = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.config.custom_allowlist
        ]
        
        self._initialized = True
        return True

    async def moderate_prompt(self, prompt: str) -> ModerationResult:
        """Moderate prompt using local rules."""
        flagged_categories = []
        confidence_scores = {}
        block_reason = None
        suggestions = []

        # Check allowlist first (always safe)
        for pattern in self._compiled_allowlist:
            if pattern.search(prompt):
                return ModerationResult(
                    is_safe=True,
                    severity=ModerationSeverity.SAFE,
                    flagged_categories=[],
                    confidence_scores={},
                    requires_review=False,
                )

        # Check blocklist
        for pattern in self._compiled_blocklist:
            if pattern.search(prompt):
                return ModerationResult(
                    is_safe=False,
                    severity=ModerationSeverity.BLOCKED,
                    flagged_categories=[ModerationCategory.ILLEGAL],
                    confidence_scores={"blocklist_match": 1.0},
                    requires_review=False,
                    block_reason="Content matches blocklist pattern",
                )

        # Check for common unsafe patterns
        unsafe_patterns = {
            ModerationCategory.SEXUAL: [
                r"\b(nude|naked|porn|xxx|sex|explicit)\b",
                r"\b(uncensored|nsfw)\b",
            ],
            ModerationCategory.VIOLENCE: [
                r"\b(kill|murder|blood|gore|violent|death)\b",
                r"\b(weapon|gun|knife|bomb)\b",
            ],
            ModerationCategory.SELF_HARM: [
                r"\b(suicide|self.?harm|cutting|anorexia)\b",
            ],
            ModerationCategory.HATE: [
                r"\b(hate|racist|nazi|slur)\b",
            ],
            ModerationCategory.ILLEGAL: [
                r"\b(drugs|cocaine|heroin|meth)\b",
                r"\b(hack|crack|exploit)\b",
            ],
        }

        max_confidence = 0.0
        for category, patterns in unsafe_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    flagged_categories.append(category)
                    confidence_scores[category.value] = 0.8
                    max_confidence = max(max_confidence, 0.8)
                    break

        # Determine severity
        if not flagged_categories:
            severity = ModerationSeverity.SAFE
            is_safe = True
        elif max_confidence < 0.5:
            severity = ModerationSeverity.LOW_RISK
            is_safe = True
        elif max_confidence < 0.7:
            severity = ModerationSeverity.MEDIUM_RISK
            is_safe = not self.config.block_unsafe_prompts
        else:
            severity = ModerationSeverity.HIGH_RISK
            is_safe = False
            if self.config.block_unsafe_prompts:
                block_reason = f"Flagged for: {', '.join([c.value for c in flagged_categories])}"

        # Check if review is required
        requires_review = (
            severity in [ModerationSeverity.MEDIUM_RISK, ModerationSeverity.HIGH_RISK]
            and self.config.require_admin_review
        )

        # Generate suggestions if blocked
        if not is_safe and flagged_categories:
            suggestions = [
                "Try rephrasing your prompt to be more specific about the artistic style",
                "Avoid explicit or potentially harmful terms",
                "Focus on positive, constructive descriptions",
            ]

        return ModerationResult(
            is_safe=is_safe,
            severity=severity,
            flagged_categories=flagged_categories,
            confidence_scores=confidence_scores,
            requires_review=requires_review,
            block_reason=block_reason,
            suggestions=suggestions if suggestions else None,
        )

    async def moderate_output(self, output_data: Any) -> ModerationResult:
        """Moderate output (placeholder for future implementation)."""
        # For now, assume outputs are safe if prompts were safe
        return ModerationResult(
            is_safe=True,
            severity=ModerationSeverity.SAFE,
            flagged_categories=[],
            confidence_scores={},
            requires_review=False,
        )


class ModerationService:
    """Main moderation service that coordinates providers."""

    def __init__(self, config: ModerationConfig):
        self.config = config
        self.provider: Optional[BaseModerationProvider] = None

    async def initialize(self) -> bool:
        """Initialize moderation service."""
        if not self.config.enabled:
            return True

        # Select provider based on config
        if self.config.provider == "openai":
            # Would implement OpenAI moderation here
            self.provider = LocalModerationProvider(self.config)
        else:
            # Default to local provider
            self.provider = LocalModerationProvider(self.config)

        return await self.provider.initialize()

    async def check_prompt(self, prompt: str) -> ModerationResult:
        """Check if prompt is safe."""
        if not self.config.enabled or not self.provider:
            return ModerationResult(
                is_safe=True,
                severity=ModerationSeverity.SAFE,
                flagged_categories=[],
                confidence_scores={},
                requires_review=False,
            )

        return await self.provider.moderate_prompt(prompt)

    async def check_output(self, output_data: Any) -> ModerationResult:
        """Check if output is safe."""
        if not self.config.enabled or not self.provider:
            return ModerationResult(
                is_safe=True,
                severity=ModerationSeverity.SAFE,
                flagged_categories=[],
                confidence_scores={},
                requires_review=False,
            )

        return await self.provider.moderate_output(output_data)

    def is_enabled(self) -> bool:
        """Check if moderation is enabled."""
        return self.config.enabled and self.provider is not None
