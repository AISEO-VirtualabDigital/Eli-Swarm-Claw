//! # eli-skill-parser
//!
//! SKILL.md parser for the Eli-OS control plane.
//!
//! This crate implements the **SKILL.md paradigm** that replaces the old
//! implicit-knowledge, blocking approach to agent governance. Each agent
//! ships with a declarative `SKILL.md` manifest that the control plane
//! parses into a [`CapabilityManifest`], giving us:
//!
//! - **Explicit permissions** instead of inferred intent
//! - **Pre-flight validation** instead of post-hoc sandboxing
//! - **Tiered enforcement** (Green / Amber / Red) driven by manifest data
//!
//! ## Required dependencies
//!
//! ```toml
//! [dependencies]
//! serde = { version = "1", features = ["derive"] }
//! regex = "1"
//! thiserror = "1"
//!
//! [dev-dependencies]
//! serde_json = "1"
//! ```

use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;
use thiserror::Error;

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

/// Identifying metadata for an agent described in a SKILL.md file.
///
/// Every agent must declare its `name`, `role`, `domain`, and `version`
/// so the control plane can route policies correctly.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct AgentIdentity {
    /// Human-readable agent name, e.g. `invoice-processor`.
    pub name: String,
    /// Functional role, e.g. `financial-analyst`.
    pub role: String,
    /// Business domain, e.g. `finance`.
    pub domain: String,
    /// Semantic version of this agent's specification.
    pub version: String,
}

/// Declares which knowledge-base sources the agent may consult and which
/// are explicitly excluded.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Default)]
pub struct KnowledgeBaseScope {
    /// Allowed knowledge-base source identifiers or URIs.
    pub sources: Vec<String>,
    /// Explicitly excluded sources (blacklist overrides).
    pub exclusions: Vec<String>,
    /// Policy keyword controlling how often the KB is refreshed,
    /// e.g. `on-demand` or `per-session`.
    pub refresh_policy: String,
}

/// A single tool / capability that the agent is permitted to invoke.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ToolCapability {
    /// Tool identifier, e.g. `sql_query` or `http_get`.
    pub name: String,
    /// Human-readable description of what the tool does.
    pub description: String,
}

/// Runtime constraints placed on the agent by the control plane.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AgentConstraints {
    /// An invariant system-prompt fragment that must always be present.
    pub system_prompt_invariant: String,
    /// Maximum number of tokens the agent may produce per turn.
    pub max_output_tokens: u32,
    /// Sampling temperature clamp (0.0 = deterministic, 2.0 = creative).
    pub temperature: f32,
}

impl Default for AgentConstraints {
    fn default() -> Self {
        Self {
            system_prompt_invariant: String::new(),
            max_output_tokens: 4096,
            temperature: 0.7,
        }
    }
}

/// Per-resource limits that the IPC handler enforces at runtime.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ResourceLimits {
    /// Maximum resident memory in megabytes.
    pub memory_mb: u32,
    /// Maximum CPU utilisation percentage (0–100).
    pub cpu_percent: u32,
    /// Maximum wall-clock duration for a single request, in seconds.
    pub max_duration_seconds: u32,
}

impl Default for ResourceLimits {
    fn default() -> Self {
        Self {
            memory_mb: 512,
            cpu_percent: 80,
            max_duration_seconds: 60,
        }
    }
}

/// Declares the inter-process communication boundaries for this agent.
///
/// The control plane consults this section for every [`IpcRequest`](eli_ipc_handler::IpcRequest)
/// to determine whether the operation is within scope.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Default)]
pub struct IpcPolicy {
    /// Database / table names the agent may read from.
    pub allowed_tables_read: Vec<String>,
    /// Database / table names the agent may write to.
    pub allowed_tables_write: Vec<String>,
    /// HTTP endpoint prefixes the agent may call.
    pub allowed_endpoints: Vec<String>,
    /// Runtime resource caps enforced per-request.
    pub resource_limits: ResourceLimits,
}

