use eli_boundary::{
    BoundaryDecisionReceipt, BoundaryError, BoundaryErrorCode, BoundaryProcessingOutcome,
    PythonBoundaryRequest,
};

#[derive(Debug)]
pub struct RuntimeTaskHandoff {
    request: PythonBoundaryRequest,
    receipt: BoundaryDecisionReceipt,
    requires_human_approval: bool,
}

impl RuntimeTaskHandoff {
    #[must_use]
    pub fn new(
        request: PythonBoundaryRequest,
        receipt: BoundaryDecisionReceipt,
        requires_human_approval: bool,
    ) -> Self {
        Self {
            request,
            receipt,
            requires_human_approval,
        }
    }

    #[must_use]
    pub fn from_boundary_outcome(
        outcome: BoundaryProcessingOutcome,
        requires_human_approval: bool,
    ) -> Self {
        let (request, receipt) = outcome.into_parts();
        Self::new(request, receipt, requires_human_approval)
    }

    #[must_use]
    pub fn request(&self) -> &PythonBoundaryRequest {
        &self.request
    }

    #[must_use]
    pub fn receipt(&self) -> &BoundaryDecisionReceipt {
        &self.receipt
    }

    #[must_use]
    pub fn requires_human_approval(&self) -> bool {
        self.requires_human_approval
    }

    #[must_use]
    pub fn into_parts(self) -> (PythonBoundaryRequest, BoundaryDecisionReceipt, bool) {
        (self.request, self.receipt, self.requires_human_approval)
    }
}

pub trait BoundaryRuntimeAdapter {
    fn adapt(
        &self,
        outcome: BoundaryProcessingOutcome,
    ) -> Result<RuntimeTaskHandoff, BoundaryError>;
}

#[derive(Clone, Debug, Default)]
pub struct DefaultBoundaryRuntimeAdapter;

impl BoundaryRuntimeAdapter for DefaultBoundaryRuntimeAdapter {
    fn adapt(
        &self,
        outcome: BoundaryProcessingOutcome,
    ) -> Result<RuntimeTaskHandoff, BoundaryError> {
        Ok(RuntimeTaskHandoff::from_boundary_outcome(outcome, true))
    }
}

fn invalid_request(message: &str) -> BoundaryError {
    BoundaryError {
        code: BoundaryErrorCode::InvalidRequest,
        message: message.to_owned(),
        retryable: false,
    }
}

pub fn validate_runtime_handoff(handoff: &RuntimeTaskHandoff) -> Result<(), BoundaryError> {
    if handoff
        .receipt()
        .correlation_id()
        .as_str()
        .trim()
        .is_empty()
    {
        return Err(invalid_request("runtime handoff has empty correlation ID"));
    }

    if handoff
        .receipt()
        .idempotency_key()
        .as_str()
        .trim()
        .is_empty()
    {
        return Err(invalid_request("runtime handoff has empty idempotency key"));
    }

    Ok(())
}

#[derive(Debug)]
pub struct RuntimeDispatchRequest {
    handoff: RuntimeTaskHandoff,
}

impl RuntimeDispatchRequest {
    #[must_use]
    pub fn new(handoff: RuntimeTaskHandoff) -> Self {
        Self { handoff }
    }

    #[must_use]
    pub fn handoff(&self) -> &RuntimeTaskHandoff {
        &self.handoff
    }

