use crate::{AuthenticationKey, AuthenticationKeyRing, KeyId};

/// Resolves authentication keys used to verify boundary envelopes.
///
/// Implementations must return only keys that are currently authorized for
/// verification. Unknown, retired, or otherwise unusable keys return `None`.
pub trait VerificationKeyStore {
    fn verification_key(&self, key_id: &KeyId) -> Option<&AuthenticationKey>;
}

/// In-memory verification-key store backed by `AuthenticationKeyRing`.
///
/// The active key and verification-only previous keys remain usable for
/// verification according to key-ring lifecycle rules.
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
    fn active_key_is_resolved() {
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
}
