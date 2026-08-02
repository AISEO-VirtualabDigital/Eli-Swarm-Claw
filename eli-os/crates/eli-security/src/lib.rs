use eli_core::{ContainmentActionId, SecurityIncidentId};
use eli_domain::{
    ContainmentAction, ContainmentActionType, ContainmentTarget, LegacyId, SecurityIncident,
    SecurityIncidentCategory, SecurityIncidentStatus, SecuritySeverity,
};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct SecurityAssessment {
    pub should_contain: bool,
    pub recommended_action: ContainmentActionType,
    pub reason: String,
}

#[derive(Clone, Debug, Default)]
pub struct SecurityEngine;

impl SecurityEngine {
    #[must_use]
    pub fn assess_incident(&self, incident: &SecurityIncident) -> SecurityAssessment {
        let should_contain = matches!(
            incident.severity,
            SecuritySeverity::High | SecuritySeverity::Critical
        ) || matches!(
            incident.category,
            SecurityIncidentCategory::AuthorityViolation
                | SecurityIncidentCategory::PolicyBypassAttempt
                | SecurityIncidentCategory::RogueAgentBehavior
                | SecurityIncidentCategory::DataBoundaryViolation
        );

        let recommended_action = match incident.category {
            SecurityIncidentCategory::UnauthorizedToolAccess => {
                ContainmentActionType::BlockToolAccess
            }
            SecurityIncidentCategory::RogueAgentBehavior => ContainmentActionType::SuspendAgent,
            SecurityIncidentCategory::AuthorityViolation
            | SecurityIncidentCategory::PolicyBypassAttempt => {
                ContainmentActionType::RevokeTaskAuthority
            }
            SecurityIncidentCategory::ContextTampering
            | SecurityIncidentCategory::DataBoundaryViolation => {
                ContainmentActionType::FreezeWorkflow
            }
            SecurityIncidentCategory::Unknown => ContainmentActionType::RequireHumanIntervention,
        };

        SecurityAssessment {
            should_contain,
            recommended_action,
            reason: "Security incident evaluated using fail-closed controls".to_owned(),
        }
    }

    #[must_use]
    pub fn create_containment_action(
        &self,
        incident: &SecurityIncident,
        target: ContainmentTarget,
    ) -> ContainmentAction {
        let assessment = self.assess_incident(incident);

        ContainmentAction {
            id: ContainmentActionId::new(),
            security_incident_id: incident.id,
            action_type: assessment.recommended_action,
            target,
            reason: assessment.reason,
        }
    }

    #[must_use]
    pub fn rogue_agent_incident(
        &self,
        agent_legacy_id: LegacyId,
        description: impl Into<String>,
    ) -> SecurityIncident {
        SecurityIncident {
            id: SecurityIncidentId::new(),
            category: SecurityIncidentCategory::RogueAgentBehavior,
            severity: SecuritySeverity::Critical,
            description: description.into(),
            related_agent_legacy_id: Some(agent_legacy_id),
            status: SecurityIncidentStatus::Open,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rogue_agent_incident_requires_containment() {
        let engine = SecurityEngine;
        let incident =
            engine.rogue_agent_incident(42, "Agent attempted execution outside assigned authority");

        let assessment = engine.assess_incident(&incident);

        assert!(assessment.should_contain);
        assert_eq!(
            assessment.recommended_action,
            ContainmentActionType::SuspendAgent
        );
    }

    #[test]
    fn containment_action_targets_legacy_agent() {
        let engine = SecurityEngine;
        let incident = engine.rogue_agent_incident(42, "Rogue agent behavior");

        let action =
            engine.create_containment_action(&incident, ContainmentTarget::AgentLegacyId(42));

        assert_eq!(action.security_incident_id, incident.id);
        assert_eq!(action.target, ContainmentTarget::AgentLegacyId(42));
    }

    #[test]
    fn low_severity_unknown_incident_requires_human_review() {
        let engine = SecurityEngine;
        let incident = SecurityIncident {
            id: SecurityIncidentId::new(),
            category: SecurityIncidentCategory::Unknown,
            severity: SecuritySeverity::Low,
            description: "Unclassified event".to_owned(),
            related_agent_legacy_id: None,
            status: SecurityIncidentStatus::Open,
        };

        let assessment = engine.assess_incident(&incident);

        assert!(!assessment.should_contain);
        assert_eq!(
            assessment.recommended_action,
            ContainmentActionType::RequireHumanIntervention
        );
    }
}
