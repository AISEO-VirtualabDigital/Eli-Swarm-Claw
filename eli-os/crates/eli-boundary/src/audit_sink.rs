use crate::BoundaryAuditEvent;

/// Boundary-layer audit-event sink.
///
/// This is a recording abstraction only. It does not write to a database,
/// emit logs, call Python, route work, execute tasks, or perform transport.
pub trait BoundaryAuditSink {
    fn record(&mut self, event: BoundaryAuditEvent);
}

/// In-memory audit sink for accepted boundary events.
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
        BoundaryAuditEvent, BoundaryDecisionReceipt, BoundaryEnvelope, BoundaryOperation,
        CorrelationId, GenerationRequest, IdempotencyKey, KeyId, PythonBoundaryRequest,
    };
    use eli_core::AgentTaskAnchorId;

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

    fn audit_event() -> BoundaryAuditEvent {
        let envelope = BoundaryEnvelope::new(
            CorrelationId::new("corr-audit-sink"),
            IdempotencyKey::new("idem-audit-sink"),
            1_000,
            5_000,
            boundary_request(),
        );

        let receipt =
            BoundaryDecisionReceipt::from_envelope(&envelope, key_id("active-key"), 2_000);

        BoundaryAuditEvent::from_parts(&receipt, &envelope.request)
    }

    #[test]
    fn new_audit_sink_is_empty() {
        let sink = InMemoryBoundaryAuditSink::new();

        assert!(sink.is_empty());
        assert_eq!(sink.len(), 0);
    }

    #[test]
    fn audit_sink_records_events_in_order() {
        let mut sink = InMemoryBoundaryAuditSink::new();

        sink.record(audit_event());
        sink.record(audit_event());

        assert_eq!(sink.len(), 2);
        assert_eq!(
            sink.events()[0].correlation_id().as_str(),
            "corr-audit-sink"
        );
        assert_eq!(
            sink.events()[1].idempotency_key().as_str(),
            "idem-audit-sink"
        );
    }
}
