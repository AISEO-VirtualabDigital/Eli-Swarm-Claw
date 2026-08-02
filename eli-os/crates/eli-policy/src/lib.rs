use eli_core::PolicyDecisionId;
use eli_domain::{
    AgentTaskAnchor, AgentTaskAnchorStatus, AuthorityLevel, HumanOrder, HumanOrderStatus,
    PolicyDecision, PolicyOutcome, PolicySubject, WorkflowDefinition,
};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct PolicyContext {
    pub human_override: bool,
    pub workflow_enabled: bool,
    pub agent_contained: bool,
}

#[derive(Clone, Debug, Default)]
pub struct PolicyEngine;

impl PolicyEngine {
    #[must_use]
    pub fn evaluate_human_order(
        &self,
        order: &HumanOrder,
        context: &PolicyContext,
    ) -> PolicyDecision {
        let outcome = if order.issued_by.authority_level == AuthorityLevel::HumanAbsolute {
            PolicyOutcome::Allow
        } else if context.human_override {
            PolicyOutcome::RequireHumanApproval
        } else {
            PolicyOutcome::Deny
        };

        PolicyDecision {
            id: PolicyDecisionId::new(),
            subject: PolicySubject::HumanOrder(order.id),
            outcome,
            reason: "Human order authority evaluated".to_owned(),
        }
    }

    #[must_use]
    pub fn evaluate_agent_task(
        &self,
        task: &AgentTaskAnchor,
        context: &PolicyContext,
    ) -> PolicyDecision {
        let outcome = if context.agent_contained || task.status == AgentTaskAnchorStatus::Contained
        {
            PolicyOutcome::Contain
        } else if task.status == AgentTaskAnchorStatus::Cancelled {
            PolicyOutcome::Deny
        } else {
            PolicyOutcome::Allow
        };

        PolicyDecision {
            id: PolicyDecisionId::new(),
            subject: PolicySubject::AgentTaskAnchor(task.id),
            outcome,
            reason: "Agent task authority evaluated".to_owned(),
        }
    }

    #[must_use]
    pub fn evaluate_workflow(
        &self,
        workflow: &WorkflowDefinition,
        context: &PolicyContext,
    ) -> PolicyDecision {
        let outcome = if !workflow.enabled || !context.workflow_enabled {
            PolicyOutcome::Deny
        } else if workflow
            .steps
            .iter()
            .any(|step| step.requires_human_approval)
        {
            PolicyOutcome::RequireHumanApproval
        } else {
            PolicyOutcome::Allow
        };

        PolicyDecision {
            id: PolicyDecisionId::new(),
            subject: PolicySubject::WorkflowDefinition(workflow.id),
            outcome,
            reason: "Workflow policy evaluated".to_owned(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use eli_core::{AgentTaskAnchorId, ContextSnapshotId, HumanOrderId, WorkflowDefinitionId};
    use eli_domain::{HumanAuthority, HumanOrderPriority, WorkflowExecutor, WorkflowStep};

    #[test]
    fn human_absolute_order_is_allowed() {
        let engine = PolicyEngine;
        let order = HumanOrder {
            id: HumanOrderId::new(),
            issued_by: HumanAuthority {
                subject: "Joseph Rainer".to_owned(),
                authority_level: AuthorityLevel::HumanAbsolute,
            },
            instruction: "Stop workflow".to_owned(),
            priority: HumanOrderPriority::Critical,
            status: HumanOrderStatus::Issued,
        };

        let decision = engine.evaluate_human_order(
            &order,
            &PolicyContext {
                human_override: false,
                workflow_enabled: true,
                agent_contained: false,
            },
        );

        assert_eq!(decision.outcome, PolicyOutcome::Allow);
    }

    #[test]
    fn contained_agent_task_is_contained() {
        let engine = PolicyEngine;
        let task = AgentTaskAnchor {
            id: AgentTaskAnchorId::new(),
            agent_legacy_id: 42,
            human_order_id: HumanOrderId::new(),
            context_snapshot_id: ContextSnapshotId::new(),
            objective: "Run crawl".to_owned(),
            status: AgentTaskAnchorStatus::Contained,
        };

        let decision = engine.evaluate_agent_task(
            &task,
            &PolicyContext {
                human_override: false,
                workflow_enabled: true,
                agent_contained: true,
            },
        );

        assert_eq!(decision.outcome, PolicyOutcome::Contain);
    }

    #[test]
    fn approval_step_requires_human_approval() {
        let engine = PolicyEngine;
        let workflow = WorkflowDefinition {
            id: WorkflowDefinitionId::new(),
            name: "Protected workflow".to_owned(),
            version: 1,
            steps: vec![WorkflowStep {
                position: 1,
                name: "Human approval".to_owned(),
                executor: WorkflowExecutor::Human,
                requires_human_approval: true,
            }],
            enabled: true,
        };

        let decision = engine.evaluate_workflow(
            &workflow,
            &PolicyContext {
                human_override: false,
                workflow_enabled: true,
                agent_contained: false,
            },
        );

        assert_eq!(decision.outcome, PolicyOutcome::RequireHumanApproval);
    }
}
