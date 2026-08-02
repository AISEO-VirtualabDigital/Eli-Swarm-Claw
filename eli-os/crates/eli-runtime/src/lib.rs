use eli_boundary::{
    BoundaryDecisionReceipt, BoundaryError, BoundaryErrorCode, BoundaryProcessingOutcome,
    PythonBoundaryRequest,
};
use std::cell::RefCell;

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

pub trait RuntimeExecutionAuditSink {
    fn record(&mut self, event: RuntimeExecutionAuditEvent);

    #[must_use]
    fn snapshot(&self) -> RuntimeExecutionAuditSnapshot;

    #[must_use]
    fn report(&self) -> RuntimeExecutionAuditReport;
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeExecutionAuditSnapshot {
    total_count: usize,
    approved_count: usize,
    completed_count: usize,
    blocked_count: usize,
    events: Vec<RuntimeExecutionAuditEvent>,
}

impl RuntimeExecutionAuditSnapshot {
    #[must_use]
    pub fn new(events: &[RuntimeExecutionAuditEvent]) -> Self {
        let mut approved_count = 0;
        let mut completed_count = 0;
        let mut blocked_count = 0;

        for event in events {
            match event {
                RuntimeExecutionAuditEvent::Approved(_) => approved_count += 1,
                RuntimeExecutionAuditEvent::Completed(_) => completed_count += 1,
                RuntimeExecutionAuditEvent::Blocked(_) => blocked_count += 1,
            }
        }

        Self {
            total_count: events.len(),
            approved_count,
            completed_count,
            blocked_count,
            events: events.to_vec(),
        }
    }

    #[must_use]
    pub fn total_count(&self) -> usize {
        self.total_count
    }

    #[must_use]
    pub fn approved_count(&self) -> usize {
        self.approved_count
    }

    #[must_use]
    pub fn completed_count(&self) -> usize {
        self.completed_count
    }

    #[must_use]
    pub fn blocked_count(&self) -> usize {
        self.blocked_count
    }

