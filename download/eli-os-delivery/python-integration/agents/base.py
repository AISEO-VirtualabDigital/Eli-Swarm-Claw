"""Eli-OS Agent Base Class.

This module defines the abstract base class that all 12 Eli-OS SEO agents
inherit from, along with the domain-specific exception types for policy
violations and escalation events.

Architecture
-----------

```text
  SKILL.md (manifest)          Rust Control Plane
  ──────────────────          ───────────────────
       │                             │
       ▼                             │
  ┌──────────┐   gRPC/UDS IPC   ┌────────────┐
  │ EliAgent │──────────────────▶│ IpcServer  │
  │ (Python)  │                  │ (Rust)     │
  └──────────┘                  └────────────┘
       │
       ├── ipc_request()  ──▶  evaluate_request RPC
       ├── report_result() ──▶  report_result RPC
       ├── escalate()      ──▶  escalate RPC
       └── heartbeat_loop()──▶  heartbeat RPC
```

Dependencies
------------
- ``structlog`` — structured logging
- ``ulid-py`` — ULID generation for request tracing
- ``grpc.aio`` — async gRPC channel (production; generated protobuf stubs)

Usage
-----

Subclass ``EliAgent`` and implement the abstract ``execute`` method::

    class MyAgent(EliAgent):
        async def execute(self, task: dict) -> dict:
            response = await self.ipc_request('read', 'some_table', {'id': task['id']})
            # ... process response ...
            await self.report_result('success', {'data': processed})
            return {'status': 'ok', 'data': processed}
"""

from __future__ import annotations

import asyncio
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

# NOTE: Production uses generated protobuf stubs from the .proto file.
#       The StubIpcClient is a prototype implementation that simulates
#       gRPC calls locally.  Replace with real gRPC stubs when the
#       proto toolchain is available.
from .ipc_client import StubIpcClient  # noqa: F401  (re-exported for convenience)

__all__ = [
    "EliAgent",
    "EscalationRequiredError",
    "IpcResponse",
    "PolicyViolationError",
    "TechnicalSeoAgent",
]

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# SKILL.md parser
# ---------------------------------------------------------------------------

