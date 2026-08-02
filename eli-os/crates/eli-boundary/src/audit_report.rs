use crate::{BoundaryAuditEvent, BoundaryAuditEventView, BoundaryAuditSnapshot};

/// Read-only verdict for a boundary audit report.
///
/// This is an in-memory classification only. It does not persist data,
/// emit logs, expose HTTP, call Python, route work, or execute tasks.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum BoundaryAuditReportVerdict {
    Empty,
    AcceptedOnly,
    ContainsRejections,
}

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
    pub fn accepted_events(&self) -> Vec<&BoundaryAuditEventView> {
        self.events
            .iter()
            .filter(|event| event.is_accepted())
            .collect()
    }

    #[must_use]
    pub fn rejected_events(&self) -> Vec<&BoundaryAuditEventView> {
        self.events
            .iter()
            .filter(|event| event.is_rejected())
            .collect()
    }

    #[must_use]
    pub fn latest_event(&self) -> Option<&BoundaryAuditEventView> {
        self.events
            .iter()
            .max_by_key(|event| event.processed_at_unix_ms())
    }

    #[must_use]
    pub fn has_accepted_events(&self) -> bool {
        self.accepted_count() > 0
    }

    #[must_use]
    pub fn has_rejected_events(&self) -> bool {
        self.rejected_count() > 0
    }

    #[must_use]
    pub fn verdict(&self) -> BoundaryAuditReportVerdict {
        if self.is_empty() {
            BoundaryAuditReportVerdict::Empty
        } else if self.has_rejected_events() {
            BoundaryAuditReportVerdict::ContainsRejections
        } else {
            BoundaryAuditReportVerdict::AcceptedOnly
        }
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
        assert!(report.accepted_events().is_empty());
        assert!(report.rejected_events().is_empty());
        assert!(report.latest_event().is_none());
        assert!(!report.has_accepted_events());
        assert!(!report.has_rejected_events());
        assert_eq!(report.verdict(), BoundaryAuditReportVerdict::Empty);
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

    #[test]
    fn report_returns_only_accepted_event_views() {
        let events = vec![
            accepted_event("corr-report-ok-1", "idem-report-ok-1", 2_000),
            rejected_event("corr-report-fail", "idem-report-fail", 2_500),
            accepted_event("corr-report-ok-2", "idem-report-ok-2", 3_000),
        ];

        let report = BoundaryAuditReport::new(&events);
        let accepted_events = report.accepted_events();

        assert_eq!(accepted_events.len(), 2);
        assert_eq!(accepted_events[0].kind(), "accepted");
        assert_eq!(accepted_events[0].correlation_id(), "corr-report-ok-1");
        assert_eq!(accepted_events[1].kind(), "accepted");
        assert_eq!(accepted_events[1].correlation_id(), "corr-report-ok-2");
    }

    #[test]
    fn report_returns_only_rejected_event_views() {
        let events = vec![
            accepted_event("corr-report-ok", "idem-report-ok", 2_000),
            rejected_event("corr-report-fail-1", "idem-report-fail-1", 2_500),
            rejected_event("corr-report-fail-2", "idem-report-fail-2", 3_000),
        ];

        let report = BoundaryAuditReport::new(&events);
        let rejected_events = report.rejected_events();

        assert_eq!(rejected_events.len(), 2);
        assert_eq!(rejected_events[0].kind(), "rejected");
        assert_eq!(rejected_events[0].correlation_id(), "corr-report-fail-1");
        assert_eq!(rejected_events[1].kind(), "rejected");
        assert_eq!(rejected_events[1].correlation_id(), "corr-report-fail-2");
    }

    #[test]
    fn report_latest_event_uses_latest_processed_timestamp() {
        let events = vec![
            accepted_event("corr-report-ok-1", "idem-report-ok-1", 4_000),
            rejected_event("corr-report-fail", "idem-report-fail", 2_000),
            accepted_event("corr-report-ok-2", "idem-report-ok-2", 3_000),
        ];

        let report = BoundaryAuditReport::new(&events);
        let latest = report.latest_event().expect("latest event must exist");

        assert_eq!(latest.correlation_id(), "corr-report-ok-1");
        assert_eq!(latest.processed_at_unix_ms(), 4_000);
    }

    #[test]
    fn report_verdict_is_accepted_only_when_no_rejections_exist() {
        let events = vec![
            accepted_event("corr-report-ok-1", "idem-report-ok-1", 2_000),
            accepted_event("corr-report-ok-2", "idem-report-ok-2", 3_000),
        ];

        let report = BoundaryAuditReport::new(&events);

        assert!(report.has_accepted_events());
        assert!(!report.has_rejected_events());
        assert_eq!(report.verdict(), BoundaryAuditReportVerdict::AcceptedOnly);
    }

    #[test]
    fn report_verdict_detects_rejections() {
        let events = vec![
            accepted_event("corr-report-ok", "idem-report-ok", 2_000),
            rejected_event("corr-report-fail", "idem-report-fail", 2_500),
        ];

        let report = BoundaryAuditReport::new(&events);

        assert!(report.has_accepted_events());
        assert!(report.has_rejected_events());
        assert_eq!(
            report.verdict(),
            BoundaryAuditReportVerdict::ContainsRejections
        );
    }
}
