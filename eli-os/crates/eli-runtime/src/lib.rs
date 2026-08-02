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