def _parse_skill_md(skill_md_path: str) -> Dict[str, Any]:
    """Parse a SKILL.md manifest file into a structured dictionary.

    Extracts the following top-level sections:

    - **Identity** — ``name``, ``role``, ``domain``, ``version``
    - **Purpose** — the full purpose paragraph
    - **Knowledge Base Scope** — ``sources``, ``exclusions``, ``refresh_policy``
    - **Capabilities** — list of tool definitions
    - **Forbidden Actions** — list of forbidden action strings
    - **Input Schema** — parsed JSON schema dict
    - **Output Schema** — parsed JSON schema dict
    - **Constraints** — list of constraint strings
    - **IPC Policy** — ``allowed_tables``, ``allowed_endpoints``, ``resource_limits``
    - **Escalation Triggers** — list of trigger descriptions

    Parameters
    ----------
    skill_md_path:
        Filesystem path to the agent's ``SKILL.md`` file.

    Returns
    -------
    dict
        Structured representation of the manifest.
    """
    path = Path(skill_md_path)
    if not path.exists():
        raise FileNotFoundError(f"SKILL.md not found: {skill_md_path}")

    text = path.read_text(encoding="utf-8")
    manifest: Dict[str, Any] = {"raw_text": text}

    # --- Identity ---
    identity_match = re.search(r"## Identity\n(.*?)(?=\n## )", text, re.DOTALL)
    if identity_match:
        block = identity_match.group(1)
        manifest["identity"] = {
            "name": _extract_field(block, "Name"),
            "role": _extract_field(block, "Role"),
            "domain": _extract_field(block, "Domain"),
            "version": _extract_field(block, "Version"),
        }

    # --- Purpose ---
    purpose_match = re.search(r"## Purpose\n(.*?)(?=\n## )", text, re.DOTALL)
    if purpose_match:
        manifest["purpose"] = purpose_match.group(1).strip()

    # --- Knowledge Base Scope ---
    kb_match = re.search(r"## Knowledge Base Scope\n(.*?)(?=\n## )", text, re.DOTALL)
    if kb_match:
        block = kb_match.group(1)
        manifest["knowledge_base_scope"] = {
            "sources": _extract_field(block, "Sources"),
            "exclusions": _extract_field(block, "Exclusions"),
            "refresh_policy": _extract_field(block, "Refresh Policy"),
        }

    # --- Capabilities ---
    caps_match = re.search(r"## Capabilities[^\n]*\n(.*?)(?=\n## )", text, re.DOTALL)
    if caps_match:
        manifest["capabilities"] = _extract_numbered_list(caps_match.group(1))

    # --- Forbidden Actions ---
    forbidden_match = re.search(r"## Forbidden Actions\n(.*?)(?=\n## )", text, re.DOTALL)
    if forbidden_match:
        manifest["forbidden_actions"] = _extract_numbered_list(forbidden_match.group(1))

    # --- Input Schema ---
    input_schema_match = re.search(r"## Input Schema\n```json\n(.*?)```", text, re.DOTALL)
    if input_schema_match:
        import json
        try:
            manifest["input_schema"] = json.loads(input_schema_match.group(1).strip())
        except json.JSONDecodeError:
            manifest["input_schema"] = input_schema_match.group(1).strip()

    # --- Output Schema ---
    output_schema_match = re.search(r"## Output Schema\n```json\n(.*?)```", text, re.DOTALL)
    if output_schema_match:
        import json
        try:
            manifest["output_schema"] = json.loads(output_schema_match.group(1).strip())
        except json.JSONDecodeError:
            manifest["output_schema"] = output_schema_match.group(1).strip()

    # --- Constraints ---
    constraints_match = re.search(r"## Constraints\n(.*?)(?=\n## )", text, re.DOTALL)
    if constraints_match:
        manifest["constraints"] = _extract_bullet_list(constraints_match.group(1))

    # --- IPC Policy ---
    ipc_match = re.search(r"## IPC Policy\n(.*?)(?=\n## )", text, re.DOTALL)
    if ipc_match:
        manifest["ipc_policy"] = _parse_ipc_policy(ipc_match.group(1))

    # --- Escalation Triggers ---
    esc_match = re.search(r"## Escalation Triggers\n(.*?)(?=$|\n# )", text, re.DOTALL)
    if esc_match:
        manifest["escalation_triggers"] = _extract_numbered_list(esc_match.group(1))

    return manifest


def _extract_field(block: str, field_name: str) -> Optional[str]:
    """Extract a ``- Field: value`` entry from a markdown block."""
    pattern = rf"^-\s*{re.escape(field_name)}:\s*(.+)$"
    match = re.search(pattern, block, re.MULTILINE)
    return match.group(1).strip() if match else None


def _extract_numbered_list(block: str) -> list[str]:
    """Extract a numbered list (``1. ...``) from a markdown block."""
    return [
        line.strip().lstrip("0123456789.").strip()
        for line in block.strip().splitlines()
        if re.match(r"^\s*\d+\.\s", line)
    ]


def _extract_bullet_list(block: str) -> list[str]:
    """Extract a bullet list (``- ...``) from a markdown block."""
    return [
        line.strip().lstrip("-").strip()
        for line in block.strip().splitlines()
        if re.match(r"^\s*-\s", line)
    ]


