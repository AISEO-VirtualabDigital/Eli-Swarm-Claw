use crate::{
    AuthenticatedBoundaryEnvelope, AuthenticationKeyRing, BoundaryEnvelope, BoundaryError,
    BoundaryProcessor, InMemoryReplayStore, InMemoryVerificationKeyStore, PythonBoundaryRequest,
    ReplayStore, SigningKeyStore, VerificationKeyStore,
};

/// Boundary-level facade for signing and processing authenticated envelopes.
///
/// This is a pure boundary primitive. It does not route work, execute tasks,
/// call Python, run agents, persist state, or perform network transport.
#[derive(Debug)]
pub struct BoundaryGateway<K = InMemoryVerificationKeyStore, R = InMemoryReplayStore> {
    processor: BoundaryProcessor<K, R>,
}

impl BoundaryGateway<InMemoryVerificationKeyStore, InMemoryReplayStore> {
    #[must_use]
    pub fn new(key_ring: AuthenticationKeyRing) -> Self {
        Self {
            processor: BoundaryProcessor::new(key_ring),
        }
    }
}

impl<K, R> BoundaryGateway<K, R>
where
    K: VerificationKeyStore,
    R: ReplayStore,
{
    #[must_use]
    pub fn with_stores(key_store: K, replay_store: R) -> Self {
        Self {
            processor: BoundaryProcessor::with_stores(key_store, replay_store),
        }
    }

    pub fn process(
        &mut self,
        authenticated: AuthenticatedBoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<PythonBoundaryRequest, BoundaryError> {
        self.processor.process(authenticated, now_unix_ms)
    }

    #[must_use]
    pub fn processor(&self) -> &BoundaryProcessor<K, R> {
        &self.processor
    }
}

impl<K, R> BoundaryGateway<K, R>
where
    K: SigningKeyStore + VerificationKeyStore,
    R: ReplayStore,
{
    pub fn sign(
        &self,
        envelope: BoundaryEnvelope,
    ) -> Result<AuthenticatedBoundaryEnvelope, BoundaryError> {
        AuthenticatedBoundaryEnvelope::sign_with_store(envelope, self.processor.key_store())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        AuthenticationKey, AuthenticationKeyMetadata, BoundaryOperation, CorrelationId,
        GenerationRequest, IdempotencyKey, KeyId, ManagedAuthenticationKey,
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
    fn gateway_signs_and_processes_active_key_envelope() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let mut gateway = BoundaryGateway::new(ring);

        let authenticated = gateway
            .sign(boundary_envelope(
                "corr-gateway-active",
                "idem-gateway-active",
            ))
            .expect("gateway signing must succeed");

        assert_eq!(authenticated.key_id.as_str(), "active-key");

        let request = gateway
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("gateway processing must succeed");

        assert_eq!(request.agent_legacy_id, Some(42));
        assert_eq!(gateway.processor().replay_store().len(), 1);
    }

    #[test]
    fn gateway_signs_with_current_key_after_rotation() {
        let current = managed_active_key("previous-key", 1, 500, 500);
        let next = managed_active_key("active-key", 2, 1_500, 1_500);

        let mut ring = AuthenticationKeyRing::new(current).expect("key ring must be valid");
        ring.rotate(next, 1_500).expect("key rotation must succeed");

        let gateway = BoundaryGateway::new(ring);

        let authenticated = gateway
            .sign(boundary_envelope(
                "corr-gateway-rotated",
                "idem-gateway-rotated",
            ))
            .expect("gateway signing must use current active key");

        assert_eq!(authenticated.key_id.as_str(), "active-key");
    }

    #[test]
    fn gateway_processes_previous_key_envelope_after_rotation() {
        let previous_key = authentication_key(1);
        let current = managed_active_key("previous-key", 1, 500, 500);
        let next = managed_active_key("active-key", 2, 1_500, 1_500);

        let mut ring = AuthenticationKeyRing::new(current).expect("key ring must be valid");
        ring.rotate(next, 1_500).expect("key rotation must succeed");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-gateway-previous", "idem-gateway-previous"),
            key_id("previous-key"),
            &previous_key,
        )
        .expect("previous-key envelope must be signed");

        let mut gateway = BoundaryGateway::new(ring);

        gateway
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("previous verification-only key must remain usable");

        assert_eq!(gateway.processor().replay_store().len(), 1);
    }

    #[test]
    fn gateway_unknown_key_does_not_consume_replay_key() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-gateway-unknown", "idem-gateway-unknown"),
            key_id("unknown-key"),
            &authentication_key(9),
        )
        .expect("unknown-key envelope can be locally signed");

        let mut gateway = BoundaryGateway::new(ring);

        gateway
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect_err("unknown key must fail closed");

        assert!(gateway.processor().replay_store().is_empty());
    }

    #[test]
    fn gateway_rejects_replayed_envelope() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let mut gateway = BoundaryGateway::new(ring);

        let authenticated = gateway
            .sign(boundary_envelope(
                "corr-gateway-replay",
                "idem-gateway-replay",
            ))
            .expect("gateway signing must succeed");

        let replayed = authenticated.clone();

        gateway
            .process(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("first envelope must be accepted");

        gateway
            .process(replayed, PROCESSING_TIME_UNIX_MS)
            .expect_err("replayed envelope must be rejected");

        assert_eq!(gateway.processor().replay_store().len(), 1);
    }
}
