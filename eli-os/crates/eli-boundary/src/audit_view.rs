use crate::{BoundaryAuditEvent, BoundaryAuditEventKind};

/// Read-only projection of a boundary audit event.
///
/// This is a safe view model only. It does not persist data, emit logs,
/// expose HTTP, call Python, route work, or execute tasks.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BoundaryAuditEventView {
    kind: String,
    correlation_id: String,
    idempotency_key: String,
    key_id: String,
    operation: String,
    issued_at_unix_ms: u64,
    expires_at_unix_ms: u64,
    processed_at_unix_ms: u64,
    failure_code: Option<String>,
    failure_message: Option<String>,
}

impl BoundaryAuditEventView {
    #[must_use]
    pub fn from_event(event: &BoundaryAuditEvent) -> Self {
        Self {
            kind: match event.kind() {
                BoundaryAuditEventKind::Accepted => "accepted".to_owned(),
                BoundaryAuditEventKind::Rejected => "rejected".to_owned(),
            },
            correlation_id: event.correlation_id().as_str().to_owned(),
            idempotency_key: event.idempotency_key().as_str().to_owned(),
            key_id: event.key_id().as_str().to_owned(),
            operation: format!("{:?}", event.operation()),
            issued_at_unix_ms: event.issued_at_unix_ms(),
            expires_at_unix_ms: event.expires_at_unix_ms(),
            processed_at_unix_ms: event.processed_at_unix_ms(),
            failure_code: event.failure_code().map(str::to_owned),
            failure_message: event.failure_message().map(str::to_owned),
        }
    }

    #[must_use]
    pub fn from_events(events: &[BoundaryAuditEvent]) -> Vec<Self> {
        events.iter().map(Self::from_event).collect()
    }

    #[must_use]
    pub fn kind(&self) -> &str {
        &self.kind
    }

    #[must_use]
    pub fn correlation_id(&self) -> &str {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        &self.idempotency_key
    }

    #[must_use]
    pub fn key_id(&self) -> &str {
        &self.key_id
    }

    #[must_use]
    pub fn operation(&self) -> &str {
        &self.operation
    }

    #[must_use]
    pub fn issued_at_unix_ms(&self) -> u64 {
        self.issued_at_unix_ms
    }

    #[must_use]
    pub fn expires_at_unix_ms(&self) -> u64 {
        self.expires_at_unix_ms
    }

    #[must_use]
    pub fn processed_at_unix_ms(&self) -> u64 {
        self.processed_at_unix_ms
    }

    #[must_use]
    pub fn failure_code(&self) -> Option<&str> {
        self.failure_code.as_deref()
    }

    #[must_use]
    pub fn failure_message(&self) -> Option<&str> {
        self.failure_message.as_deref()
    }

    #[must_use]
    pub fn is_accepted(&self) -> bool {
        self.kind == "accepted"
    }

    #[must_use]
    pub fn is_rejected(&self) -> bool {
        self.kind == "rejected"
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

    fn accepted_event() -> BoundaryAuditEvent {
        let envelope = boundary_envelope("corr-view-ok", "idem-view-ok");

        let receipt =
            BoundaryDecisionReceipt::from_envelope(&envelope, key_id("active-key"), 2_000);

        BoundaryAuditEvent::from_parts(&receipt, &envelope.request)
    }

    fn rejected_event() -> BoundaryAuditEvent {
        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope("corr-view-fail", "idem-view-fail"),
            key_id("unknown-key"),
            &authentication_key(),
        )
        .expect("test envelope must be signed");

        let error = BoundaryError {
            code: BoundaryErrorCode::InvalidRequest,
            message: "boundary envelope references an unknown or unusable key ID".to_owned(),
            retryable: false,
        };

        BoundaryAuditEvent::rejected_from_authenticated(&authenticated, &error, 2_500)
    }

    #[test]
    fn accepted_event_view_exposes_read_only_fields() {
        let view = BoundaryAuditEventView::from_event(&accepted_event());

        assert_eq!(view.kind(), "accepted");
        assert!(view.is_accepted());
        assert!(!view.is_rejected());
        assert_eq!(view.correlation_id(), "corr-view-ok");
        assert_eq!(view.idempotency_key(), "idem-view-ok");
        assert_eq!(view.key_id(), "active-key");
        assert_eq!(view.operation(), "GenerateImage");
        assert_eq!(view.issued_at_unix_ms(), 1_000);
        assert_eq!(view.expires_at_unix_ms(), 6_000);
        assert_eq!(view.processed_at_unix_ms(), 2_000);
        assert_eq!(view.failure_code(), None);
        assert_eq!(view.failure_message(), None);
    }

    #[test]
    fn rejected_event_view_exposes_failure_fields() {
        let view = BoundaryAuditEventView::from_event(&rejected_event());

        assert_eq!(view.kind(), "rejected");
        assert!(!view.is_accepted());
        assert!(view.is_rejected());
        assert_eq!(view.correlation_id(), "corr-view-fail");
        assert_eq!(view.idempotency_key(), "idem-view-fail");
        assert_eq!(view.key_id(), "unknown-key");
        assert_eq!(view.operation(), "GenerateImage");
        assert_eq!(view.processed_at_unix_ms(), 2_500);
        assert_eq!(view.failure_code(), Some("InvalidRequest"));
        assert_eq!(
            view.failure_message(),
            Some("boundary envelope references an unknown or unusable key ID")
        );
    }

    #[test]
    fn event_views_can_be_created_from_event_slice() {
        let events = vec![accepted_event(), rejected_event()];
        let views = BoundaryAuditEventView::from_events(&events);

        assert_eq!(views.len(), 2);
        assert_eq!(views[0].kind(), "accepted");
        assert_eq!(views[1].kind(), "rejected");
        assert_eq!(views[0].correlation_id(), "corr-view-ok");
        assert_eq!(views[1].correlation_id(), "corr-view-fail");
    }
}
