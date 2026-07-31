"""Tests for content moderation service."""

import pytest
from eliseo.services.moderation import (
    ModerationConfig,
    ModerationSeverity,
    ModerationCategory,
    LocalModerationProvider,
    ModerationService,
)


@pytest.fixture
def default_moderation_config():
    """Create default moderation config."""
    return ModerationConfig(
        enabled=True,
        provider="local",
        block_unsafe_prompts=True,
        require_admin_review=False,
    )


@pytest.mark.asyncio
async def test_safe_prompt(default_moderation_config):
    """Test that safe prompts pass moderation."""
    provider = LocalModerationProvider(default_moderation_config)
    await provider.initialize()
    
    result = await provider.moderate_prompt("A beautiful landscape painting")
    
    assert result.is_safe is True
    assert result.severity == ModerationSeverity.SAFE
    assert len(result.flagged_categories) == 0


@pytest.mark.asyncio
async def test_sexual_content_blocked(default_moderation_config):
    """Test that sexual content is blocked."""
    provider = LocalModerationProvider(default_moderation_config)
    await provider.initialize()
    
    result = await provider.moderate_prompt("Nude woman posing")
    
    assert result.is_safe is False
    assert ModerationCategory.SEXUAL in result.flagged_categories
    assert result.block_reason is not None


@pytest.mark.asyncio
async def test_violence_content_blocked(default_moderation_config):
    """Test that violent content is blocked."""
    provider = LocalModerationProvider(default_moderation_config)
    await provider.initialize()
    
    result = await provider.moderate_prompt("Kill someone with a knife")
    
    assert result.is_safe is False
    assert ModerationCategory.VIOLENCE in result.flagged_categories


@pytest.mark.asyncio
async def test_self_harm_content_blocked(default_moderation_config):
    """Test that self-harm content is blocked."""
    provider = LocalModerationProvider(default_moderation_config)
    await provider.initialize()
    
    result = await provider.moderate_prompt("Suicide methods")
    
    assert result.is_safe is False
    assert ModerationCategory.SELF_HARM in result.flagged_categories


@pytest.mark.asyncio
async def test_hate_speech_blocked(default_moderation_config):
    """Test that hate speech is blocked."""
    provider = LocalModerationProvider(default_moderation_config)
    await provider.initialize()
    
    result = await provider.moderate_prompt("Hate against certain group")
    
    assert result.is_safe is False
    assert ModerationCategory.HATE in result.flagged_categories


@pytest.mark.asyncio
async def test_illegal_content_blocked(default_moderation_config):
    """Test that illegal content is blocked."""
    provider = LocalModerationProvider(default_moderation_config)
    await provider.initialize()
    
    result = await provider.moderate_prompt("How to make drugs like cocaine")
    
    assert result.is_safe is False
    assert ModerationCategory.ILLEGAL in result.flagged_categories


@pytest.mark.asyncio
async def test_custom_blocklist(default_moderation_config):
    """Test custom blocklist functionality."""
    config = ModerationConfig(
        enabled=True,
        provider="local",
        block_unsafe_prompts=True,
        custom_blocklist=["forbidden_word", "blocked_term"],
    )
    provider = LocalModerationProvider(config)
    await provider.initialize()
    
    result = await provider.moderate_prompt("This contains forbidden_word")
    
    assert result.is_safe is False
    assert result.severity == ModerationSeverity.BLOCKED


@pytest.mark.asyncio
async def test_custom_allowlist_overrides(default_moderation_config):
    """Test that allowlist overrides blocklist."""
    config = ModerationConfig(
        enabled=True,
        provider="local",
        block_unsafe_prompts=True,
        custom_blocklist=["bad_word"],
        custom_allowlist=["artistic nude study"],
    )
    provider = LocalModerationProvider(config)
    await provider.initialize()
    
    # This should be safe due to allowlist
    result = await provider.moderate_prompt("Artistic nude study for class")
    
    assert result.is_safe is True
    assert result.severity == ModerationSeverity.SAFE


@pytest.mark.asyncio
async def test_moderation_disabled(default_moderation_config):
    """Test that moderation service can be disabled."""
    config = ModerationConfig(
        enabled=False,
        provider="local",
    )
    service = ModerationService(config)
    await service.initialize()
    
    # When service is disabled, it should return safe result
    result = await service.check_prompt("Violent and explicit content")
    
    assert result.is_safe is True
    assert service.is_enabled() is False


@pytest.mark.asyncio
async def test_requires_review_flag(default_moderation_config):
    """Test review requirement flag."""
    config = ModerationConfig(
        enabled=True,
        provider="local",
        require_admin_review=True,
    )
    provider = LocalModerationProvider(config)
    await provider.initialize()
    
    # Create a medium-risk prompt
    result = await provider.moderate_prompt("Somewhat violent scene")
    
    if result.severity in [ModerationSeverity.MEDIUM_RISK, ModerationSeverity.HIGH_RISK]:
        assert result.requires_review is True


@pytest.mark.asyncio
async def test_suggestions_provided_when_blocked(default_moderation_config):
    """Test that suggestions are provided when content is blocked."""
    provider = LocalModerationProvider(default_moderation_config)
    await provider.initialize()
    
    result = await provider.moderate_prompt("Explicit violent hate speech")
    
    if not result.is_safe:
        assert result.suggestions is not None
        assert len(result.suggestions) > 0


@pytest.mark.asyncio
async def test_moderation_service_initialization(default_moderation_config):
    """Test moderation service initialization."""
    service = ModerationService(default_moderation_config)
    result = await service.initialize()
    
    assert result is True
    assert service.is_enabled() is True


@pytest.mark.asyncio
async def test_moderation_service_check_prompt(default_moderation_config):
    """Test moderation service prompt checking."""
    service = ModerationService(default_moderation_config)
    await service.initialize()
    
    safe_result = await service.check_prompt("Safe artistic prompt")
    assert safe_result.is_safe is True
    
    unsafe_result = await service.check_prompt("Violent explicit content")
    assert unsafe_result.is_safe is False


@pytest.mark.asyncio
async def test_moderation_service_output_check(default_moderation_config):
    """Test moderation service output checking."""
    service = ModerationService(default_moderation_config)
    await service.initialize()
    
    # Output moderation currently passes through
    result = await service.check_output({"image_url": "test.png"})
    
    assert result.is_safe is True