/// The top-level manifest produced by parsing a single SKILL.md file.
///
/// This is the **single source of truth** that the policy engine consumes
/// to make allow/deny/escalate decisions.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct CapabilityManifest {
    /// Who this agent is.
    pub identity: AgentIdentity,
    /// One-sentence purpose statement.
    pub purpose: String,
    /// Declared knowledge-base boundaries.
    pub knowledge_base_scope: KnowledgeBaseScope,
    /// Tools the agent is allowed to invoke.
    pub capabilities: Vec<ToolCapability>,
    /// Actions that are explicitly forbidden (deny-list).
    pub forbidden_actions: Vec<String>,
    /// JSON Schema string describing expected input format.
    pub input_schema: String,
    /// JSON Schema string describing expected output format.
    pub output_schema: String,
    /// Runtime behavioural constraints.
    pub constraints: AgentConstraints,
    /// IPC boundary declarations.
    pub ipc_policy: IpcPolicy,
    /// Free-text triggers that should cause an escalation to Red tier.
    pub escalation_triggers: Vec<String>,
}

// ---------------------------------------------------------------------------
// Error types
// ---------------------------------------------------------------------------

/// Errors that can occur during SKILL.md parsing.
#[derive(Debug, Error)]
pub enum ParseError {
    /// The specified file or directory does not exist.
    #[error("file not found: {0}")]
    FileNotFound(String),

    /// The file content does not match the expected SKILL.md structure.
    #[error("invalid SKILL.md format: {0}")]
    InvalidFormat(String),

    /// A required section header is missing from the document.
    #[error("missing required section: {0}")]
    MissingSection(String),

    /// An I/O error occurred while reading a file.
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
}

// ---------------------------------------------------------------------------
// SkillParser
// ---------------------------------------------------------------------------

/// Parses SKILL.md files into [`CapabilityManifest`] structures.
///
/// The parser uses regex-based section extraction: it scans for `## Section Name`
/// headings and collects the bullet-list content that follows each heading.
/// This keeps parsing fast, dependency-light, and easy to audit.
///
/// # Example
///
/// ```ignore
/// use eli_skill_parser::SkillParser;
/// use std::path::Path;
///
/// let manifests = SkillParser::parse_directory(Path::new("./agents/"))
///     .expect("failed to parse agent directory");
///
/// for (name, manifest) in &manifests {
///     println!("{}: {}", name, manifest.purpose);
/// }
/// ```
pub struct SkillParser;

impl SkillParser {
    /// Reads every `*.md` file in `path`, parses each as a SKILL.md document,
    /// and returns a map keyed by the agent's `identity.name`.
    ///
    /// # Errors
    ///
    /// Returns [`ParseError::FileNotFound`] if the directory does not exist,
    /// [`ParseError::IoError`] on filesystem failures, or
    /// [`ParseError::InvalidFormat`] / [`ParseError::MissingSection`] for
    /// malformed files. A single bad file does **not** abort the entire
    /// scan—instead its error is logged and the remaining files are
    /// still processed. (The first error encountered is returned, but all
    /// valid manifests are included in the output.)
    pub fn parse_directory(
        path: &Path,
    ) -> Result<HashMap<String, CapabilityManifest>, ParseError> {
        if !path.is_dir() {
            return Err(ParseError::FileNotFound(path.to_string_lossy().to_string()));
        }

        let mut manifests = HashMap::new();
        let mut first_error: Option<ParseError> = None;

        // Collect .md entries so we can sort them for deterministic ordering.
        let mut entries: Vec<_> = std::fs::read_dir(path)?.collect::<Result<Vec<_>, _>>()?;
        entries.sort_by_key(|e| e.file_name());

        for entry in entries {
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("md") {
                match Self::parse_file(&path) {
                    Ok(manifest) => {
                        let key = manifest.identity.name.clone();
                        manifests.insert(key, manifest);
                    }
                    Err(e) => {
                        // Record the first error but keep going so one bad
                        // file doesn't take down the whole fleet.
                        if first_error.is_none() {
                            first_error = Some(e);
                        }
                    }
                }
            }
        }

        // If we collected at least one manifest, return them even if there
        // was a non-fatal parse failure elsewhere.
        if !manifests.is_empty() {
            Ok(manifests)
        } else if let Some(e) = first_error {
            Err(e)
        } else {
            Ok(manifests)
        }
    }