    #[must_use]
    pub fn events(&self) -> &[RuntimeExecutionAuditEvent] {
        &self.events
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.total_count == 0
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RuntimeExecutionAuditReport {
    snapshot: RuntimeExecutionAuditSnapshot,
    events: Vec<RuntimeExecutionAuditEvent>,
}

impl RuntimeExecutionAuditReport {
    #[must_use]
    pub fn new(events: &[RuntimeExecutionAuditEvent]) -> Self {
        Self {
            snapshot: RuntimeExecutionAuditSnapshot::new(events),
            events: events.to_vec(),
        }
    }

    #[must_use]
    pub fn snapshot(&self) -> &RuntimeExecutionAuditSnapshot {
        &self.snapshot
    }

    #[must_use]
    pub fn events(&self) -> &[RuntimeExecutionAuditEvent] {
        &self.events
    }

    #[must_use]
    pub fn total_count(&self) -> usize {
        self.snapshot.total_count()
    }

    #[must_use]
    pub fn approved_count(&self) -> usize {
        self.snapshot.approved_count()
    }

    #[must_use]
    pub fn completed_count(&self) -> usize {
        self.snapshot.completed_count()
    }

    #[must_use]
    pub fn blocked_count(&self) -> usize {
        self.snapshot.blocked_count()
    }
}

#[derive(Clone, Debug, Default)]
pub struct InMemoryRuntimeExecutionAuditSink {
    events: Vec<RuntimeExecutionAuditEvent>,
}

impl InMemoryRuntimeExecutionAuditSink {
    #[must_use]
    pub fn new() -> Self {
        Self { events: Vec::new() }
    }

    #[must_use]
    pub fn events(&self) -> &[RuntimeExecutionAuditEvent] {
        &self.events
    }

    #[must_use]
    pub fn snapshot(&self) -> RuntimeExecutionAuditSnapshot {
        RuntimeExecutionAuditSnapshot::new(&self.events)
    }

    #[must_use]
    pub fn report(&self) -> RuntimeExecutionAuditReport {
        RuntimeExecutionAuditReport::new(&self.events)
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

impl RuntimeExecutionAuditSink for InMemoryRuntimeExecutionAuditSink {
    fn record(&mut self, event: RuntimeExecutionAuditEvent) {
        self.events.push(event);
    }

    fn snapshot(&self) -> RuntimeExecutionAuditSnapshot {
        RuntimeExecutionAuditSnapshot::new(&self.events)
    }

    fn report(&self) -> RuntimeExecutionAuditReport {
        RuntimeExecutionAuditReport::new(&self.events)
    }
}

pub struct DryRunRuntimeController<
    P = SafeRuntimeExecutionPolicy,
    E = DryRunRuntimeExecutor<SafeRuntimeExecutionPolicy>,
    S = InMemoryRuntimeExecutionAuditSink,
> {
    policy: P,
    executor: E,
    sink: RefCell<S>,
}

impl<P, E, S> DryRunRuntimeController<P, E, S>
where
    P: RuntimeExecutionPolicy,
    E: RuntimeExecutor,
    S: RuntimeExecutionAuditSink,
{
    #[must_use]
    pub fn new(policy: P, executor: E, sink: S) -> Self {
        Self {
            policy,
            executor,
            sink: RefCell::new(sink),
        }
    }

    #[must_use]
    pub fn policy(&self) -> &P {
        &self.policy
    }

    #[must_use]
    pub fn executor(&self) -> &E {
        &self.executor
    }

    #[must_use]
    pub fn snapshot(&self) -> RuntimeExecutionAuditSnapshot {
        self.sink.borrow().snapshot()
    }

    #[must_use]
    pub fn report(&self) -> RuntimeExecutionAuditReport {
        self.sink.borrow().report()
    }

    pub fn execute(
        &self,
        command: &RuntimeExecutionCommand,
        approval: Option<&RuntimeExecutionApprovalReceipt>,
    ) -> RuntimeExecutionResult {
        let permission = self.policy.evaluate(command);
        let result = match permission {
            RuntimeExecutionPermission::Allowed => self.executor.execute(command, None),
            RuntimeExecutionPermission::RequiresHumanApproval => {
                if let Some(approval) = approval {
                    self.sink
                        .borrow_mut()
                        .record(RuntimeExecutionAuditEvent::Approved(approval.clone()));
                    self.executor.execute(command, Some(approval))
                } else {
                    self.executor.execute(command, None)
                }
            }
            RuntimeExecutionPermission::Denied { .. } => self.executor.execute(command, None),
        };

        let event = match result.status() {
            RuntimeExecutionStatus::DryRunCompleted => {
                RuntimeExecutionAuditEvent::Completed(result.clone())
            }
            RuntimeExecutionStatus::BlockedRequiresApproval
            | RuntimeExecutionStatus::BlockedDenied
            | RuntimeExecutionStatus::Failed => RuntimeExecutionAuditEvent::Blocked(result.clone()),
        };

        self.sink.borrow_mut().record(event);
        result
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

#[derive(Clone, Debug, PartialEq, Eq, Default)]
pub struct RuntimePilotState {
    approvals: Vec<RuntimeExecutionApprovalReceipt>,
    results: Vec<RuntimeExecutionResult>,
    audit_events: Vec<RuntimeExecutionAuditEvent>,
}

impl RuntimePilotState {
    #[must_use]
    pub fn new(
        approvals: Vec<RuntimeExecutionApprovalReceipt>,
        results: Vec<RuntimeExecutionResult>,
        audit_events: Vec<RuntimeExecutionAuditEvent>,
    ) -> Self {
        Self {
            approvals,
            results,
            audit_events,
        }
    }

    #[must_use]
    pub fn approvals(&self) -> &[RuntimeExecutionApprovalReceipt] {
        &self.approvals
    }

    #[must_use]
    pub fn results(&self) -> &[RuntimeExecutionResult] {
        &self.results
    }

    #[must_use]
    pub fn audit_events(&self) -> &[RuntimeExecutionAuditEvent] {
        &self.audit_events
    }

    #[must_use]
    pub fn approval_count(&self) -> usize {
        self.approvals.len()
    }

    #[must_use]
    pub fn result_count(&self) -> usize {
        self.results.len()
    }

    #[must_use]
    pub fn audit_event_count(&self) -> usize {
        self.audit_events.len()
    }

    #[must_use]
    pub fn snapshot(&self) -> RuntimeExecutionAuditSnapshot {
        RuntimeExecutionAuditSnapshot::new(&self.audit_events)
    }
}

#[derive(Clone, Debug, Default)]
pub struct InMemoryPilotStateStore {
    state: RuntimePilotState,
}

impl InMemoryPilotStateStore {
    #[must_use]
    pub fn new() -> Self {
        Self {
            state: RuntimePilotState::new(Vec::new(), Vec::new(), Vec::new()),
        }
    }

    pub fn record_approval(&mut self, approval: &RuntimeExecutionApprovalReceipt) {
        self.state.approvals.push(approval.clone());
    }

    pub fn record_result(&mut self, result: &RuntimeExecutionResult) {
        self.state.results.push(result.clone());
    }

    pub fn record_audit_event(&mut self, event: &RuntimeExecutionAuditEvent) {
        self.state.audit_events.push(event.clone());
    }

    #[must_use]
    pub fn state(&self) -> &RuntimePilotState {
        &self.state
    }

    #[must_use]
    pub fn snapshot(&self) -> RuntimeExecutionAuditSnapshot {
        self.state.snapshot()
    }

    #[must_use]
    pub fn report(&self) -> RuntimeExecutionAuditReport {
        RuntimeExecutionAuditReport::new(&self.state.audit_events)
    }
}

impl RuntimeExecutionRepository for InMemoryPilotStateStore {
    fn store_execution_approval(
        &mut self,
        receipt: &RuntimeExecutionApprovalReceipt,
    ) -> Result<(), BoundaryError> {
        self.record_approval(receipt);
        Ok(())
    }

    fn store_execution_result(
        &mut self,
        result: &RuntimeExecutionResult,
    ) -> Result<(), BoundaryError> {
        self.record_result(result);
        Ok(())
    }

    fn store_execution_audit_event(
        &mut self,
        event: &RuntimeExecutionAuditEvent,
    ) -> Result<(), BoundaryError> {
        self.record_audit_event(event);
        Ok(())
    }
}

#[cfg(test)]
mod phase_5_pilot_persistence_tests {
    use super::*;
    #[test]
    fn in_memory_store_records_approvals() {
        let mut store = InMemoryPilotStateStore::new();
        let approval = RuntimeExecutionApprovalReceipt::new(
            "corr-pilot-approval",
            "idem-pilot-approval",
            "human-operator",
            6_000,
        );

        store.record_approval(&approval);

        let state = store.state();
        assert_eq!(state.approval_count(), 1);
        assert_eq!(state.audit_event_count(), 0);
    }

    #[test]
    fn in_memory_store_records_execution_results() {
        let mut store = InMemoryPilotStateStore::new();
        let result = RuntimeExecutionResult::dry_run_completed(
            "corr-pilot-result",
            "idem-pilot-result",
            "dry-run completed",
        );

        store.record_result(&result);

        let state = store.state();
        assert_eq!(state.result_count(), 1);
        assert_eq!(state.snapshot().total_count(), 0);
    }

    #[test]
    fn in_memory_store_records_blocked_events() {
        let mut store = InMemoryPilotStateStore::new();
        let blocked = RuntimeExecutionAuditEvent::Blocked(RuntimeExecutionResult::blocked_denied(
            "corr-pilot-blocked",
            "idem-pilot-blocked",
            "blocked by policy",
        ));

        store.record_audit_event(&blocked);

        let state = store.state();
        assert_eq!(state.audit_event_count(), 1);
        assert_eq!(state.snapshot().blocked_count(), 1);
    }

    #[test]
    fn snapshot_counts_remain_correct() {
        let mut store = InMemoryPilotStateStore::new();
        store.record_audit_event(&RuntimeExecutionAuditEvent::Approved(
            RuntimeExecutionApprovalReceipt::new("corr-a", "idem-a", "human-operator", 1_000),
        ));
        store.record_audit_event(&RuntimeExecutionAuditEvent::Completed(
            RuntimeExecutionResult::dry_run_completed("corr-b", "idem-b", "completed one"),
        ));
        store.record_audit_event(&RuntimeExecutionAuditEvent::Blocked(
            RuntimeExecutionResult::blocked_denied("corr-c", "idem-c", "blocked one"),
        ));

        let snapshot = store.snapshot();
        assert_eq!(snapshot.total_count(), 3);
        assert_eq!(snapshot.approved_count(), 1);
        assert_eq!(snapshot.completed_count(), 1);
        assert_eq!(snapshot.blocked_count(), 1);
    }

    #[test]
    fn persistence_layer_does_not_execute_work() {
        let mut store = InMemoryPilotStateStore::new();
        let result =
            RuntimeExecutionResult::blocked_denied("corr-no-work", "idem-no-work", "dry-run only");

        store.record_result(&result);

        let snapshot = store.snapshot();
        assert_eq!(snapshot.total_count(), 0);
        assert_eq!(snapshot.blocked_count(), 0);
    }
}

#[cfg(test)]
mod phase_4_observability_and_controller_tests {
    use super::*;

    #[test]
    fn approved_dry_run_execution_records_approval_and_completion_audit_events() {
        let sink = InMemoryRuntimeExecutionAuditSink::new();
        let controller = DryRunRuntimeController::new(
            SafeRuntimeExecutionPolicy,
            DryRunRuntimeExecutor::default(),
            sink,
        );

        let command = RuntimeExecutionCommand::dry_run(
            "corr-phase-4-approved",
            "idem-phase-4-approved",
            "preview audit trail",
        );
        let approval = RuntimeExecutionApprovalReceipt::new(
            "corr-phase-4-approved",
            "idem-phase-4-approved",
            "human-operator",
            4_000,
        );

        let result = controller.execute(&command, Some(&approval));

        assert_eq!(result.status(), &RuntimeExecutionStatus::DryRunCompleted);
        assert_eq!(result.correlation_id(), "corr-phase-4-approved");
        assert_eq!(result.idempotency_key(), "idem-phase-4-approved");

        let snapshot = controller.snapshot();
        assert_eq!(snapshot.total_count(), 2);
        assert_eq!(snapshot.approved_count(), 1);
        assert_eq!(snapshot.completed_count(), 1);
        assert_eq!(snapshot.blocked_count(), 0);
        assert_eq!(snapshot.events().len(), 2);
        assert_eq!(
            snapshot.events()[0].correlation_id(),
            "corr-phase-4-approved"
        );
        assert_eq!(
            snapshot.events()[1].correlation_id(),
            "corr-phase-4-approved"
        );
    }

    #[test]
    fn unapproved_dry_run_execution_records_blocked_audit_event() {
        let sink = InMemoryRuntimeExecutionAuditSink::new();
        let controller = DryRunRuntimeController::new(
            SafeRuntimeExecutionPolicy,
            DryRunRuntimeExecutor::default(),
            sink,
        );

        let command = RuntimeExecutionCommand::dry_run(
            "corr-phase-4-blocked",
            "idem-phase-4-blocked",
            "preview blocked audit trail",
        );

        let result = controller.execute(&command, None);

        assert_eq!(
            result.status(),
            &RuntimeExecutionStatus::BlockedRequiresApproval
        );

        let snapshot = controller.snapshot();
        assert_eq!(snapshot.total_count(), 1);
        assert_eq!(snapshot.approved_count(), 0);
        assert_eq!(snapshot.completed_count(), 0);
        assert_eq!(snapshot.blocked_count(), 1);
    }

    #[test]
    fn denied_live_execution_kind_records_blocked_audit_event() {
        let sink = InMemoryRuntimeExecutionAuditSink::new();
        let controller = DryRunRuntimeController::new(
            SafeRuntimeExecutionPolicy,
            DryRunRuntimeExecutor::default(),
            sink,
        );

        let command = RuntimeExecutionCommand::new(
            "corr-phase-4-live-denied",
            "idem-phase-4-live-denied",
            RuntimeExecutionKind::ShellCommand,
            "attempt shell execution",
            true,
        );

        let result = controller.execute(&command, None);

        assert_eq!(result.status(), &RuntimeExecutionStatus::BlockedDenied);

        let snapshot = controller.snapshot();
        assert_eq!(snapshot.total_count(), 1);
        assert_eq!(snapshot.blocked_count(), 1);
    }

    #[test]
    fn audit_snapshot_preserves_order() {
        let sink = InMemoryRuntimeExecutionAuditSink::new();
        let mut sink = sink;
        sink.record(RuntimeExecutionAuditEvent::Blocked(
            RuntimeExecutionResult::blocked_denied("corr-a", "idem-a", "blocked one"),
        ));
        sink.record(RuntimeExecutionAuditEvent::Approved(
            RuntimeExecutionApprovalReceipt::new("corr-b", "idem-b", "human-operator", 5_000),
        ));
        sink.record(RuntimeExecutionAuditEvent::Completed(
            RuntimeExecutionResult::dry_run_completed("corr-c", "idem-c", "completed one"),
        ));

        let snapshot = sink.snapshot();

        assert_eq!(snapshot.events().len(), 3);
        assert_eq!(snapshot.events()[0].correlation_id(), "corr-a");
        assert_eq!(snapshot.events()[1].correlation_id(), "corr-b");
        assert_eq!(snapshot.events()[2].correlation_id(), "corr-c");
    }

    #[test]
    fn audit_report_counts_approved_completed_and_blocked_events() {
        let sink = InMemoryRuntimeExecutionAuditSink::new();
        let mut sink = sink;
        sink.record(RuntimeExecutionAuditEvent::Approved(
            RuntimeExecutionApprovalReceipt::new("corr-a", "idem-a", "human-operator", 1_000),
        ));
        sink.record(RuntimeExecutionAuditEvent::Completed(
            RuntimeExecutionResult::dry_run_completed("corr-b", "idem-b", "completed one"),
        ));
        sink.record(RuntimeExecutionAuditEvent::Blocked(
            RuntimeExecutionResult::blocked_denied("corr-c", "idem-c", "blocked one"),
        ));

        let report = sink.report();

        assert_eq!(report.total_count(), 3);
        assert_eq!(report.approved_count(), 1);
        assert_eq!(report.completed_count(), 1);
        assert_eq!(report.blocked_count(), 1);
        assert_eq!(report.events().len(), 3);
    }

    #[test]
    fn controller_does_not_perform_live_execution() {
        let sink = InMemoryRuntimeExecutionAuditSink::new();
        let controller = DryRunRuntimeController::new(
            SafeRuntimeExecutionPolicy,
            DryRunRuntimeExecutor::default(),
            sink,
        );

        let command = RuntimeExecutionCommand::new(
            "corr-phase-4-live",
            "idem-phase-4-live",
            RuntimeExecutionKind::ShellCommand,
            "attempt shell command",
            true,
        );

        let result = controller.execute(&command, None);

        assert_eq!(result.status(), &RuntimeExecutionStatus::BlockedDenied);
        assert!(result
            .message()
            .contains("outside the Phase 3 dry-run boundary"));
        assert_eq!(controller.snapshot().blocked_count(), 1);
    }
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
