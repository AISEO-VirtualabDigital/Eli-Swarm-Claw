use crate::{BoundaryAuditEvent, BoundaryAuditEventView, BoundaryAuditSnapshot};

/// Read-only boundary audit report.
///
/// This combines a snapshot summary with safe event views for later UI,
/// report, log, or transport use. It does not persist data, emit logs,
/// expose HTTP, call Python, route work, or execute tasks.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BoundaryAuditReport {
    snapshot: BoundaryAuditSnapshot,
    events: Vec<BoundaryAuditEventView>,
}

impl BoundaryAuditReport {
    #[must_use]
    pub fn new(events: &[BoundaryAuditEvent]) -> Self {
        Self {
            snapshot: BoundaryAuditSnapshot::new(events),
            events: BoundaryAuditEventView::from_events(events),
        }
    }

    #[must_use]
    pub fn snapshot(&self) -> &BoundaryAuditSnapshot {
        &self.snapshot
    }

    #[must_use]
    pub fn events(&self) -> &[BoundaryAuditEventView] {
        &self.events
    }

    #[must_use]
    pub fn total_count(&self) -> usize {
        self.snapshot.total_count()
    }

    #[must_use]
    pub fn accepted_count(&self) -> usize {
        self.snapshot.accepted_count()
    }

    #[must_use]
    pub fn rejected_count(&self) -> usize {
        self.snapshot.rejected_count()
    }

    #[must_use]
    pub fn latest_processed_at_unix_ms(&self) -> Option<u64> {
        self.snapshot.latest_processed_at_unix_ms()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.snapshot.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        AuthenticatedBoundaryEnvelope, AuthenticationKey, BoundaryAuditEvent,
        BoundaryDecisionReceipt, BoundaryEnvelope, BoundaryError, BoundaryErrorCode,
        BoundaryOperation, CorrelationId, GenerationRequest, IdempotencyKey, KeyId,
        PythonBoundaryRequest,
    };
    use eli_core::AgentTaskAnchorId;

    fn authentication_key() -> AuthenticationKey {
        AuthenticationKey::new(b"0123456789abcdef0123456789abcdef".to_vec())
            .expect("valid authentication key")
    }

    fn key_id(value: &str) -> KeyId {
        KeyId::new(value).expect("valid key ID")
    }

    fn boundary_request() -> PythonBoundaryRequest {
        PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(101),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Create image"),
        )
    }

    fn boundary_envelope(correlation_id: &str, idempotency_key: &str) -> BoundaryEnvelope {
        BoundaryEnvelope::new(
            CorrelationId::new(correlation_id),
            IdempotencyKey::new(idempotency_key),
            1_000,
            5_000,
            boundary_request(),
        )
    }

    fn accepted_event(
        correlation_id: &str,
        idempotency_key: &str,
        processed_at_unix_ms: u64,
    ) -> BoundaryAuditEvent {
        let envelope = boundary_envelope(correlation_id, idempotency_key);
        let receipt = BoundaryDecisionReceipt::from_envelope(
            &envelope,
            key_id("active-key"),
            processed_at_unix_ms,
        );

        BoundaryAuditEvent::from_parts(&receipt, &envelope.request)
    }

    fn rejected_event(
        correlation_id: &str,
        idempotency_key: &str,
        processed_at_unix_ms: u64,
    ) -> BoundaryAuditEvent {
        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope(correlation_id, idempotency_key),
            key_id("unknown-key"),
            &authentication_key(),
        )
        .expect("test envelope must be signed");

        let error = BoundaryError {
            code: BoundaryErrorCode::InvalidRequest,
            message: "boundary envelope references an unknown or unusable key ID".to_owned(),
            retryable: false,
        };

        BoundaryAuditEvent::rejected_from_authenticated(
            &authenticated,
            &error,
            processed_at_unix_ms,
        )
    }

    #[test]
    fn empty_report_has_empty_snapshot_and_no_event_views() {
        let report = BoundaryAuditReport::new(&[]);

        assert!(report.is_empty());
        assert_eq!(report.total_count(), 0);
        assert_eq!(report.accepted_count(), 0);
        assert_eq!(report.rejected_count(), 0);
        assert_eq!(report.latest_processed_at_unix_ms(), None);
        assert!(report.events().is_empty());
    }

    #[test]
    fn report_combines_snapshot_and_event_views() {
        let events = vec![
            accepted_event("corr-report-ok", "idem-report-ok", 2_000),
            rejected_event("corr-report-fail", "idem-report-fail", 2_500),
        ];

        let report = BoundaryAuditReport::new(&events);

        assert!(!report.is_empty());
        assert_eq!(report.total_count(), 2);
        assert_eq!(report.accepted_count(), 1);
        assert_eq!(report.rejected_count(), 1);
        assert_eq!(report.latest_processed_at_unix_ms(), Some(2_500));

        assert_eq!(report.events().len(), 2);
        assert_eq!(report.events()[0].kind(), "accepted");
        assert_eq!(report.events()[0].correlation_id(), "corr-report-ok");
        assert_eq!(report.events()[1].kind(), "rejected");
        assert_eq!(report.events()[1].correlation_id(), "corr-report-fail");
        assert_eq!(report.events()[1].failure_code(), Some("InvalidRequest"));
    }

    #[test]
    fn report_snapshot_accessor_matches_direct_counts() {
        let events = vec![
            accepted_event("corr-report-ok-1", "idem-report-ok-1", 2_000),
            accepted_event("corr-report-ok-2", "idem-report-ok-2", 3_000),
            rejected_event("corr-report-fail", "idem-report-fail", 2_500),
        ];

        let report = BoundaryAuditReport::new(&events);
        let snapshot = report.snapshot();

        assert_eq!(snapshot.total_count(), report.total_count());
        assert_eq!(snapshot.accepted_count(), report.accepted_count());
        assert_eq!(snapshot.rejected_count(), report.rejected_count());
        assert_eq!(
            snapshot.latest_processed_at_unix_ms(),
            report.latest_processed_at_unix_ms()
        );
    }
}
