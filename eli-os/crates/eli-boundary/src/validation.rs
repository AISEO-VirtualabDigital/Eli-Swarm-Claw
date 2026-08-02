use crate::{
    BOUNDARY_PROTOCOL_VERSION, BoundaryError, BoundaryErrorCode, BoundaryOperation,
    PythonBoundaryRequest,
};

pub trait ValidateBoundary {
    fn validate(&self) -> Result<(), BoundaryError>;
}

impl ValidateBoundary for PythonBoundaryRequest {
    fn validate(&self) -> Result<(), BoundaryError> {
        validate_protocol_version(self.protocol_version)?;
        validate_legacy_ids(self)?;
        validate_operation_payload(self)?;
        validate_provider_config(self)?;

        Ok(())
    }
}

fn validate_protocol_version(protocol_version: u16) -> Result<(), BoundaryError> {
    if protocol_version != BOUNDARY_PROTOCOL_VERSION {
        return Err(BoundaryError {
            code: BoundaryErrorCode::UnsupportedProtocolVersion,
            message: format!("unsupported boundary protocol version: {protocol_version}"),
            retryable: false,
        });
    }

    Ok(())
}

fn validate_legacy_ids(request: &PythonBoundaryRequest) -> Result<(), BoundaryError> {
    for (name, value) in [
        ("project_legacy_id", request.project_legacy_id),
        ("domain_legacy_id", request.domain_legacy_id),
        ("agent_legacy_id", request.agent_legacy_id),
    ] {
        if value.is_some_and(|id| id <= 0) {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: format!("{name} must be a positive signed integer"),
                retryable: false,
            });
        }
    }

    Ok(())
}

fn validate_operation_payload(request: &PythonBoundaryRequest) -> Result<(), BoundaryError> {
    match request.operation {
        BoundaryOperation::GenerateImage | BoundaryOperation::GenerateVideo => {
            let generation_request =
                request
                    .generation_request
                    .as_ref()
                    .ok_or_else(|| BoundaryError {
                        code: BoundaryErrorCode::InvalidRequest,
                        message: "generation operation requires generation_request".to_owned(),
                        retryable: false,
                    })?;

            if generation_request.prompt.trim().is_empty() {
                return Err(BoundaryError {
                    code: BoundaryErrorCode::InvalidRequest,
                    message: "generation prompt must not be empty".to_owned(),
                    retryable: false,
                });
            }

            if request.external_job_id.is_some() {
                return Err(BoundaryError {
                    code: BoundaryErrorCode::InvalidRequest,
                    message: "generation operation must not include external_job_id".to_owned(),
                    retryable: false,
                });
            }
        }

        BoundaryOperation::CheckJobStatus | BoundaryOperation::CancelJob => {
            if request
                .external_job_id
                .as_deref()
                .is_none_or(|job_id| job_id.trim().is_empty())
            {
                return Err(BoundaryError {
                    code: BoundaryErrorCode::InvalidRequest,
                    message: "job operation requires external_job_id".to_owned(),
                    retryable: false,
                });
            }

            if request.generation_request.is_some() {
                return Err(BoundaryError {
                    code: BoundaryErrorCode::InvalidRequest,
                    message: "job operation must not include generation_request".to_owned(),
                    retryable: false,
                });
            }
        }

        BoundaryOperation::EstimateCost => {
            let generation_request =
                request
                    .generation_request
                    .as_ref()
                    .ok_or_else(|| BoundaryError {
                        code: BoundaryErrorCode::InvalidRequest,
                        message: "cost estimation requires generation_request".to_owned(),
                        retryable: false,
                    })?;

            if generation_request.prompt.trim().is_empty() {
                return Err(BoundaryError {
                    code: BoundaryErrorCode::InvalidRequest,
                    message: "cost estimation prompt must not be empty".to_owned(),
                    retryable: false,
                });
            }
        }
    }

    Ok(())
}

