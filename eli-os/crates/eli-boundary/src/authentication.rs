use crate::key_rotation::KeyId;
use crate::{BoundaryEnvelope, BoundaryError, BoundaryErrorCode};
use hmac::{Hmac, Mac};
use serde::{Deserialize, Serialize};
use sha2::Sha256;
use std::fmt;

type HmacSha256 = Hmac<Sha256>;

const MINIMUM_AUTHENTICATION_KEY_BYTES: usize = 32;

#[derive(Clone)]
pub struct AuthenticationKey(Vec<u8>);

impl AuthenticationKey {
    pub fn new(key: impl Into<Vec<u8>>) -> Result<Self, BoundaryError> {
        let key = key.into();

        if key.len() < MINIMUM_AUTHENTICATION_KEY_BYTES {
            return Err(BoundaryError {
                code: BoundaryErrorCode::InvalidRequest,
                message: format!(
                    "authentication key must contain at least \
                     {MINIMUM_AUTHENTICATION_KEY_BYTES} bytes"
                ),
                retryable: false,
            });
        }

        Ok(Self(key))
    }

    fn as_bytes(&self) -> &[u8] {
        &self.0
    }
}

impl fmt::Debug for AuthenticationKey {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("AuthenticationKey")
            .field("value", &"[REDACTED]")
            .finish()
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct AuthenticatedBoundaryEnvelope {
    pub envelope: BoundaryEnvelope,
    pub key_id: KeyId,
    pub authentication_tag: String,
}

impl AuthenticatedBoundaryEnvelope {
    pub fn sign(
        envelope: BoundaryEnvelope,
        key_id: KeyId,
        key: &AuthenticationKey,
    ) -> Result<Self, BoundaryError> {
        let authentication_tag = calculate_authentication_tag(&envelope, key)?;

        Ok(Self {
            envelope,
            key_id,
            authentication_tag,
        })
    }

    pub fn verify(&self, key: &AuthenticationKey) -> Result<(), BoundaryError> {
        if self.authentication_tag.trim().is_empty() {
            return Err(authentication_failure("boundary envelope is unsigned"));
        }

        let supplied_tag = hex::decode(&self.authentication_tag).map_err(|_| {
            authentication_failure("boundary authentication tag is not valid hexadecimal")
        })?;

        let canonical_payload = canonical_envelope_bytes(&self.envelope)?;

        let mut mac = HmacSha256::new_from_slice(key.as_bytes())
            .map_err(|_| authentication_failure("authentication key could not initialize HMAC"))?;

        mac.update(&canonical_payload);

        mac.verify_slice(&supplied_tag)
            .map_err(|_| authentication_failure("boundary envelope authentication failed"))
    }
}

fn calculate_authentication_tag(
    envelope: &BoundaryEnvelope,
    key: &AuthenticationKey,
) -> Result<String, BoundaryError> {
    let canonical_payload = canonical_envelope_bytes(envelope)?;

    let mut mac = HmacSha256::new_from_slice(key.as_bytes())
        .map_err(|_| authentication_failure("authentication key could not initialize HMAC"))?;

    mac.update(&canonical_payload);

    Ok(hex::encode(mac.finalize().into_bytes()))
}

fn canonical_envelope_bytes(envelope: &BoundaryEnvelope) -> Result<Vec<u8>, BoundaryError> {
    serde_json::to_vec(envelope).map_err(|_| BoundaryError {
        code: BoundaryErrorCode::SerializationFailure,
        message: "boundary envelope could not be serialized".to_owned(),
        retryable: false,
    })
}

fn authentication_failure(message: &str) -> BoundaryError {
    BoundaryError {
        code: BoundaryErrorCode::InvalidRequest,
        message: message.to_owned(),
        retryable: false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        BoundaryOperation, CorrelationId, GenerationRequest, IdempotencyKey, PythonBoundaryRequest,
    };
    use eli_core::AgentTaskAnchorId;

    fn authentication_key() -> AuthenticationKey {
        AuthenticationKey::new(b"0123456789abcdef0123456789abcdef".to_vec())
            .expect("valid authentication key")
    }

    fn different_authentication_key() -> AuthenticationKey {
        AuthenticationKey::new(b"abcdef0123456789abcdef0123456789".to_vec())
            .expect("valid authentication key")
    }

    fn test_key_id() -> KeyId {
        KeyId::new("test-key").expect("valid test key ID")
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
            CorrelationId::new("corr-auth-001"),
            IdempotencyKey::new("idem-auth-001"),
            1_000,
            5_000,
            request,
        )
    }

    #[test]
    fn signed_envelope_verifies_with_correct_key() {
        let key = authentication_key();

        let authenticated =
            AuthenticatedBoundaryEnvelope::sign(boundary_envelope(), test_key_id(), &key)
                .expect("sign envelope");

        assert_eq!(authenticated.key_id.as_str(), "test-key");
        assert_eq!(authenticated.verify(&key), Ok(()));
    }

    #[test]
    fn modified_payload_is_rejected() {
        let key = authentication_key();

        let mut authenticated =
            AuthenticatedBoundaryEnvelope::sign(boundary_envelope(), test_key_id(), &key)
                .expect("sign envelope");

        authenticated
            .envelope
            .request
            .generation_request
            .as_mut()
            .expect("generation request")
            .prompt = "Tampered prompt".to_owned();

        let error = authenticated
            .verify(&key)
            .expect_err("tampered envelope must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
        assert!(!error.retryable);
    }

    #[test]
    fn wrong_key_is_rejected() {
        let signing_key = authentication_key();
        let verification_key = different_authentication_key();

        let authenticated =
            AuthenticatedBoundaryEnvelope::sign(boundary_envelope(), test_key_id(), &signing_key)
                .expect("sign envelope");

        let error = authenticated
            .verify(&verification_key)
            .expect_err("wrong key must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn unsigned_envelope_is_rejected() {
        let authenticated = AuthenticatedBoundaryEnvelope {
            envelope: boundary_envelope(),
            key_id: test_key_id(),
            authentication_tag: String::new(),
        };

        let error = authenticated
            .verify(&authentication_key())
            .expect_err("unsigned envelope must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn malformed_authentication_tag_is_rejected() {
        let authenticated = AuthenticatedBoundaryEnvelope {
            envelope: boundary_envelope(),
            key_id: test_key_id(),
            authentication_tag: "not-hexadecimal".to_owned(),
        };

        let error = authenticated
            .verify(&authentication_key())
            .expect_err("malformed tag must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn authentication_key_is_redacted_in_debug_output() {
        let key = authentication_key();
        let debug_output = format!("{key:?}");

        assert!(debug_output.contains("[REDACTED]"));
        assert!(!debug_output.contains("0123456789abcdef0123456789abcdef"));
    }

    #[test]
    fn short_authentication_key_is_rejected() {
        let error = AuthenticationKey::new(b"too-short".to_vec()).expect_err("short key must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }
}
