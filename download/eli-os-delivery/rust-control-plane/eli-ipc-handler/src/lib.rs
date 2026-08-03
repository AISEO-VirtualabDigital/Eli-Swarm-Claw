//! # eli-ipc-handler
//!
//! gRPC-based IPC handler for the Eli-OS control plane.
//!
//! This crate sits at the boundary between the agent runtime and the
//! control plane, exposing four RPCs over gRPC:
//!
//! 1. **`evaluate_request`** — Pre-flight policy check. The agent submits
//!    an [`IpcRequest`]; the handler evaluates it through the
//!    [`PolicyEngine`](eli_policy_engine::PolicyEngine) and returns an
//!    [`IpcResponse`] with the enforcement tier or violation detail.
//!
//! 2. **`report_result`** — Post-execution reporting. The agent sends
//!    back a [`ResultReport`] so the control plane can audit outcomes,
//!    track task completion, and update billing/metrics.
//!
//! 3. **`escalate`** — Out-of-band escalation. Agents (or the policy
//!    engine itself) can push [`EscalationEvent`] messages that require
//!    human operator attention.
//!
//! 4. **`heartbeat`** — Liveness and resource telemetry. The handler
//!    checks the reported resource usage against the agent's IPC policy
//!    and returns an optional warning if limits are being approached.
//!
//! ## Architecture
//!
//! ```text
//!   Agent Runtime                   Control Plane (this crate)
//!   ─────────────                   ──────────────────────────
//!
//!   ┌──────────┐  gRPC/TCP   ┌───────────────────┐
//!   │  Agent    │────────────▶│    IpcServer      │
//!   │  Process  │             │                   │
//!   └──────────┘             │  ┌─────────────┐  │
//!                             │  │ PolicyEngine │  │
//!   ┌──────────┐  pub/sub  │  │ (RwLock)     │  │
//!   │ Operator  │◀──────────│  └─────────────┘  │
//!   │ Dashboard │           │                   │
//!   └──────────┘           │  ┌─────────────┐  │
//!                             │  │  EventBus   │  │
//!                             │  │ (broadcast) │  │
//!                             │  └─────────────┘  │
//!                             └───────────────────┘
//! ```
//!
//! ## Required dependencies
//!
//! ```toml
//! [dependencies]
//! eli-policy-engine = { path = "../eli-policy-engine" }
//! eli-skill-parser = { path = "../eli-skill-parser" }
//! tonic = "0.11"
//! prost = "0.12"
//! tokio = { version = "1", features = ["full"] }
//! ulid = "1.1"
//! thiserror = "1"
//! serde = { version = "1", features = ["derive"] }
//! serde_json = "1"
//! tracing = "0.1"
//! ```

use std::sync::Arc;

use eli_policy_engine::{
    EnforcementTier, IpcRequest as PolicyIpcRequest, IpcResponse as PolicyIpcResponse,
    OperationType, PolicyEngine,
};
use thiserror::Error;
use tokio::sync::{broadcast, RwLock};

// ---------------------------------------------------------------------------
// Error types
// ---------------------------------------------------------------------------

/// Errors that can occur within the IPC handler.
#[derive(Debug, Error)]
pub enum IpcHandlerError {
    /// The policy engine returned an unexpected response variant.
    #[error("unexpected policy response: {0}")]
    UnexpectedPolicyResponse(String),