def _parse_ipc_policy(block: str) -> Dict[str, Any]:
    """Parse the IPC Policy section into a structured dict."""
    policy: Dict[str, Any] = {}

    # Allowed Tables
    tables_match = re.search(r"Allowed Tables:\n(.*?)(?=\n-\s|$)", block, re.DOTALL)
    if tables_match:
        policy["allowed_tables"] = _extract_bullet_list(tables_match.group(1))

    # Allowed Endpoints
    endpoints_match = re.search(r"Allowed Endpoints:\n(.*?)(?=\n-\s|$)", block, re.DOTALL)
    if endpoints_match:
        policy["allowed_endpoints"] = _extract_bullet_list(endpoints_match.group(1))

    # Resource Limits
    limits_match = re.search(r"Resource Limits:\s*\{([^}]+)\}", block)
    if limits_match:
        limits_str = "{" + limits_match.group(1) + "}"
        import json
        try:
            policy["resource_limits"] = json.loads(limits_str)
        except json.JSONDecodeError:
            policy["resource_limits"] = limits_str

    return policy


# ---------------------------------------------------------------------------
# IPC Response (mirrors Rust IpcResponse)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IpcResponse:
    """Mirrors the Rust ``IpcResponse`` returned by the gRPC IPC handler.

    Attributes
    ----------
    approved:
        Whether the request was approved by the policy engine.
    tier:
        The enforcement tier (``"GREEN"``, ``"AMBER"``, ``"RED"``).
        Only present when approved.
    violation_detail:
        JSON-encoded ``PolicyViolationDetail`` if the request was denied.
    escalation_reason:
        Human-readable reason if the request was escalated.
    raw:
        The full response dict as received from the IPC client.
    """
    approved: bool
    tier: Optional[str] = None
    violation_detail: Optional[Dict[str, Any]] = None
    escalation_reason: Optional[str] = None
    raw: Optional[Dict[str, Any]] = field(default=None, repr=False)

    @property
    def status(self) -> str:
        """Return a string status: ``'approved'``, ``'policy_violation'``, or ``'escalated'``."""
        if self.approved:
            return "approved"
        if self.violation_detail is not None:
            return "policy_violation"
        if self.escalation_reason is not None:
            return "escalated"
        return "unknown"


# ---------------------------------------------------------------------------
# Exception types
# ---------------------------------------------------------------------------

@dataclass
class PolicyViolationError(Exception):
    """Raised when the Rust control plane denies an IPC request.

    Carries the full ``PolicyViolationDetail`` from the policy engine,
    enabling agents (and the orchestrator) to make informed retry or
    escalation decisions.

    Attributes
    ----------
    agent_id:
        The agent that issued the violating request.
    operation_type:
        The IPC operation type that was attempted (``read``, ``write``, etc.).
    target_resource:
        The table, endpoint, or command the agent tried to access.
    violated_section:
        The SKILL.md section that was violated (e.g. ``"IPC Policy"``,
        ``"Forbidden Actions"``).
    rule_text:
        The exact rule text from the SKILL.md that was violated.
    tier:
        The enforcement tier (``"GREEN"``, ``"AMBER"``, ``"RED"``).
    explanation:
        Human-readable explanation of why this is a violation.
    suggested_resolution:
        Suggested fix the agent can attempt.
    """
    agent_id: str
    operation_type: str
    target_resource: str
    violated_section: str
    rule_text: str
    tier: str
    explanation: str
    suggested_resolution: str

    def __str__(self) -> str:
        return (
            f"PolicyViolationError: Agent '{self.agent_id}' attempted "
            f"{self.operation_type.upper()} on '{self.target_resource}'\n"
            f"  Tier:           {self.tier}\n"
            f"  Violated:       {self.violated_section}\n"
            f"  Rule:           {self.rule_text}\n"
            f"  Explanation:    {self.explanation}\n"
            f"  Suggested Fix:  {self.suggested_resolution}"
        )


@dataclass
class EscalationRequiredError(Exception):
    """Raised when the Rust control plane escalates an IPC request.

    Escalation means the request requires human operator review or
    the orchestrator's intervention before it can proceed.

    Attributes
    ----------
    agent_id:
        The agent that triggered the escalation.
    reason:
        Human-readable reason for the escalation.
    context:
        Structured context dict providing additional details.
    """
    agent_id: str
    reason: str
    context: Dict[str, Any]

    def __str__(self) -> str:
        ctx_summary = ", ".join(f"{k}={v}" for k, v in self.context.items())
        return (
            f"EscalationRequiredError: Agent '{self.agent_id}' requires escalation\n"
            f"  Reason:  {self.reason}\n"
            f"  Context: {ctx_summary}"
        )


