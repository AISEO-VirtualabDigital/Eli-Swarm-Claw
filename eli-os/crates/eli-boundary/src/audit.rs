use crate::{
    AuthenticatedBoundaryEnvelope, BoundaryDecisionReceipt, BoundaryError, BoundaryOperation,
    BoundaryProcessingOutcome, CorrelationId, IdempotencyKey, KeyId, PythonBoundaryRequest,
};

/// Boundary-layer audit event kind.
///
/// This is an in-memory event model only. It does not persist data, emit logs,
/// write to a database, call Python, route work, or execute tasks.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum BoundaryAuditEventKind {
    Accepted,
    Rejected,
}

/// Immutable audit event describing a boundary decision.
///
/// Accepted events are derived after authentication, validation, and replay
/// protection have succeeded. Rejected events describe failed boundary attempts
/// without performing persistence, log emission, routing, or execution.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BoundaryAuditEvent {
    kind: BoundaryAuditEventKind,
    correlation_id: CorrelationId,
    idempotency_key: IdempotencyKey,
    key_id: KeyId,
    operation: BoundaryOperation,
    issued_at_unix_ms: u64,
    expires_at_unix_ms: u64,
    processed_at_unix_ms: u64,
    failure_code: Option<String>,
    failure_message: Option<String>,
}

impl BoundaryAuditEvent {
    #[must_use]
    pub fn accepted(outcome: &BoundaryProcessingOutcome) -> Self {
        let receipt = outcome.receipt();
        let request = outcome.request();

        Self::from_parts(receipt, request)
    }

    #[must_use]
    pub fn from_parts(receipt: &BoundaryDecisionReceipt, request: &PythonBoundaryRequest) -> Self {
        Self {
            kind: BoundaryAuditEventKind::Accepted,
            correlation_id: receipt.correlation_id().clone(),
            idempotency_key: receipt.idempotency_key().clone(),
            key_id: receipt.key_id().clone(),
            operation: request.operation.clone(),
            issued_at_unix_ms: receipt.issued_at_unix_ms(),
            expires_at_unix_ms: receipt.expires_at_unix_ms(),
            processed_at_unix_ms: receipt.processed_at_unix_ms(),
            failure_code: None,
            failure_message: None,
        }
    }

    #[must_use]
    pub fn rejected_from_authenticated(
        authenticated: &AuthenticatedBoundaryEnvelope,
        error: &BoundaryError,
        processed_at_unix_ms: u64,
    ) -> Self {
        Self {
            kind: BoundaryAuditEventKind::Rejected,
            correlation_id: authenticated.envelope.correlation_id.clone(),
            idempotency_key: authenticated.envelope.idempotency_key.clone(),
            key_id: authenticated.key_id.clone(),
            operation: authenticated.envelope.request.operation.clone(),
            issued_at_unix_ms: authenticated.envelope.issued_at_unix_ms,
            expires_at_unix_ms: authenticated.envelope.expires_at_unix_ms,
            processed_at_unix_ms,
            failure_code: Some(format!("{:?}", error.code)),
            failure_message: Some(error.message.clone()),
        }
    }

    #[must_use]
    pub fn kind(&self) -> &BoundaryAuditEventKind {
        &self.kind
    }

    #[must_use]
    pub fn correlation_id(&self) -> &CorrelationId {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &IdempotencyKey {
        &self.idempotency_key
    }

    #[must_use]
    pub fn key_id(&self) -> &KeyId {
        &self.key_id
    }

    #[must_use]
    pub fn operation(&self) -> &BoundaryOperation {
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
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        AuthenticatedBoundaryEnvelope, AuthenticationKey, BoundaryDecisionReceipt,
        BoundaryEnvelope, BoundaryErrorCode, BoundaryOperation, GenerationRequest,
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

    fn boundary_envelope() -> BoundaryEnvelope {
        BoundaryEnvelope::new(
            CorrelationId::new("corr-audit"),
            IdempotencyKey::new("idem-audit"),
            1_000,
            5_000,
            boundary_request(),
        )
    }

    #[test]
    fn accepted_event_captures_receipt_and_request_metadata() {
        let envelope = boundary_envelope();
        let receipt =
            BoundaryDecisionReceipt::from_envelope(&envelope, key_id("active-key"), 2_000);

        let event = BoundaryAuditEvent::from_parts(&receipt, &envelope.request);

        assert_eq!(event.kind(), &BoundaryAuditEventKind::Accepted);
        assert_eq!(event.correlation_id().as_str(), "corr-audit");
        assert_eq!(event.idempotency_key().as_str(), "idem-audit");
        assert_eq!(event.key_id().as_str(), "active-key");
        assert_eq!(event.operation(), &BoundaryOperation::GenerateImage);
        assert_eq!(event.issued_at_unix_ms(), 1_000);
        assert_eq!(event.expires_at_unix_ms(), 6_000);
        assert_eq!(event.processed_at_unix_ms(), 2_000);
        assert_eq!(event.failure_code(), None);
        assert_eq!(event.failure_message(), None);
    }

    #[test]
    fn accepted_event_can_be_created_from_processing_outcome() {
        let envelope = boundary_envelope();
        let receipt =
            BoundaryDecisionReceipt::from_envelope(&envelope, key_id("active-key"), 2_000);

        let outcome = BoundaryProcessingOutcome::accepted(envelope.request, receipt);
        let event = BoundaryAuditEvent::accepted(&outcome);

        assert_eq!(event.kind(), &BoundaryAuditEventKind::Accepted);
        assert_eq!(event.correlation_id().as_str(), "corr-audit");
        assert_eq!(event.idempotency_key().as_str(), "idem-audit");
        assert_eq!(event.key_id().as_str(), "active-key");
        assert_eq!(event.operation(), &BoundaryOperation::GenerateImage);
        assert_eq!(event.failure_code(), None);
        assert_eq!(event.failure_message(), None);
    }

    #[test]
    fn rejected_event_captures_failure_metadata() {
        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope(),
            key_id("unknown-key"),
            &authentication_key(),
        )
        .expect("test envelope must be signed");

        let error = BoundaryError {
            code: BoundaryErrorCode::InvalidRequest,
            message: "boundary envelope references an unknown or unusable key ID".to_owned(),
            retryable: false,
        };

        let event = BoundaryAuditEvent::rejected_from_authenticated(&authenticated, &error, 2_000);

        assert_eq!(event.kind(), &BoundaryAuditEventKind::Rejected);
        assert_eq!(event.correlation_id().as_str(), "corr-audit");
        assert_eq!(event.idempotency_key().as_str(), "idem-audit");
        assert_eq!(event.key_id().as_str(), "unknown-key");
        assert_eq!(event.operation(), &BoundaryOperation::GenerateImage);
        assert_eq!(event.issued_at_unix_ms(), 1_000);
        assert_eq!(event.expires_at_unix_ms(), 6_000);
        assert_eq!(event.processed_at_unix_ms(), 2_000);
        assert_eq!(event.failure_code(), Some("InvalidRequest"));
        assert_eq!(
            event.failure_message(),
            Some("boundary envelope references an unknown or unusable key ID")
        );
    }
}
