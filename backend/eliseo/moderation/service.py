"""Content moderation service for AI media generation."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from enum import Enum
import re


class ModerationStatus(str, Enum):
    """Moderation decision status."""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs_review"
    PROVIDER_ERROR_ALLOWED = "provider_error_allowed_by_config"
    PROVIDER_ERROR_BLOCKED = "provider_error_blocked_by_config"


class ModerationCategory(str, Enum):
    """Categories of content that may need moderation."""
    SEXUAL = "sexual"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    HATE = "hate"
    HARASSMENT = "harassment"
    ILLEGAL = "illegal_activity"
    COPYRIGHT = "copyright"
    IMPERSONATION = "impersonation"
    POLITICS = "political_manipulation"


class ModerationResult:
    """Result from moderation check."""
    
    def __init__(
        self,
        status: ModerationStatus,
        flagged_categories: Optional[List[ModerationCategory]] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
        error_message: Optional[str] = None,
        provider_response: Optional[Dict[str, Any]] = None,
    ):
        self.status = status
        self.flagged_categories = flagged_categories or []
        self.confidence_scores = confidence_scores or {}
        self.error_message = error_message
        self.provider_response = provider_response
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "flagged_categories": [c.value for c in self.flagged_categories],
            "confidence_scores": self.confidence_scores,
            "error_message": self.error_message,
            "provider_response": self.provider_response,
        }


class ModerationProvider(ABC):
    """Abstract base class for moderation providers."""

    @abstractmethod
    async def moderate_prompt(self, prompt: str) -> ModerationResult:
        """Check if a prompt is safe."""
        pass

    @abstractmethod
    async def moderate_output(self, output_data: bytes, context: str) -> ModerationResult:
        """Check if generated output is safe."""
        pass


class RuleBasedModerationProvider(ModerationProvider):
    """Rule-based moderation using blocklists and patterns (fallback when no API)."""

    # Blocklist of problematic terms
    BLOCKED_TERMS = [
        # Violence
        "kill", "murder", "death", "blood", "gore", "torture",
        # Sexual
        "nude", "naked", "porn", "sex", "xxx", "explicit",
        # Self-harm
        "suicide", "self-harm", "cutting", "anorexia",
        # Hate
        "racist", "nazi", "supremacist", "slur",
        # Illegal
        "bomb", "weapon", "drugs", "cocaine", "heroin",
    ]

    # Patterns for detecting problematic requests
    PATTERNS = [
        r"\b(kill|murder|die)\s+(person|human|someone)\b",
        r"\b(naked|nude|bare)\s+(body|woman|man)\b",
        r"\b(make|create|generate)\s+(bomb|weapon|drug)",
        r"\b(celebrity|famous)\s+(naked|nude)",
    ]

    def __init__(self, custom_blocklist: Optional[List[str]] = None):
        self.blocked_terms = set(self.BLOCKED_TERMS)
        if custom_blocklist:
            self.blocked_terms.update([t.lower() for t in custom_blocklist])
        
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.PATTERNS]

    async def moderate_prompt(self, prompt: str) -> ModerationResult:
        """Check prompt against rules."""
        prompt_lower = prompt.lower()
        flagged_categories = []
        confidence_scores = {}
        
        # Check blocked terms
        found_terms = []
        for term in self.blocked_terms:
            if term in prompt_lower:
                found_terms.append(term)
        
        # Check patterns
        pattern_matches = []
        for pattern in self.compiled_patterns:
            if pattern.search(prompt):
                pattern_matches.append(pattern.pattern)
        
        # Categorize findings
        violence_keywords = {"kill", "murder", "death", "blood", "gore", "torture", "bomb", "weapon"}
        sexual_keywords = {"nude", "naked", "porn", "sex", "xxx", "explicit"}
        self_harm_keywords = {"suicide", "self-harm", "cutting", "anorexia"}
        hate_keywords = {"racist", "nazi", "supremacist", "slur"}
        illegal_keywords = {"bomb", "weapon", "drugs", "cocaine", "heroin"}
        
        if any(term in found_terms for term in violence_keywords):
            flagged_categories.append(ModerationCategory.VIOLENCE)
            confidence_scores["violence"] = 0.9
        
        if any(term in found_terms for term in sexual_keywords):
            flagged_categories.append(ModerationCategory.SEXUAL)
            confidence_scores["sexual"] = 0.9
        
        if any(term in found_terms for term in self_harm_keywords):
            flagged_categories.append(ModerationCategory.SELF_HARM)
            confidence_scores["self_harm"] = 0.95
        
        if any(term in found_terms for term in hate_keywords):
            flagged_categories.append(ModerationCategory.HATE)
            confidence_scores["hate"] = 0.95
        
        if any(term in found_terms for term in illegal_keywords):
            flagged_categories.append(ModerationCategory.ILLEGAL)
            confidence_scores["illegal"] = 0.9
        
        # Decision
        if flagged_categories:
            return ModerationResult(
                status=ModerationStatus.BLOCKED,
                flagged_categories=flagged_categories,
                confidence_scores=confidence_scores,
                error_message=f"Prompt contains prohibited content: {', '.join(found_terms)}",
            )
        
        return ModerationResult(
            status=ModerationStatus.ALLOWED,
            confidence_scores={"safe": 1.0},
        )

    async def moderate_output(self, output_data: bytes, context: str) -> ModerationResult:
        """Output moderation not supported in rule-based mode."""
        # In production, you'd use vision models to analyze generated images
        return ModerationResult(
            status=ModerationStatus.ALLOWED,
            confidence_scores={"not_checked": 1.0},
        )


class OpenAIModerationProvider(ModerationProvider):
    """OpenAI Moderation API provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._session = None

    async def _get_session(self):
        """Lazy initialize HTTP session."""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self._session

    async def close(self):
        """Close HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def moderate_prompt(self, prompt: str) -> ModerationResult:
        """Check prompt using OpenAI Moderation API."""
        try:
            session = await self._get_session()
            
            async with session.post(
                "https://api.openai.com/v1/moderation",
                json={"input": prompt}
            ) as resp:
                if resp.status != 200:
                    return ModerationResult(
                        status=ModerationStatus.PROVIDER_ERROR_ALLOWED,
                        error_message=f"Moderation API error: {resp.status}",
                    )
                
                data = await resp.json()
                results = data.get("results", [{}])[0]
                categories = results.get("categories", {})
                category_scores = results.get("category_scores", {})
                
                flagged_categories = []
                confidence_scores = {}
                
                # Map OpenAI categories to our categories
                if categories.get("sexual"):
                    flagged_categories.append(ModerationCategory.SEXUAL)
                    confidence_scores["sexual"] = category_scores.get("sexual", 0)
                
                if categories.get("hate"):
                    flagged_categories.append(ModerationCategory.HATE)
                    confidence_scores["hate"] = category_scores.get("hate", 0)
                
                if categories.get("self-harm"):
                    flagged_categories.append(ModerationCategory.SELF_HARM)
                    confidence_scores["self_harm"] = category_scores.get("self-harm", 0)
                
                if categories.get("violence"):
                    flagged_categories.append(ModerationCategory.VIOLENCE)
                    confidence_scores["violence"] = category_scores.get("violence", 0)
                
                if flagged_categories:
                    return ModerationResult(
                        status=ModerationStatus.BLOCKED,
                        flagged_categories=flagged_categories,
                        confidence_scores=confidence_scores,
                        provider_response=data,
                    )
                
                return ModerationResult(
                    status=ModerationStatus.ALLOWED,
                    confidence_scores=confidence_scores,
                    provider_response=data,
                )
                
        except Exception as e:
            return ModerationResult(
                status=ModerationStatus.PROVIDER_ERROR_ALLOWED,
                error_message=f"Moderation failed: {str(e)}",
            )

    async def moderate_output(self, output_data: bytes, context: str) -> ModerationResult:
        """Output moderation not directly supported by OpenAI moderation API."""
        # Could use GPT-4 Vision in the future
        return ModerationResult(
            status=ModerationStatus.ALLOWED,
            confidence_scores={"not_checked": 1.0},
        )


class ModerationService:
    """Main moderation service that orchestrates providers."""

    def __init__(
        self,
        provider: ModerationProvider,
        block_unsafe: bool = True,
        require_admin_review: bool = False,
    ):
        self.provider = provider
        self.block_unsafe = block_unsafe
        self.require_admin_review = require_admin_review

    async def check_prompt(self, prompt: str) -> ModerationResult:
        """Check if a prompt is safe to process."""
        result = await self.provider.moderate_prompt(prompt)
        
        # Override based on configuration
        if result.status == ModerationStatus.BLOCKED and not self.block_unsafe:
            result.status = ModerationStatus.PROVIDER_ERROR_ALLOWED
        
        if result.status == ModerationStatus.ALLOWED and self.require_admin_review:
            result.status = ModerationStatus.NEEDS_REVIEW
        
        return result

    async def check_output(self, output_data: bytes, context: str) -> ModerationResult:
        """Check if generated output is safe."""
        return await self.provider.moderate_output(output_data, context)