# ---------------------------------------------------------------------------
# EliAgent — abstract base class
# ---------------------------------------------------------------------------

class EliAgent(ABC):
    """Abstract base class for all 12 Eli-OS SEO agents.

    Every concrete agent:

    1. Reads its ``SKILL.md`` manifest at construction time.
    2. Connects to the Rust control plane via the gRPC IPC client.
    3. Routes all inter-agent and resource access through
       ``ipc_request()`` so the policy engine can enforce the
       Green / Amber / Red tier model.
    4. Reports results back to the kernel via ``report_result()``.
    5. Sends heartbeats to signal liveness.

    Parameters
    ----------
    skill_md_path:
        Absolute path to this agent's ``SKILL.md`` manifest file.
    ipc_client:
        An ``EliIpcClient`` (or ``StubIpcClient``) instance.  If ``None``,
        a ``StubIpcClient`` is created with default settings.
    """

    def __init__(
        self,
        skill_md_path: str,
        ipc_client: Optional[Any] = None,
    ) -> None:
        # Parse the SKILL.md manifest
        self._manifest: Dict[str, Any] = _parse_skill_md(skill_md_path)

        # Structured logger bound to this agent
        self._log = structlog.get_logger(
            "eli_agent",
            agent_id=self.agent_id,
            domain=self.domain,
        )
        self._log.info(
            "agent_initialized",
            agent_id=self.agent_id,
            domain=self.domain,
            version=self._manifest.get("identity", {}).get("version", "unknown"),
        )

        # IPC client — connects to the Rust kernel over gRPC/UDS
        if ipc_client is not None:
            self.ipc_client = ipc_client
        else:
            from .ipc_client import StubIpcClient
            self.ipc_client = StubIpcClient()

        # Heartbeat task handle (set by heartbeat_loop)
        self._heartbeat_task: Optional[asyncio.Task[None]] = None

    # -- Properties --------------------------------------------------------

    @property
    def agent_id(self) -> str:
        """Return the agent's identity name from the parsed SKILL.md.

        This value must match the key used in the Rust policy engine's
        manifest map.
        """
        return self._manifest.get("identity", {}).get("name", "unknown_agent")

    @property
    def domain(self) -> str:
        """Return the agent's domain from the parsed SKILL.md."""
        return self._manifest.get("identity", {}).get("domain", "unknown_domain")

    @property
    def manifest(self) -> Dict[str, Any]:
        """Return the full parsed SKILL.md manifest dictionary."""
        return self._manifest

    # -- Abstract method ----------------------------------------------------

    @abstractmethod
    async def execute(self, task: dict) -> dict:
        """Execute a task assigned by the orchestrator.

        Subclasses must implement this method.  The implementation
        should:

        1. Call ``self.ipc_request()`` for any data reads/writes.
        2. Process the data according to the agent's domain logic.
        3. Call ``self.report_result()`` to notify the kernel of completion.
        4. Return a result dict.

        Parameters
        ----------
        task:
            A task dictionary.  The exact shape depends on the agent
            type and is defined in the agent's SKILL.md ``Input Schema``.

        Returns
        -------
        dict
            The execution result, conforming to the agent's SKILL.md
            ``Output Schema``.
        """
        ...  # pragma: no cover

    # -- IPC methods --------------------------------------------------------

    async def ipc_request(
        self,
        operation_type: str,
        target_resource: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> IpcResponse:
        """Send a policy-gated IPC request to the Rust control plane.

        Constructs an ``IpcRequest`` with a ULID and timestamp, sends it
        via the gRPC IPC client's ``evaluate()`` method, and interprets
        the response:

        - **approved** → returns the ``IpcResponse``
        - **policy_violation** → raises :class:`PolicyViolationError`
        - **escalated** → raises :class:`EscalationRequiredError`

        Parameters
        ----------
        operation_type:
            One of ``"read"``, ``"write"``, ``"execute"``, ``"delete"``.
        target_resource:
            The table name, endpoint URL, or command identifier.
        payload:
            Optional request payload (will be JSON-serialized by the client).

        Returns
        -------
        IpcResponse
            The approved response from the policy engine.

        Raises
        ------
        PolicyViolationError
            If the request violates the agent's SKILL.md policy.
        EscalationRequiredError
            If the request requires human operator review.
        """
        # Generate ULID for distributed tracing.
        # Dependency: ``pip install ulid-py``
        try:
            import ulid
            request_ulid = str(ulid.new())
        except ImportError:
            # Fallback: timestamp + random hex
            request_ulid = f"{int(time.time() * 1000):012x}{int(time.time() * 1000) % 0xFFFF:04x}"

        # Build the request dict matching the Rust IpcRequest struct
        request: Dict[str, Any] = {
            "agent_id": self.agent_id,
            "operation_type": operation_type.upper(),
            "target_resource": target_resource,
            "payload": payload,
            "request_ulid": request_ulid,
            "timestamp": int(time.time()),
        }

        self._log.debug(
            "ipc_request_sent",
            operation_type=operation_type,
            target_resource=target_resource,
            request_ulid=request_ulid,
        )

        # Send to the Rust kernel via gRPC
        response_dict = await self.ipc_client.evaluate(request)

        # Wrap in the typed IpcResponse dataclass
        response = IpcResponse(
            approved=response_dict.get("approved", False),
            tier=response_dict.get("tier"),
            violation_detail=response_dict.get("violation_detail"),
            escalation_reason=response_dict.get("escalation_reason"),
            raw=response_dict,
        )

        # Dispatch based on the policy verdict
        status = response.status
        self._log.debug(
            "ipc_response_received",
            request_ulid=request_ulid,
            status=status,
            tier=response.tier,
        )

        if status == "approved":
            return response

        if status == "policy_violation":
            detail = response.violation_detail or {}
            raise PolicyViolationError(
                agent_id=detail.get("agent_id", self.agent_id),
                operation_type=detail.get("operation_type", operation_type),
                target_resource=detail.get("target_resource", target_resource),
                violated_section=detail.get("violated_section", "unknown"),
                rule_text=detail.get("rule_text", "unknown"),
                tier=detail.get("tier", "RED"),
                explanation=detail.get("explanation", "No explanation provided."),
                suggested_resolution=detail.get(
                    "suggested_resolution", "No resolution suggested."
                ),
            )

        if status == "escalated":
            raise EscalationRequiredError(
                agent_id=self.agent_id,
                reason=response.escalation_reason or "No reason provided.",
                context=payload or {},
            )

        # Unknown status — treat as a policy violation for safety
        self._log.warning(
            "ipc_unknown_status",
            request_ulid=request_ulid,
            response=response_dict,
        )
        raise PolicyViolationError(
            agent_id=self.agent_id,
            operation_type=operation_type,
            target_resource=target_resource,
            violated_section="unknown",
            rule_text="Unknown IPC response status",
            tier="RED",
            explanation=f"Received unknown status from IPC handler: {response_dict}",
            suggested_resolution="Check IPC handler logs and retry.",
        )

    async def report_result(
        self,
        result_type: str,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Report an execution result to the Rust control plane.

        This maps to the ``report_result`` gRPC RPC.  The kernel uses
        these reports for audit logging, task tracking, and billing.

        Parameters
        ----------
        result_type:
            One of ``"success"``, ``"error"``, ``"partial"``.
        payload:
            The result payload (JSON-serializable dict).
        task_id:
            Optional task ID this result pertains to.  If ``None``,
            a ULID is generated.

        Returns
        -------
        dict
            The acknowledgement from the control plane, including
            ``success``, ``message``, and ``audit_ulid``.
        """
        try:
            import ulid
            effective_task_id = task_id or str(ulid.new())
        except ImportError:
            effective_task_id = task_id or f"{int(time.time() * 1000):012x}"

        request: Dict[str, Any] = {
            "agent_id": self.agent_id,
            "task_id": effective_task_id,
            "result_type": result_type,
            "payload": payload,
            "timestamp": int(time.time()),
        }

        self._log.info(
            "reporting_result",
            result_type=result_type,
            task_id=effective_task_id,
        )

        ack = await self.ipc_client.report_result(request)

        if not ack.get("success", False):
            self._log.error(
                "report_result_failed",
                message=ack.get("message", "unknown error"),
            )

        return ack

    async def escalate(
        self,
        trigger_reason: str,
        context: Dict[str, Any],
        severity: str = "high",
    ) -> Dict[str, Any]:
        """Send an escalation event to the Rust control plane.

        This maps to the ``escalate`` gRPC RPC.  Use this when the
        agent encounters conditions defined in its SKILL.md
        ``Escalation Triggers`` section.

        Parameters
        ----------
        trigger_reason:
            Human-readable description of why the escalation was triggered.
        context:
            Structured context dict for the operator.
        severity:
            One of ``"low"``, ``"medium"``, ``"high"``, ``"critical"``.

        Returns
        -------
        dict
            The acknowledgement from the control plane.
        """
        request: Dict[str, Any] = {
            "agent_id": self.agent_id,
            "trigger_reason": trigger_reason,
            "context": context,
            "severity": severity,
            "timestamp": int(time.time()),
        }

        self._log.warning(
            "escalation_triggered",
            trigger_reason=trigger_reason,
            severity=severity,
        )

        ack = await self.ipc_client.escalate(request)

        if not ack.get("success", False):
            self._log.error(
                "escalate_failed",
                message=ack.get("message", "unknown error"),
            )

        return ack

    async def heartbeat_loop(self) -> None:
        """Run a background task that sends heartbeats every 30 seconds.

        The heartbeat carries the agent's current status and resource
        usage to the Rust kernel.  The kernel checks these against the
        agent's declared IPC policy ``Resource Limits`` and may return
        a warning if limits are being approached.

        This method is designed to be run as an ``asyncio`` background
        task::

            asyncio.create_task(agent.heartbeat_loop())

        The loop runs until cancelled (e.g. on agent shutdown).
        """
        import resource as resource_module  # stdlib

        self._log.info("heartbeat_loop_started")

        try:
            while True:
                # Gather resource telemetry
                try:
                    # rusage is Unix-only; fall back gracefully
                    usage = resource_module.getrusage(resource_module.RUSAGE_SELF)
                    memory_usage_mb = usage.ru_maxrss / 1024.0  # macOS: bytes; Linux: KB
                    if memory_usage_mb > 100_000:
                        # Likely Linux where ru_maxrss is in KB
                        memory_usage_mb = usage.ru_maxrss / 1024.0
                except (ValueError, AttributeError):
                    memory_usage_mb = 0.0

                heartbeat_request: Dict[str, Any] = {
                    "agent_id": self.agent_id,
                    "status": "processing",
                    "tasks_completed": 0,  # Subclasses should track this
                    "memory_usage_mb": round(memory_usage_mb, 2),
                }

                try:
                    ack = await self.ipc_client.heartbeat(heartbeat_request)
                    warning = ack.get("resource_warning")
                    if warning:
                        self._log.warning(
                            "heartbeat_resource_warning",
                            warning=warning,
                        )
                except Exception as exc:
                    # Heartbeat failures should not crash the agent
                    self._log.error(
                        "heartbeat_failed",
                        error=str(exc),
                    )

                await asyncio.sleep(30)

        except asyncio.CancelledError:
            self._log.info("heartbeat_loop_stopped")

    def start_heartbeat(self) -> asyncio.Task[None]:
        """Start the heartbeat loop as a background task.

        Returns the ``asyncio.Task`` so it can be cancelled on shutdown.

        Returns
        -------
        asyncio.Task
            The background heartbeat task.
        """
        self._heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        return self._heartbeat_task

    async def shutdown(self) -> None:
        """Gracefully shut down the agent.

        Cancels the heartbeat loop and closes the IPC client.
        """
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if hasattr(self.ipc_client, "close"):
            await self.ipc_client.close()

        self._log.info("agent_shutdown_complete", agent_id=self.agent_id)


# ---------------------------------------------------------------------------
# Concrete example subclass: TechnicalSeoAgent
# ---------------------------------------------------------------------------

class TechnicalSeoAgent(EliAgent):
    """Example concrete agent: Technical SEO Specialist.

    Demonstrates the full lifecycle of an agent execution:

    1. Reads crawl results from the ``crawl_results`` table via IPC.
    2. Processes the crawl data to produce technical SEO findings.
    3. Writes the audit findings to the ``tech_seo_audits`` table via IPC.
    4. Reports the result to the kernel.

    This is a **reference implementation** — the actual processing
    logic would use the tools listed in the Technical SEO SKILL.md
    (HTTP status checker, robots.txt parser, Core Web Vitals scanner, etc.).
    """

    async def execute(self, task: dict) -> dict:
        """Execute a technical SEO audit task.

        Parameters
        ----------
        task:
            Must contain at minimum ``{"crawl_id": "..."}``.
            May also contain ``"target_urls"`` and ``"audit_scope"``.

        Returns
        -------
        dict
            The audit result conforming to the Technical SEO output schema.
        """
        crawl_id = task.get("crawl_id")
        if not crawl_id:
            raise ValueError("Task must contain a 'crawl_id' field.")

        self._log.info("tech_seo_execute_start", crawl_id=crawl_id)

        # Step 1: Read crawl results via IPC (policy-gated)
        crawl_response = await self.ipc_request(
            "read",
            "crawl_results",
            {"crawl_id": crawl_id},
        )
        crawl_data = crawl_response.raw or {}
        self._log.debug("crawl_data_retrieved", crawl_id=crawl_id)

        # Step 2: Process the crawl data to produce findings.
        #         In production, this calls real tools (HTTP checker,
        #         Core Web Vitals scanner, etc.).  Here we simulate.
        target_urls = task.get("target_urls", [])
        audit_scope = task.get("audit_scope", "full")

        findings: list[Dict[str, Any]] = []
        for url in target_urls:
            # Simulated finding — real implementation would use actual tools
            findings.append({
                "url": url,
                "category": "crawlability",
                "severity": "medium",
                "issue": f"Simulated: {url} returns soft 404 for non-existent paths",
                "evidence": "HTTP 200 with minimal content (< 200 bytes)",
                "recommendation": "Return proper 404 status codes for non-existent URLs",
                "reference": "https://developers.google.com/search/docs/crawling-indexing/404-soft-404s",
            })

        audit_id = f"audit-{crawl_id}"
        audit_result: Dict[str, Any] = {
            "agent": self.agent_id,
            "audit_id": audit_id,
            "target_urls": target_urls,
            "findings": findings,
            "summary": {
                "total_issues": len(findings),
                "critical_count": sum(1 for f in findings if f["severity"] == "critical"),
                "crawl_budget_waste_percent": 0.0,
                "avg_lcp_ms": None,
                "avg_cls_score": None,
                "avg_inp_ms": None,
            },
            "audit_scope": audit_scope,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        # Step 3: Write audit findings via IPC (policy-gated)
        await self.ipc_request(
            "write",
            "tech_seo_audits",
            {"findings": findings, "audit_id": audit_id},
        )

        # Step 4: Report result to the kernel
        await self.report_result(
            "audit_complete",
            {"audit_id": audit_id, "total_findings": len(findings)},
            task_id=crawl_id,
        )

        self._log.info(
            "tech_seo_execute_complete",
            audit_id=audit_id,
            findings_count=len(findings),
        )

        return audit_result
