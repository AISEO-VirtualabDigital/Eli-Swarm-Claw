use crate::{BoundaryEnvelope, BoundaryError, ReplayGuard};

/// Storage contract for atomic replay and idempotency protection.
///
/// Implementations must reject an already-consumed idempotency key and consume
/// a new key only after the envelope passes integrity validation.
pub trait ReplayStore {
    fn check_and_consume(
        &mut self,
        envelope: &BoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<(), BoundaryError>;

    fn len(&self) -> usize;

    fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

/// Current in-memory replay-store implementation.
///
/// This preserves `ReplayGuard` behavior while allowing a persistent or
/// distributed implementation to be introduced later.
#[derive(Debug)]
pub struct InMemoryReplayStore {
    guard: ReplayGuard,
}

impl InMemoryReplayStore {
    #[must_use]
    pub fn new() -> Self {
        Self {
            guard: ReplayGuard::new(),
        }
    }

    #[must_use]
    pub fn guard(&self) -> &ReplayGuard {
        &self.guard
    }
}

impl Default for InMemoryReplayStore {
    fn default() -> Self {
        Self::new()
    }
}

impl ReplayStore for InMemoryReplayStore {
    fn check_and_consume(
        &mut self,
        envelope: &BoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<(), BoundaryError> {
        self.guard.accept(envelope, now_unix_ms)
    }

    fn len(&self) -> usize {
        self.guard.len()
    }

    fn is_empty(&self) -> bool {
        self.guard.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        BoundaryOperation, CorrelationId, GenerationRequest, IdempotencyKey, PythonBoundaryRequest,
    };
    use eli_core::AgentTaskAnchorId;

    fn envelope(idempotency_key: &str) -> BoundaryEnvelope {
        let request = PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(101),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Create image"),
        );

        BoundaryEnvelope::new(
            CorrelationId::new("corr-replay-store"),
            IdempotencyKey::new(idempotency_key),
            1_000,
            5_000,
            request,
        )
    }

    #[test]
    fn new_store_is_empty() {
        let store = InMemoryReplayStore::new();

        assert!(store.is_empty());
        assert_eq!(store.len(), 0);
    }

    #[test]
    fn valid_envelope_is_consumed_once() {
        let mut store = InMemoryReplayStore::new();
        let envelope = envelope("idem-replay-store");

        store
            .check_and_consume(&envelope, 2_000)
            .expect("first consumption must succeed");

        assert_eq!(store.len(), 1);

        let error = store
            .check_and_consume(&envelope, 2_000)
            .expect_err("duplicate consumption must fail");

        assert!(!error.retryable);
        assert_eq!(store.len(), 1);
    }

    #[test]
    fn invalid_envelope_does_not_consume_key() {
        let mut store = InMemoryReplayStore::new();
        let envelope = envelope("idem-expired");

        store
            .check_and_consume(&envelope, 10_000)
            .expect_err("expired envelope must fail");

        assert!(store.is_empty());
    }
}
