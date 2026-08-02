use crate::{BoundaryAuditEvent, BoundaryAuditEventKind, BoundaryAuditReport};

/// Boundary-layer audit-event sink.
///
/// This is a recording abstraction only. It does not write to a database,
/// emit logs, call Python, route work, execute tasks, or perform transport.
pub trait BoundaryAuditSink {
    fn record(&mut self, event: BoundaryAuditEvent);
}

/// Read-only summary of audit events currently held by an audit sink.
///
/// This is an in-memory reporting primitive only. It does not persist data,
/// emit telemetry, write logs, or expose a transport API.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BoundaryAuditSnapshot {
    total_count: usize,
    accepted_count: usize,
    rejected_count: usize,
    latest_processed_at_unix_ms: Option<u64>,
}

impl BoundaryAuditSnapshot {
    #[must_use]
    pub fn new(events: &[BoundaryAuditEvent]) -> Self {
        let mut accepted_count = 0;
        let mut rejected_count = 0;
        let mut latest_processed_at_unix_ms: Option<u64> = None;

        for event in events {
            match event.kind() {
                BoundaryAuditEventKind::Accepted => accepted_count += 1,
                BoundaryAuditEventKind::Rejected => rejected_count += 1,
            }

            latest_processed_at_unix_ms = Some(
                latest_processed_at_unix_ms.map_or(event.processed_at_unix_ms(), |latest| {
                    latest.max(event.processed_at_unix_ms())
                }),
            );
        }

        Self {
            total_count: events.len(),
            accepted_count,
            rejected_count,
            latest_processed_at_unix_ms,
        }
    }

    #[must_use]
    pub fn total_count(&self) -> usize {
        self.total_count
    }

    #[must_use]
    pub fn accepted_count(&self) -> usize {
        self.accepted_count
    }

    #[must_use]
    pub fn rejected_count(&self) -> usize {
        self.rejected_count
    }

    #[must_use]
    pub fn latest_processed_at_unix_ms(&self) -> Option<u64> {
        self.latest_processed_at_unix_ms
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.total_count == 0
    }
}

/// In-memory audit sink for accepted and rejected boundary events.
///
/// This preserves audit events for local inspection and test coverage while
/// keeping persistence, log emission, and external telemetry out of scope.
#[derive(Clone, Debug, Default)]
pub struct InMemoryBoundaryAuditSink {
    events: Vec<BoundaryAuditEvent>,
}

impl InMemoryBoundaryAuditSink {
    #[must_use]
    pub fn new() -> Self {
        Self { events: Vec::new() }
    }

    #[must_use]
    pub fn events(&self) -> &[BoundaryAuditEvent] {
        &self.events
    }

    #[must_use]
    pub fn accepted_events(&self) -> Vec<&BoundaryAuditEvent> {
        self.events
            .iter()
            .filter(|event| event.kind() == &BoundaryAuditEventKind::Accepted)
            .collect()
    }

    #[must_use]
    pub fn rejected_events(&self) -> Vec<&BoundaryAuditEvent> {
        self.events
            .iter()
            .filter(|event| event.kind() == &BoundaryAuditEventKind::Rejected)
            .collect()
    }

    #[must_use]
    pub fn latest_event(&self) -> Option<&BoundaryAuditEvent> {
        self.events
            .iter()
            .max_by_key(|event| event.processed_at_unix_ms())
    }

    #[must_use]
    pub fn snapshot(&self) -> BoundaryAuditSnapshot {
        BoundaryAuditSnapshot::new(&self.events)
    }

    #[must_use]
    pub fn report(&self) -> BoundaryAuditReport {
        BoundaryAuditReport::new(&self.events)
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.events.len()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.events.is_empty()
    }
}

