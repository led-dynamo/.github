use serde::{Deserialize, Serialize};
use std::cmp::Ordering;

/// A deterministic logical version. Higher counters win; actor is the stable tie-breaker.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct Version {
    pub counter: u64,
    pub actor: String,
}

impl Version {
    #[must_use]
    pub fn new(counter: u64, actor: impl Into<String>) -> Self {
        Self {
            counter,
            actor: actor.into(),
        }
    }
}

/// State paired with the logical version that produced it.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct VersionedState<T> {
    pub version: Version,
    pub value: T,
}

impl<T> VersionedState<T> {
    #[must_use]
    pub fn new(version: Version, value: T) -> Self {
        Self { version, value }
    }
}

/// The deterministic action a caller should take after comparing local and remote state.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ReconcileDecision {
    KeepLocal,
    AcceptRemote,
    Equivalent,
    Conflict,
}

/// Compare two snapshots without performing transport or persistence side effects.
#[must_use]
pub fn reconcile<T: PartialEq>(
    local: &VersionedState<T>,
    remote: &VersionedState<T>,
) -> ReconcileDecision {
    match local.version.cmp(&remote.version) {
        Ordering::Greater => ReconcileDecision::KeepLocal,
        Ordering::Less => ReconcileDecision::AcceptRemote,
        Ordering::Equal if local.value == remote.value => ReconcileDecision::Equivalent,
        Ordering::Equal => ReconcileDecision::Conflict,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn newer_remote_state_is_accepted() {
        let local = VersionedState::new(Version::new(4, "api-a"), "old");
        let remote = VersionedState::new(Version::new(5, "api-b"), "new");

        assert_eq!(reconcile(&local, &remote), ReconcileDecision::AcceptRemote);
    }

    #[test]
    fn actor_is_a_deterministic_tie_breaker() {
        let local = VersionedState::new(Version::new(7, "device-a"), "left");
        let remote = VersionedState::new(Version::new(7, "device-b"), "right");

        assert_eq!(reconcile(&local, &remote), ReconcileDecision::AcceptRemote);
    }

    #[test]
    fn identical_version_and_value_are_equivalent() {
        let local = VersionedState::new(Version::new(8, "web"), "same");
        let remote = local.clone();

        assert_eq!(reconcile(&local, &remote), ReconcileDecision::Equivalent);
    }

    #[test]
    fn identical_version_with_different_values_is_a_conflict() {
        let local = VersionedState::new(Version::new(9, "api"), "left");
        let remote = VersionedState::new(Version::new(9, "api"), "right");

        assert_eq!(reconcile(&local, &remote), ReconcileDecision::Conflict);
    }
}
