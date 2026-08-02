use crate::{
    AuthenticatedBoundaryEnvelope, AuthenticationKeyRing, BoundaryAuditEvent, BoundaryAuditSink,
    BoundaryAuditSnapshot, BoundaryEnvelope, BoundaryError, BoundaryGateway,
    BoundaryProcessingOutcome, InMemoryBoundaryAuditSink, InMemoryReplayStore,
    InMemoryVerificationKeyStore, PythonBoundaryRequest, ReplayStore, SigningKeyStore,
    VerificationKeyStore,
};

/// Boundary gateway wrapper with an owned audit sink.
///
/// This is still a pure boundary primitive. It does not persist audit events,
/// emit logs, call Python, route work, execute tasks, or perform transport.
#[derive(Debug)]
pub struct AuditedBoundaryGateway<
    K = InMemoryVerificationKeyStore,
    R = InMemoryReplayStore,
    A = InMemoryBoundaryAuditSink,
> {
    gateway: BoundaryGateway<K, R>,
    audit_sink: A,
}

impl
    AuditedBoundaryGateway<
        InMemoryVerificationKeyStore,
        InMemoryReplayStore,
        InMemoryBoundaryAuditSink,
    >
{
    #[must_use]
    pub fn new(key_ring: AuthenticationKeyRing) -> Self {
        Self {
            gateway: BoundaryGateway::new(key_ring),
            audit_sink: InMemoryBoundaryAuditSink::new(),
        }
    }
}

impl<K, R, A> AuditedBoundaryGateway<K, R, A>
where
    K: VerificationKeyStore,
    R: ReplayStore,
    A: BoundaryAuditSink,
{
    #[must_use]
    pub fn with_parts(gateway: BoundaryGateway<K, R>, audit_sink: A) -> Self {
        Self {
            gateway,
            audit_sink,
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
        self.gateway
            .process_with_audit(authenticated, now_unix_ms, &mut self.audit_sink)
    }

    pub fn process_with_full_audit(
        &mut self,
        authenticated: AuthenticatedBoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<BoundaryProcessingOutcome, BoundaryError> {
        match self.gateway.process_with_audit(
            authenticated.clone(),
            now_unix_ms,
            &mut self.audit_sink,
        ) {
            Ok(outcome) => Ok(outcome),
            Err(error) => {
                let audit_event = BoundaryAuditEvent::rejected_from_authenticated(
                    &authenticated,
                    &error,
                    now_unix_ms,
                );

                self.audit_sink.record(audit_event);

                Err(error)
            }
        }
    }

    #[must_use]
    pub fn gateway(&self) -> &BoundaryGateway<K, R> {
        &self.gateway
    }

    #[must_use]
    pub fn audit_sink(&self) -> &A {
        &self.audit_sink
    }
}

impl<K, R> AuditedBoundaryGateway<K, R, InMemoryBoundaryAuditSink>
where
    K: VerificationKeyStore,
    R: ReplayStore,
{
    #[must_use]
    pub fn audit_snapshot(&self) -> BoundaryAuditSnapshot {
        self.audit_sink.snapshot()
    }
}

impl<K, R, A> AuditedBoundaryGateway<K, R, A>
where
    K: SigningKeyStore + VerificationKeyStore,
    R: ReplayStore,
    A: BoundaryAuditSink,
{
    pub fn sign(
        &self,
        envelope: BoundaryEnvelope,
    ) -> Result<AuthenticatedBoundaryEnvelope, BoundaryError> {
        self.gateway.sign(envelope)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        AuthenticationKey, AuthenticationKeyMetadata, BoundaryAuditEventKind, BoundaryOperation,
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
    fn audited_gateway_full_audit_records_rejected_event_on_failure() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-full-audit-fail", "idem-full-audit-fail"),
            key_id("unknown-key"),
            &authentication_key(9),
        )
        .expect("unknown-key envelope can be locally signed");

        let mut gateway = AuditedBoundaryGateway::new(ring);

        gateway
            .process_with_full_audit(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect_err("unknown key must fail closed");

        let events = gateway.audit_sink().events();

        assert_eq!(events.len(), 1);
        assert_eq!(events[0].kind(), &BoundaryAuditEventKind::Rejected);
        assert_eq!(events[0].correlation_id().as_str(), "corr-full-audit-fail");
        assert_eq!(events[0].idempotency_key().as_str(), "idem-full-audit-fail");
        assert_eq!(events[0].key_id().as_str(), "unknown-key");
        assert_eq!(events[0].operation(), &BoundaryOperation::GenerateImage);
        assert_eq!(events[0].failure_code(), Some("InvalidRequest"));
        assert!(
            events[0]
                .failure_message()
                .expect("failure message must exist")
                .contains("unknown or unusable key ID")
        );

        assert!(gateway.gateway().processor().replay_store().is_empty());
    }

    #[test]
    fn audited_gateway_full_audit_records_accepted_event_on_success() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let mut gateway = AuditedBoundaryGateway::new(ring);

        let authenticated = gateway
            .sign(boundary_envelope(
                "corr-full-audit-ok",
                "idem-full-audit-ok",
            ))
            .expect("audited gateway signing must succeed");

        let outcome = gateway
            .process_with_full_audit(authenticated, PROCESSING_TIME_UNIX_MS)
            .expect("full audit processing must succeed");

        assert_eq!(outcome.request().agent_legacy_id, Some(42));

        let events = gateway.audit_sink().events();

        assert_eq!(events.len(), 1);
        assert_eq!(events[0].kind(), &BoundaryAuditEventKind::Accepted);
        assert_eq!(events[0].correlation_id().as_str(), "corr-full-audit-ok");
        assert_eq!(events[0].idempotency_key().as_str(), "idem-full-audit-ok");
        assert_eq!(events[0].key_id().as_str(), "active-key");
        assert_eq!(events[0].failure_code(), None);
        assert_eq!(events[0].failure_message(), None);
    }
    #[test]
    fn audited_gateway_snapshot_reports_empty_state() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let gateway = AuditedBoundaryGateway::new(ring);
        let snapshot = gateway.audit_snapshot();

        assert!(snapshot.is_empty());
        assert_eq!(snapshot.total_count(), 0);
        assert_eq!(snapshot.accepted_count(), 0);
        assert_eq!(snapshot.rejected_count(), 0);
        assert_eq!(snapshot.latest_processed_at_unix_ms(), None);
    }

    #[test]
    fn audited_gateway_snapshot_counts_accepted_and_rejected_events() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 500, 500))
            .expect("key ring must be valid");

        let mut gateway = AuditedBoundaryGateway::new(ring);

        let accepted = gateway
            .sign(boundary_envelope("corr-snapshot-ok", "idem-snapshot-ok"))
            .expect("audited gateway signing must succeed");

        gateway
            .process_with_full_audit(accepted, PROCESSING_TIME_UNIX_MS)
            .expect("accepted envelope must succeed");

        let rejected = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-snapshot-fail", "idem-snapshot-fail"),
            key_id("unknown-key"),
            &authentication_key(9),
        )
        .expect("unknown-key envelope can be locally signed");

        gateway
            .process_with_full_audit(rejected, PROCESSING_TIME_UNIX_MS + 500)
            .expect_err("unknown key must fail closed");

        let snapshot = gateway.audit_snapshot();

        assert_eq!(snapshot.total_count(), 2);
        assert_eq!(snapshot.accepted_count(), 1);
        assert_eq!(snapshot.rejected_count(), 1);
        assert_eq!(
            snapshot.latest_processed_at_unix_ms(),
            Some(PROCESSING_TIME_UNIX_MS + 500)
        );
    }
}