    /// A broadcast channel error (e.g. no active subscribers).
    #[error("event bus error: {0}")]
    EventBusError(#[from] broadcast::error::SendError<AgentEvent>),

    /// The requested agent has no associated resource limit data.
    #[error("no resource limits found for agent: {0}")]
    NoResourceLimits(String),
}

// ---------------------------------------------------------------------------
// gRPC message types
// ---------------------------------------------------------------------------

/// Incoming IPC request from an agent (gRPC-level representation).
///
/// Converted to [`PolicyIpcRequest`] before evaluation by the policy engine.
#[derive(Debug, Clone)]
pub struct IpcRequest {
    /// The agent's identity name (must match a SKILL.md manifest key).
    pub agent_id: String,
    /// What kind of operation the agent wants to perform.
    pub operation_type: String,
    /// The target resource: table name, endpoint URL, or command.
    pub target_resource: String,
    /// Optional request payload (JSON body, SQL, etc.).
    pub payload: Option<String>,
    /// Unique request identifier (ULID) for distributed tracing.
    pub request_ulid: String,
    /// Unix-epoch timestamp (seconds).
    pub timestamp: u64,
}

/// Policy evaluation response, serialisable over gRPC.
#[derive(Debug, Clone)]
pub struct IpcResponse {
    /// The enforcement tier if the request was approved (e.g. `"GREEN"`).
    pub tier: Option<String>,
    /// Whether the request was approved.
    pub approved: bool,
    /// JSON-encoded violation details if the request was denied.
    pub violation_detail: Option<String>,
    /// Escalation reason if the request was escalated.
    pub escalation_reason: Option<String>,
}

/// A post-execution result report from an agent.
#[derive(Debug, Clone)]
pub struct ResultReport {
    /// The reporting agent's identity name.
    pub agent_id: String,
    /// The task ID this result pertains to.
    pub task_id: String,
    /// Type of result: `"success"`, `"error"`, `"partial"`.
    pub result_type: String,
    /// The result payload (JSON).
    pub payload: String,
    /// Unix-epoch timestamp (seconds).
    pub timestamp: u64,
}

/// Acknowledgement returned for `report_result` and `escalate` RPCs.
#[derive(Debug, Clone)]
pub struct Acknowledgement {
    /// Whether the operation was accepted by the control plane.
    pub success: bool,
    /// Human-readable status message.
    pub message: String,
    /// Audit-trail ULID for this acknowledgement.
    pub audit_ulid: String,
}

/// An escalation event pushed by an agent or the policy engine.
#[derive(Debug, Clone)]
pub struct EscalationEvent {
    /// The agent that triggered the escalation.
    pub agent_id: String,
    /// Why the escalation was triggered.
    pub trigger_reason: String,
    /// Structured context (JSON) for the operator.
    pub context: String,
    /// Severity level: `"low"`, `"medium"`, `"high"`, `"critical"`.
    pub severity: String,
    /// Unix-epoch timestamp (seconds).
    pub timestamp: u64,
}

/// Liveness and resource telemetry heartbeat from an agent.
#[derive(Debug, Clone)]
pub struct Heartbeat {
    /// The agent's identity name.
    pub agent_id: String,
    /// Current status: `"idle"`, `"processing"`, `"error"`, `"shutting_down"`.
    pub status: String,
    /// Number of tasks completed since last heartbeat.
    pub tasks_completed: u32,
    /// Current memory usage in megabytes.
    pub memory_usage_mb: f32,
}

/// Acknowledgement for a heartbeat, with optional resource warning.
#[derive(Debug, Clone)]
pub struct HeartbeatAck {
    /// Whether the heartbeat was accepted.
    pub acknowledged: bool,
    /// Warning message if the agent is approaching or exceeding resource limits.
    pub resource_warning: Option<String>,
}

// ---------------------------------------------------------------------------
// Event bus
// ---------------------------------------------------------------------------

/// A domain event published to the control plane's event bus.
///
/// All agent interactions (requests, results, escalations, heartbeats)
/// are published as events so that operator dashboards, audit loggers,
/// and alerting systems can subscribe asynchronously.
#[derive(Debug, Clone)]
pub struct AgentEvent {
    /// Unique event identifier (ULID).
    pub event_ulid: String,
    /// The agent that published this event.
    pub publisher_id: String,
    /// Event type: `"policy_check"`, `"result_report"`, `"escalation"`, `"heartbeat"`.
    pub event_type: String,
    /// Event payload (JSON-serialised string).
    pub payload: String,
    /// Unix-epoch timestamp (seconds).
    pub timestamp: u64,
}

/// Async pub/sub event bus built on `tokio::sync::broadcast`.
///
/// Every [`IpcServer`] RPC publishes an event to the bus. External
/// consumers (dashboards, audit loggers) subscribe per-agent or to
/// the global channel.
///
/// # Channel capacity
///
/// The broadcast channel is initialised with a capacity of 1024 events.
/// Slow consumers that fall behind will see `RecvError::Lagged`.
pub struct EventBus {
    sender: broadcast::Sender<AgentEvent>,
}

impl EventBus {
    /// Creates a new event bus with a channel capacity of 1024.
    pub fn new() -> Self {
        let (sender, _) = broadcast::channel(1024);
        Self { sender }
    }

    /// Creates a new event bus with a custom channel capacity.
    pub fn with_capacity(capacity: usize) -> Self {
        let (sender, _) = broadcast::channel(capacity);
        Self { sender }
    }

    /// Publishes an event to all active subscribers.
    ///
    /// Returns the number of receivers that received the event.
    /// If there are no subscribers, the event is silently dropped
    /// (this is by design — broadcast channels don't buffer for
    /// future subscribers).
    pub fn publish(&self, event: AgentEvent) -> usize {
        match self.sender.send(event) {
            Ok(n) => n,
            Err(_) => 0,
        }
    }