fn validate_provider_config(request: &PythonBoundaryRequest) -> Result<(), BoundaryError> {
    let Some(config) = request.provider_config.as_ref() else {
        return Ok(());
    };

    if config.api_key.is_some() {
        return Err(BoundaryError {
            code: BoundaryErrorCode::InvalidRequest,
            message: "provider API keys must not cross the boundary".to_owned(),
            retryable: false,
        });
    }

    if !config.enabled {
        return Err(BoundaryError {
            code: BoundaryErrorCode::ProviderUnavailable,
            message: "provider is disabled".to_owned(),
            retryable: true,
        });
    }

    if config.timeout_seconds <= 0 {
        return Err(BoundaryError {
            code: BoundaryErrorCode::InvalidRequest,
            message: "provider timeout_seconds must be positive".to_owned(),
            retryable: false,
        });
    }

    if config.max_retries < 0 {
        return Err(BoundaryError {
            code: BoundaryErrorCode::InvalidRequest,
            message: "provider max_retries must not be negative".to_owned(),
            retryable: false,
        });
    }

    if config.priority <= 0 {
        return Err(BoundaryError {
            code: BoundaryErrorCode::InvalidRequest,
            message: "provider priority must be positive".to_owned(),
            retryable: false,
        });
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{GenerationRequest, ProviderConfig, ProviderType, PythonBoundaryRequest};
    use eli_core::AgentTaskAnchorId;

    fn valid_generation_request() -> PythonBoundaryRequest {
        PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(101),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Create image"),
        )
    }

    #[test]
    fn valid_generation_request_passes() {
        let request = valid_generation_request();

        assert_eq!(request.validate(), Ok(()));
    }

    #[test]
    fn rejects_unsupported_protocol_version() {
        let mut request = valid_generation_request();
        request.protocol_version = BOUNDARY_PROTOCOL_VERSION + 1;

        let error = request.validate().expect_err("must reject version");

        assert_eq!(error.code, BoundaryErrorCode::UnsupportedProtocolVersion);
    }

    #[test]
    fn rejects_non_positive_legacy_ids() {
        let mut request = valid_generation_request();
        request.project_legacy_id = Some(0);

        let error = request.validate().expect_err("must reject invalid id");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn rejects_generation_without_payload() {
        let mut request = valid_generation_request();
        request.generation_request = None;

        let error = request.validate().expect_err("must require payload");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn rejects_empty_generation_prompt() {
        let mut request = valid_generation_request();
        request
            .generation_request
            .as_mut()
            .expect("generation payload")
            .prompt = "   ".to_owned();

        let error = request.validate().expect_err("must reject empty prompt");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn rejects_status_check_without_job_id() {
        let mut request = valid_generation_request();
        request.operation = BoundaryOperation::CheckJobStatus;
        request.generation_request = None;
        request.external_job_id = None;

        let error = request.validate().expect_err("must require job id");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn rejects_api_key_crossing_boundary() {
        let mut request = valid_generation_request();
        request.provider_config = Some(ProviderConfig {
            provider_type: ProviderType::Mock,
            api_key: Some("secret".to_owned()),
            base_url: None,
            model_name: None,
            timeout_seconds: 300,
            max_retries: 3,
            rate_limit_requests: None,
            rate_limit_period_seconds: None,
            enabled: true,
            priority: 1,
        });

        let error = request.validate().expect_err("must reject API key");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn disabled_provider_fails_closed() {
        let mut request = valid_generation_request();
        request.provider_config = Some(ProviderConfig {
            provider_type: ProviderType::Mock,
            api_key: None,
            base_url: None,
            model_name: None,
            timeout_seconds: 300,
            max_retries: 3,
            rate_limit_requests: None,
            rate_limit_period_seconds: None,
            enabled: false,
            priority: 1,
        });

        let error = request.validate().expect_err("disabled provider must fail");

        assert_eq!(error.code, BoundaryErrorCode::ProviderUnavailable);
        assert!(error.retryable);
    }
}