impl BoundaryAuditSink for InMemoryBoundaryAuditSink {
    fn record(&mut self, event: BoundaryAuditEvent) {
        self.events.push(event);
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

    fn accepted_audit_event(
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

    fn rejected_audit_event(
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
    fn new_audit_sink_is_empty() {
        let sink = InMemoryBoundaryAuditSink::new();

        assert!(sink.is_empty());
        assert_eq!(sink.len(), 0);
        assert!(sink.snapshot().is_empty());
        assert!(sink.report().is_empty());
        assert!(sink.accepted_events().is_empty());
        assert!(sink.rejected_events().is_empty());
        assert!(sink.latest_event().is_none());
    }

    #[test]
    fn audit_sink_records_events_in_order() {
        let mut sink = InMemoryBoundaryAuditSink::new();

        sink.record(accepted_audit_event(
            "corr-audit-sink",
            "idem-audit-sink",
            2_000,
        ));
        sink.record(accepted_audit_event(
            "corr-audit-sink-2",
            "idem-audit-sink-2",
            2_500,
        ));

        assert_eq!(sink.len(), 2);
        assert_eq!(
            sink.events()[0].correlation_id().as_str(),
            "corr-audit-sink"
        );
        assert_eq!(
            sink.events()[1].idempotency_key().as_str(),
            "idem-audit-sink-2"
        );
    }

    #[test]
    fn snapshot_reports_empty_sink() {
        let sink = InMemoryBoundaryAuditSink::new();
        let snapshot = sink.snapshot();

        assert!(snapshot.is_empty());
        assert_eq!(snapshot.total_count(), 0);
        assert_eq!(snapshot.accepted_count(), 0);
        assert_eq!(snapshot.rejected_count(), 0);
        assert_eq!(snapshot.latest_processed_at_unix_ms(), None);
    }

    #[test]
    fn report_projects_snapshot_and_event_views() {
        let mut sink = InMemoryBoundaryAuditSink::new();

        sink.record(accepted_audit_event("corr-ok-1", "idem-ok-1", 2_000));
        sink.record(rejected_audit_event("corr-fail-1", "idem-fail-1", 2_500));

        let report = sink.report();

        assert_eq!(report.total_count(), 2);
        assert_eq!(report.accepted_count(), 1);
        assert_eq!(report.rejected_count(), 1);
        assert_eq!(report.latest_processed_at_unix_ms(), Some(2_500));
        assert_eq!(report.events().len(), 2);
        assert_eq!(report.events()[0].kind(), "accepted");
        assert_eq!(report.events()[1].kind(), "rejected");
    }

    #[test]
    fn snapshot_counts_accepted_and_rejected_events() {
        let mut sink = InMemoryBoundaryAuditSink::new();

        sink.record(accepted_audit_event("corr-ok-1", "idem-ok-1", 2_000));
        sink.record(rejected_audit_event("corr-fail-1", "idem-fail-1", 2_500));
        sink.record(accepted_audit_event("corr-ok-2", "idem-ok-2", 3_000));

        let snapshot = sink.snapshot();

        assert!(!snapshot.is_empty());
        assert_eq!(snapshot.total_count(), 3);
        assert_eq!(snapshot.accepted_count(), 2);
        assert_eq!(snapshot.rejected_count(), 1);
        assert_eq!(snapshot.latest_processed_at_unix_ms(), Some(3_000));
    }

    #[test]
    fn snapshot_uses_latest_processed_timestamp_regardless_of_order() {
        let mut sink = InMemoryBoundaryAuditSink::new();

        sink.record(accepted_audit_event("corr-ok-1", "idem-ok-1", 4_000));
        sink.record(rejected_audit_event("corr-fail-1", "idem-fail-1", 2_000));
        sink.record(accepted_audit_event("corr-ok-2", "idem-ok-2", 3_000));

        let snapshot = sink.snapshot();

        assert_eq!(snapshot.total_count(), 3);
        assert_eq!(snapshot.latest_processed_at_unix_ms(), Some(4_000));
    }

    #[test]
    fn accepted_events_returns_only_accepted_events() {
        let mut sink = InMemoryBoundaryAuditSink::new();

        sink.record(accepted_audit_event("corr-ok-1", "idem-ok-1", 2_000));
        sink.record(rejected_audit_event("corr-fail-1", "idem-fail-1", 2_500));
        sink.record(accepted_audit_event("corr-ok-2", "idem-ok-2", 3_000));

        let accepted_events = sink.accepted_events();

        assert_eq!(accepted_events.len(), 2);
        assert_eq!(accepted_events[0].correlation_id().as_str(), "corr-ok-1");
        assert_eq!(accepted_events[1].correlation_id().as_str(), "corr-ok-2");
    }

    #[test]
    fn rejected_events_returns_only_rejected_events() {
        let mut sink = InMemoryBoundaryAuditSink::new();

        sink.record(accepted_audit_event("corr-ok-1", "idem-ok-1", 2_000));
        sink.record(rejected_audit_event("corr-fail-1", "idem-fail-1", 2_500));
        sink.record(rejected_audit_event("corr-fail-2", "idem-fail-2", 3_000));

        let rejected_events = sink.rejected_events();

        assert_eq!(rejected_events.len(), 2);
        assert_eq!(rejected_events[0].correlation_id().as_str(), "corr-fail-1");
        assert_eq!(rejected_events[1].correlation_id().as_str(), "corr-fail-2");
    }

    #[test]
    fn latest_event_returns_event_with_latest_processed_timestamp() {
        let mut sink = InMemoryBoundaryAuditSink::new();

        sink.record(accepted_audit_event("corr-ok-1", "idem-ok-1", 4_000));
        sink.record(rejected_audit_event("corr-fail-1", "idem-fail-1", 2_000));
        sink.record(accepted_audit_event("corr-ok-2", "idem-ok-2", 3_000));

        let latest = sink.latest_event().expect("latest event must exist");

        assert_eq!(latest.correlation_id().as_str(), "corr-ok-1");
        assert_eq!(latest.processed_at_unix_ms(), 4_000);
    }
}
