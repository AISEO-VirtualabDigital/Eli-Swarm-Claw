use crate::validation::ValidateBoundary;
use crate::{
    AuthenticatedBoundaryEnvelope, AuthenticationKeyRing, BoundaryDecisionReceipt, BoundaryError,
    BoundaryErrorCode, BoundaryProcessingOutcome, InMemoryReplayStore,
    InMemoryVerificationKeyStore, PythonBoundaryRequest, ReplayStore, VerificationKeyStore,
};

/// Processes authenticated Python–Rust boundary envelopes.
///
/// Processing order:
///
/// 1. Resolve the verification key using the envelope key ID.
/// 2. Verify cryptographic authentication.
/// 3. Validate protocol, schema, and timestamps.
/// 4. Validate the enclosed request.
/// 5. Atomically check and consume the replay key.
/// 6. Return the validated request or processing outcome.
///
/// Authentication and validation failures never consume replay keys.
#[derive(Debug)]
pub struct BoundaryProcessor<K = InMemoryVerificationKeyStore, R = InMemoryReplayStore> {
    key_store: K,
    replay_store: R,
}

impl BoundaryProcessor<InMemoryVerificationKeyStore, InMemoryReplayStore> {
    #[must_use]
    pub fn new(key_ring: AuthenticationKeyRing) -> Self {
        Self {
            key_store: InMemoryVerificationKeyStore::new(key_ring),
            replay_store: InMemoryReplayStore::new(),
        }
    }
}

impl<K, R> BoundaryProcessor<K, R>
where
    K: VerificationKeyStore,
    R: ReplayStore,
{
    #[must_use]
    pub fn with_stores(key_store: K, replay_store: R) -> Self {
        Self {
            key_store,
            replay_store,
        }
    }

    pub fn process(
        &mut self,
        authenticated: AuthenticatedBoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<PythonBoundaryRequest, BoundaryError> {
        self.process_with_receipt(authenticated, now_unix_ms)
            .map(BoundaryProcessingOutcome::into_request)
    }

    pub fn process_with_receipt(
        &mut self,
        authenticated: AuthenticatedBoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<BoundaryProcessingOutcome, BoundaryError> {
        let verification_key = self
            .key_store
            .verification_key(&authenticated.key_id)
            .ok_or_else(|| BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "boundary envelope references an unknown or unusable key ID".to_owned(),
                retryable: false,
            })?;

        authenticated.verify(verification_key)?;
        authenticated.envelope.validate_at(now_unix_ms)?;
        authenticated.envelope.request.validate()?;

        self.replay_store
            .check_and_consume(&authenticated.envelope, now_unix_ms)?;

        let receipt = BoundaryDecisionReceipt::accepted(&authenticated, now_unix_ms);
        let request = authenticated.envelope.request;

        Ok(BoundaryProcessingOutcome::accepted(request, receipt))
    }

    #[must_use]
    pub fn key_store(&self) -> &K {
        &self.key_store
    }

    #[must_use]
    pub fn replay_store(&self) -> &R {
        &self.replay_store
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
            .expect("managed key must be valid")
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

        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-active", "idem-active"),
            key_id("active-key"),
            &active_key,
        )
        .expect("envelope must be signed");

        let mut processor = BoundaryProcessor::new(ring);

        let request = processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("envelope must be accepted");

        assert_eq!(request.agent_legacy_id, Some(42));
        assert_eq!(processor.replay_store().len(), 1);
    }

    #[test]
    fn process_with_receipt_returns_request_and_receipt() {
        let active_key = authentication_key(1);

        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-outcome", "idem-outcome"),
            key_id("active-key"),
            &active_key,
        )
        .expect("envelope must be signed");

        let mut processor = BoundaryProcessor::new(ring);

        let outcome = processor
            .process_with_receipt(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("envelope must be accepted with receipt");

        assert_eq!(outcome.request().agent_legacy_id, Some(42));
        assert_eq!(outcome.receipt().correlation_id().as_str(), "corr-outcome");
        assert_eq!(outcome.receipt().idempotency_key().as_str(), "idem-outcome");
        assert_eq!(outcome.receipt().key_id().as_str(), "active-key");
        assert_eq!(
            outcome.receipt().processed_at_unix_ms(),
            PROCESSING_TIME_UNIX_MS
        );
        assert_eq!(processor.replay_store().len(), 1);
    }

    #[test]
    fn previous_key_is_accepted_after_rotation() {
        let previous_key = authentication_key(1);
        let current = managed_active_key("previous-key", 1, 500, 500);
        let next = managed_active_key("active-key", 2, 1_500, 1_500);

        let mut ring = AuthenticationKeyRing::new(current).expect("key ring must be valid");

        ring.rotate(next, 1_500).expect("rotation must succeed");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-previous", "idem-previous"),
            key_id("previous-key"),
            &previous_key,
        )
        .expect("envelope must be signed");

        let mut processor = BoundaryProcessor::new(ring);

        processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("verification-only key must remain usable");

        assert_eq!(processor.replay_store().len(), 1);
    }

    #[test]
    fn unknown_key_does_not_consume_replay_key() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-unknown", "idem-unknown"),
            key_id("unknown-key"),
            &authentication_key(9),
        )
        .expect("envelope must be signed");

        let mut processor = BoundaryProcessor::new(ring);

        processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect_err("unknown key must fail");

        assert!(processor.replay_store().is_empty());
    }

    #[test]
    fn wrong_key_does_not_consume_replay_key() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-wrong", "idem-wrong"),
            key_id("active-key"),
            &authentication_key(9),
        )
        .expect("envelope must be signed");

        let mut processor = BoundaryProcessor::new(ring);

        processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect_err("wrong key must fail");

        assert!(processor.replay_store().is_empty());
    }

    #[test]
    fn replayed_envelope_is_rejected() {
        let active_key = authentication_key(1);

        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-replay", "idem-replay"),
            key_id("active-key"),
            &active_key,
        )
        .expect("envelope must be signed");

        let replayed = authenticated.clone();
        let mut processor = BoundaryProcessor::new(ring);

        processor
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("first request must pass");

        processor
            .process(replayed, PROCESSING_TIME_UNIX_MS)
            .expect_err("replay must fail");

        assert_eq!(processor.replay_store().len(), 1);
    }
}
