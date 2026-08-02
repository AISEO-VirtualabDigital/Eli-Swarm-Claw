import json
from pathlib import Path

from eliseo.providers.base import (
    GenerationRequest,
    JobStatus,
    ProviderType,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "contracts"
    / "fixtures"
    / "generation_request.json"
)


def load_fixture() -> dict:
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_fixture_uses_expected_protocol_version() -> None:
    fixture = load_fixture()

    assert fixture["protocol_version"] == 1


def test_fixture_preserves_python_owned_integer_ids() -> None:
    fixture = load_fixture()

    assert fixture["project_legacy_id"] == 101
    assert fixture["domain_legacy_id"] == 202
    assert fixture["agent_legacy_id"] == 42

    assert isinstance(fixture["project_legacy_id"], int)
    assert isinstance(fixture["domain_legacy_id"], int)
    assert isinstance(fixture["agent_legacy_id"], int)


def test_fixture_matches_python_generation_request() -> None:
    fixture = load_fixture()
    request_payload = fixture["generation_request"]

    request = GenerationRequest(**request_payload)

    assert request.prompt == "Create an SEO audit graphic"
    assert request.width == 1024
    assert request.height == 1024
    assert request.steps == 30
    assert request.guidance_scale == 7.5
    assert request.batch_size == 1
    assert request.output_format == "png"


def test_python_generation_defaults_match_rust_contract() -> None:
    request = GenerationRequest(prompt="Create an SEO audit graphic")

    assert request.width == 1024
    assert request.height == 1024
    assert request.steps == 30
    assert request.guidance_scale == 7.5
    assert request.batch_size == 1
    assert request.output_format == "png"


def test_provider_enum_values_match_rust_contract() -> None:
    assert ProviderType.OPENAI_DALLE.value == "openai_dalle"
    assert ProviderType.OPENAI_VIDEO.value == "openai_video"
    assert ProviderType.STABILITY_AI.value == "stability_ai"
    assert ProviderType.RUNWAYML.value == "runwayml"
    assert ProviderType.REPLICATE.value == "replicate"
    assert ProviderType.ELEVENLABS.value == "elevenlabs"
    assert ProviderType.GOOGLE_VERTEX.value == "google_vertex"
    assert ProviderType.MOCK.value == "mock"


def test_job_status_values_match_rust_contract() -> None:
    assert JobStatus.QUEUED.value == "queued"
    assert JobStatus.PROCESSING.value == "processing"
    assert JobStatus.COMPLETED.value == "completed"
    assert JobStatus.FAILED.value == "failed"
    assert JobStatus.CANCELLED.value == "cancelled"
    assert JobStatus.RETRYING.value == "retrying"
    assert JobStatus.PARTIALLY_COMPLETED.value == "partially_completed"