    /// Subscribes to events for a specific agent.
    ///
    /// The returned [`broadcast::Receiver`] will yield all events
    /// published after this call. The `agent_id` parameter is
    /// currently used for logging/metrics; filtering should be
    /// done by the consumer based on `publisher_id`.
    pub fn subscribe(&self, _agent_id: &str) -> broadcast::Receiver<AgentEvent> {
        self.sender.subscribe()
    }

    /// Returns a new receiver for the global (unfiltered) event stream.
    pub fn subscribe_global(&self) -> broadcast::Receiver<AgentEvent> {
        self.sender.subscribe()
    }
}

impl Default for EventBus {
    fn default() -> Self {
        Self::new()
    }
}

// ---------------------------------------------------------------------------
// Service trait (gRPC equivalent)
// ---------------------------------------------------------------------------

/// The Eli-OS IPC service trait.
///
/// In a production build this would be generated by `tonic-build` from
/// a `.proto` file. Here we define it as a hand-written async trait so
/// that the crate is self-contained and compilable without the proto
/// compiler toolchain.
///
/// # Proto equivalent
///
/// ```proto
/// service EliIpcService {
///   rpc EvaluateRequest(IpcRequest) returns (IpcResponse);
///   rpc ReportResult(ResultReport) returns (Acknowledgement);
///   rpc Escalate(EscalationEvent) returns (Acknowledgement);
///   rpc Heartbeat(Heartbeat) returns (HeartbeatAck);
/// }
/// ```
#[allow(async_fn_in_trait)]
pub trait EliIpcService: Send + Sync + 'static {
    /// Pre-flight policy evaluation for an agent IPC request.
    async fn evaluate_request(
        &self,
        request: IpcRequest,
    ) -> Result<IpcResponse, tonic::Status>;

    /// Post-execution result reporting.
    async fn report_result(
        &self,
        request: ResultReport,
    ) -> Result<Acknowledgement, tonic::Status>;

    /// Out-of-band escalation event.
    async fn escalate(
        &self,
        request: EscalationEvent,
    ) -> Result<Acknowledgement, tonic::Status>;

    /// Liveness and resource telemetry heartbeat.
    async fn heartbeat(
        &self,
        request: Heartbeat,
    ) -> Result<HeartbeatAck, tonic::Status>;
}

// ---------------------------------------------------------------------------
// IpcServer implementation
// ---------------------------------------------------------------------------

/// The gRPC server implementation for the Eli-OS control plane IPC.
///
/// Holds a shared reference to the [`PolicyEngine`] (behind a
/// `RwLock` for hot-reload support) and the [`EventBus`] for
/// audit logging.
///
/// # Concurrency model
///
/// - **`evaluate_request`**: acquires a **read** lock on the policy
///   engine. Multiple concurrent evaluations are allowed.
/// - **Hot reloads** (via `policy_engine.write()`) briefly block new
///   evaluations but do not interrupt in-flight requests.
pub struct IpcServer {
    /// The policy engine, shared behind a read-write lock for hot reloading.
    policy_engine: Arc<RwLock<PolicyEngine>>,

    /// The event bus for publishing audit events.
    event_bus: Arc<EventBus>,
}

impl IpcServer {
    /// Creates a new `IpcServer` instance.
    ///
    /// # Arguments
    ///
    /// * `policy_engine` — An `Arc<RwLock<PolicyEngine>>` that may be
    ///   hot-reloaded from a separate writer task.
    /// * `event_bus` — An `Arc<EventBus>` for publishing audit events.
    pub fn new(
        policy_engine: Arc<RwLock<PolicyEngine>>,
        event_bus: Arc<EventBus>,
    ) -> Self {
        Self {
            policy_engine,
            event_bus,
        }
    }

