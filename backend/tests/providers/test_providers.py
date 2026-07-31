"""Tests for provider abstraction layer."""

import pytest
import asyncio
from eliseo.providers.base import (
    ProviderType,
    ProviderConfig,
    GenerationRequest,
    JobStatus,
)
from eliseo.providers.mock_provider import MockProvider


@pytest.fixture
def mock_provider_config():
    """Create mock provider configuration."""
    return ProviderConfig(
        provider_type=ProviderType.MOCK,
        timeout_seconds=30,
        max_retries=3,
    )


@pytest.fixture
def generation_request():
    """Create a standard generation request."""
    return GenerationRequest(
        prompt="A beautiful sunset over mountains",
        width=1024,
        height=1024,
        steps=30,
        guidance_scale=7.5,
    )


@pytest.mark.asyncio
async def test_mock_provider_initialization(mock_provider_config):
    """Test mock provider initializes correctly."""
    provider = MockProvider(mock_provider_config)
    result = await provider.initialize()
    
    assert result is True
    assert provider._initialized is True


@pytest.mark.asyncio
async def test_mock_image_generation(mock_provider_config, generation_request):
    """Test mock image generation."""
    provider = MockProvider(mock_provider_config)
    await provider.initialize()
    
    response = await provider.generate_image(generation_request)
    
    assert response.job_id is not None
    assert response.status == JobStatus.COMPLETED
    assert response.provider == ProviderType.MOCK
    assert response.asset_urls is not None
    assert len(response.asset_urls) > 0
    assert "images" in response.asset_urls[0]
    assert response.cost_usd == 0.0
    assert response.processing_time_ms > 0


@pytest.mark.asyncio
async def test_mock_video_generation(mock_provider_config, generation_request):
    """Test mock video generation."""
    provider = MockProvider(mock_provider_config)
    await provider.initialize()
    
    response = await provider.generate_video(generation_request)
    
    assert response.job_id is not None
    assert response.status == JobStatus.COMPLETED
    assert response.provider == ProviderType.MOCK
    assert response.asset_urls is not None
    assert "videos" in response.asset_urls[0]
    assert response.cost_usd == 0.0


@pytest.mark.asyncio
async def test_check_job_status(mock_provider_config, generation_request):
    """Test checking job status."""
    provider = MockProvider(mock_provider_config)
    await provider.initialize()
    
    # Generate first to create job
    gen_response = await provider.generate_image(generation_request)
    
    # Check status
    status_response = await provider.check_status(gen_response.job_id)
    
    assert status_response.job_id == gen_response.job_id
    assert status_response.status == JobStatus.COMPLETED


@pytest.mark.asyncio
async def test_cancel_job(mock_provider_config, generation_request):
    """Test cancelling a job."""
    provider = MockProvider(mock_provider_config)
    await provider.initialize()
    
    # Generate first
    gen_response = await provider.generate_image(generation_request)
    
    # Cancel
    cancel_result = await provider.cancel_job(gen_response.job_id)
    
    assert cancel_result is True
    
    # Verify status changed
    status_response = await provider.check_status(gen_response.job_id)
    assert status_response.status == JobStatus.CANCELLED


@pytest.mark.asyncio
async def test_check_nonexistent_job(mock_provider_config):
    """Test checking status of nonexistent job."""
    provider = MockProvider(mock_provider_config)
    await provider.initialize()
    
    response = await provider.check_status("nonexistent-job-id")
    
    assert response.status == JobStatus.FAILED
    assert response.error_message == "Job not found"


@pytest.mark.asyncio
async def test_cost_estimate(mock_provider_config, generation_request):
    """Test cost estimation."""
    provider = MockProvider(mock_provider_config)
    await provider.initialize()
    
    cost = provider.get_cost_estimate(generation_request)
    
    assert cost == 0.0  # Mock is free


def test_provider_is_available(mock_provider_config):
    """Test provider availability check."""
    provider = MockProvider(mock_provider_config)
    
    # Not available before initialization
    assert provider.is_available() is False
    
    # Available after initialization
    asyncio.run(provider.initialize())
    assert provider.is_available() is True


@pytest.mark.asyncio
async def test_health_check(mock_provider_config):
    """Test provider health check."""
    provider = MockProvider(mock_provider_config)
    await provider.initialize()
    
    health = await provider.health_check()
    
    assert health["provider"] == "mock"
    assert health["available"] is True
    assert health["initialized"] is True


@pytest.mark.asyncio
async def test_clear_jobs(mock_provider_config, generation_request):
    """Test clearing all mock jobs."""
    provider = MockProvider(mock_provider_config)
    await provider.initialize()
    
    # Create some jobs
    await provider.generate_image(generation_request)
    await provider.generate_image(generation_request)
    
    # Clear
    provider.clear_jobs()
    
    # Verify cleared
    status = await provider.check_status("any-job")
    assert status.status == JobStatus.FAILED
