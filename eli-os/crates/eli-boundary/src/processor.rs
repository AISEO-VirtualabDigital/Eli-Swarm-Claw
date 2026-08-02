use crate::validation::ValidateBoundary;
use crate::{
    AuthenticatedBoundaryEnvelope, AuthenticationKeyRing, BoundaryError, BoundaryErrorCode,
    PythonBoundaryRequest, ReplayGuard,
};

/// Processes authenticated Python–Rust boundary envelopes.
///
/// Processing order:
///
/// 1. Resolve the verification key using the envelope key ID.
/// 2. Verify cryptographic authentication.
/// 3. Validate envelope protocol, schema, and timestamps.
/// 4. Validate the enclosed boundary request.
/// 5. Check and consume the replay/idempotency key.
/// 6. Return the validated request.
///
/// Replay keys are consumed only after authentication and validation succeed.
#[derive(Debug)]
pub struct BoundaryProcessor {
    key_ring: AuthenticationKeyRing,
    replay_guard: ReplayGuard,
}

impl BoundaryProcessor {
    pub fn new(key_ring: AuthenticationKeyRing) -> Self {
        Self {
            key_ring,
            replay_guard: ReplayGuard::new(),
        }
    }

    pub fn process(
        &mut self,
        authenticated: AuthenticatedBoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<PythonBoundaryRequest, BoundaryError> {
        let verification_key = self
            .key_ring
            .verification_key(&authenticated.key_id)
            .ok_or_else(|| BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: "boundary envelope references an unknown or unusable key ID".to_owned(),
                retryable: false,
            })?;

        authenticated.verify(verification_key)?;

        authenticated.envelope.validate_at(now_unix_ms)?;

        authenticated.envelope.request.validate()?;

        self.replay_guard
            .accept(&authenticated.envelope, now_unix_ms)?;

        Ok(authenticated.envelope.request)
    }

    #[must_use]
    pub fn key_ring(&self) -> &AuthenticationKeyRing {
        &self.key_ring
    }

    #[must_use]
    pub fn replay_guard(&self) -> &ReplayGuard {
        &self.replay_guard
    }
}
