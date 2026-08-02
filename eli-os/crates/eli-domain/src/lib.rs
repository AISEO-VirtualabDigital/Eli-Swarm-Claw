use eli_core::{
    AgentTaskAnchorId, ContainmentActionId, ContextSnapshotId, HumanOrderId,
    ManualRewireRecordId, PolicyDecisionId, SecurityIncidentId, WorkflowDefinitionId,
};
use serde::{Deserialize, Serialize};

pub type LegacyId = i64;

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct AgentTaskAnchor {
    pub id: AgentTaskAnchorId,
    pub agent_legacy_id: LegacyId,
    pub human_order_id: HumanOrderId,
    pub context_snapshot_id: ContextSnapshotId,
    pub objective: String,
    pub status: AgentTaskAnchorStatus,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum AgentTaskAnchorStatus {
    Pending,
    Active,
    Completed,
    Cancelled,
    Contained,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct HumanOrder {
    pub id: HumanOrderId,
    pub issued_by: HumanAuthority,
    pub instruction: String,
    pub priority: HumanOrderPriority,
    pub status: HumanOrderStatus,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct HumanAuthority {
    pub subject: String,
    pub authority_level: AuthorityLevel,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum AuthorityLevel {
    HumanAbsolute,
    ObsidianRelay,
    AgentTaskBound,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum HumanOrderPriority {
    Normal,
    High,
    Critical,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum HumanOrderStatus {
    Issued,
    Accepted,
    InProgress,
    Completed,
    Rejected,
    Cancelled,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct ContextSnapshot {
    pub id: ContextSnapshotId,
    pub source: ContextSource,
    pub payload: String,
    pub immutable: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum ContextSource {
    Human,
    Obsidian,
    Agent,
    System,
    LegacyApplication,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct WorkflowDefinition {
    pub id: WorkflowDefinitionId,
    pub name: String,
    pub version: u32,
    pub steps: Vec<WorkflowStep>,
    pub enabled: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct WorkflowStep {
    pub position: u32,
    pub name: String,
    pub executor: WorkflowExecutor,
    pub requires_human_approval: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum WorkflowExecutor {
    RustControlPlane,
    PythonApplication,
    Human,
    ExternalProvider,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct ManualRewireRecord {
    pub id: ManualRewireRecordId,
    pub workflow_definition_id: WorkflowDefinitionId,
    pub performed_by: HumanAuthority,
    pub reason: String,
    pub previous_version: u32,
    pub new_version: u32,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct PolicyDecision {
    pub id: PolicyDecisionId,
    pub subject: PolicySubject,
    pub outcome: PolicyOutcome,
    pub reason: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum PolicySubject {
    HumanOrder(HumanOrderId),
    AgentTaskAnchor(AgentTaskAnchorId),
    WorkflowDefinition(WorkflowDefinitionId),
    LegacyEntity(LegacyId),
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum PolicyOutcome {
    Allow,
    Deny,
    RequireHumanApproval,
    Contain,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct SecurityIncident {
    pub id: SecurityIncidentId,
    pub category: SecurityIncidentCategory,
    pub severity: SecuritySeverity,
    pub description: String,
    pub related_agent_legacy_id: Option<LegacyId>,
    pub status: SecurityIncidentStatus,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum SecurityIncidentCategory {
    AuthorityViolation,
    PolicyBypassAttempt,
    UnauthorizedToolAccess,
    ContextTampering,
    RogueAgentBehavior,
    DataBoundaryViolation,
    Unknown,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum SecuritySeverity {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum SecurityIncidentStatus {
    Open,
    Investigating,
    Contained,
    Resolved,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct ContainmentAction {
    pub id: ContainmentActionId,
    pub security_incident_id: SecurityIncidentId,
    pub action_type: ContainmentActionType,
    pub target: ContainmentTarget,
    pub reason: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum ContainmentActionType {
    SuspendAgent,
    RevokeTaskAuthority,
    BlockToolAccess,
    FreezeWorkflow,
    RequireHumanIntervention,
    TerminateExecution,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum ContainmentTarget {
    AgentLegacyId(LegacyId),
    AgentTaskAnchor(AgentTaskAnchorId),
    WorkflowDefinition(WorkflowDefinitionId),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn human_absolute_authority_is_explicit() {
        let authority = HumanAuthority {
            subject: "Joseph Rainer".to_owned(),
            authority_level: AuthorityLevel::HumanAbsolute,
        };

        assert_eq!(authority.authority_level, AuthorityLevel::HumanAbsolute);
    }

    #[test]
    fn python_owned_entities_keep_legacy_integer_ids() {
        let incident = SecurityIncident {
            id: SecurityIncidentId::new(),
            category: SecurityIncidentCategory::RogueAgentBehavior,
            severity: SecuritySeverity::Critical,
            description: "Agent exceeded assigned authority".to_owned(),
            related_agent_legacy_id: Some(42),
            status: SecurityIncidentStatus::Open,
        };

        assert_eq!(incident.related_agent_legacy_id, Some(42));
    }

    #[test]
    fn manual_rewire_preserves_version_history() {
        let record = ManualRewireRecord {
            id: ManualRewireRecordId::new(),
            workflow_definition_id: WorkflowDefinitionId::new(),
            performed_by: HumanAuthority {
                subject: "Joseph Rainer".to_owned(),
                authority_level: AuthorityLevel::HumanAbsolute,
            },
            reason: "Human override".to_owned(),
            previous_version: 1,
            new_version: 2,
        };

        assert!(record.new_version > record.previous_version);
    }
}