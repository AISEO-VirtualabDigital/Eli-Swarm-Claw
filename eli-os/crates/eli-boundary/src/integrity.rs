use crate::{
    BOUNDARY_PROTOCOL_VERSION, BoundaryError, BoundaryErrorCode, PythonBoundaryRequest,
    ValidateBoundary,
};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

pub const BOUNDARY_SCHEMA_FINGERPRINT: &str = "eli-boundary:v1:python-rust-generation-contract";

#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd, Serialize, Deserialize)]
pub struct CorrelationId(String);

impl CorrelationId {
    #[must_use]
    pub fn new(value: impl Into<String>) -> Self {
        Self(value.into())
    }

    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd, Serialize, Deserialize)]
pub struct IdempotencyKey(String);

impl IdempotencyKey {
    #[must_use]
    pub fn new(value: impl Into<String>) -> Self {
        Self(value.into())
    }

    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct BoundaryEnvelope {
    pub protocol_version: u16,
    pub schema_fingerprint: String,
    pub correlation_id: CorrelationId,
    pub idempotency_key: IdempotencyKey,
    pub issued_at_unix_ms: u64,
    pub expires_at_unix_ms: u64,
    pub request: PythonBoundaryRequest,
}

impl BoundaryEnvelope {
    #[must_use]
    pub fn new(
        correlation_id: CorrelationId,
        idempotency_key: IdempotencyKey,
        issued_at_unix_ms: u64,
        ttl_ms: u64,
        request: PythonBoundaryRequest,
    ) -> Self {
        Self {
            protocol_version: BOUNDARY_PROTOCOL_VERSION,
            schema_fingerprint: BOUNDARY_SCHEMA_FINGERPRINT.to_owned(),
            correlation_id,
            idempotency_key,
            issued_at_unix_ms,
            expires_at_unix_ms: issued_at_unix_ms.saturating_add(ttl_ms),
            request,
        }
    }

    pub fn validate_at(&self, now_unix_ms: u64) -> Result<(), BoundaryError> {
        if self.protocol_version != BOUNDARY_PROTOCOL_VERSION {
            return Err(BoundaryError {
                code: BoundaryErrorCode::UnsupportedProtocolVersion,
                message: format!(
                    "unsupported envelope protocol version: {}",
                    self.protocol_version
                ),
                retryable: false,
            });
        }

        if self.schema_fingerprint != BOUNDARY_SCHEMA_FINGERPRINT {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "boundary schema fingerprint mismatch".to_owned(),
                retryable: false,
            });
        }

        if self.correlation_id.as_str().trim().is_empty() {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "correlation_id must not be empty".to_owned(),
                retryable: false,
            });
        }

        if self.idempotency_key.as_str().trim().is_empty() {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "idempotency_key must not be empty".to_owned(),
                retryable: false,
            });
        }

        if self.expires_at_unix_ms <= self.issued_at_unix_ms {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "envelope expiry must be later than issue time".to_owned(),
                retryable: false,
            });
        }

        if now_unix_ms < self.issued_at_unix_ms {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "envelope issue time is in the future".to_owned(),
                retryable: false,
            });
        }

        if now_unix_ms >= self.expires_at_unix_ms {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "boundary envelope has expired".to_owned(),
                retryable: false,
            });
        }

        self.request.validate()
    }
}

#[derive(Clone, Debug, Default)]
pub struct ReplayGuard {
    consumed_keys: BTreeSet<IdempotencyKey>,
}

impl ReplayGuard {
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    pub fn accept(
        &mut self,
        envelope: &BoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<(), BoundaryError> {
        envelope.validate_at(now_unix_ms)?;

        if self.consumed_keys.contains(&envelope.idempotency_key) {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "duplicate or replayed boundary request".to_owned(),
                retryable: false,
            });
        }

        self.consumed_keys.insert(envelope.idempotency_key.clone());

        Ok(())
    }

    #[must_use]
    pub fn contains(&self, key: &IdempotencyKey) -> bool {
        self.consumed_keys.contains(key)
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.consumed_keys.len()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.consumed_keys.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{BoundaryOperation, GenerationRequest, PythonBoundaryRequest};
    use eli_core::AgentTaskAnchorId;

    fn valid_request() -> PythonBoundaryRequest {
        PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(101),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Create image"),
        )
    }

    fn valid_envelope() -> BoundaryEnvelope {
        BoundaryEnvelope::new(
            CorrelationId::new("corr-001"),
            IdempotencyKey::new("idem-001"),
            1_000,
            5_000,
            valid_request(),
        )
    }

    #[test]
    fn valid_envelope_passes_integrity_validation() {
        let envelope = valid_envelope();

        assert_eq!(envelope.validate_at(2_000), Ok(()));
    }

    #[test]
    fn expired_envelope_fails_closed() {
        let envelope = valid_envelope();

        let error = envelope
            .validate_at(6_000)
            .expect_err("expired envelope must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
        assert!(!error.retryable);
    }

    #[test]
    fn future_issued_envelope_fails_closed() {
        let envelope = valid_envelope();

        let error = envelope
            .validate_at(999)
            .expect_err("future-issued envelope must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn schema_mismatch_fails_closed() {
        let mut envelope = valid_envelope();
        envelope.schema_fingerprint = "unexpected-schema".to_owned();

        let error = envelope
            .validate_at(2_000)
            .expect_err("schema mismatch must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn replay_guard_rejects_duplicate_idempotency_key() {
        let envelope = valid_envelope();
        let mut guard = ReplayGuard::new();

        assert_eq!(guard.accept(&envelope, 2_000), Ok(()));

        let error = guard
            .accept(&envelope, 2_001)
            .expect_err("duplicate request must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
        assert_eq!(guard.len(), 1);
    }

    #[test]
    fn replay_guard_tracks_consumed_key() {
        let envelope = valid_envelope();
        let key = envelope.idempotency_key.clone();
        let mut guard = ReplayGuard::new();

        guard
            .accept(&envelope, 2_000)
            .expect("first request must pass");

        assert!(guard.contains(&key));
    }
}