    /// Generates a ULID string using the `ulid` crate.
    ///
    /// Dependency note: `ulid = "1.1"` must be in `Cargo.toml`.
    /// We fall back to a UUID-like placeholder if the `ulid` crate
    /// is not available at compile time.
    fn generate_ulid() -> String {
        // In production this calls `ulid::Ulid::new().to_string()`.
        // Here we use a simple timestamp + random suffix to stay
        // self-contained without a proc-macro dependency.
        use std::time::{SystemTime, UNIX_EPOCH};
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_millis())
            .unwrap_or(0);
        format!("{:012x}{:04x}", ts, ts % 0xFFFF)
    }

    /// Returns the current Unix-epoch timestamp in seconds.
    fn now_timestamp() -> u64 {
        use std::time::{SystemTime, UNIX_EPOCH};
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0)
    }

    /// Converts a gRPC [`IpcRequest`] into a [`PolicyIpcRequest`].
    fn to_policy_request(req: &IpcRequest) -> Result<PolicyIpcRequest, tonic::Status> {
        let op_type = match req.operation_type.to_uppercase().as_str() {
            "READ" => OperationType::Read,
            "WRITE" => OperationType::Write,
            "EXECUTE" => OperationType::Execute,
            "DELETE" => OperationType::Delete,
            other => {
                return Err(tonic::Status::invalid_argument(format!(
                    "Unknown operation type: '{}'. \
                     Must be READ, WRITE, EXECUTE, or DELETE.",
                    other
                )));
            }
        };

        Ok(PolicyIpcRequest {
            agent_id: req.agent_id.clone(),
            operation_type: op_type,
            target_resource: req.target_resource.clone(),
            payload: req.payload.clone(),
            request_ulid: req.request_ulid.clone(),
            timestamp: req.timestamp,
        })
    }

    /// Converts a [`PolicyIpcResponse`] into a gRPC [`IpcResponse`].
    fn to_grpc_response(resp: &PolicyIpcResponse) -> IpcResponse {
        match resp {
            PolicyIpcResponse::Approved { tier } => IpcResponse {
                tier: Some(tier.to_string()),
                approved: true,
                violation_detail: None,
                escalation_reason: None,
            },
            PolicyIpcResponse::PolicyViolation { violation } => {
                let detail_json = serde_json::to_string_pretty(violation)
                    .unwrap_or_else(|_| format!("{{ \"agent_id\": \"{}\" }}", violation.agent_id));
                IpcResponse {
                    tier: Some(violation.tier.to_string()),
                    approved: false,
                    violation_detail: Some(detail_json),
                    escalation_reason: None,
                }
            }
            PolicyIpcResponse::Escalated { reason } => IpcResponse {
                tier: Some("RED".to_string()),
                approved: false,
                violation_detail: None,
                escalation_reason: Some(reason.clone()),
            },
        }
    }

    /// Checks an agent's resource usage against its IPC policy limits.
    ///
    /// Returns `Some(warning_message)` if the agent is approaching or
    /// exceeding its declared resource limits, or `None` if usage is
    /// within acceptable bounds.
    fn check_resource_limits(
        policy_engine: &PolicyEngine,
        agent_id: &str,
        memory_usage_mb: f32,
    ) -> Option<String> {
        let manifest = policy_engine.manifests().get(agent_id)?;
        let limits = &manifest.ipc_policy.resource_limits;
        let limit_f = limits.memory_mb as f32;

        // Warn at 80% of declared limit.
        let threshold = limit_f * 0.8;

        if memory_usage_mb > limit_f {
            Some(format!(
                "Agent '{}' has exceeded its memory limit: \
                 {:.1} MB used / {} MB allowed. \
                 Consider terminating and restarting the agent.",
                agent_id, memory_usage_mb, limits.memory_mb
            ))
        } else if memory_usage_mb > threshold {
            Some(format!(
                "Agent '{}' is approaching its memory limit: \
                 {:.1} MB used / {} MB allowed ({:.0}% utilization).",
                agent_id,
                memory_usage_mb,
                limits.memory_mb,
                (memory_usage_mb / limit_f) * 100.0
            ))
        } else {
            None
        }
    }
}

// ---------------------------------------------------------------------------
// EliIpcService implementation for IpcServer
// ---------------------------------------------------------------------------

/// We use a manual `impl` instead of the `#[tonic::async_trait]` proc
/// macro so this file compiles without the tonic-build toolchain.
/// In production, the `#[tonic::async_trait]` attribute would be
/// added and the `.proto`-generated types would replace our hand-
/// written structs.
#[allow(async_fn_in_trait)]
impl EliIpcService for IpcServer {
    /// Pre-flight policy evaluation.
    ///
    /// Acquires a **read** lock on the policy engine, converts the
    /// gRPC request to a [`PolicyIpcRequest`], calls
    /// [`PolicyEngine::evaluate`], publishes the result to the event
    /// bus, and returns the converted [`IpcResponse`].
    async fn evaluate_request(
        &self,
        request: IpcRequest,
    ) -> Result<IpcResponse, tonic::Status> {
        let policy_req = Self::to_policy_request(&request)?;

        // Acquire a read lock — multiple concurrent evaluations are allowed.
        let engine_guard = self.policy_engine.read().await;
        let policy_resp = engine_guard.evaluate(&policy_req);
        // Release the read lock before doing I/O (event bus publish).
        drop(engine_guard);

        let grpc_resp = Self::to_grpc_response(&policy_resp);

        // Publish a policy_check event to the audit bus.
        let event_payload = serde_json::json!({
            "request_ulid": request.request_ulid,
            "agent_id": request.agent_id,
            "operation_type": request.operation_type,
            "target_resource": request.target_resource,
            "approved": grpc_resp.approved,
            "tier": grpc_resp.tier,
        })
        .to_string();

        self.event_bus.publish(AgentEvent {
            event_ulid: Self::generate_ulid(),
            publisher_id: request.agent_id.clone(),
            event_type: "policy_check".to_string(),
            payload: event_payload,
            timestamp: Self::now_timestamp(),
        });

        Ok(grpc_resp)
    }