    #[must_use]
    pub fn into_handoff(self) -> RuntimeTaskHandoff {
        self.handoff
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeHumanApprovalRequest {
    correlation_id: String,
    idempotency_key: String,
    reason: String,
}

impl RuntimeHumanApprovalRequest {
    #[must_use]
    pub fn new(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        reason: impl Into<String>,
    ) -> Self {
        Self {
            correlation_id: correlation_id.into(),
            idempotency_key: idempotency_key.into(),
            reason: reason.into(),
        }
    }

    #[must_use]
    pub fn correlation_id(&self) -> &str {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        &self.idempotency_key
    }

    #[must_use]
    pub fn reason(&self) -> &str {
        &self.reason
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeDispatchReceipt {
    correlation_id: String,
    idempotency_key: String,
    queued: bool,
}

impl RuntimeDispatchReceipt {
    #[must_use]
    pub fn queued(correlation_id: impl Into<String>, idempotency_key: impl Into<String>) -> Self {
        Self {
            correlation_id: correlation_id.into(),
            idempotency_key: idempotency_key.into(),
            queued: true,
        }
    }

    #[must_use]
    pub fn correlation_id(&self) -> &str {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        &self.idempotency_key
    }

    #[must_use]
    pub fn queued_flag(&self) -> bool {
        self.queued
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeDispatchRejection {
    correlation_id: String,
    idempotency_key: String,
    reason: String,
}

impl RuntimeDispatchRejection {
    #[must_use]
    pub fn new(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        reason: impl Into<String>,
    ) -> Self {
        Self {
            correlation_id: correlation_id.into(),
            idempotency_key: idempotency_key.into(),
            reason: reason.into(),
        }
    }

    #[must_use]
    pub fn correlation_id(&self) -> &str {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        &self.idempotency_key
    }

    #[must_use]
    pub fn reason(&self) -> &str {
        &self.reason
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RuntimeDispatchDecision {
    RequiresHumanApproval(RuntimeHumanApprovalRequest),
    Queued(RuntimeDispatchReceipt),
    Rejected(RuntimeDispatchRejection),
}

impl RuntimeDispatchDecision {
    #[must_use]
    pub fn requires_human_approval(&self) -> bool {
        matches!(self, Self::RequiresHumanApproval(_))
    }

    #[must_use]
    pub fn is_queued(&self) -> bool {
        matches!(self, Self::Queued(_))
    }

    #[must_use]
    pub fn is_rejected(&self) -> bool {
        matches!(self, Self::Rejected(_))
    }
}

pub trait RuntimeDispatchGate {
    fn decide(&self, request: &RuntimeDispatchRequest) -> RuntimeDispatchDecision;
}

#[derive(Clone, Debug, Default)]
pub struct HumanApprovalDispatchGate;

impl RuntimeDispatchGate for HumanApprovalDispatchGate {
    fn decide(&self, request: &RuntimeDispatchRequest) -> RuntimeDispatchDecision {
        let handoff = request.handoff();

        let correlation_id = handoff.receipt().correlation_id().as_str();
        let idempotency_key = handoff.receipt().idempotency_key().as_str();

        if handoff.requires_human_approval() {
            RuntimeDispatchDecision::RequiresHumanApproval(RuntimeHumanApprovalRequest::new(
                correlation_id,
                idempotency_key,
                "human approval is required before runtime dispatch",
            ))
        } else {
            RuntimeDispatchDecision::Queued(RuntimeDispatchReceipt::queued(
                correlation_id,
                idempotency_key,
            ))
        }
    }
}

use std::collections::VecDeque;

pub trait RuntimeQueue {
    fn enqueue(
        &mut self,
        handoff: RuntimeTaskHandoff,
    ) -> Result<RuntimeDispatchReceipt, BoundaryError>;

    fn dequeue(&mut self) -> Option<RuntimeTaskHandoff>;

    fn len(&self) -> usize;

    fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

#[derive(Debug, Default)]
pub struct InMemoryRuntimeQueue {
    items: VecDeque<RuntimeTaskHandoff>,
}

impl InMemoryRuntimeQueue {
    #[must_use]
    pub fn new() -> Self {
        Self {
            items: VecDeque::new(),
        }
    }
}

impl RuntimeQueue for InMemoryRuntimeQueue {
    fn enqueue(
        &mut self,
        handoff: RuntimeTaskHandoff,
    ) -> Result<RuntimeDispatchReceipt, BoundaryError> {
        let receipt = RuntimeDispatchReceipt::queued(
            handoff.receipt().correlation_id().as_str(),
            handoff.receipt().idempotency_key().as_str(),
        );

        self.items.push_back(handoff);

        Ok(receipt)
    }

    fn dequeue(&mut self) -> Option<RuntimeTaskHandoff> {
        self.items.pop_front()
    }

    fn len(&self) -> usize {
        self.items.len()
    }
}

#[derive(Debug)]
pub struct RuntimeWorkerInput {
    handoff: RuntimeTaskHandoff,
}

impl RuntimeWorkerInput {
    #[must_use]
    pub fn new(handoff: RuntimeTaskHandoff) -> Self {
        Self { handoff }
    }

    #[must_use]
    pub fn handoff(&self) -> &RuntimeTaskHandoff {
        &self.handoff
    }

    #[must_use]
    pub fn into_handoff(self) -> RuntimeTaskHandoff {
        self.handoff
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeWorkerOutput {
    correlation_id: String,
    idempotency_key: String,
    status: RuntimeWorkerStatus,
}

impl RuntimeWorkerOutput {
    #[must_use]
    pub fn completed(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
    ) -> Self {
        Self {
            correlation_id: correlation_id.into(),
            idempotency_key: idempotency_key.into(),
            status: RuntimeWorkerStatus::Completed,
        }
    }

    #[must_use]
    pub fn failed(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        retryable: bool,
    ) -> Self {
        Self {
            correlation_id: correlation_id.into(),
            idempotency_key: idempotency_key.into(),
            status: RuntimeWorkerStatus::Failed { retryable },
        }
    }

    #[must_use]
    pub fn correlation_id(&self) -> &str {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        &self.idempotency_key
    }

    #[must_use]
    pub fn status(&self) -> &RuntimeWorkerStatus {
        &self.status
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RuntimeWorkerStatus {
    Completed,
    Failed { retryable: bool },
}

pub trait BoundaryReceiptRepository {
    fn store_receipt(&mut self, receipt: &BoundaryDecisionReceipt) -> Result<(), BoundaryError>;
}

pub trait RuntimeDispatchRepository {
    fn store_dispatch_receipt(
        &mut self,
        receipt: &RuntimeDispatchReceipt,
    ) -> Result<(), BoundaryError>;

    fn store_dispatch_rejection(
        &mut self,
        rejection: &RuntimeDispatchRejection,
    ) -> Result<(), BoundaryError>;
}

pub trait RuntimeWorkerRepository {
    fn store_worker_output(&mut self, output: &RuntimeWorkerOutput) -> Result<(), BoundaryError>;
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RuntimeExecutionKind {
    DryRun,
    ShellCommand,
    PythonBridge,
    BrowserAutomation,
    ExternalApiCall,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeExecutionCommand {
    correlation_id: String,
    idempotency_key: String,
    kind: RuntimeExecutionKind,
    summary: String,
    requires_human_approval: bool,
}

impl RuntimeExecutionCommand {
    #[must_use]
    pub fn new(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        kind: RuntimeExecutionKind,
        summary: impl Into<String>,
        requires_human_approval: bool,
    ) -> Self {
        Self {
            correlation_id: correlation_id.into(),
            idempotency_key: idempotency_key.into(),
            kind,
            summary: summary.into(),
            requires_human_approval,
        }
    }

    #[must_use]
    pub fn dry_run(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        summary: impl Into<String>,
    ) -> Self {
        Self::new(
            correlation_id,
            idempotency_key,
            RuntimeExecutionKind::DryRun,
            summary,
            true,
        )
    }

    #[must_use]
    pub fn correlation_id(&self) -> &str {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        &self.idempotency_key
    }

    #[must_use]
    pub fn kind(&self) -> &RuntimeExecutionKind {
        &self.kind
    }

    #[must_use]
    pub fn summary(&self) -> &str {
        &self.summary
    }

    #[must_use]
    pub fn requires_human_approval(&self) -> bool {
        self.requires_human_approval
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RuntimeExecutionPermission {
    Allowed,
    RequiresHumanApproval,
    Denied { reason: String },
}

impl RuntimeExecutionPermission {
    #[must_use]
    pub fn is_allowed(&self) -> bool {
        matches!(self, Self::Allowed)
    }

    #[must_use]
    pub fn requires_human_approval(&self) -> bool {
        matches!(self, Self::RequiresHumanApproval)
    }

    #[must_use]
    pub fn is_denied(&self) -> bool {
        matches!(self, Self::Denied { .. })
    }
}

pub trait RuntimeExecutionPolicy {
    fn evaluate(&self, command: &RuntimeExecutionCommand) -> RuntimeExecutionPermission;
}

#[derive(Clone, Debug, Default)]
pub struct SafeRuntimeExecutionPolicy;

impl RuntimeExecutionPolicy for SafeRuntimeExecutionPolicy {
    fn evaluate(&self, command: &RuntimeExecutionCommand) -> RuntimeExecutionPermission {
        match command.kind() {
            RuntimeExecutionKind::DryRun => {
                if command.requires_human_approval() {
                    RuntimeExecutionPermission::RequiresHumanApproval
                } else {
                    RuntimeExecutionPermission::Allowed
                }
            }
            RuntimeExecutionKind::ShellCommand
            | RuntimeExecutionKind::PythonBridge
            | RuntimeExecutionKind::BrowserAutomation
            | RuntimeExecutionKind::ExternalApiCall => RuntimeExecutionPermission::Denied {
                reason: "live execution is outside the Phase 3 dry-run boundary".to_owned(),
            },
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeExecutionApprovalReceipt {
    correlation_id: String,
    idempotency_key: String,
    approved_by: String,
    approved_at_unix_ms: u64,
}

impl RuntimeExecutionApprovalReceipt {
    #[must_use]
    pub fn new(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        approved_by: impl Into<String>,
        approved_at_unix_ms: u64,
    ) -> Self {
        Self {
            correlation_id: correlation_id.into(),
            idempotency_key: idempotency_key.into(),
            approved_by: approved_by.into(),
            approved_at_unix_ms,
        }
    }

    #[must_use]
    pub fn correlation_id(&self) -> &str {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        &self.idempotency_key
    }

    #[must_use]
    pub fn approved_by(&self) -> &str {
        &self.approved_by
    }

    #[must_use]
    pub fn approved_at_unix_ms(&self) -> u64 {
        self.approved_at_unix_ms
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RuntimeExecutionStatus {
    DryRunCompleted,
    BlockedRequiresApproval,
    BlockedDenied,
    Failed,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeExecutionResult {
    correlation_id: String,
    idempotency_key: String,
    status: RuntimeExecutionStatus,
    message: String,
}

impl RuntimeExecutionResult {
    #[must_use]
    pub fn new(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        status: RuntimeExecutionStatus,
        message: impl Into<String>,
    ) -> Self {
        Self {
            correlation_id: correlation_id.into(),
            idempotency_key: idempotency_key.into(),
            status,
            message: message.into(),
        }
    }

    #[must_use]
    pub fn dry_run_completed(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        message: impl Into<String>,
    ) -> Self {
        Self::new(
            correlation_id,
            idempotency_key,
            RuntimeExecutionStatus::DryRunCompleted,
            message,
        )
    }

    #[must_use]
    pub fn blocked_requires_approval(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
    ) -> Self {
        Self::new(
            correlation_id,
            idempotency_key,
            RuntimeExecutionStatus::BlockedRequiresApproval,
            "human approval is required before execution",
        )
    }

    #[must_use]
    pub fn blocked_denied(
        correlation_id: impl Into<String>,
        idempotency_key: impl Into<String>,
        message: impl Into<String>,
    ) -> Self {
        Self::new(
            correlation_id,
            idempotency_key,
            RuntimeExecutionStatus::BlockedDenied,
            message,
        )
    }

    #[must_use]
    pub fn correlation_id(&self) -> &str {
        &self.correlation_id
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        &self.idempotency_key
    }

    #[must_use]
    pub fn status(&self) -> &RuntimeExecutionStatus {
        &self.status
    }

    #[must_use]
    pub fn message(&self) -> &str {
        &self.message
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RuntimeExecutionAuditEvent {
    Approved(RuntimeExecutionApprovalReceipt),
    Completed(RuntimeExecutionResult),
    Blocked(RuntimeExecutionResult),
}

impl RuntimeExecutionAuditEvent {
    #[must_use]
    pub fn correlation_id(&self) -> &str {
        match self {
            Self::Approved(receipt) => receipt.correlation_id(),
            Self::Completed(result) | Self::Blocked(result) => result.correlation_id(),
        }
    }

    #[must_use]
    pub fn idempotency_key(&self) -> &str {
        match self {
            Self::Approved(receipt) => receipt.idempotency_key(),
            Self::Completed(result) | Self::Blocked(result) => result.idempotency_key(),
        }
    }
}

pub trait RuntimeExecutor {
    fn execute(
        &self,
        command: &RuntimeExecutionCommand,
        approval: Option<&RuntimeExecutionApprovalReceipt>,
    ) -> RuntimeExecutionResult;
}

#[derive(Clone, Debug)]
pub struct DryRunRuntimeExecutor<P = SafeRuntimeExecutionPolicy> {
    policy: P,
}

impl<P> DryRunRuntimeExecutor<P>
where
    P: RuntimeExecutionPolicy,
{
    #[must_use]
    pub fn new(policy: P) -> Self {
        Self { policy }
    }

    #[must_use]
    pub fn policy(&self) -> &P {
        &self.policy
    }
}

impl Default for DryRunRuntimeExecutor<SafeRuntimeExecutionPolicy> {
    fn default() -> Self {
        Self {
            policy: SafeRuntimeExecutionPolicy,
        }
    }
}

impl<P> RuntimeExecutor for DryRunRuntimeExecutor<P>
where
    P: RuntimeExecutionPolicy,
{
    fn execute(
        &self,
        command: &RuntimeExecutionCommand,
        approval: Option<&RuntimeExecutionApprovalReceipt>,
    ) -> RuntimeExecutionResult {
        match self.policy.evaluate(command) {
            RuntimeExecutionPermission::Allowed => RuntimeExecutionResult::dry_run_completed(
                command.correlation_id(),
                command.idempotency_key(),
                format!("dry-run execution accepted: {}", command.summary()),
            ),
            RuntimeExecutionPermission::RequiresHumanApproval => {
                if approval.is_some() {
                    RuntimeExecutionResult::dry_run_completed(
                        command.correlation_id(),
                        command.idempotency_key(),
                        format!("dry-run execution approved: {}", command.summary()),
                    )
                } else {
                    RuntimeExecutionResult::blocked_requires_approval(
                        command.correlation_id(),
                        command.idempotency_key(),
                    )
                }
            }
            RuntimeExecutionPermission::Denied { reason } => {
                RuntimeExecutionResult::blocked_denied(
                    command.correlation_id(),
                    command.idempotency_key(),
                    reason,
                )
            }
        }
    }
}

pub trait RuntimeExecutionRepository {
    fn store_execution_approval(
        &mut self,
        receipt: &RuntimeExecutionApprovalReceipt,
    ) -> Result<(), BoundaryError>;

    fn store_execution_result(
        &mut self,
        result: &RuntimeExecutionResult,
    ) -> Result<(), BoundaryError>;

    fn store_execution_audit_event(
        &mut self,
        event: &RuntimeExecutionAuditEvent,
    ) -> Result<(), BoundaryError>;
}

#[cfg(test)]
mod phase_3_execution_tests {
    use super::*;

    #[test]
    fn safe_policy_requires_approval_for_default_dry_run_command() {
        let command = RuntimeExecutionCommand::dry_run(
            "corr-phase-3",
            "idem-phase-3",
            "preview execution boundary",
        );

        let policy = SafeRuntimeExecutionPolicy;
        let permission = policy.evaluate(&command);

        assert!(permission.requires_human_approval());
    }

    #[test]
    fn safe_policy_denies_live_execution_kinds() {
        let policy = SafeRuntimeExecutionPolicy;

        let command = RuntimeExecutionCommand::new(
            "corr-phase-3",
            "idem-phase-3",
            RuntimeExecutionKind::ShellCommand,
            "attempt shell command",
            true,
        );

        let permission = policy.evaluate(&command);

        assert!(permission.is_denied());

        match permission {
            RuntimeExecutionPermission::Denied { reason } => {
                assert!(reason.contains("outside the Phase 3 dry-run boundary"));
            }
            _ => panic!("expected denied permission"),
        }
    }

    #[test]
    fn dry_run_executor_blocks_without_approval() {
        let executor = DryRunRuntimeExecutor::default();

        let command = RuntimeExecutionCommand::dry_run(
            "corr-phase-3",
            "idem-phase-3",
            "preview execution boundary",
        );

        let result = executor.execute(&command, None);

        assert_eq!(
            result.status(),
            &RuntimeExecutionStatus::BlockedRequiresApproval
        );
        assert_eq!(result.correlation_id(), "corr-phase-3");
        assert_eq!(result.idempotency_key(), "idem-phase-3");
    }

    #[test]
    fn dry_run_executor_completes_with_approval() {
        let executor = DryRunRuntimeExecutor::default();

        let command = RuntimeExecutionCommand::dry_run(
            "corr-phase-3",
            "idem-phase-3",
            "preview execution boundary",
        );

        let approval = RuntimeExecutionApprovalReceipt::new(
            "corr-phase-3",
            "idem-phase-3",
            "human-operator",
            3_000,
        );

        let result = executor.execute(&command, Some(&approval));

        assert_eq!(result.status(), &RuntimeExecutionStatus::DryRunCompleted);
        assert!(result.message().contains("dry-run execution approved"));
    }

    #[test]
    fn execution_audit_event_preserves_identity() {
        let receipt = RuntimeExecutionApprovalReceipt::new(
            "corr-phase-3",
            "idem-phase-3",
            "human-operator",
            3_000,
        );

        let event = RuntimeExecutionAuditEvent::Approved(receipt);

        assert_eq!(event.correlation_id(), "corr-phase-3");
        assert_eq!(event.idempotency_key(), "idem-phase-3");
    }
}
