use eli_core::{AgentTaskAnchorId, PolicyDecisionId};
use eli_domain::LegacyId;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

pub const BOUNDARY_PROTOCOL_VERSION: u16 = 1;

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProviderType {
    OpenaiDalle,
    OpenaiVideo,
    StabilityAi,
    Runwayml,
    Replicate,
    Elevenlabs,
    GoogleVertex,
    Mock,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum JobStatus {
    Queued,
    Processing,
    Completed,
    Failed,
    Cancelled,
    Retrying,
    PartiallyCompleted,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct GenerationRequest {
    pub prompt: String,
    pub negative_prompt: Option<String>,
    pub width: Option<i64>,
    pub height: Option<i64>,
    pub steps: Option<i64>,
    pub guidance_scale: Option<f64>,
    pub seed: Option<i64>,
    pub model: Option<String>,
    pub style_preset: Option<String>,
    pub batch_size: Option<i64>,
    pub output_format: Option<String>,
    pub extra_params: Option<BTreeMap<String, Value>>,
}

impl GenerationRequest {
    #[must_use]
    pub fn with_python_defaults(prompt: impl Into<String>) -> Self {
        Self {
            prompt: prompt.into(),
            negative_prompt: None,
            width: Some(1024),
            height: Some(1024),
            steps: Some(30),
            guidance_scale: Some(7.5),
            seed: None,
            model: None,
            style_preset: None,
            batch_size: Some(1),
            output_format: Some("png".to_owned()),
            extra_params: None,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct GenerationResponse {
    pub job_id: String,
    pub status: JobStatus,
    pub provider: ProviderType,
    pub asset_urls: Option<Vec<String>>,
    pub thumbnail_url: Option<String>,
    pub metadata: Option<BTreeMap<String, Value>>,
    pub error_message: Option<String>,
    pub cost_usd: Option<f64>,
    pub processing_time_ms: Option<i64>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ProviderConfig {
    pub provider_type: ProviderType,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub api_key: Option<String>,

    pub base_url: Option<String>,
    pub model_name: Option<String>,
    pub timeout_seconds: i64,
    pub max_retries: i64,
    pub rate_limit_requests: Option<i64>,
    pub rate_limit_period_seconds: Option<i64>,
    pub enabled: bool,
    pub priority: i64,
}

impl ProviderConfig {
    #[must_use]
    pub fn safe_for_transport(mut self) -> Self {
        self.api_key = None;
        self
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BoundaryOperation {
    GenerateImage,
    GenerateVideo,
    CheckJobStatus,
    CancelJob,
    EstimateCost,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct PythonBoundaryRequest {
    pub protocol_version: u16,

    pub agent_task_anchor_id: AgentTaskAnchorId,

    pub project_legacy_id: Option<LegacyId>,
    pub domain_legacy_id: Option<LegacyId>,
    pub agent_legacy_id: Option<LegacyId>,

    pub operation: BoundaryOperation,

    pub generation_request: Option<GenerationRequest>,
    pub provider_config: Option<ProviderConfig>,
    pub external_job_id: Option<String>,
}

impl PythonBoundaryRequest {
    #[must_use]
    pub fn generation(
        agent_task_anchor_id: AgentTaskAnchorId,
        project_legacy_id: Option<LegacyId>,
        agent_legacy_id: Option<LegacyId>,
        operation: BoundaryOperation,
        generation_request: GenerationRequest,
    ) -> Self {
        Self {
            protocol_version: BOUNDARY_PROTOCOL_VERSION,
            agent_task_anchor_id,
            project_legacy_id,
            domain_legacy_id: None,
            agent_legacy_id,
            operation,
            generation_request: Some(generation_request),
            provider_config: None,
            external_job_id: None,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct PythonBoundaryResponse {
    pub protocol_version: u16,

    pub agent_task_anchor_id: AgentTaskAnchorId,

    pub project_legacy_id: Option<LegacyId>,
    pub domain_legacy_id: Option<LegacyId>,
    pub agent_legacy_id: Option<LegacyId>,

    pub accepted: bool,
    pub policy_decision_id: Option<PolicyDecisionId>,

    pub generation_response: Option<GenerationResponse>,
    pub error: Option<BoundaryError>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BoundaryErrorCode {
    UnsupportedProtocolVersion,
    InvalidRequest,
    PolicyDenied,
    ProviderUnavailable,
    ProviderFailure,
    SerializationFailure,
    InternalFailure,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct BoundaryError {
    pub code: BoundaryErrorCode,
    pub message: String,
    pub retryable: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn python_enum_values_use_snake_case() {
        let provider =
            serde_json::to_string(&ProviderType::OpenaiDalle).expect("serialize provider");
        let status =
            serde_json::to_string(&JobStatus::PartiallyCompleted).expect("serialize status");

        assert_eq!(provider, "\"openai_dalle\"");
        assert_eq!(status, "\"partially_completed\"");
    }

    #[test]
    fn generation_request_matches_python_defaults() {
        let request = GenerationRequest::with_python_defaults("Create an audit graphic");

        assert_eq!(request.width, Some(1024));
        assert_eq!(request.height, Some(1024));
        assert_eq!(request.steps, Some(30));
        assert_eq!(request.guidance_scale, Some(7.5));
        assert_eq!(request.batch_size, Some(1));
        assert_eq!(request.output_format.as_deref(), Some("png"));
    }

    #[test]
    fn python_owned_ids_remain_signed_integers() {
        let request = PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(101),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Generate image"),
        );

        let json = serde_json::to_value(&request).expect("serialize boundary request");

        assert_eq!(json["project_legacy_id"], 101);
        assert_eq!(json["agent_legacy_id"], 42);
    }

    #[test]
    fn boundary_request_round_trips_through_json() {
        let original = PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(7),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Generate image"),
        );

        let json = serde_json::to_string(&original).expect("serialize request");
        let decoded: PythonBoundaryRequest =
            serde_json::from_str(&json).expect("deserialize request");

        assert_eq!(decoded, original);
    }

    #[test]
    fn provider_api_key_is_removed_before_transport() {
        let config = ProviderConfig {
            provider_type: ProviderType::Mock,
            api_key: Some("secret-value".to_owned()),
            base_url: None,
            model_name: None,
            timeout_seconds: 300,
            max_retries: 3,
            rate_limit_requests: None,
            rate_limit_period_seconds: None,
            enabled: true,
            priority: 1,
        }
        .safe_for_transport();

        assert_eq!(config.api_key, None);
    }
}
#[test]
fn canonical_python_fixture_deserializes_in_rust() {
    let fixture = include_str!("../../../../contracts/fixtures/generation_request.json");

    let request: PythonBoundaryRequest =
        serde_json::from_str(fixture).expect("deserialize canonical fixture");

    assert_eq!(request.protocol_version, BOUNDARY_PROTOCOL_VERSION);
    assert_eq!(request.project_legacy_id, Some(101));
    assert_eq!(request.domain_legacy_id, Some(202));
    assert_eq!(request.agent_legacy_id, Some(42));
    assert_eq!(request.operation, BoundaryOperation::GenerateImage);

    let generation = request
        .generation_request
        .expect("generation request must exist");

    assert_eq!(generation.prompt, "Create an SEO audit graphic");
    assert_eq!(generation.width, Some(1024));
    assert_eq!(generation.height, Some(1024));
    assert_eq!(generation.steps, Some(30));
    assert_eq!(generation.guidance_scale, Some(7.5));
    assert_eq!(generation.batch_size, Some(1));
    assert_eq!(generation.output_format.as_deref(), Some("png"));
}
mod validation;
pub use validation::*;

mod integrity;
pub use integrity::*;

mod authentication;
pub use authentication::*;