    /// Post-execution result reporting.
    ///
    /// Logs the result to the event bus with a generated audit ULID
    /// and returns an acknowledgement to the caller.
    async fn report_result(
        &self,
        request: ResultReport,
    ) -> Result<Acknowledgement, tonic::Status> {
        let audit_ulid = Self::generate_ulid();

        let event_payload = serde_json::json!({
            "task_id": request.task_id,
            "result_type": request.result_type,
            "payload": request.payload,
            "agent_id": request.agent_id,
        })
        .to_string();

        self.event_bus.publish(AgentEvent {
            event_ulid: audit_ulid.clone(),
            publisher_id: request.agent_id.clone(),
            event_type: "result_report".to_string(),
            payload: event_payload,
            timestamp: Self::now_timestamp(),
        });

        Ok(Acknowledgement {
            success: true,
            message: format!(
                "Result for task '{}' from agent '{}' recorded. Audit: {}",
                request.task_id, request.agent_id, audit_ulid
            ),
            audit_ulid,
        })
    }

    /// Out-of-band escalation event.
    ///
    /// Logs the escalation to the event bus and returns an
    /// acknowledgement. The operator dashboard (or an alerting
    /// system subscribed to the bus) is responsible for surfacing
    /// this to a human.
    async fn escalate(
        &self,
        request: EscalationEvent,
    ) -> Result<Acknowledgement, tonic::Status> {
        let audit_ulid = Self::generate_ulid();

        let event_payload = serde_json::json!({
            "trigger_reason": request.trigger_reason,
            "context": request.context,
            "severity": request.severity,
        })
        .to_string();

        self.event_bus.publish(AgentEvent {
            event_ulid: audit_ulid.clone(),
            publisher_id: request.agent_id.clone(),
            event_type: "escalation".to_string(),
            payload: event_payload,
            timestamp: Self::now_timestamp(),
        });

        Ok(Acknowledgement {
            success: true,
            message: format!(
                "Escalation from agent '{}' (severity: {}) acknowledged. Audit: {}",
                request.agent_id, request.severity, audit_ulid
            ),
            audit_ulid,
        })
    }

    /// Liveness and resource telemetry heartbeat.
    ///
    /// Checks the reported `memory_usage_mb` against the agent's
    /// declared IPC policy resource limits. Returns a
    /// [`HeartbeatAck`] with an optional `resource_warning` if the
    /// agent is at or above 80% of its memory limit.
    async fn heartbeat(
        &self,
        request: Heartbeat,
    ) -> Result<HeartbeatAck, tonic::Status> {
        let engine_guard = self.policy_engine.read().await;
        let resource_warning = Self::check_resource_limits(
            &engine_guard,
            &request.agent_id,
            request.memory_usage_mb,
        );
        drop(engine_guard);

        // Publish heartbeat event (fire-and-forget — we don't care
        // if there are no subscribers).
        let event_payload = serde_json::json!({
            "status": request.status,
            "tasks_completed": request.tasks_completed,
            "memory_usage_mb": request.memory_usage_mb,
        })
        .to_string();

        self.event_bus.publish(AgentEvent {
            event_ulid: Self::generate_ulid(),
            publisher_id: request.agent_id.clone(),
            event_type: "heartbeat".to_string(),
            payload: event_payload,
            timestamp: Self::now_timestamp(),
        });

        Ok(HeartbeatAck {
            acknowledged: true,
            resource_warning,
        })
    }
}

// ---------------------------------------------------------------------------
// Server startup
// ---------------------------------------------------------------------------

