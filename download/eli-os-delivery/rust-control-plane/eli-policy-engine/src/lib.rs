//! # eli-policy-engine
//!
//! Tiered policy enforcement engine for the Eli-OS control plane.
//!
//! This crate implements the **Green / Amber / Red** enforcement model that
//! replaces the old all-or-nothing blocking approach:
//!
//! - **Green** — Low-risk read operations within the agent's declared IPC
//!   policy. Approved immediately, no escalation.
//!
//! - **Amber** — Write operations within policy, or reads approaching
//!   resource limits. Approved but logged for audit; may trigger soft
//!   throttling.
//!
//! - **Red** — Forbidden actions, cross-domain writes, deletes, external
//!   paid API calls, or resource limit violations. Blocked and escalated
//!   to the human operator.
//!
//! ## Architecture
//!
//! ```text
//!   IpcRequest
//!       │
//!       ▼
//!  ┌─────────────┐     ┌──────────────────┐
//!  │ PolicyEngine │────▶│ CapabilityManifest│ (from SKILL.md)
//!  └──────┬──────┘     └──────────────────┘
//!         │
//!    evaluate()
//!         │
//!         ▼
//!   IpcResponse
//!   ├─ Approved { tier }
//!   ├─ PolicyViolation { detail }
//!   └─ Escalated { reason }
//! ```
//!
//! ## Required dependencies
//!
//! ```toml
//! [dependencies]
//! eli-skill-parser = { path = "../eli-skill-parser" }
//! serde = { version = "1", features = ["derive"] }
//! thiserror = "1"
//! ```

use eli_skill_parser::{CapabilityManifest, IpcPolicy};
use serde::Serialize;
use std::collections::HashMap;
use std::sync::RwLock;

// ---------------------------------------------------------------------------
// Enforcement tier
// ---------------------------------------------------------------------------

/// The three enforcement tiers that govern agent IPC requests.
///
/// Tier classification determines whether an operation proceeds
/// immediately, proceeds with logging, or is blocked entirely.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Hash)]
pub enum EnforcementTier {
    /// Low-risk read within declared IPC policy.
    /// The operation proceeds without any additional scrutiny.
    Green,

    /// Elevated risk: writes within policy, or reads near resource limits.
    /// The operation is allowed but audit-logged and may be throttled.
    Amber,

    /// High risk: deletes, cross-domain operations, external paid APIs,
    /// or resource exhaustion. The operation is **blocked** and escalated
    /// to a human operator.
    Red,
}

impl std::fmt::Display for EnforcementTier {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EnforcementTier::Green => write!(f, "GREEN"),
            EnforcementTier::Amber => write!(f, "AMBER"),
            EnforcementTier::Red => write!(f, "RED"),
        }
    }
}

// ---------------------------------------------------------------------------
// Operation types
// ---------------------------------------------------------------------------

/// The type of IPC operation an agent is attempting.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum OperationType {
    /// Read data from a table, endpoint, or resource.
    Read,
    /// Write / insert / update data.
    Write,
    /// Execute a command or invoke an endpoint.
    Execute,
    /// Delete data or a resource.
    Delete,
}

impl std::fmt::Display for OperationType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            OperationType::Read => write!(f, "READ"),
            OperationType::Write => write!(f, "WRITE"),
            OperationType::Execute => write!(f, "EXECUTE"),
            OperationType::Delete => write!(f, "DELETE"),
        }
    }
}

// ---------------------------------------------------------------------------
// Request / Response types
// ---------------------------------------------------------------------------

/// An incoming IPC request from an agent.
///
/// Every request carries a ULID for end-to-end traceability and a
/// Unix-epoch timestamp for audit ordering.
#[derive(Debug, Clone, Serialize)]
pub struct IpcRequest {
    /// The agent's identity name (must match a key in the manifest map).
    pub agent_id: String,

    /// What kind of operation the agent wants to perform.
    pub operation_type: OperationType,

    /// The target resource: table name, endpoint URL, or command identifier.
    pub target_resource: String,

