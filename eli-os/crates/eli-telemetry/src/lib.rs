use eli_core::{
    AgentTaskAnchorId, ContainmentActionId, HumanOrderId, PolicyDecisionId, SecurityIncidentId,
    WorkflowDefinitionId,
};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct TelemetryEvent {
    pub sequence: u64,
    pub category: TelemetryCategory,
    pub message: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum TelemetryCategory {
    HumanOrder(HumanOrderId),
    AgentTask(AgentTaskAnchorId),
    Workflow(WorkflowDefinitionId),
    PolicyDecision(PolicyDecisionId),
    SecurityIncident(SecurityIncidentId),
    ContainmentAction(ContainmentActionId),
    System,
}

#[derive(Clone, Debug, Default)]
pub struct TelemetryRecorder {
    events: Vec<TelemetryEvent>,
    next_sequence: u64,
}

impl TelemetryRecorder {
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    pub fn record(&mut self, category: TelemetryCategory, message: impl Into<String>) -> u64 {
        let sequence = self.next_sequence;
        self.next_sequence = self.next_sequence.saturating_add(1);

        self.events.push(TelemetryEvent {
            sequence,
            category,
            message: message.into(),
        });

        sequence
    }

    #[must_use]
    pub fn events(&self) -> &[TelemetryEvent] {
        &self.events
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.events.len()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.events.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn telemetry_sequences_are_monotonic() {
        let mut recorder = TelemetryRecorder::new();

        let first = recorder.record(TelemetryCategory::System, "Control plane started");
        let second = recorder.record(
            TelemetryCategory::HumanOrder(HumanOrderId::new()),
            "Human order received",
        );

        assert_eq!(first, 0);
        assert_eq!(second, 1);
        assert_eq!(recorder.len(), 2);
    }

    #[test]
    fn telemetry_preserves_typed_event_references() {
        let mut recorder = TelemetryRecorder::new();
        let incident_id = SecurityIncidentId::new();

        recorder.record(
            TelemetryCategory::SecurityIncident(incident_id),
            "Security incident opened",
        );

        assert_eq!(
            recorder.events()[0].category,
            TelemetryCategory::SecurityIncident(incident_id)
        );
    }

    #[test]
    fn new_recorder_is_empty() {
        let recorder = TelemetryRecorder::new();

        assert!(recorder.is_empty());
    }
}