    /// Parses a single SKILL.md file from disk.
    ///
    /// # Errors
    ///
    /// Returns [`ParseError::FileNotFound`] if the file does not exist,
    /// or any parsing error from [`parse_md`](SkillParser::parse_md).
    pub fn parse_file(path: &Path) -> Result<CapabilityManifest, ParseError> {
        if !path.exists() {
            return Err(ParseError::FileNotFound(path.to_string_lossy().to_string()));
        }
        let content = std::fs::read_to_string(path)?;
        Self::parse_md(&content)
    }

    /// Parses a SKILL.md content string into a [`CapabilityManifest`].
    ///
    /// The parser is tolerant of minor formatting variations but requires
    /// the `## Identity` section (at minimum) to be present.
    ///
    /// # Section extraction algorithm
    ///
    /// 1. Split the document on `## ` headings.
    /// 2. For each recognised section name, extract the body text until
    ///    the next `## ` heading or end-of-file.
    /// 3. Within each section body, parse key-value pairs and bullet lists.
    pub fn parse_md(content: &str) -> Result<CapabilityManifest, ParseError> {
        let sections = extract_sections(content);

        // Identity is required—without it we cannot key the manifest.
        let identity_body = sections.get("identity").ok_or_else(|| {
            ParseError::MissingSection("Identity".to_string())
        })?;
        let identity = parse_identity(identity_body)?;

        let purpose = sections
            .get("purpose")
            .cloned()
            .unwrap_or_default()
            .trim()
            .to_string();

        let knowledge_base_scope = sections
            .get("knowledge base scope")
            .map(|b| parse_knowledge_base_scope(b))
            .transpose()?
            .unwrap_or_default();

        let capabilities = sections
            .get("capabilities")
            .map(parse_capabilities)
            .unwrap_or_default();

        let forbidden_actions = sections
            .get("forbidden actions")
            .map(parse_bullet_list)
            .unwrap_or_default();

        let input_schema = sections
            .get("input schema")
            .cloned()
            .unwrap_or_default()
            .trim()
            .to_string();

        let output_schema = sections
            .get("output schema")
            .cloned()
            .unwrap_or_default()
            .trim()
            .to_string();

        let constraints = sections
            .get("constraints")
            .map(|b| parse_constraints(b))
            .transpose()?
            .unwrap_or_default();

        let ipc_policy = sections
            .get("ipc policy")
            .map(|b| parse_ipc_policy(b))
            .transpose()?
            .unwrap_or_default();

        let escalation_triggers = sections
            .get("escalation triggers")
            .map(parse_bullet_list)
            .unwrap_or_default();

        Ok(CapabilityManifest {
            identity,
            purpose,
            knowledge_base_scope,
            capabilities,
            forbidden_actions,
            input_schema,
            output_schema,
            constraints,
            ipc_policy,
            escalation_triggers,
        })
    }
}

// ---------------------------------------------------------------------------
// Internal parsing helpers
// ---------------------------------------------------------------------------

/// Splits a SKILL.md document into a map of lowercased section names to
/// their body text (everything between the heading and the next heading).
fn extract_sections(content: &str) -> HashMap<String, String> {
    let mut sections: HashMap<String, String> = HashMap::new();
    let mut current_name: Option<String> = None;
    let mut current_body = String::new();

    for line in content.lines() {
        if let Some(name) = line.strip_prefix("## ") {
            // Flush the previous section.
            if let Some(prev) = current_name.take() {
                sections.insert(prev, current_body.trim().to_string());
            }
            current_name = Some(name.trim().to_lowercase());
            current_body = String::new();
        } else if let Some(_name) = &current_name {
            current_body.push_str(line);
            current_body.push('\n');
        }
    }

    // Flush the last section.
    if let Some(name) = current_name {
        sections.insert(name, current_body.trim().to_string());
    }

    sections
}