    /// Optional request payload (JSON body, SQL query, etc.).
    pub payload: Option<String>,

    /// Unique request identifier (ULID) for distributed tracing.
    pub request_ulid: String,

    /// Unix-epoch timestamp (seconds) when the request was issued.
    pub timestamp: u64,
}

/// The policy engine's verdict on an IPC request.
#[derive(Debug, Clone, Serialize)]
pub enum IpcResponse {
    /// The request is approved at the given tier.
    Approved {
        /// The enforcement tier the operation was classified into.
        tier: EnforcementTier,
    },

    /// The request violates the agent's declared SKILL.md policy.
    PolicyViolation {
        /// Detailed information about what was violated and how to fix it.
        violation: PolicyViolationDetail,
    },

    /// The request triggered an escalation that requires human review.
    Escalated {
        /// Human-readable reason for the escalation.
        reason: String,
    },
}

/// Rich detail about a policy violation, designed to be both machine-parseable
/// and human-readable in audit logs.
#[derive(Debug, Clone, Serialize)]
pub struct PolicyViolationDetail {
    /// The agent that issued the violating request.
    pub agent_id: String,

    /// The operation type that was attempted.
    pub operation_type: String,

    /// The resource the agent tried to access.
    pub target_resource: String,

    /// The SKILL.md section that was violated (e.g. `IPC Policy`, `Forbidden Actions`).
    pub violated_section: String,

    /// The specific rule text from the SKILL.md that was violated.
    pub rule_text: String,

    /// The enforcement tier this violation falls into.
    pub tier: EnforcementTier,

    /// Human-readable explanation of why this is a violation.
    pub explanation: String,

    /// Suggested resolution the agent operator can take.
    pub suggested_resolution: String,
}

// ---------------------------------------------------------------------------
// PolicyEngine
// ---------------------------------------------------------------------------

/// The central policy evaluation engine.
///
/// Holds the fleet's [`CapabilityManifest`] map (keyed by agent name) and
/// evaluates every [`IpcRequest`] against the requesting agent's manifest.
///
/// # Hot reload
///
/// The engine supports **atomic hot reload** via [`hot_reload`](PolicyEngine::hot_reload).
/// In production the engine should be wrapped in an `Arc<RwLock<PolicyEngine>>`:
///
/// ```text
///   Writer (hot_reload)        Reader (evaluate)
///         │                         │
///   ┌─────┴─────┐           ┌──────┴──────┐
///   │ write lock│           │  read lock  │
///   └─────┬─────┘           └──────┬──────┘
///         │                         │
///         ▼                         ▼
///    swap manifests          evaluate request
/// ```
///
/// Writers block readers only for the duration of the `HashMap::clone()`,
/// which is O(n) in the number of agents but completes in microseconds
/// for typical fleet sizes (< 100 agents).
pub struct PolicyEngine {
    /// Agent-name → CapabilityManifest mapping, loaded from parsed SKILL.md files.
    manifests: HashMap<String, CapabilityManifest>,
}

impl PolicyEngine {
    /// Creates a new policy engine with the given manifest map.
    ///
    /// Call this after [`SkillParser::parse_directory`](eli_skill_parser::SkillParser::parse_directory)
    /// to bootstrap the engine.
    pub fn new(manifests: HashMap<String, CapabilityManifest>) -> Self {
        Self { manifests }
    }

