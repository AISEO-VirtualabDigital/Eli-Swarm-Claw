use crate::{AuthenticationKey, AuthenticationKeyRing, KeyId};

/// Resolves authentication keys authorized to verify boundary envelopes.
///
/// Implementations must return only active or verification-only keys.
/// Unknown, retired, or otherwise unusable keys return `None`.
pub trait VerificationKeyStore {
    fn verification_key(&self, key_id: &KeyId) -> Option<&AuthenticationKey>;
}

/// Resolves the currently active authentication signing key.
///
/// Implementations must never return retired or verification-only keys for
/// signing. Returning `None` causes signing to fail closed.
pub trait SigningKeyStore {
    fn active_signing_key(&self) -> Option<(&KeyId, &AuthenticationKey)>;
}

/// In-memory authentication-key store backed by `AuthenticationKeyRing`.
///
/// The active key may sign and verify. Previous verification-only keys may
/// verify but cannot sign.
#[derive(Clone, Debug)]
pub struct InMemoryVerificationKeyStore {
    key_ring: AuthenticationKeyRing,
}

impl InMemoryVerificationKeyStore {
    #[must_use]
    pub fn new(key_ring: AuthenticationKeyRing) -> Self {
        Self { key_ring }
    }

    #[must_use]
    pub fn key_ring(&self) -> &AuthenticationKeyRing {
        &self.key_ring
    }

    #[must_use]
    pub fn key_ring_mut(&mut self) -> &mut AuthenticationKeyRing {
        &mut self.key_ring
    }
}

impl VerificationKeyStore for InMemoryVerificationKeyStore {
    fn verification_key(&self, key_id: &KeyId) -> Option<&AuthenticationKey> {
        self.key_ring.verification_key(key_id)
    }
}

impl SigningKeyStore for InMemoryVerificationKeyStore {
    fn active_signing_key(&self) -> Option<(&KeyId, &AuthenticationKey)> {
        let active = self.key_ring.active();

        if !active.can_sign() {
            return None;
        }

        Some((&active.metadata().key_id, active.key()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{AuthenticationKeyMetadata, ManagedAuthenticationKey};

    fn authentication_key(seed: u8) -> AuthenticationKey {
        AuthenticationKey::new(vec![seed; 32]).expect("test authentication key must be valid")
    }

    fn key_id(value: &str) -> KeyId {
        KeyId::new(value).expect("test key ID must be valid")
    }

    fn managed_active_key(
        key_id_value: &str,
        seed: u8,
        created_at_unix_ms: u64,
        activated_at_unix_ms: u64,
    ) -> ManagedAuthenticationKey {
        let metadata = AuthenticationKeyMetadata::active(
            key_id(key_id_value),
            created_at_unix_ms,
            activated_at_unix_ms,
        )
        .expect("active key metadata must be valid");

        ManagedAuthenticationKey::new(metadata, authentication_key(seed))
            .expect("managed authentication key must be valid")
    }

    #[test]
    fn active_key_is_resolved_for_verification() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 100, 100))
            .expect("key ring must be valid");

        let store = InMemoryVerificationKeyStore::new(ring);

        assert!(store.verification_key(&key_id("active-key")).is_some());
    }

    #[test]
    fn previous_key_is_resolved_after_rotation() {
        let current = managed_active_key("previous-key", 1, 100, 100);
        let next = managed_active_key("active-key", 2, 200, 200);

        let mut ring = AuthenticationKeyRing::new(current).expect("key ring must be valid");

        ring.rotate(next, 200).expect("key rotation must succeed");

        let store = InMemoryVerificationKeyStore::new(ring);

        assert!(store.verification_key(&key_id("previous-key")).is_some());
        assert!(store.verification_key(&key_id("active-key")).is_some());
    }

    #[test]
    fn unknown_key_is_not_resolved() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 100, 100))
            .expect("key ring must be valid");

        let store = InMemoryVerificationKeyStore::new(ring);

        assert!(store.verification_key(&key_id("unknown-key")).is_none());
    }

    #[test]
    fn active_key_is_resolved_for_signing() {
        let ring = AuthenticationKeyRing::new(managed_active_key("active-key", 1, 100, 100))
            .expect("key ring must be valid");

        let store = InMemoryVerificationKeyStore::new(ring);

        let (resolved_id, _) = store
            .active_signing_key()
            .expect("active signing key must be available");

        assert_eq!(resolved_id.as_str(), "active-key");
    }

    #[test]
    fn rotation_changes_the_active_signing_key() {
        let current = managed_active_key("previous-key", 1, 100, 100);
        let next = managed_active_key("active-key", 2, 200, 200);

        let mut ring = AuthenticationKeyRing::new(current).expect("key ring must be valid");

        ring.rotate(next, 200).expect("key rotation must succeed");

        let store = InMemoryVerificationKeyStore::new(ring);

        let (resolved_id, _) = store
            .active_signing_key()
            .expect("rotated active signing key must be available");

        assert_eq!(resolved_id.as_str(), "active-key");
        assert!(store.verification_key(&key_id("previous-key")).is_some());
    }
}
