use crate::{
    AuthenticatedBoundaryEnvelope, BoundaryEnvelope, CorrelationId, IdempotencyKey, KeyId,
};

/// Immutable summary of an accepted boundary-processing decision.
///
/// This is a boundary-layer receipt only. It does not persist data, execute
/// work, route tasks, call Python, or authorize runtime actions.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BoundaryDecisionReceipt {
    correlation_id: CorrelationId,
    idempotency_key: IdempotencyKey,
    key_id: KeyId,
    issued_at_unix_ms: u64,
    expires_at_unix_ms: u64,
    processed_at_unix_ms: u64,
}

impl BoundaryDecisionReceipt {
    #[must_use]
    pub fn accepted(
        authenticated: &AuthenticatedBoundaryEnvelope,
        processed_at_unix_ms: u64,
    ) -> Self {
        Self {
            correlation_id: authenticated.envelope.correlation_id.clone(),
            idempotency_key: authenticated.envelope.idempotency_key.clone(),
            key_id: authenticated.key_id.clone(),
            issued_at_unix_ms: authenticated.envelope.issued_at_unix_ms,
            expires_at_unix_ms: authenticated.envelope.expires_at_unix_ms,
            processed_at_unix_ms,
        }
    }

    #[must_use]
    pub fn from_envelope(
        envelope: &BoundaryEnvelope,
        key_id: KeyId,
        processed_at_unix_ms: u64,
    ) -> Self {
        Self {
            correlation_id: envelope.correlation_id.clone(),
            idempotency_key: envelope.idempotency_key.clone(),
            key_id,
            issued_at_unix_ms: envelope.issued_at_unix_ms,
            expires_at_unix_ms: envelope.expires_at_unix_ms,
            processed_at_unix_ms,
        }
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
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        AuthenticatedBoundaryEnvelope, AuthenticationKey, BoundaryOperation, GenerationRequest,
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

    fn boundary_envelope() -> BoundaryEnvelope {
        let request = PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(101),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Create image"),
        );

        BoundaryEnvelope::new(
            CorrelationId::new("corr-decision"),
            IdempotencyKey::new("idem-decision"),
            1_000,
            5_000,
            request,
        )
    }

    #[test]
    fn accepted_receipt_captures_authenticated_envelope_metadata() {
        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope(),
            key_id("active-key"),
            &authentication_key(),
        )
        .expect("envelope must be signed");

        let receipt = BoundaryDecisionReceipt::accepted(&authenticated, 2_000);

        assert_eq!(receipt.correlation_id().as_str(), "corr-decision");
        assert_eq!(receipt.idempotency_key().as_str(), "idem-decision");
        assert_eq!(receipt.key_id().as_str(), "active-key");
        assert_eq!(receipt.issued_at_unix_ms(), 1_000);
        assert_eq!(receipt.expires_at_unix_ms(), 6_000);
        assert_eq!(receipt.processed_at_unix_ms(), 2_000);
    }

    #[test]
    fn receipt_can_be_created_from_plain_envelope_and_key_id() {
        let envelope = boundary_envelope();

        let receipt =
            BoundaryDecisionReceipt::from_envelope(&envelope, key_id("manual-key"), 2_500);

        assert_eq!(receipt.correlation_id().as_str(), "corr-decision");
        assert_eq!(receipt.idempotency_key().as_str(), "idem-decision");
        assert_eq!(receipt.key_id().as_str(), "manual-key");
        assert_eq!(receipt.processed_at_unix_ms(), 2_500);
    }
}