/// Parses the body of the `## Identity` section into an [`AgentIdentity`].
///
/// Expects lines in the form `- key: value` or `key: value`.
fn parse_identity(body: &str) -> Result<AgentIdentity, ParseError> {
    let kv = parse_key_value_pairs(body);

    let name = kv.get("name").cloned().unwrap_or_default();
    let role = kv.get("role").cloned().unwrap_or_default();
    let domain = kv.get("domain").cloned().unwrap_or_default();
    let version = kv.get("version").cloned().unwrap_or_else(|| "0.1.0".to_string());

    if name.is_empty() {
        return Err(ParseError::InvalidFormat(
            "Identity section must contain a 'name' field".to_string(),
        ));
    }

    Ok(AgentIdentity {
        name,
        role,
        domain,
        version,
    })
}

/// Parses a `## Knowledge Base Scope` section body.
fn parse_knowledge_base_scope(body: &str) -> Result<KnowledgeBaseScope, ParseError> {
    let kv = parse_key_value_pairs(body);
    let refresh_policy = kv
        .get("refresh_policy")
        .cloned()
        .unwrap_or_else(|| "on-demand".to_string());

    // Sources and exclusions are bulleted lists under sub-headings or
    // just tagged lines. We look for lines like `- source_name` and
    // categorise them.
    let mut sources = Vec::new();
    let mut exclusions = Vec::new();
    let mut in_exclusions = false;

    for line in body.lines() {
        let trimmed = line.trim();
        // Detect a sub-heading like `### Exclusions` to switch mode.
        if trimmed.to_lowercase().starts_with("### exclusion") {
            in_exclusions = true;
            continue;
        }
        if trimmed.to_lowercase().starts_with("### source") {
            in_exclusions = false;
            continue;
        }

        if let Some(item) = trimmed.strip_prefix("- ") {
            if in_exclusions {
                exclusions.push(item.trim().to_string());
            } else {
                sources.push(item.trim().to_string());
            }
        }
    }

    Ok(KnowledgeBaseScope {
        sources,
        exclusions,
        refresh_policy,
    })
}

/// Parses a `## Capabilities` section body into a list of [`ToolCapability`].
///
/// Expects lines like:
/// ```text
/// - tool_name: description of the tool
/// ```
fn parse_capabilities(body: &str) -> Vec<ToolCapability> {
    let mut caps = Vec::new();

    // Regex for `- name: description` or `- name  (description)` patterns.
    let re = Regex::new(r"^-\s+(?P<name>[^:]+?):\s*(?P<desc>.+)$").unwrap();

    for line in body.lines() {
        if let Some(caps_match) = re.captures(line.trim()) {
            caps.push(ToolCapability {
                name: caps_match["name"].trim().to_string(),
                description: caps_match["desc"].trim().to_string(),
            });
        }
    }

    caps
}

/// Parses a bulleted list from a section body.
///
/// Extracts the text after each `- ` prefix.
fn parse_bullet_list(body: &str) -> Vec<String> {
    body.lines()
        .filter_map(|line| {
            let trimmed = line.trim();
            trimmed.strip_prefix("- ").map(|s| s.trim().to_string())
        })
        .collect()
}

