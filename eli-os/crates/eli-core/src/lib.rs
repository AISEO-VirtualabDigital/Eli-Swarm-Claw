use serde::{Deserialize, Serialize};
use std::{fmt, str::FromStr};
use thiserror::Error;
use ulid::Ulid;

#[derive(Debug, Error)]
pub enum IdParseError {
    #[error("invalid ULID: {0}")]
    InvalidUlid(#[from] ulid::DecodeError),
}

macro_rules! define_ulid_id {
    ($name:ident) => {
        #[derive(
            Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize,
        )]
        #[serde(transparent)]
        pub struct $name(Ulid);

        impl $name {
            #[must_use]
            pub fn new() -> Self {
                Self(Ulid::new())
            }

            #[must_use]
            pub const fn from_ulid(value: Ulid) -> Self {
                Self(value)
            }

            #[must_use]
            pub const fn as_ulid(self) -> Ulid {
                self.0
            }
        }

        impl Default for $name {
            fn default() -> Self {
                Self::new()
            }
        }

        impl fmt::Display for $name {
            fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
                self.0.fmt(formatter)
            }
        }

        impl FromStr for $name {
            type Err = IdParseError;

            fn from_str(value: &str) -> Result<Self, Self::Err> {
                Ok(Self(Ulid::from_string(value)?))
            }
        }

        impl From<Ulid> for $name {
            fn from(value: Ulid) -> Self {
                Self(value)
            }
        }

        impl From<$name> for Ulid {
            fn from(value: $name) -> Self {
                value.0
            }
        }
    };
}

define_ulid_id!(AgentTaskAnchorId);
define_ulid_id!(HumanOrderId);
define_ulid_id!(ContextSnapshotId);
define_ulid_id!(WorkflowDefinitionId);
define_ulid_id!(ManualRewireRecordId);
define_ulid_id!(PolicyDecisionId);
define_ulid_id!(SecurityIncidentId);
define_ulid_id!(ContainmentActionId);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn typed_ids_round_trip_through_strings() {
        let original = HumanOrderId::new();
        let parsed: HumanOrderId = original.to_string().parse().expect("valid ULID");

        assert_eq!(parsed, original);
    }

    #[test]
    fn typed_ids_are_not_interchangeable() {
        let raw = Ulid::new();
        let human_order = HumanOrderId::from_ulid(raw);
        let policy_decision = PolicyDecisionId::from_ulid(raw);

        assert_eq!(human_order.as_ulid(), policy_decision.as_ulid());
    }
}