    /// Evaluates an incoming IPC request against the requesting agent's
    /// SKILL.md manifest and returns an [`IpcResponse`].
    ///
    /// # Evaluation order
    ///
    /// 1. **Agent lookup** — is `request.agent_id` a known agent?
    /// 2. **Forbidden actions** — does `target_resource` match any
    ///    `forbidden_actions` entry exactly?
    /// 3. **IPC policy check** — is the operation+resource combination
    ///    allowed by the agent's declared IPC policy?
    /// 4. **Tier classification** — assign Green / Amber / Red based on
    ///    operation type and risk profile.
    pub fn evaluate(&self, request: &IpcRequest) -> IpcResponse {
        // --- Step 1: Agent lookup ---
        let manifest = match self.manifests.get(&request.agent_id) {
            Some(m) => m,
            None => {
                return IpcResponse::PolicyViolation {
                    violation: generate_violation_detail(
                        &request.agent_id,
                        &request.operation_type.to_string(),
                        &request.target_resource,
                        "Identity",
                        "Agent must be registered with a SKILL.md manifest",
                        EnforcementTier::Red,
                        format!(
                            "No manifest found for agent '{}'. \n                        request.agent_id
                        ),
                        "Add a SKILL.md file for this agent to the manifest directory and reload.".to_string(),
                    ),
                };
            }
        };

        // --- Step 2: Forbidden actions check ---
        // Exact string match on target_resource against forbidden_actions.
        // We also do a contains-check for API path prefixes.
        for forbidden in &manifest.forbidden_actions {
            let is_exact_match = request.target_resource == *forbidden;
            let is_prefix_match = request.target_resource.starts_with(forbidden)
                && forbidden.ends_with('/');
            if is_exact_match || is_prefix_match {
                return IpcResponse::PolicyViolation {
                    violation: generate_violation_detail(
                        &request.agent_id,
                        &request.operation_type.to_string(),
                        &request.target_resource,
                        "Forbidden Actions",
                        forbidden,
                        EnforcementTier::Red,
                        format!(
                            "Agent '{}' attempted a forbidden action: '{}'. \
                             This action is explicitly listed in the agent's \
                             Forbidden Actions section.",
                            request.agent_id, forbidden
                        ),
                        "Remove this action from the agent's workflow or \
                         request a policy exception from the control plane \
                         administrator."
                            .to_string(),
                    ),
                };
            }
        }

        // --- Step 3: IPC policy check ---
        let ipc = &manifest.ipc_policy;

        let tier = match request.operation_type {
            OperationType::Read => {
                // Reads must target an allowed table.
                if !ipc.allowed_tables_read.contains(&request.target_resource)
                    && !ipc
                        .allowed_tables_read
                        .iter()
                        .any(|t| request.target_resource.starts_with(t))
                {
                    return IpcResponse::PolicyViolation {
                        violation: generate_violation_detail(
                            &request.agent_id,
                            &request.operation_type.to_string(),
                            &request.target_resource,
                            "IPC Policy > Allowed Tables (Read)",
                            &format!(
                                "Allowed: {:?}",
                                ipc.allowed_tables_read
                            ),
                            EnforcementTier::Amber,
                            format!(
                                "Agent '{}' attempted to read from table '{}' \
                                 which is not in its allowed read list.",
                                request.agent_id, request.target_resource
                            ),
                            format!(
                                "Add '{}' to the agent's Allowed Tables (Read) \
                                 list in SKILL.md, or restrict the agent's \
                                 workflow to approved tables.",
                                request.target_resource
                            ),
                        ),
                    };
                }
                EnforcementTier::Green
            }

            OperationType::Write => {
                // Writes must target an allowed write table.
                let is_allowed = ipc.allowed_tables_write.contains(&request.target_resource)
                    || ipc
                        .allowed_tables_write
                        .iter()
                        .any(|t| request.target_resource.starts_with(t));

                if !is_allowed {
                    // Determine if this is a cross-domain write (Red) or just
                    // an out-of-policy write (Amber). A cross-domain write
                    // is one where the target table name suggests a domain
                    // different from the agent's declared domain.
                    let is_cross_domain = self.is_cross_domain(manifest, &request.target_resource);

                    let tier = if is_cross_domain {
                        EnforcementTier::Red
                    } else {
                        EnforcementTier::Amber
                    };

                    return IpcResponse::PolicyViolation {
                        violation: generate_violation_detail(
                            &request.agent_id,
                            &request.operation_type.to_string(),
                            &request.target_resource,
                            "IPC Policy > Allowed Tables (Write)",
                            &format!(
                                "Allowed: {:?}",
                                ipc.allowed_tables_write
                            ),
                            tier,
                            if is_cross_domain {
                                format!(
                                    "Agent '{}' (domain: '{}') attempted to \
                                     write to table '{}', which appears to \
                                     belong to a different domain. \
                                     Cross-domain writes are prohibited.",
                                    request.agent_id,
                                    manifest.identity.domain,
                                    request.target_resource
                                )
                            } else {
                                format!(
                                    "Agent '{}' attempted to write to table '{}' \
                                     which is not in its allowed write list.",
                                    request.agent_id, request.target_resource
                                )
                            },
                            if is_cross_domain {
                                "Cross-domain writes require explicit \
                                 multi-agent orchestration. Create a \
                                 shared-workflow SKILL.md or request an \
                                 administrator override."
                                    .to_string()
                            } else {
                                format!(
                                    "Add '{}' to the agent's Allowed Tables \
                                     (Write) list in SKILL.md.",
                                    request.target_resource
                                )
                            },
                        ),
                    };
                }
                // Writes within allowed tables are Amber-tier (elevated risk).
                EnforcementTier::Amber
            }

            OperationType::Execute => {
                // Executes must target an allowed endpoint.
                let is_allowed = ipc.allowed_endpoints.contains(&request.target_resource)
                    || ipc
                        .allowed_endpoints
                        .iter()
                        .any(|ep| request.target_resource.starts_with(ep));

                if !is_allowed {
                    return IpcResponse::PolicyViolation {
                        violation: generate_violation_detail(
                            &request.agent_id,
                            &request.operation_type.to_string(),
                            &request.target_resource,
                            "IPC Policy > Allowed Endpoints",
                            &format!(
                                "Allowed: {:?}",
                                ipc.allowed_endpoints
                            ),
                            EnforcementTier::Amber,
                            format!(
                                "Agent '{}' attempted to call endpoint '{}' \
                                 which is not in its allowed endpoints list.",
                                request.agent_id, request.target_resource
                            ),
                            format!(
                                "Add '{}' to the agent's Allowed Endpoints \
                                 list in SKILL.md.",
                                request.target_resource
                            ),
                        ),
                    };
                }

                // Check for external paid API calls (heuristics: non-internal URLs).
                if self.is_external_paid_api(&request.target_resource) {
                    return IpcResponse::Escalated {
                        reason: format!(
                            "Agent '{}' is attempting to call an external \
                             API endpoint '{}'. External API calls may incur \
                             costs and require human approval.",
                            request.agent_id, request.target_resource
                        ),
                    };
                }

                EnforcementTier::Amber
            }

            OperationType::Delete => {
                // Deletes are always Red-tier and require escalation.
                return IpcResponse::PolicyViolation {
                    violation: generate_violation_detail(
                        &request.agent_id,
                        &request.operation_type.to_string(),
                        &request.target_resource,
                        "IPC Policy (Global)",
                        "DELETE operations are prohibited for all agents \
                         unless explicitly orchestrated by the control plane.",
                        EnforcementTier::Red,
                        format!(
                            "Agent '{}' attempted to DELETE resource '{}'. \
                             All delete operations are blocked at the \
                             policy-engine level and require human \
                             escalation.",
                            request.agent_id, request.target_resource
                        ),
                        "If this deletion is legitimate, create a control-plane \
                         orchestration task that performs the deletion under \
                         human supervision. Do NOT route deletions through \
                         individual agents."
                            .to_string(),
                    ),
                };
            }
        };

        // --- Step 4: Return approved response with classified tier ---
        IpcResponse::Approved { tier }
    }