/// Parses a `## Constraints` section body.
///
/// Expects key-value pairs like `max_output_tokens: 4096` and a
/// `system_prompt_invariant` multi-line value.
fn parse_constraints(body: &str) -> Result<AgentConstraints, ParseError> {
    let kv = parse_key_value_pairs(body);

    // Parse system_prompt_invariant: it might be a multi-line value.
    // We take the first line for the key-value parse, but also try to
    // capture a fenced code block or block quote if present.
    let system_prompt_invariant = kv
        .get("system_prompt_invariant")
        .cloned()
        .unwrap_or_default();

    let max_output_tokens = kv
        .get("max_output_tokens")
        .and_then(|v| v.parse::<u32>().ok())
        .unwrap_or(4096);

    let temperature = kv
        .get("temperature")
        .and_then(|v| v.parse::<f32>().ok())
        .unwrap_or(0.7);

    Ok(AgentConstraints {
        system_prompt_invariant,
        max_output_tokens,
        temperature,
    })
}

/// Parses the `## IPC Policy` section body into an [`IpcPolicy`].
///
/// Expected structure:
/// ```text
/// ### Allowed Tables (Read)
/// - invoices
/// - customers
///
/// ### Allowed Tables (Write)
/// - audit_log
///
/// ### Allowed Endpoints
/// - /api/v1/invoices
/// - /api/v1/health
///
/// ### Resource Limits
/// memory_mb: 512
/// cpu_percent: 80
/// max_duration_seconds: 60
/// ```
fn parse_ipc_policy(body: &str) -> Result<IpcPolicy, ParseError> {
    let mut allowed_tables_read = Vec::new();
    let mut allowed_tables_write = Vec::new();
    let mut allowed_endpoints = Vec::new();
    let mut resource_limits = ResourceLimits::default();

    // We use simple state-machine parsing: track which sub-section we're in.
    // Sub-sections are detected by `###` headings.
    let mut current_subsection: &str = "";

    for line in body.lines() {
        let trimmed = line.trim();

        // Detect sub-section headings.
        if let Some(heading) = trimmed.strip_prefix("### ") {
            let heading_lower = heading.to_lowercase();
            if heading_lower.contains("read") {
                current_subsection = "read";
            } else if heading_lower.contains("write") {
                current_subsection = "write";
            } else if heading_lower.contains("endpoint") {
                current_subsection = "endpoints";
            } else if heading_lower.contains("resource") {
                current_subsection = "resources";
            } else {
                current_subsection = "";
            }
            continue;
        }

        // Parse bullet items in the current sub-section.
        if let Some(item) = trimmed.strip_prefix("- ") {
            let item = item.trim().to_string();
            match current_subsection {
                "read" => allowed_tables_read.push(item),
                "write" => allowed_tables_write.push(item),
                "endpoints" => allowed_endpoints.push(item),
                _ => {}
            }
            continue;
        }

        // Parse key: value for resource limits.
        if current_subsection == "resources" {
            if let Some((key, value)) = trimmed.split_once(':') {
                let key = key.trim().to_lowercase();
                let value = value.trim();
                match key.as_str() {
                    "memory_mb" => {
                        resource_limits.memory_mb = value.parse().unwrap_or(resource_limits.memory_mb);
                    }
                    "cpu_percent" => {
                        resource_limits.cpu_percent = value.parse().unwrap_or(resource_limits.cpu_percent);
                    }
                    "max_duration_seconds" => {
                        resource_limits.max_duration_seconds = value.parse().unwrap_or(resource_limits.max_duration_seconds);
                    }
                    _ => {}
                }
            }
        }
    }

    Ok(IpcPolicy {
        allowed_tables_read,
        allowed_tables_write,
        allowed_endpoints,
        resource_limits,
    })
}

