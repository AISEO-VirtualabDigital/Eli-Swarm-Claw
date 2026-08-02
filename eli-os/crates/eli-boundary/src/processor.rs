use crate::validation::ValidateBoundary;
use crate::{
    AuthenticatedBoundaryEnvelope, AuthenticationKeyRing, BoundaryError, BoundaryErrorCode,
    PythonBoundaryRequest, ReplayGuard,
};

/// Processes authenticated Python–Rust boundary envelopes.
///
/// Processing order:
///
/// 1. Resolve the verification key using the envelope key ID.
/// 2. Verify cryptographic authentication.
/// 3. Validate envelope protocol, schema, and timestamps.
/// 4. Validate the enclosed boundary request.
/// 5. Check and consume the replay/idempotency key.
/// 6. Return the validated request.
///
/// Replay keys are consumed only after authentication and validation succeed.
#[derive(Debug)]
pub struct BoundaryProcessor {
    key_ring: AuthenticationKeyRing,
    replay_guard: ReplayGuard,
}

impl BoundaryProcessor {
    pub fn new(key_ring: AuthenticationKeyRing) -> Self {
        Self {
            key_ring,
            replay_guard: ReplayGuard::new(),
        }
    }

    pub fn process(
        &mut self,
        authenticated: AuthenticatedBoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<PythonBoundaryRequest, BoundaryError> {
        let verification_key = self
            .key_ring
            .verification_key(&authenticated.key_id)
            .ok_or_else(|| BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "boundary envelope references an unknown or unusable key ID".to_owned(),
                retryable: false,
            })?;

        authenticated.verify(verification_key)?;

        authenticated.envelope.validate_at(now_unix_ms)?;

        authenticated.envelope.request.validate()?;

        self.replay_guard
            .accept(&authenticated.envelope, now_unix_ms)?;

        Ok(authenticated.envelope.request)
    }

    #[must_use]
    pub fn key_ring(&self) -> &AuthenticationKeyRing {
        &self.key_ring
    }

    #[must_use]
    pub fn replay_guard(&self) -> &ReplayGuard {
        &self.replay_guard
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        AuthenticationKey, AuthenticationKeyMetadata, BoundaryEnvelope, BoundaryOperation,
        CorrelationId, GenerationRequest, IdempotencyKey, KeyId, ManagedAuthenticationKey,
    };
    use eli_core::AgentTaskAnchorId;

    const ISSUED_AT_UNIX_MS: u64 = 1_000;
    const TTL_MS: u64 = 5_000;
    const PROCESSING_TIME_UNIX_MS: u64 = 2_000;

    fn authentication_key(seed: u8) -> AuthenticationKey {
        AuthenticationKey::new(vec![seed; 32]).expect("test authentication key must be valid")
    }

    fn key_id(value: &str) -> KeyId {
        KeyId::new(value).expect("test key ID must be valid")
    }

    fn managed_active_key(
        key_id_value: &str,
        seed: u8,
        created_at_unix_ms: u64,
        activated_at_unix_ms: u64,
    ) -> ManagedAuthenticationKey {
        let metadata = AuthenticationKeyMetadata::active(
            key_id(key_id_value),
            created_at_unix_ms,
            activated_at_unix_ms,
        )
        .expect("active key metadata must be valid");

        ManagedAuthenticationKey::new(metadata, authentication_key(seed))
            .expect("managed authentication key must be valid")
    }

    fn boundary_envelope(correlation_id: &str, idempotency_key: &str) -> BoundaryEnvelope {
        let request = PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(101),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Create image"),
        );

        BoundaryEnvelope::new(
            CorrelationId::new(correlation_id),
            IdempotencyKey::new(idempotency_key),
            ISSUED_AT_UNIX_MS,
            TTL_MS,
            request,
        )
    }

    #[test]
    fn active_key_envelope_is_accepted() {
        let active_key = authentication_key(1);
        let active_key_id = key_id("active-key");

        let managed_active = managed_active_key("active-key", 1, 500, 500);
        let key_ring = AuthenticationKeyRing::new(managed_active).expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-active", "idem-active"),
            active_key_id,
            &active_key,
        )
        .expect("active-key envelope must be signed");

        let mut processor = BoundaryProcessor::new(key_ring);

        let request = processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("active-key envelope must be accepted");

        assert_eq!(request.agent_legacy_id, Some(42));
        assert_eq!(processor.replay_guard().len(), 1);
    }

    #[test]
    fn previous_key_envelope_is_accepted_after_rotation() {
        let previous_key = authentication_key(1);
        let previous_key_id = key_id("previous-key");

        let current = managed_active_key("previous-key", 1, 500, 500);
        let next = managed_active_key("current-key", 2, 1_500, 1_500);

        let mut key_ring = AuthenticationKeyRing::new(current).expect("key ring must be valid");

        key_ring
            .rotate(next, 1_500)
            .expect("key rotation must succeed");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-previous", "idem-previous"),
            previous_key_id,
            &previous_key,
        )
        .expect("previous-key envelope must be signed");

        let mut processor = BoundaryProcessor::new(key_ring);

        processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("verification-only previous key must remain usable");

        assert_eq!(processor.replay_guard().len(), 1);
    }

    #[test]
    fn unknown_key_id_is_rejected_without_consuming_replay_key() {
        let managed_active = managed_active_key("active-key", 1, 500, 500);
        let key_ring = AuthenticationKeyRing::new(managed_active).expect("key ring must be valid");

        let unknown_key = authentication_key(9);

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-unknown", "idem-unknown"),
            key_id("unknown-key"),
            &unknown_key,
        )
        .expect("unknown-key envelope can still be locally signed");

        let mut processor = BoundaryProcessor::new(key_ring);

        let error = processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect_err("unknown key ID must fail closed");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
        assert!(processor.replay_guard().is_empty());
    }

    #[test]
    fn wrong_key_for_valid_key_id_is_rejected_without_consuming_replay_key() {
        let managed_active = managed_active_key("active-key", 1, 500, 500);
        let key_ring = AuthenticationKeyRing::new(managed_active).expect("key ring must be valid");

        let wrong_signing_key = authentication_key(9);

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-wrong-key", "idem-wrong-key"),
            key_id("active-key"),
            &wrong_signing_key,
        )
        .expect("envelope must be locally signed");

        let mut processor = BoundaryProcessor::new(key_ring);

        let error = processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect_err("wrong signing key must fail authentication");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
        assert!(processor.replay_guard().is_empty());
    }

    #[test]
    fn replayed_valid_envelope_is_rejected() {
        let active_key = authentication_key(1);
        let active_key_id = key_id("active-key");

        let managed_active = managed_active_key("active-key", 1, 500, 500);
        let key_ring = AuthenticationKeyRing::new(managed_active).expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-replay", "idem-replay"),
            active_key_id,
            &active_key,
        )
        .expect("valid envelope must be signed");

        let replayed = authenticated.clone();
        let mut processor = BoundaryProcessor::new(key_ring);

        processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("first request must be accepted");

        let error = processor
            .process(replayed, PROCESSING_TIME_UNIX_MS)
            .expect_err("replayed request must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
        assert_eq!(processor.replay_guard().len(), 1);
    }
}