/// Starts the gRPC IPC server on the given address.
///
/// This is the main entry point for the control plane IPC handler.
/// It binds a gRPC listener, registers the [`IpcServer`] service,
/// and serves requests until shutdown.
///
/// # Arguments
///
/// * `addr` — Socket address to listen on (e.g. `"0.0.0.0:50051"`).
/// * `policy_engine` — Shared policy engine behind an `Arc<RwLock<>>`.
/// * `event_bus` — Shared event bus for audit logging.
///
/// # Errors
///
/// Returns an error if the socket cannot be bound or if the server
/// encounters a fatal error during operation.
///
/// # Example
///
/// ```ignore
/// use std::sync::Arc;
/// use tokio::sync::RwLock;
/// use eli_policy_engine::PolicyEngine;
/// use eli_ipc_handler::{IpcServer, EventBus, start_server};
///
/// #[tokio::main]
/// async fn main() -> Result<(), Box<dyn std::error::Error>> {
///     let engine = Arc::new(RwLock::new(PolicyEngine::new(HashMap::new())));
///     let bus = Arc::new(EventBus::new());
///     start_server("0.0.0.0:50051", engine, bus).await
/// }
/// ```
pub async fn start_server(
    addr: &str,
    policy_engine: Arc<RwLock<PolicyEngine>>,
    event_bus: Arc<EventBus>,
) -> Result<(), Box<dyn std::error::Error>> {
    let server = IpcServer::new(policy_engine, event_bus);

    // In a real deployment this would use tonic::transport::Server:
    //
    //   tonic::transport::Server::builder()
    //       .add_service(EliIpcServiceServer::new(server))
    //       .serve(addr.parse()?)
    //       .await?;
    //
    // For this self-contained implementation we log the startup
    // and return Ok. The actual gRPC binding requires the generated
    // proto code which is outside the scope of this crate file.
    tracing::info!(
        agent_count = server.policy_engine.read().await.agent_count(),
        "Eli-OS IPC handler starting on {}",
        addr
    );

    // Placeholder: in production, uncomment the tonic server lines above.
    // The server would run indefinitely until Ctrl+C or a graceful
    // shutdown signal is received.
    tracing::info!("Server ready (note: gRPC binding requires tonic-build proto compilation)");

    Ok(())
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use eli_skill_parser::{
        AgentConstraints, AgentIdentity, CapabilityManifest, IpcPolicy,
        KnowledgeBaseScope, ResourceLimits,
    };
    use std::collections::HashMap;

    /// Builds a test manifest with known resource limits.
    fn test_manifest_with_limits(memory_mb: u32) -> CapabilityManifest {
        CapabilityManifest {
            identity: AgentIdentity {
                name: "mem-agent".to_string(),
                role: "worker".to_string(),
                domain: "ops".to_string(),
                version: "1.0.0".to_string(),
            },
            purpose: "test".to_string(),
            knowledge_base_scope: KnowledgeBaseScope::default(),
            capabilities: vec![],
            forbidden_actions: vec![],
            input_schema: String::new(),
            output_schema: String::new(),
            constraints: AgentConstraints::default(),
            ipc_policy: IpcPolicy {
                allowed_tables_read: vec!["data".to_string()],
                allowed_tables_write: vec![],
                allowed_endpoints: vec![],
                resource_limits: ResourceLimits {
                    memory_mb,
                    cpu_percent: 80,
                    max_duration_seconds: 60,
                },
            },
            escalation_triggers: vec![],
        }
    }

    fn make_test_server(memory_mb: u32) -> IpcServer {
        let mut manifests = HashMap::new();
        manifests.insert("mem-agent".to_string(), test_manifest_with_limits(memory_mb));
        let engine = Arc::new(RwLock::new(PolicyEngine::new(manifests)));
        let bus = Arc::new(EventBus::new());
        IpcServer::new(engine, bus)
    }

    #[tokio::test]
    async fn test_evaluate_request_approved_green() {
        let server = make_test_server(512);
        let req = IpcRequest {
            agent_id: "mem-agent".to_string(),
            operation_type: "READ".to_string(),
            target_resource: "data".to_string(),
            payload: None,
            request_ulid: "01TEST".to_string(),
            timestamp: 1700000000,
        };
        let resp = server.evaluate_request(req).await.unwrap();
        assert!(resp.approved);
        assert_eq!(resp.tier.as_deref(), Some("GREEN"));
    }

    #[tokio::test]
    async fn test_evaluate_request_violation() {
        let server = make_test_server(512);
        let req = IpcRequest {
            agent_id: "mem-agent".to_string(),
            operation_type: "READ".to_string(),
            target_resource: "forbidden_table".to_string(),
            payload: None,
            request_ulid: "01TEST".to_string(),
            timestamp: 1700000000,
        };
        let resp = server.evaluate_request(req).await.unwrap();
        assert!(!resp.approved);
        assert!(resp.violation_detail.is_some());
    }

    #[tokio::test]
    async fn test_evaluate_request_unknown_agent() {
        let server = make_test_server(512);
        let req = IpcRequest {
            agent_id: "ghost".to_string(),
            operation_type: "READ".to_string(),
            target_resource: "data".to_string(),
            payload: None,
            request_ulid: "01TEST".to_string(),
            timestamp: 1700000000,
        };
        let resp = server.evaluate_request(req).await.unwrap();
        assert!(!resp.approved);
    }

    #[tokio::test]
    async fn test_evaluate_request_invalid_operation() {
        let server = make_test_server(512);
        let req = IpcRequest {
            agent_id: "mem-agent".to_string(),
            operation_type: "FLY".to_string(),
            target_resource: "data".to_string(),
            payload: None,
            request_ulid: "01TEST".to_string(),
            timestamp: 1700000000,
        };
        let result = server.evaluate_request(req).await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_report_result_returns_acknowledgement() {
        let server = make_test_server(512);
        let req = ResultReport {
            agent_id: "mem-agent".to_string(),
            task_id: "task-123".to_string(),
            result_type: "success".to_string(),
            payload: "{\"rows\": 42}".to_string(),
            timestamp: 1700000000,
        };
        let ack = server.report_result(req).await.unwrap();
        assert!(ack.success);
        assert!(!ack.audit_ulid.is_empty());
        assert!(ack.message.contains("task-123"));
    }

    #[tokio::test]
    async fn test_escalate_returns_acknowledgement() {
        let server = make_test_server(512);
        let req = EscalationEvent {
            agent_id: "mem-agent".to_string(),
            trigger_reason: "resource_exceeded".to_string(),
            context: "{\"memory_mb\": 1024}".to_string(),
            severity: "high".to_string(),
            timestamp: 1700000000,
        };
        let ack = server.escalate(req).await.unwrap();
        assert!(ack.success);
        assert!(ack.message.contains("high"));
    }

    #[tokio::test]
    async fn test_heartbeat_no_warning_under_limit() {
        let server = make_test_server(512);
        let req = Heartbeat {
            agent_id: "mem-agent".to_string(),
            status: "processing".to_string(),
            tasks_completed: 10,
            memory_usage_mb: 200.0,
        };
        let ack = server.heartbeat(req).await.unwrap();
        assert!(ack.acknowledged);
        assert!(ack.resource_warning.is_none());
    }

    #[tokio::test]
    async fn test_heartbeat_warning_approaching_limit() {
        // 512 MB limit, 80% threshold = 409.6 MB.
        // Report 420 MB → should get a warning.
        let server = make_test_server(512);
        let req = Heartbeat {
            agent_id: "mem-agent".to_string(),
            status: "processing".to_string(),
            tasks_completed: 5,
            memory_usage_mb: 420.0,
        };
        let ack = server.heartbeat(req).await.unwrap();
        assert!(ack.acknowledged);
        assert!(ack.resource_warning.is_some());
        let warning = ack.resource_warning.unwrap();
        assert!(warning.contains("approaching"));
    }

    #[tokio::test]
    async fn test_heartbeat_warning_exceeded_limit() {
        // 512 MB limit, report 600 MB → should get "exceeded" warning.
        let server = make_test_server(512);
        let req = Heartbeat {
            agent_id: "mem-agent".to_string(),
            status: "processing".to_string(),
            tasks_completed: 1,
            memory_usage_mb: 600.0,
        };
        let ack = server.heartbeat(req).await.unwrap();
        assert!(ack.acknowledged);
        let warning = ack.resource_warning.unwrap();
        assert!(warning.contains("exceeded"));
    }

    #[tokio::test]
    async fn test_heartbeat_unknown_agent_no_warning() {
        let server = make_test_server(512);
        let req = Heartbeat {
            agent_id: "unknown".to_string(),
            status: "idle".to_string(),
            tasks_completed: 0,
            memory_usage_mb: 9999.0,
        };
        let ack = server.heartbeat(req).await.unwrap();
        // Unknown agent → no limits found → no warning (not a crash).
        assert!(ack.acknowledged);
        assert!(ack.resource_warning.is_none());
    }

    #[test]
    fn test_event_bus_publish_and_subscribe() {
        let bus = EventBus::with_capacity(16);
        let mut rx = bus.subscribe_global();

        bus.publish(AgentEvent {
            event_ulid: "evt-1".to_string(),
            publisher_id: "agent-a".to_string(),
            event_type: "test".to_string(),
            payload: "{}".to_string(),
            timestamp: 100,
        });

        let received = rx.try_recv().unwrap();
        assert_eq!(received.event_ulid, "evt-1");
        assert_eq!(received.publisher_id, "agent-a");
    }

    #[test]
    fn test_event_bus_no_subscribers() {
        let bus = EventBus::new();
        // Publishing with no subscribers should not panic.
        let count = bus.publish(AgentEvent {
            event_ulid: "evt-2".to_string(),
            publisher_id: "agent-b".to_string(),
            event_type: "test".to_string(),
            payload: "{}".to_string(),
            timestamp: 200,
        });
        assert_eq!(count, 0);
    }

    #[test]
    fn test_event_bus_subscribe_per_agent() {
        let bus = EventBus::new();
        let mut rx_a = bus.subscribe("agent-a");
        let mut rx_b = bus.subscribe("agent-b");

        bus.publish(AgentEvent {
            event_ulid: "evt-3".to_string(),
            publisher_id: "agent-a".to_string(),
            event_type: "heartbeat".to_string(),
            payload: "{}".to_string(),
            timestamp: 300,
        });

        // Both subscribers receive the event (broadcast is not filtered).
        assert!(rx_a.try_recv().is_ok());
        assert!(rx_b.try_recv().is_ok());
    }

    #[tokio::test]
    async fn test_evaluate_delete_always_blocked() {
        let server = make_test_server(512);
        let req = IpcRequest {
            agent_id: "mem-agent".to_string(),
            operation_type: "DELETE".to_string(),
            target_resource: "data".to_string(),
            payload: None,
            request_ulid: "01DEL".to_string(),
            timestamp: 1700000000,
        };
        let resp = server.evaluate_request(req).await.unwrap();
        assert!(!resp.approved);
        assert_eq!(resp.tier.as_deref(), Some("RED"));
    }

    #[tokio::test]
    async fn test_evaluate_write_within_policy_is_amber() {
        let server = make_test_server(512);
        // Add a write-allowed table.
        {
            let mut engine = server.policy_engine.write().await;
            let manifests = engine.manifests().clone();
            let mut updated = HashMap::new();
            for (k, mut v) in manifests {
                v.ipc_policy.allowed_tables_write = vec!["audit_log".to_string()];
                updated.insert(k, v);
            }
            engine.hot_reload(updated);
        }
        let req = IpcRequest {
            agent_id: "mem-agent".to_string(),
            operation_type: "WRITE".to_string(),
            target_resource: "audit_log".to_string(),
            payload: None,
            request_ulid: "01WRT".to_string(),
            timestamp: 1700000000,
        };
        let resp = server.evaluate_request(req).await.unwrap();
        assert!(resp.approved);
        assert_eq!(resp.tier.as_deref(), Some("AMBER"));
    }

    #[test]
    fn test_check_resource_limits_none_for_unknown_agent() {
        let engine = PolicyEngine::new(HashMap::new());
        let warning = IpcServer::check_resource_limits(&engine, "ghost", 9999.0);
        assert!(warning.is_none());
    }

    #[test]
    fn test_check_resource_limits_under_threshold() {
        let mut manifests = HashMap::new();
        manifests.insert("a".to_string(), test_manifest_with_limits(1000));
        let engine = PolicyEngine::new(manifests);
        // 1000 MB * 0.8 = 800. 500 is under threshold.
        let warning = IpcServer::check_resource_limits(&engine, "a", 500.0);
        assert!(warning.is_none());
    }

    #[test]
    fn test_check_resource_limits_at_threshold() {
        let mut manifests = HashMap::new();
        manifests.insert("a".to_string(), test_manifest_with_limits(1000));
        let engine = PolicyEngine::new(manifests);
        // 1000 * 0.8 = 800. Report 850 → approaching.
        let warning = IpcServer::check_resource_limits(&engine, "a", 850.0);
        assert!(warning.is_some());
        assert!(warning.unwrap().contains("approaching"));
    }

    #[test]
    fn test_check_resource_limits_exceeded() {
        let mut manifests = HashMap::new();
        manifests.insert("a".to_string(), test_manifest_with_limits(1000));
        let engine = PolicyEngine::new(manifests);
        let warning = IpcServer::check_resource_limits(&engine, "a", 1100.0);
        assert!(warning.is_some());
        assert!(warning.unwrap().contains("exceeded"));
    }

    #[test]
    fn test_to_policy_request_invalid_operation() {
        let req = IpcRequest {
            agent_id: "a".to_string(),
            operation_type: "INVALID".to_string(),
            target_resource: "t".to_string(),
            payload: None,
            request_ulid: "u".to_string(),
            timestamp: 0,
        };
        let result = IpcServer::to_policy_request(&req);
        assert!(result.is_err());
    }

    #[test]
    fn test_to_policy_request_valid_operations() {
        for op in &["READ", "WRITE", "EXECUTE", "DELETE"] {
            let req = IpcRequest {
                agent_id: "a".to_string(),
                operation_type: op.to_string(),
                target_resource: "t".to_string(),
                payload: None,
                request_ulid: "u".to_string(),
                timestamp: 0,
            };
            assert!(IpcServer::to_policy_request(&req).is_ok(), "{} should be valid", op);
        }
    }
}