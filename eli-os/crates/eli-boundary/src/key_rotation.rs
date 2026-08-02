use crate::{AuthenticationKey, BoundaryError, BoundaryErrorCode};
use std::fmt;

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct KeyId(String);

impl KeyId {
    pub fn new(value: impl Into<String>) -> Result<Self, BoundaryError> {
        let value = value.into();

        if value.trim().is_empty() {
            return Err(invalid_key_metadata("key ID must not be empty"));
        }

        Ok(Self(value))
    }

    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AuthenticationAlgorithm {
    HmacSha256,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AuthenticationKeyStatus {
    Active,
    VerificationOnly,
    Retired,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AuthenticationKeyMetadata {
    pub key_id: KeyId,
    pub algorithm: AuthenticationAlgorithm,
    pub status: AuthenticationKeyStatus,
    pub created_at_unix_ms: u64,
    pub activated_at_unix_ms: Option<u64>,
    pub retired_at_unix_ms: Option<u64>,
}

impl AuthenticationKeyMetadata {
    pub fn active(
        key_id: KeyId,
        created_at_unix_ms: u64,
        activated_at_unix_ms: u64,
    ) -> Result<Self, BoundaryError> {
        if activated_at_unix_ms < created_at_unix_ms {
            return Err(invalid_key_metadata(
                "key activation time must not precede creation time",
            ));
        }

        Ok(Self {
            key_id,
            algorithm: AuthenticationAlgorithm::HmacSha256,
            status: AuthenticationKeyStatus::Active,
            created_at_unix_ms,
            activated_at_unix_ms: Some(activated_at_unix_ms),
            retired_at_unix_ms: None,
        })
    }

    pub fn mark_verification_only(&mut self, retired_at_unix_ms: u64) -> Result<(), BoundaryError> {
        let activated_at_unix_ms = self.activated_at_unix_ms.ok_or_else(|| {
            invalid_key_metadata("an unactivated key cannot become verification-only")
        })?;

        if retired_at_unix_ms < activated_at_unix_ms {
            return Err(invalid_key_metadata(
                "key retirement time must not precede activation time",
            ));
        }

        self.status = AuthenticationKeyStatus::VerificationOnly;
        self.retired_at_unix_ms = Some(retired_at_unix_ms);

        Ok(())
    }

    pub fn mark_retired(&mut self, retired_at_unix_ms: u64) -> Result<(), BoundaryError> {
        if retired_at_unix_ms < self.created_at_unix_ms {
            return Err(invalid_key_metadata(
                "key retirement time must not precede creation time",
            ));
        }

        self.status = AuthenticationKeyStatus::Retired;
        self.retired_at_unix_ms = Some(retired_at_unix_ms);

        Ok(())
    }

    #[must_use]
    pub fn can_sign(&self) -> bool {
        self.status == AuthenticationKeyStatus::Active
    }

    #[must_use]
    pub fn can_verify(&self) -> bool {
        matches!(
            self.status,
            AuthenticationKeyStatus::Active | AuthenticationKeyStatus::VerificationOnly
        )
    }
}

#[derive(Clone)]
pub struct ManagedAuthenticationKey {
    metadata: AuthenticationKeyMetadata,
    key: AuthenticationKey,
}

impl ManagedAuthenticationKey {
    pub fn new(
        metadata: AuthenticationKeyMetadata,
        key: AuthenticationKey,
    ) -> Result<Self, BoundaryError> {
        if metadata.status == AuthenticationKeyStatus::Retired {
            return Err(invalid_key_metadata(
                "a retired key cannot be installed as a managed key",
            ));
        }

        Ok(Self { metadata, key })
    }

    #[must_use]
    pub fn metadata(&self) -> &AuthenticationKeyMetadata {
        &self.metadata
    }

    #[must_use]
    pub fn key(&self) -> &AuthenticationKey {
        &self.key
    }

    #[must_use]
    pub fn can_sign(&self) -> bool {
        self.metadata.can_sign()
    }

    #[must_use]
    pub fn can_verify(&self) -> bool {
        self.metadata.can_verify()
    }
}

impl fmt::Debug for ManagedAuthenticationKey {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("ManagedAuthenticationKey")
            .field("metadata", &self.metadata)
            .field("key", &"[REDACTED]")
            .finish()
    }
}

#[derive(Clone, Debug)]
pub struct AuthenticationKeyRing {
    active: ManagedAuthenticationKey,
    previous: Vec<ManagedAuthenticationKey>,
}

impl AuthenticationKeyRing {
    pub fn new(active: ManagedAuthenticationKey) -> Result<Self, BoundaryError> {
        if !active.can_sign() {
            return Err(invalid_key_metadata(
                "key ring requires an active signing key",
            ));
        }

        Ok(Self {
            active,
            previous: Vec::new(),
        })
    }

    #[must_use]
    pub fn active(&self) -> &ManagedAuthenticationKey {
        &self.active
    }

    #[must_use]
    pub fn previous(&self) -> &[ManagedAuthenticationKey] {
        &self.previous
    }

    pub fn rotate(
        &mut self,
        next_active: ManagedAuthenticationKey,
        rotated_at_unix_ms: u64,
    ) -> Result<(), BoundaryError> {
        if !next_active.can_sign() {
            return Err(invalid_key_metadata(
                "replacement key must have active status",
            ));
        }

        if next_active.metadata().key_id == self.active.metadata().key_id {
            return Err(invalid_key_metadata(
                "replacement key ID must differ from the current active key ID",
            ));
        }

        let mut previous_active = self.active.clone();
        previous_active
            .metadata
            .mark_verification_only(rotated_at_unix_ms)?;

        self.previous.push(previous_active);
        self.active = next_active;

        Ok(())
    }

    #[must_use]
    pub fn verification_key(&self, key_id: &KeyId) -> Option<&AuthenticationKey> {
        if self.active.metadata().key_id == *key_id && self.active.can_verify() {
            return Some(self.active.key());
        }

        self.previous
            .iter()
            .find(|managed| managed.metadata().key_id == *key_id && managed.can_verify())
            .map(ManagedAuthenticationKey::key)
    }
}

fn invalid_key_metadata(message: &str) -> BoundaryError {
    BoundaryError {
        code: BoundaryErrorCode::InvalidRequest,
        message: message.to_owned(),
        retryable: false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn authentication_key(seed: u8) -> AuthenticationKey {
        AuthenticationKey::new(vec![seed; 32]).expect("test key must be valid")
    }

    fn managed_active_key(
        key_id: &str,
        created_at_unix_ms: u64,
        activated_at_unix_ms: u64,
        seed: u8,
    ) -> ManagedAuthenticationKey {
        let metadata = AuthenticationKeyMetadata::active(
            KeyId::new(key_id).expect("key ID must be valid"),
            created_at_unix_ms,
            activated_at_unix_ms,
        )
        .expect("metadata must be valid");

        ManagedAuthenticationKey::new(metadata, authentication_key(seed))
            .expect("managed key must be valid")
    }

    #[test]
    fn empty_key_id_is_rejected() {
        let error = KeyId::new("   ").expect_err("empty key ID must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn activation_before_creation_is_rejected() {
        let error = AuthenticationKeyMetadata::active(
            KeyId::new("key-1").expect("key ID must be valid"),
            200,
            100,
        )
        .expect_err("invalid activation time must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
    }

    #[test]
    fn active_key_can_sign_and_verify() {
        let managed = managed_active_key("key-1", 100, 100, 1);

        assert!(managed.can_sign());
        assert!(managed.can_verify());
    }

    #[test]
    fn rotation_preserves_previous_key_for_verification_only() {
        let current = managed_active_key("key-1", 100, 100, 1);
        let next = managed_active_key("key-2", 200, 200, 2);
        let previous_id = current.metadata().key_id.clone();

        let mut key_ring = AuthenticationKeyRing::new(current).expect("key ring must be valid");

        key_ring.rotate(next, 250).expect("rotation must succeed");

        assert_eq!(key_ring.active().metadata().key_id.as_str(), "key-2");
        assert_eq!(key_ring.previous().len(), 1);
        assert!(!key_ring.previous()[0].can_sign());
        assert!(key_ring.previous()[0].can_verify());
        assert!(key_ring.verification_key(&previous_id).is_some());
    }

    #[test]
    fn duplicate_rotation_key_id_is_rejected() {
        let current = managed_active_key("key-1", 100, 100, 1);
        let duplicate = managed_active_key("key-1", 200, 200, 2);

        let mut key_ring = AuthenticationKeyRing::new(current).expect("key ring must be valid");

        let error = key_ring
            .rotate(duplicate, 250)
            .expect_err("duplicate key ID must fail");

        assert_eq!(error.code, BoundaryErrorCode::InvalidRequest);
        assert!(key_ring.previous().is_empty());
    }

    #[test]
    fn managed_key_debug_output_redacts_secret() {
        let managed = managed_active_key("key-1", 100, 100, 7);
        let debug_output = format!("{managed:?}");

        assert!(debug_output.contains("[REDACTED]"));
        assert!(!debug_output.contains(&format!("{:?}", vec![7_u8; 32])));
    }
}