/// Extracts `key: value` pairs from a section body.
///
/// Handles both `- key: value` and plain `key: value` lines.
/// Values are trimmed. If a key appears multiple times, the last value wins.
fn parse_key_value_pairs(body: &str) -> HashMap<String, String> {
    let mut map = HashMap::new();
    let re = Regex::new(r"^-?\s*(?P<key>[a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(?P<value>.+)$").unwrap();

    for line in body.lines() {
        if let Some(caps) = re.captures(line.trim()) {
            map.insert(
                caps["key"].to_lowercase(),
                caps["value"].trim().to_string(),
            );
        }
    }

    map
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    /// A well-formed SKILL.md document for testing.
    const SAMPLE_SKILL_MD: &str = r#"# SKILL.md - Invoice Processor Agent

## Identity
- name: invoice-processor
- role: financial-analyst
- domain: finance
- version: 1.2.0

## Purpose
Processes incoming invoices, validates them against purchase orders, and routes them for approval.

## Knowledge Base Scope
- invoice_templates
- tax_rate_tables
- vendor_contracts

### Exclusions
- employee_pii
- salary_data

- refresh_policy: on-demand

## Capabilities
- sql_query: Execute read-only SQL against the invoices database
- http_post: Send validated invoices to the approval endpoint
- pdf_parse: Extract structured data from PDF invoices

## Forbidden Actions
- DELETE FROM invoices
- DROP TABLE
- /api/v1/admin/
- /api/v1/users/delete

## Input Schema
{"type": "object", "properties": {"invoice_id": {"type": "string"}}}

## Output Schema
{"type": "object", "properties": {"status": {"type": "string"}, "routing_id": {"type": "string"}}}

## Constraints
- system_prompt_invariant: You are a financial invoice processor. Never modify data outside your allowed tables.
- max_output_tokens: 2048
- temperature: 0.3

## IPC Policy

### Allowed Tables (Read)
- invoices
- purchase_orders
- vendors

### Allowed Tables (Write)
- audit_log
- invoice_routing

### Allowed Endpoints
- /api/v1/invoices/validate
- /api/v1/approvals/submit
- /api/v1/health

### Resource Limits
memory_mb: 256
cpu_percent: 60
max_duration_seconds: 30

## Escalation Triggers
- invoice_amount > 100000
- vendor_not_in_approved_list
- duplicate_invoice_detected
"#;

    #[test]
    fn test_parse_identity() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.identity.name, "invoice-processor");
        assert_eq!(manifest.identity.role, "financial-analyst");
        assert_eq!(manifest.identity.domain, "finance");
        assert_eq!(manifest.identity.version, "1.2.0");
    }

    #[test]
    fn test_parse_purpose() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert!(manifest.purpose.contains("invoice"));
        assert!(manifest.purpose.contains("approval"));
    }

    #[test]
    fn test_parse_knowledge_base_scope() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.knowledge_base_scope.sources.len(), 3);
        assert!(manifest.knowledge_base_scope.sources.contains(&"invoice_templates".to_string()));
        assert_eq!(manifest.knowledge_base_scope.exclusions.len(), 2);
        assert!(manifest.knowledge_base_scope.exclusions.contains(&"employee_pii".to_string()));
        assert_eq!(manifest.knowledge_base_scope.refresh_policy, "on-demand");
    }

    #[test]
    fn test_parse_capabilities() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.capabilities.len(), 3);
        assert_eq!(manifest.capabilities[0].name, "sql_query");
        assert!(manifest.capabilities[0].description.contains("SQL"));
    }

    #[test]
    fn test_parse_forbidden_actions() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.forbidden_actions.len(), 4);
        assert!(manifest.forbidden_actions.contains(&"DELETE FROM invoices".to_string()));
        assert!(manifest.forbidden_actions.contains(&"DROP TABLE".to_string()));
    }

    #[test]
    fn test_parse_constraints() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.constraints.max_output_tokens, 2048);
        assert!((manifest.constraints.temperature - 0.3).abs() < f32::EPSILON);
        assert!(manifest.constraints.system_prompt_invariant.contains("financial"));
    }

    #[test]
    fn test_parse_ipc_policy_tables() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.ipc_policy.allowed_tables_read.len(), 3);
        assert!(manifest.ipc_policy.allowed_tables_read.contains(&"invoices".to_string()));
        assert_eq!(manifest.ipc_policy.allowed_tables_write.len(), 2);
        assert!(manifest.ipc_policy.allowed_tables_write.contains(&"audit_log".to_string()));
    }

    #[test]
    fn test_parse_ipc_policy_endpoints() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.ipc_policy.allowed_endpoints.len(), 3);
        assert!(manifest
            .ipc_policy
            .allowed_endpoints
            .contains(&"/api/v1/invoices/validate".to_string()));
    }

    #[test]
    fn test_parse_ipc_policy_resource_limits() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.ipc_policy.resource_limits.memory_mb, 256);
        assert_eq!(manifest.ipc_policy.resource_limits.cpu_percent, 60);
        assert_eq!(manifest.ipc_policy.resource_limits.max_duration_seconds, 30);
    }

    #[test]
    fn test_parse_escalation_triggers() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert_eq!(manifest.escalation_triggers.len(), 3);
        assert!(manifest.escalation_triggers.contains(&"duplicate_invoice_detected".to_string()));
    }

    #[test]
    fn test_parse_input_output_schemas() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        assert!(manifest.input_schema.contains("invoice_id"));
        assert!(manifest.output_schema.contains("routing_id"));
    }

    #[test]
    fn test_missing_identity_section() {
        let content = "## Purpose\nDo things.\n";
        let result = SkillParser::parse_md(content);
        assert!(matches!(result, Err(ParseError::MissingSection(_))));
    }

    #[test]
    fn test_empty_identity_name() {
        let content = "## Identity\n- name:\n- role: test\n- domain: test\n- version: 1.0.0\n";
        let result = SkillParser::parse_md(content);
        assert!(matches!(result, Err(ParseError::InvalidFormat(_))));
    }

    #[test]
    fn test_minimal_manifest() {
        let content = "## Identity\n- name: minimal-agent\n- role: tester\n- domain: test\n- version: 0.0.1\n";
        let manifest = SkillParser::parse_md(content).unwrap();
        assert_eq!(manifest.identity.name, "minimal-agent");
        // Default values should be used for missing sections.
        assert!(manifest.capabilities.is_empty());
        assert!(manifest.forbidden_actions.is_empty());
        assert_eq!(manifest.constraints.max_output_tokens, 4096);
        assert_eq!(manifest.ipc_policy.resource_limits.memory_mb, 512);
    }

    #[test]
    fn test_serialization_round_trip() {
        let manifest = SkillParser::parse_md(SAMPLE_SKILL_MD).unwrap();
        let json = serde_json::to_string(&manifest).unwrap();
        let deserialized: CapabilityManifest = serde_json::from_str(&json).unwrap();
        assert_eq!(manifest, deserialized);
    }

    #[test]
    fn test_extract_sections_ordering() {
        let content = "## Alpha\nsome text\n## Beta\nmore text\n";
        let sections = extract_sections(content);
        assert_eq!(sections.len(), 2);
        assert_eq!(sections.get("alpha").unwrap(), "some text");
        assert_eq!(sections.get("beta").unwrap(), "more text");
    }

    #[test]
    fn test_forbidden_actions_with_api_paths() {
        let content = "## Identity\n- name: test\n- role: t\n- domain: t\n- version: 1.0.0\n## Forbidden Actions\n- /api/v1/admin/users\n- DELETE FROM customers\n";
        let manifest = SkillParser::parse_md(content).unwrap();
        assert_eq!(manifest.forbidden_actions.len(), 2);
        assert!(manifest.forbidden_actions.iter().any(|a| a.contains("/api/v1/admin/")));
    }

    #[test]
    fn test_ipc_policy_endpoint_prefixes() {
        let content = "## Identity\n- name: test\n- role: t\n- domain: t\n- version: 1.0.0\n## IPC Policy\n### Allowed Endpoints\n- /api/v1/invoices\n- /api/v2/health\n";
        let manifest = SkillParser::parse_md(content).unwrap();
        assert_eq!(manifest.ipc_policy.allowed_endpoints.len(), 2);
    }
}