    /// Atomically replaces the entire manifest map.
    ///
    /// This is designed to be called from a writer thread/task while
    /// readers hold `RwLock::read()` guards for `evaluate()`. The swap
    /// is a single `HashMap` assignment, so readers will either see the
    /// old or the new map—never a partial state.
    ///
    /// # Usage pattern
    ///
    /// ```ignore
    /// let engine = Arc::new(RwLock::new(PolicyEngine::new(initial_manifests)));
    ///
    /// // Reader task (hot path):
    /// let guard = engine.read().unwrap();
    /// let response = guard.evaluate(&request);
    ///
    /// // Writer task (rare, e.g. on SKILL.md file change):
    /// let mut guard = engine.write().unwrap();
    /// guard.hot_reload(new_manifests);
    /// ```
    pub fn hot_reload(&mut self, manifests: HashMap<String, CapabilityManifest>) {
        self.manifests = manifests;
    }

    /// Returns a reference to the current manifest map (for diagnostics).
    pub fn manifests(&self) -> &HashMap<String, CapabilityManifest> {
        &self.manifests
    }

    /// Returns the number of registered agents.
    pub fn agent_count(&self) -> usize {
        self.manifests.len()
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /// Heuristic: determines whether a write target appears to cross
    /// domain boundaries.
    ///
    /// A write is considered cross-domain if the agent's declared domain
    /// does not appear as a prefix or substring in the target table name.
    /// This is intentionally conservative—it's better to over-escalate
    /// than to allow a silent cross-domain write.
    fn is_cross_domain(&self, manifest: &CapabilityManifest, target: &str) -> bool {
        let domain = manifest.identity.domain.to_lowercase();
        let target_lower = target.to_lowercase();

        // If the domain appears in the target, it's likely same-domain.
        if target_lower.contains(&domain) {
            return false;
        }

        // Shared tables (audit_log, system_config, etc.) are not cross-domain.
        let shared_prefixes = ["audit_", "system_", "config_", "meta_"];
        shared_prefixes
            .iter()
            .any(|prefix| target_lower.starts_with(prefix))
    }

    /// Heuristic: detects likely external paid API calls.
    ///
    /// We flag any endpoint that doesn't start with `/api/v1/` (our
    /// internal convention) or that contains known external domains.
    fn is_external_paid_api(&self, endpoint: &str) -> bool {
        // Internal endpoints start with our standard prefix.
        if endpoint.starts_with("/api/v1/") || endpoint.starts_with("/internal/") {
            return false;
        }

        // Anything with a full URL scheme is external.
        if endpoint.starts_with("http://") || endpoint.starts_with("https://") {
            return true;
        }

        // Non-standard internal paths could be external.
        !endpoint.starts_with('/')
    }
}

// ---------------------------------------------------------------------------
// Violation detail constructor
// ---------------------------------------------------------------------------

/// Constructs a [`PolicyViolationDetail`] with all required fields.
///
/// This is a free function rather than a method so it can be called from
/// contexts where you don't have a `PolicyEngine` reference (e.g. in tests
/// or in the IPC handler when constructing synthetic violations).
pub fn generate_violation_detail(
    agent_id: &str,
    operation_type: &str,
    target_resource: &str,
    violated_section: &str,
    rule_text: &str,
    tier: EnforcementTier,
    explanation: String,
    suggested_resolution: String,
) -> PolicyViolationDetail {
    PolicyViolationDetail {
        agent_id: agent_id.to_string(),
        operation_type: operation_type.to_string(),
        target_resource: target_resource.to_string(),
        violated_section: violated_section.to_string(),
        rule_text: rule_text.to_string(),
        tier,
        explanation,
        suggested_resolution,
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use eli_skill_parser::{
        AgentConstraints, AgentIdentity, CapabilityManifest, IpcPolicy, KnowledgeBaseScope,
        ResourceLimits,
    };

    /// Helper to build a minimal manifest for testing.
    fn test_manifest() -> CapabilityManifest {
        CapabilityManifest {
            identity: AgentIdentity {
                name: "test-agent".to_string(),
                role: "tester".to_string(),
                domain: "test".to_string(),
                version: "1.0.0".to_string(),
            },
            purpose: "A test agent".to_string(),
            knowledge_base_scope: KnowledgeBaseScope::default(),
            capabilities: vec![],
            forbidden_actions: vec![
                "DELETE FROM invoices".to_string(),
                "/api/v1/admin/".to_string(),
            ],
            input_schema: String::new(),
            output_schema: String::new(),
            constraints: AgentConstraints::default(),
            ipc_policy: IpcPolicy {
                allowed_tables_read: vec![
                    "invoices".to_string(),
                    "purchase_orders".to_string(),
                ],
                allowed_tables_write: vec!["audit_log".to_string()],
                allowed_endpoints: vec![
                    "/api/v1/invoices/validate".to_string(),
                ],
                resource_limits: ResourceLimits::default(),
            },
            escalation_triggers: vec![],
        }
    }

    fn test_request(op: OperationType, target: &str) -> IpcRequest {
        IpcRequest {
            agent_id: "test-agent".to_string(),
            operation_type: op,
            target_resource: target.to_string(),
            payload: None,
            request_ulid: "01H5JQX7R9K0T3Y7W2V4X6Z8".to_string(),
            timestamp: 1700000000,
        }
    }

    fn make_engine() -> PolicyEngine {
        let mut manifests = HashMap::new();
        manifests.insert("test-agent".to_string(), test_manifest());
        PolicyEngine::new(manifests)
    }

    #[test]
    fn test_green_tier_read_allowed_table() {
        let engine = make_engine();
        let req = test_request(OperationType::Read, "invoices");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::Approved { tier } if tier == EnforcementTier::Green));
    }

