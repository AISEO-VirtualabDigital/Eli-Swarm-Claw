use crate::authentication::{AuthenticatedBoundaryEnvelope, AuthenticationKey};
use crate::integrity::ReplayGuard;
use crate::validation::ValidateBoundary;
use crate::{BoundaryError, PythonBoundaryRequest};

/// Processes authenticated Python–Rust boundary envelopes.
///
/// Processing order:
///
/// 1. Verify cryptographic authentication.
/// 2. Validate envelope protocol, schema, and timestamps.
/// 3. Validate the enclosed boundary request.
/// 4. Check and consume the replay/idempotency key.
/// 5. Return the validated request.
///
/// Replay keys are consumed only after authentication and request validation
/// succeed.
#[derive(Debug)]
pub struct BoundaryProcessor {
    authentication_key: AuthenticationKey,
    replay_guard: ReplayGuard,
}

impl BoundaryProcessor {
    #[must_use]
    pub fn new(authentication_key: AuthenticationKey) -> Self {
        Self {
            authentication_key,
            replay_guard: ReplayGuard::new(),
        }
    }

    pub fn process(
        &mut self,
        authenticated: AuthenticatedBoundaryEnvelope,
        now_unix_ms: u64,
    ) -> Result<PythonBoundaryRequest, BoundaryError> {
        authenticated.verify(&self.authentication_key)?;

        authenticated.envelope.validate_at(now_unix_ms)?;

        authenticated.envelope.request.validate()?;

        self.replay_guard
            .accept(&authenticated.envelope, now_unix_ms)?;

        Ok(authenticated.envelope.request)
    }

    #[must_use]
    pub fn replay_guard(&self) -> &ReplayGuard {
        &self.replay_guard
    }
}