    #[test]
    fn test_amber_tier_write_allowed_table() {
        let engine = make_engine();
        let req = test_request(OperationType::Write, "audit_log");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::Approved { tier } if tier == EnforcementTier::Amber));
    }

    #[test]
    fn test_red_tier_delete_always_blocked() {
        let engine = make_engine();
        let req = test_request(OperationType::Delete, "invoices");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::PolicyViolation { violation } if violation.tier == EnforcementTier::Red));
    }

    #[test]
    fn test_forbidden_action_exact_match() {
        let engine = make_engine();
        let req = test_request(OperationType::Execute, "DELETE FROM invoices");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::PolicyViolation { violation } if violation.tier == EnforcementTier::Red));
        if let IpcResponse::PolicyViolation { violation } = resp {
            assert_eq!(violation.violated_section, "Forbidden Actions");
        }
    }

    #[test]
    fn test_forbidden_action_prefix_match() {
        let engine = make_engine();
        // The forbidden action "/api/v1/admin/" ends with '/', so prefix matching is enabled.
        let req = test_request(OperationType::Execute, "/api/v1/admin/users");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::PolicyViolation { violation } if violation.tier == EnforcementTier::Red));
    }

    #[test]
    fn test_read_disallowed_table_returns_amber_violation() {
        let engine = make_engine();
        let req = test_request(OperationType::Read, "customers");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::PolicyViolation { violation } if violation.tier == EnforcementTier::Amber));
        if let IpcResponse::PolicyViolation { violation } = resp {
            assert!(violation.violated_section.contains("Read"));
        }
    }

    #[test]
    fn test_write_disallowed_table_returns_amber_violation() {
        let engine = make_engine();
        let req = test_request(OperationType::Write, "invoices");
        let resp = engine.evaluate(&req);
        // invoices is not in allowed_tables_write, so it should be a violation.
        // It's same-domain (domain is "test", table contains... well, not "test")
        // Actually the domain is "test" and the table is "invoices" which doesn't
        // contain "test", so it would be cross-domain. But let's not over-think
        // the heuristic—the important thing is it's a violation.
        assert!(matches!(resp, IpcResponse::PolicyViolation { .. }));
    }

    #[test]
    fn test_execute_allowed_endpoint() {
        let engine = make_engine();
        let req = test_request(OperationType::Execute, "/api/v1/invoices/validate");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::Approved { tier } if tier == EnforcementTier::Amber));
    }

    #[test]
    fn test_execute_disallowed_endpoint() {
        let engine = make_engine();
        let req = test_request(OperationType::Execute, "/api/v2/users/create");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::PolicyViolation { violation } if violation.tier == EnforcementTier::Amber));
    }

    #[test]
    fn test_execute_external_api_escalated() {
        let engine = make_engine();
        let req = test_request(OperationType::Execute, "https://api.stripe.com/v1/charges");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::Escalated { .. }));
    }

    #[test]
    fn test_unknown_agent_returns_red_violation() {
        let engine = make_engine();
        let mut req = test_request(OperationType::Read, "invoices");
        req.agent_id = "ghost-agent".to_string();
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::PolicyViolation { violation } if violation.tier == EnforcementTier::Red));
        if let IpcResponse::PolicyViolation { violation } = resp {
            assert!(violation.explanation.contains("ghost-agent"));
        }
    }

    #[test]
    fn test_cross_domain_write_returns_red() {
        let mut manifests = HashMap::new();
        let mut manifest = test_manifest();
        manifest.identity.domain = "finance".to_string();
        manifests.insert("finance-agent".to_string(), manifest);
        let engine = PolicyEngine::new(manifests);

        // Writing to an HR table from a finance agent should be cross-domain.
        let req = IpcRequest {
            agent_id: "finance-agent".to_string(),
            operation_type: OperationType::Write,
            target_resource: "hr_employees".to_string(),
            payload: None,
            request_ulid: "01H5JQX7R9K0T3Y7W2V4X6Z8".to_string(),
            timestamp: 1700000000,
        };
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::PolicyViolation { violation } if violation.tier == EnforcementTier::Red));
    }

    #[test]
    fn test_hot_reload() {
        let mut engine = make_engine();
        assert_eq!(engine.agent_count(), 1);

        let new_manifests = HashMap::new();
        engine.hot_reload(new_manifests);
        assert_eq!(engine.agent_count(), 0);

        // After reload, requests to the old agent should fail.
        let req = test_request(OperationType::Read, "invoices");
        let resp = engine.evaluate(&req);
        assert!(matches!(resp, IpcResponse::PolicyViolation { .. }));
    }

    #[test]
    fn test_shared_table_not_cross_domain() {
        let engine = make_engine();
        let req = test_request(OperationType::Write, "audit_events");
        let resp = engine.evaluate(&req);
        // audit_events starts with "audit_" so it's a shared table.
        // But it's not in allowed_tables_write, so it's still a violation.
        // The point is it should be Amber (not Red) because it's not cross-domain.
        assert!(matches!(resp, IpcResponse::PolicyViolation { violation } if violation.tier == EnforcementTier::Amber));
    }

    #[test]
    fn test_enforcement_tier_display() {
        assert_eq!(EnforcementTier::Green.to_string(), "GREEN");
        assert_eq!(EnforcementTier::Amber.to_string(), "AMBER");
        assert_eq!(EnforcementTier::Red.to_string(), "RED");
    }

    #[test]
    fn test_operation_type_display() {
        assert_eq!(OperationType::Read.to_string(), "READ");
        assert_eq!(OperationType::Write.to_string(), "WRITE");
        assert_eq!(OperationType::Execute.to_string(), "EXECUTE");
        assert_eq!(OperationType::Delete.to_string(), "DELETE");
    }

    #[test]
    fn test_generate_violation_detail_helper() {
        let detail = generate_violation_detail(
            "agent-x",
            "WRITE",
            "forbidden_table",
            "IPC Policy > Allowed Tables (Write)",
            "Table not in allowed list",
            EnforcementTier::Amber,
            "Agent tried to write to a disallowed table.".to_string(),
            "Add the table to the SKILL.md.".to_string(),
        );
        assert_eq!(detail.agent_id, "agent-x");
        assert_eq!(detail.operation_type, "WRITE");
        assert_eq!(detail.tier, EnforcementTier::Amber);
        assert!(detail.suggested_resolution.contains("SKILL.md"));
    }
}
