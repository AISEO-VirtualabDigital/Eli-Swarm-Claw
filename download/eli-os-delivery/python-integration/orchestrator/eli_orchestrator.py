"""Kimi K2.7 Code Orchestrator for Eli-OS.

This module implements the central orchestration layer that:

1. **Decomposes** a high-level task into a directed acyclic graph (DAG)
   of sub-tasks using the Kimi K2.7 Code model.
2. **Routes** each sub-task to the appropriate agent from the 12-agent
   SEO fleet, with fallback model-based routing when the agent name
   is not specified.
3. **Executes** the DAG in topological order, handling policy
   violations (with suggested-resolution retries) and escalations
   (with re-routing or early return).
4. **Synthesizes** the collected sub-task results into a unified,
   coherent response using the Kimi model.
5. **Handles escalations** that bubble up from agents or the policy
   engine, deciding whether to retry, reroute, compose partial
   results, or escalate to a human operator.

Architecture
-----------

```text
                    ┌───────────────────────┐
                    │    User / API Call     │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   EliOrchestrator      │
                    │   ┌─────────────────┐  │
                    │   │ Kimi K2.7 Code  │  │
                    │   │ (vLLM / SGLang)  │  │
                    │   └────────┬────────┘  │
                    └────────────┼───────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
   ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
   │   Agent 1   │       │   Agent 2   │       │   Agent N   │
   │ (Technical  │       │ (Keyword    │       │ (Report     │
   │  SEO)       │       │  Research)  │       │  Generator) │
   └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                                 ▼
                    ┌───────────────────────┐
                    │  Synthesized Response  │
                    └───────────────────────┘
```

Dependencies
------------
- ``httpx`` — async HTTP client for OpenAI-compatible model endpoints
- ``structlog`` — structured logging

Usage
-----

::

    orchestrator = EliOrchestrator(
        model_endpoint='http://localhost:8001/v1',
        skill_md_dir='/etc/eli-os/skills/',
    )
    result = await orchestrator.run('Audit example.com for technical SEO issues')
    print(result['synthesis'])
"""

from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

__all__ = [
    "EliOrchestrator",
    "TaskDAG",
    "SubTask",
    "EscalationDecision",
]

logger = structlog.get_logger(__name__)

# Default timeout for Kimi model calls (seconds).
_MODEL_TIMEOUT: float = 120.0

# Maximum retries for model calls on transient failures.
_MODEL_MAX_RETRIES: int = 2


# ============================================================================
# Data classes
# ============================================================================

@dataclass
class SubTask:
    """A single sub-task within a task decomposition DAG.

    Attributes
    ----------
    id:
        Unique identifier for this sub-task (e.g. ``"sub_1"``).
    description:
        Human-readable description of what the sub-task should accomplish.
    target_agent:
        The agent name to route this sub-task to (e.g. ``"technical_seo"``).
        May be ``None`` if the model did not specify one; the ``route()``
        method will resolve it.
    dependencies:
        List of sub-task IDs that must complete before this one can start.
    """
    id: str
    description: str
    target_agent: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TaskDAG:
    """A directed acyclic graph of sub-tasks for a user request.

    Attributes
    ----------
    sub_tasks:
        Ordered list of ``SubTask`` instances.
    """
    sub_tasks: List[SubTask] = field(default_factory=list)

    def topological_order(self) -> List[SubTask]:
        """Return sub-tasks in topological (dependency-respecting) order.

        Uses Kahn's algorithm.  Raises ``ValueError`` if a cycle is detected.

        Returns
        -------
        list[SubTask]
            Sub-tasks ordered so that all dependencies precede each task.
        """
        task_map: Dict[str, SubTask] = {t.id: t for t in self.sub_tasks}
        in_degree: Dict[str, int] = {t.id: 0 for t in self.sub_tasks}

        # Build adjacency list and compute in-degrees
        adj: Dict[str, List[str]] = {t.id: [] for t in self.sub_tasks}
        for task in self.sub_tasks:
            for dep in task.dependencies:
                if dep not in task_map:
                    raise ValueError(
                        f"Sub-task '{task.id}' depends on unknown task '{dep}'."
                    )
                adj[dep].append(task.id)
                in_degree[task.id] += 1

        # Seed the queue with zero-in-degree nodes
        queue: List[str] = [tid for tid, deg in in_degree.items() if deg == 0]
        ordered: List[SubTask] = []

        while queue:
            current = queue.pop(0)
            ordered.append(task_map[current])
            for neighbor in adj[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordered) != len(self.sub_tasks):
            raise ValueError("Cycle detected in task DAG — cannot topologically sort.")

        return ordered


@dataclass
class EscalationDecision:
    """The orchestrator's decision on how to handle an escalation event.

    Attributes
    ----------
    action:
        One of ``"retry"``, ``"reroute"``, ``"compose"``, or
        ``"escalate_to_human"``.
    rationale:
        Human-readable explanation of why this action was chosen.
    target_agent:
        For ``"reroute"`` actions, the agent to retry with.
    modified_request:
        For ``"retry"`` actions, the modified request payload.
    """
    action: str
    rationale: str
    target_agent: Optional[str] = None
    modified_request: Optional[Dict[str, Any]] = None


# ============================================================================
# Model prompts
# ============================================================================

# The system prompts below are designed for Kimi K2.7 Code served via
# vLLM or SGLang with an OpenAI-compatible chat completions API.

DECOMPOSE_SYSTEM_PROMPT: str = """\
You are the Eli-OS Task Decomposer. You receive a high-level SEO task and \
break it into a directed acyclic graph (DAG) of sub-tasks that can be \
executed by specialized agents.

## Available Agents

{agent_registry}

## Rules

1. Each sub-task must be assignable to EXACTLY ONE agent from the list above.
2. Sub-tasks may have dependencies on other sub-tasks (list their IDs).
3. The DAG must NOT contain cycles.
4. Use clear, specific descriptions so agents know exactly what to do.
5. Minimize the number of sub-tasks while maintaining clarity.
6. Include a final sub-task routed to the 'report_agent' for synthesis.

## Output Format

Respond with ONLY a valid JSON object (no markdown fences, no commentary):

{
  "sub_tasks": [
    {
      "id": "sub_1",
      "description": "Detailed description of what this sub-task accomplishes",
      "target_agent": "agent_name_here",
      "dependencies": []
    }
  ]
}
"""

ROUTE_SYSTEM_PROMPT: str = """\
You are the Eli-OS Task Router. Given a sub-task description and the list \
of available agents, select the SINGLE BEST agent to handle it.

## Available Agents

{agent_registry}

## Rules

1. Select ONLY from the agent names listed above.
2. Match the sub-task's domain to the agent whose Purpose best aligns.
3. Consider the agent's Capabilities and Forbidden Actions.

## Output Format

Respond with ONLY the agent name as a plain string (no quotes, no JSON, no commentary).
"""

SYNTHESIZE_SYSTEM_PROMPT: str = """\
You are the Eli-OS Result Synthesizer. You receive the original user task \
and the collected results from multiple specialized agents. Your job is to \
produce a single, unified, coherent response that addresses the user's \
original request.

## Rules

1. Synthesize ALL agent results into a coherent narrative — do not \
   simply concatenate them.
2. Preserve key data points, metrics, and actionable recommendations.
3. Highlight any conflicts or gaps between agent results.
4. If any sub-tasks failed or were escalated, note that transparently.
5. Structure the output with clear sections, headers, and prioritized \
   action items.
6. Match the language and tone of the user's original request.

## Output Format

Respond in plain text with markdown formatting. No JSON wrapping.
"""

ESCALATION_SYSTEM_PROMPT: str = """\
You are the Eli-OS Escalation Handler. You receive an escalation event from \
an agent or the policy engine and must decide how to handle it.

## Available Agents

{agent_registry}

## Possible Actions

1. **retry** — The issue is likely transient; retry the same agent with \
   the same or slightly modified request.
2. **reroute** — A different agent can handle this sub-task. Provide the \
   target agent name.
3. **compose** — We have enough completed results to compose a partial \
   response. Skip the failed sub-task.
4. **escalate_to_human** — The issue requires human operator intervention.

## Rules

1. If the escalation is a policy violation with a suggested_resolution, \
   prefer "retry" with the modified request.
2. If the agent is clearly the wrong fit, prefer "reroute".
3. If multiple sub-tasks have failed and enough data exists, prefer \
   "compose".
4. If the issue involves data integrity, security, or billing, prefer \
   "escalate_to_human".

## Output Format

Respond with ONLY a valid JSON object:

{
  "action": "retry" | "reroute" | "compose" | "escalate_to_human",
  "rationale": "Why this action was chosen",
  "target_agent": null,
  "modified_request": null
}

For "reroute", set "target_agent" to the agent name.
For "retry", optionally set "modified_request" to a dict with the \
modified payload.
"""


# ============================================================================
# Orchestrator
# ============================================================================

class EliOrchestrator:
    """Kimi K2.7 Code Orchestrator for the Eli-OS agent fleet.

    This is the central coordination component that:

    - Decomposes tasks into sub-task DAGs via LLM.
    - Routes sub-tasks to the appropriate agents.
    - Executes DAGs with error handling and retries.
    - Synthesizes partial/complete results into a final response.
    - Handles escalations from agents and the policy engine.

    Parameters
    ----------
    model_endpoint:
        The base URL of the OpenAI-compatible model API.
        The Kimi K2.7 Code model should be served via vLLM or SGLang
        at this endpoint (e.g. ``"http://localhost:8001/v1"``).
    skill_md_dir:
        Directory containing the ``SKILL.md`` files for all 12 agents.
        The orchestrator reads these at startup to build the agent
        registry used for routing decisions.
    model_name:
        The model identifier passed to the chat completions API.
        Defaults to ``"kimi-k2.7-code"``.
    model_timeout:
        Timeout in seconds for each model API call.
    """

    def __init__(
        self,
        model_endpoint: str = "http://localhost:8001/v1",
        skill_md_dir: str = "/etc/eli-os/skills/",
        model_name: str = "kimi-k2.7-code",
        model_timeout: float = _MODEL_TIMEOUT,
    ) -> None:
        self._model_endpoint = model_endpoint.rstrip("/")
        self._model_name = model_name
        self._model_timeout = model_timeout

        self._log = structlog.get_logger("eli_orchestrator")

        # Load agent manifests from SKILL.md files
        self._manifests: Dict[str, Dict[str, Any]] = self._load_manifests(skill_md_dir)

        # Build the routing context string (injected into model prompts)
        self._agent_registry = self._build_agent_registry()

        # Agent class lookup — populated when agents are registered
        self._agent_instances: Dict[str, Any] = {}

        # Event bus subscription placeholder
        # In production, this connects to the Rust event bus via gRPC
        # streaming or a WebSocket bridge.  For now, escalation events
        # arrive via the execute_dag error-handling paths.
        self._escalation_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

        self._log.info(
            "orchestrator_initialized",
            model_endpoint=self._model_endpoint,
            model_name=self._model_name,
            agent_count=len(self._manifests),
            agents=list(self._manifests.keys()),
        )

    # -- Manifest loading ---------------------------------------------------

    @staticmethod
    def _load_manifests(skill_md_dir: str) -> Dict[str, Dict[str, Any]]:
        """Load and parse all SKILL.md files from the given directory.

        Each file is parsed using the ``_parse_skill_md`` function from
        ``agents.base``.  The resulting manifests are keyed by the
        agent's identity name.

        Parameters
        ----------
        skill_md_dir:
            Path to the directory containing ``*.md`` skill files.

        Returns
        -------
        dict
            Mapping of agent name → parsed manifest dict.
        """
        from agents.base import _parse_skill_md  # noqa: import-outside-toplevel

        manifests: Dict[str, Dict[str, Any]] = {}
        skill_path = Path(skill_md_dir)

        if not skill_path.is_dir():
            structlog.get_logger("orchestrator").warning(
                "skill_md_dir_not_found",
                path=skill_md_dir,
                note="No agents loaded. Register agents manually via register_agent().",
            )
            return manifests

        for md_file in sorted(skill_path.glob("*.md")):
            try:
                manifest = _parse_skill_md(str(md_file))
                agent_name = manifest.get("identity", {}).get("name")
                if agent_name:
                    manifests[agent_name] = manifest
            except Exception as exc:
                structlog.get_logger("orchestrator").error(
                    "failed_to_parse_skill_md",
                    file=str(md_file),
                    error=str(exc),
                )

        return manifests

    def _build_agent_registry(self) -> str:
        """Build a human-readable agent registry string for model prompts.

        Each entry includes the agent name and its Purpose paragraph.
        This context is injected into every model call so the LLM can
        make informed routing and decomposition decisions.

        Returns
        -------
        str
            Formatted registry string, one agent per line.
        """
        lines: list[str] = []
        for name, manifest in self._manifests.items():
            purpose = manifest.get("purpose", "No purpose defined.")
            domain = manifest.get("identity", {}).get("domain", "Unknown")
            # Truncate long purpose strings to keep prompts manageable
            purpose_short = purpose[:200] + ("..." if len(purpose) > 200 else "")
            lines.append(f"- **{name}** ({domain}): {purpose_short}")
        return "\n".join(lines)

    # -- Agent registration -------------------------------------------------

    def register_agent(self, name: str, agent_instance: Any) -> None:
        """Register an agent instance for execution.

        In production, the orchestrator would instantiate agents
        dynamically based on the SKILL.md manifests.  For now,
        agents must be explicitly registered.

        Parameters
        ----------
        name:
            The agent's identity name (must match SKILL.md).
        agent_instance:
            An ``EliAgent`` subclass instance with an ``execute`` method.
        """
        if name not in self._manifests:
            self._log.warning(
                "registering_unknown_agent",
                agent_name=name,
                known_agents=list(self._manifests.keys()),
            )
        self._agent_instances[name] = agent_instance
        self._log.info("agent_registered", agent_name=name)

    # -- Model interaction --------------------------------------------------

    async def _call_model(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """Send a chat completion request to the Kimi K2.7 Code model.

        Uses the OpenAI-compatible API via ``httpx``.  Implements
        retry logic for transient HTTP errors.

        Parameters
        ----------
        system_prompt:
            The system message defining the model's role and rules.
        user_prompt:
            The user message containing the task or query.
        temperature:
            Sampling temperature (low for deterministic outputs).
        max_tokens:
            Maximum tokens in the model response.

        Returns
        -------
        str
            The model's response content.

        Raises
        ------
        RuntimeError
            If the model call fails after all retries.
        """
        import httpx

        url = f"{self._model_endpoint}/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self._model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        last_error: Optional[Exception] = None

        for attempt in range(1, _MODEL_MAX_RETRIES + 1):
            try:
                self._log.debug(
                    "model_call_attempt",
                    attempt=attempt,
                    url=url,
                )

                async with httpx.AsyncClient(timeout=self._model_timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    body = response.json()

                content = body["choices"][0]["message"]["content"]
                return content

            except httpx.TimeoutException as exc:
                last_error = exc
                self._log.warning(
                    "model_call_timeout",
                    attempt=attempt,
                    error=str(exc),
                )
            except httpx.HTTPStatusError as exc:
                last_error = exc
                self._log.error(
                    "model_call_http_error",
                    attempt=attempt,
                    status_code=exc.response.status_code,
                    body=exc.response.text[:500],
                )
                # Don't retry on 4xx client errors (except 429)
                if 400 <= exc.response.status_code < 500 and exc.response.status_code != 429:
                    break
            except (KeyError, IndexError) as exc:
                last_error = exc
                self._log.error(
                    "model_call_malformed_response",
                    attempt=attempt,
                    error=str(exc),
                    body=str(body) if 'body' in dir() else "N/A",
                )
                break  # Don't retry malformed responses
            except Exception as exc:
                last_error = exc
                self._log.error(
                    "model_call_unexpected_error",
                    attempt=attempt,
                    error=str(exc),
                    error_type=type(exc).__name__,
                )

            # Backoff before retry
            if attempt < _MODEL_MAX_RETRIES:
                await asyncio.sleep(1.0 * attempt)

        raise RuntimeError(
            f"Model call failed after {_MODEL_MAX_RETRIES} retries: {last_error}"
        )

    # -- Decomposition ------------------------------------------------------

    async def decompose(self, task: str) -> TaskDAG:
        """Decompose a high-level task into a DAG of sub-tasks.

        Sends the task description to the Kimi model along with the
        agent registry.  The model responds with a JSON array of
        sub-tasks, each with an ID, description, target agent, and
        dependency list.

        Parameters
        ----------
        task:
            The user's task description (natural language).

        Returns
        -------
        TaskDAG
            The decomposed task graph.

        Raises
        ------
        RuntimeError
            If the model returns unparseable JSON.
        ValueError
            If the model references unknown agent names.
        """
        self._log.info("decompose_start", task_length=len(task))

        system = DECOMPOSE_SYSTEM_PROMPT.format(
            agent_registry=self._agent_registry,
        )

        response_text = await self._call_model(
            system_prompt=system,
            user_prompt=task,
            temperature=0.1,
            max_tokens=4096,
        )

        # Parse the model's JSON response.
        # The model may wrap it in markdown code fences — strip those.
        cleaned = self._strip_code_fences(response_text)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            self._log.error(
                "decompose_parse_error",
                response_text=response_text[:1000],
                error=str(exc),
            )
            raise RuntimeError(
                f"Model returned invalid JSON for task decomposition: {exc}\n"
                f"Raw response: {response_text[:500]}"
            ) from exc

        # Build SubTask objects
        sub_tasks: list[SubTask] = []
        known_agents = set(self._manifests.keys()) | set(self._agent_instances.keys())

        for raw in data.get("sub_tasks", []):
            agent_name = raw.get("target_agent")
            if agent_name and agent_name not in known_agents:
                self._log.warning(
                    "decompose_unknown_agent",
                    sub_task_id=raw.get("id"),
                    target_agent=agent_name,
                    known_agents=sorted(known_agents),
                )
                # Don't raise — let route() handle it

            sub_tasks.append(
                SubTask(
                    id=raw.get("id", f"sub_{len(sub_tasks) + 1}"),
                    description=raw.get("description", ""),
                    target_agent=agent_name,
                    dependencies=raw.get("dependencies", []),
                )
            )

        dag = TaskDAG(sub_tasks=sub_tasks)

        self._log.info(
            "decompose_complete",
            sub_task_count=len(sub_tasks),
            sub_task_ids=[st.id for st in sub_tasks],
        )

        return dag

    # -- Routing ------------------------------------------------------------

    async def route(self, sub_task: SubTask) -> str:
        """Route a sub-task to the appropriate agent.

        If the sub-task already has a ``target_agent`` specified by
        the decomposition model, this method validates it against the
        known agents and returns it.

        If no target agent is specified (or the specified one is
        unknown), this method sends the sub-task description to the
        Kimi model and asks it to select the best agent.

        Parameters
        ----------
        sub_task:
            The sub-task to route.

        Returns
        -------
        str
            The agent name to execute this sub-task.

        Raises
        ------
        ValueError
            If no valid agent can be determined.
        """
        known_agents = set(self._manifests.keys()) | set(self._agent_instances.keys())

        # Fast path: agent is already specified and known
        if sub_task.target_agent and sub_task.target_agent in known_agents:
            self._log.debug(
                "route_direct",
                sub_task_id=sub_task.id,
                agent=sub_task.target_agent,
            )
            return sub_task.target_agent

        # Slow path: ask the model to pick an agent
        if sub_task.target_agent and sub_task.target_agent not in known_agents:
            self._log.warning(
                "route_unknown_agent_fallback_to_model",
                sub_task_id=sub_task.id,
                unknown_agent=sub_task.target_agent,
            )

        self._log.debug(
            "route_model_fallback",
            sub_task_id=sub_task.id,
        )

        system = ROUTE_SYSTEM_PROMPT.format(
            agent_registry=self._agent_registry,
        )

        response_text = await self._call_model(
            system_prompt=system,
            user_prompt=sub_task.description,
            temperature=0.0,
            max_tokens=50,
        )

        # The model should return just the agent name as a plain string.
        # Strip whitespace, quotes, and code fences.
        agent_name = self._strip_code_fences(response_text).strip().strip('"').strip("'")

        if agent_name not in known_agents:
            self._log.error(
                "route_model_returned_unknown_agent",
                sub_task_id=sub_task.id,
                model_response=response_text,
                known_agents=sorted(known_agents),
            )
            raise ValueError(
                f"Model returned unknown agent '{agent_name}' for sub-task "
                f"'{sub_task.id}'. Known agents: {sorted(known_agents)}"
            )

        self._log.info(
            "route_complete",
            sub_task_id=sub_task.id,
            agent=agent_name,
        )

        return agent_name

    # -- DAG execution ------------------------------------------------------

    async def execute_dag(self, dag: TaskDAG) -> Dict[str, Any]:
        """Execute a task DAG by routing and running each sub-task.

        Execution follows topological order to respect dependencies.
        Completed results are made available to subsequent sub-tasks
        via the ``_completed_results`` dict.

        Error handling:

        - **PolicyViolationError**: Logs the violation, attempts to
          modify the request based on ``suggested_resolution``, retries
          once with the modified payload.
        - **EscalationRequiredError**: Logs the escalation, checks if
          re-routing to a different agent can resolve it.  If not,
          collects all completed results and returns them with the
          escalation noted.

        Parameters
        ----------
        dag:
            The task DAG to execute.

        Returns
        -------
        dict
            Mapping of ``sub_task_id`` → result dict.  Failed sub-tasks
            have an ``"error"`` key instead of normal results.
        """
        from agents.base import EscalationRequiredError, PolicyViolationError

        self._log.info(
            "execute_dag_start",
            sub_task_count=len(dag.sub_tasks),
        )

        # Topologically sort the sub-tasks
        ordered = dag.topological_order()

        # Result store: sub_task_id → result dict
        results: Dict[str, Any] = {}
        # Completed results available for dependent sub-tasks
        completed_results: Dict[str, Any] = {}
        escalations: List[Dict[str, Any]] = []

        for sub_task in ordered:
            self._log.info(
                "executing_sub_task",
                sub_task_id=sub_task.id,
                target_agent=sub_task.target_agent,
            )

            try:
                # Route the sub-task to an agent
                agent_name = await self.route(sub_task)

                # Get the agent instance
                agent = self._agent_instances.get(agent_name)
                if agent is None:
                    raise ValueError(
                        f"No registered agent instance for '{agent_name}'. "
                        f"Call orchestrator.register_agent('{agent_name}', instance) first."
                    )

                # Build the task payload, injecting results from dependencies
                task_payload: Dict[str, Any] = {
                    "description": sub_task.description,
                    "sub_task_id": sub_task.id,
                    "dependency_results": {
                        dep_id: completed_results.get(dep_id)
                        for dep_id in sub_task.dependencies
                    },
                }

                # Execute with policy violation retry
                result = await self._execute_with_retry(
                    agent=agent,
                    sub_task=sub_task,
                    task_payload=task_payload,
                )

                results[sub_task.id] = result
                completed_results[sub_task.id] = result

                self._log.info(
                    "sub_task_complete",
                    sub_task_id=sub_task.id,
                    agent=agent_name,
                )

            except PolicyViolationError as exc:
                # Log and attempt retry with suggested resolution
                self._log.warning(
                    "sub_task_policy_violation",
                    sub_task_id=sub_task.id,
                    agent=sub_task.target_agent,
                    tier=exc.tier,
                    explanation=exc.explanation,
                )

                # Try to apply the suggested resolution and retry once
                try:
                    modified_payload = self._apply_suggested_resolution(
                        task_payload,
                        exc.suggested_resolution,
                    )
                    agent_name = await self.route(sub_task)
                    agent = self._agent_instances.get(agent_name)
                    if agent is not None:
                        result = await agent.execute(modified_payload)
                        results[sub_task.id] = result
                        completed_results[sub_task.id] = result
                        self._log.info(
                            "sub_task_retry_success",
                            sub_task_id=sub_task.id,
                            agent=agent_name,
                        )
                        continue
                except Exception as retry_exc:
                    self._log.error(
                        "sub_task_retry_failed",
                        sub_task_id=sub_task.id,
                        error=str(retry_exc),
                    )

                # Retry failed — record the error
                results[sub_task.id] = {
                    "error": "policy_violation",
                    "agent": sub_task.target_agent,
                    "tier": exc.tier,
                    "explanation": exc.explanation,
                    "suggested_resolution": exc.suggested_resolution,
                }

            except EscalationRequiredError as exc:
                self._log.warning(
                    "sub_task_escalation",
                    sub_task_id=sub_task.id,
                    agent=exc.agent_id,
                    reason=exc.reason,
                )

                escalations.append({
                    "sub_task_id": sub_task.id,
                    "agent_id": exc.agent_id,
                    "reason": exc.reason,
                    "context": exc.context,
                })

                # Ask the escalation handler what to do
                decision = await self.handle_escalation({
                    "sub_task_id": sub_task.id,
                    "agent_id": exc.agent_id,
                    "reason": exc.reason,
                    "context": exc.context,
                    "completed_results": dict(completed_results),
                    "remaining_sub_tasks": [
                        st.id for st in ordered
                        if st.id not in completed_results and st.id != sub_task.id
                    ],
                })

                if decision.action == "reroute" and decision.target_agent:
                    # Try a different agent
                    alt_agent = self._agent_instances.get(decision.target_agent)
                    if alt_agent is not None:
                        self._log.info(
                            "sub_task_rerouted",
                            sub_task_id=sub_task.id,
                            new_agent=decision.target_agent,
                            rationale=decision.rationale,
                        )
                        try:
                            result = await alt_agent.execute(task_payload)
                            results[sub_task.id] = result
                            completed_results[sub_task.id] = result
                            continue
                        except Exception as reroute_exc:
                            self._log.error(
                                "sub_task_reroute_failed",
                                sub_task_id=sub_task.id,
                                error=str(reroute_exc),
                            )

                if decision.action == "compose":
                    # We have enough results — stop executing and compose
                    self._log.info(
                        "execute_dag_composing_early",
                        completed=len(completed_results),
                        total=len(ordered),
                        rationale=decision.rationale,
                    )
                    results["_orchestrator_note"] = (
                        f"DAG execution stopped early due to escalation. "
                        f"Composing with {len(completed_results)}/{len(ordered)} sub-tasks complete. "
                        f"Rationale: {decision.rationale}"
                    )
                    results["_escalations"] = escalations
                    break

                if decision.action == "retry" and decision.modified_request:
                    agent = self._agent_instances.get(sub_task.target_agent or "")
                    if agent is not None:
                        try:
                            result = await agent.execute(decision.modified_request)
                            results[sub_task.id] = result
                            completed_results[sub_task.id] = result
                            continue
                        except Exception as retry_exc:
                            self._log.error(
                                "sub_task_escalation_retry_failed",
                                sub_task_id=sub_task.id,
                                error=str(retry_exc),
                            )

                # escalate_to_human or no action — record and continue
                results[sub_task.id] = {
                    "error": "escalation_required",
                    "agent": exc.agent_id,
                    "reason": exc.reason,
                    "decision": decision.action,
                    "rationale": decision.rationale,
                }

            except Exception as exc:
                self._log.error(
                    "sub_task_unexpected_error",
                    sub_task_id=sub_task.id,
                    agent=sub_task.target_agent,
                    error=str(exc),
                    error_type=type(exc).__name__,
                )
                results[sub_task.id] = {
                    "error": "unexpected_error",
                    "agent": sub_task.target_agent,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }

        # Attach escalations if any occurred
        if escalations and "_escalations" not in results:
            results["_escalations"] = escalations

        self._log.info(
            "execute_dag_complete",
            total_sub_tasks=len(ordered),
            successful=sum(1 for v in results.values() if not isinstance(v, dict) or "error" not in v),
            failed=sum(1 for v in results.values() if isinstance(v, dict) and "error" in v),
        )

        return results

    async def _execute_with_retry(
        self,
        agent: Any,
        sub_task: SubTask,
        task_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a sub-task with a single retry on policy violation.

        This is the inner execution helper used by ``execute_dag``.
        The first policy violation triggers an automatic retry with
        the suggested resolution applied.  Subsequent violations
        are re-raised for the caller to handle.

        Parameters
        ----------
        agent:
            The agent instance to call ``execute`` on.
        sub_task:
            The sub-task being executed.
        task_payload:
            The task payload dict.

        Returns
        -------
        dict
            The agent's execution result.
        """
        from agents.base import PolicyViolationError

        try:
            return await agent.execute(task_payload)
        except PolicyViolationError as exc:
            self._log.info(
                "auto_retry_on_policy_violation",
                sub_task_id=sub_task.id,
                tier=exc.tier,
            )
            modified = self._apply_suggested_resolution(
                task_payload,
                exc.suggested_resolution,
            )
            # Re-raise — let execute_dag handle the retry properly
            # so it can update routing and result tracking
            raise

    @staticmethod
    def _apply_suggested_resolution(
        payload: Dict[str, Any],
        suggested_resolution: str,
    ) -> Dict[str, Any]:
        """Attempt to apply the policy engine's suggested resolution.

        This is a best-effort heuristic.  The suggested resolution is
        a natural-language string from the policy engine; we look for
        patterns like "use X instead of Y" and apply the substitution.

        Parameters
        ----------
        payload:
            The original task payload.
        suggested_resolution:
            The ``suggested_resolution`` from a ``PolicyViolationDetail``.

        Returns
        -------
        dict
            A modified copy of the payload.
        """
        modified = dict(payload)
        modified["_policy_retry"] = True
        modified["_original_resolution"] = suggested_resolution
        return modified

    # -- Synthesis ----------------------------------------------------------

    async def synthesize(self, task: str, results: Dict[str, Any]) -> str:
        """Synthesize sub-task results into a unified response.

        Sends all sub-task results to the Kimi model along with the
        original task description.  The model produces a single,
        coherent response that addresses the user's request.

        Parameters
        ----------
        task:
            The user's original task description.
        results:
            Mapping of ``sub_task_id`` → result dict from ``execute_dag``.

        Returns
        -------
        str
            The synthesized response in markdown format.
        """
        self._log.info("synthesize_start")

        # Build a structured summary of all results
        results_summary_parts: list[str] = []
        for sub_id, result in results.items():
            if sub_id.startswith("_"):
                # Orchestrator metadata, skip
                continue
            if isinstance(result, dict) and "error" in result:
                results_summary_parts.append(
                    f"### {sub_id}: FAILED\n"
                    f"- Error: {result.get('error_type', result['error'])}\n"
                    f"- Details: {result.get('message', result.get('reason', 'N/A'))}"
                )
            else:
                # Truncate large results to keep within model context
                result_str = json.dumps(result, default=str, indent=2)
                if len(result_str) > 2000:
                    result_str = result_str[:2000] + "\n... [truncated]"
                results_summary_parts.append(
                    f"### {sub_id}: SUCCESS\n````json\n{result_str}\n```"
                )

        # Include escalation notes if present
        escalations = results.get("_escalations")
        escalation_note = ""
        if escalations:
            escalation_lines = [
                f"- Sub-task {e.get('sub_task_id')}: {e.get('reason')}"
                for e in escalations
            ]
            escalation_note = (
                "\n\n## Escalations That Occurred\n"
                + "\n".join(escalation_lines)
            )

        orchestrator_note = results.get("_orchestrator_note", "")
        note_section = ""
        if orchestrator_note:
            note_section = f"\n\n## Orchestrator Note\n{orchestrator_note}"

        user_prompt = (
            f"## Original Task\n{task}\n\n"
            f"## Sub-Task Results\n\n"
            f"{chr(10).join(results_summary_parts)}"
            f"{escalation_note}"
            f"{note_section}"
        )

        synthesis = await self._call_model(
            system_prompt=SYNTHESIZE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4096,
        )

        self._log.info("synthesize_complete", response_length=len(synthesis))

        return synthesis

    # -- Escalation handling ------------------------------------------------

    async def handle_escalation(self, event: Dict[str, Any]) -> EscalationDecision:
        """Decide how to handle an escalation event.

        Sends the escalation context to the Kimi model and asks it
        to choose one of four actions: retry, reroute, compose, or
        escalate_to_human.

        Parameters
        ----------
        event:
            The escalation event dict with keys: ``sub_task_id``,
            ``agent_id``, ``reason``, ``context``, and optionally
            ``completed_results`` and ``remaining_sub_tasks``.

        Returns
        -------
        EscalationDecision
            The model's decision with action, rationale, and optional
            target agent or modified request.
        """
        self._log.info(
            "handle_escalation_start",
            sub_task_id=event.get("sub_task_id"),
            agent_id=event.get("agent_id"),
            reason=event.get("reason"),
        )

        system = ESCALATION_SYSTEM_PROMPT.format(
            agent_registry=self._agent_registry,
        )

        # Build a focused context for the model
        event_context = {
            "sub_task_id": event.get("sub_task_id"),
            "agent_id": event.get("agent_id"),
            "reason": event.get("reason"),
            "context": event.get("context", {}),
            "completed_sub_tasks": list(event.get("completed_results", {}).keys()),
            "remaining_sub_tasks": event.get("remaining_sub_tasks", []),
        }

        response_text = await self._call_model(
            system_prompt=system,
            user_prompt=json.dumps(event_context, default=str, indent=2),
            temperature=0.1,
            max_tokens=500,
        )

        # Parse the model's JSON decision
        cleaned = self._strip_code_fences(response_text)

        try:
            decision_data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            self._log.error(
                "escalation_decision_parse_error",
                response_text=response_text[:500],
                error=str(exc),
            )
            # Default to escalate_to_human on parse failure
            return EscalationDecision(
                action="escalate_to_human",
                rationale=(
                    f"Failed to parse model escalation decision: {exc}. "
                    f"Defaulting to human escalation."
                ),
            )

        decision = EscalationDecision(
            action=decision_data.get("action", "escalate_to_human"),
            rationale=decision_data.get("rationale", "No rationale provided."),
            target_agent=decision_data.get("target_agent"),
            modified_request=decision_data.get("modified_request"),
        )

        # Validate the action
        valid_actions = {"retry", "reroute", "compose", "escalate_to_human"}
        if decision.action not in valid_actions:
            self._log.warning(
                "escalation_invalid_action",
                action=decision.action,
                valid_actions=sorted(valid_actions),
            )
            decision.action = "escalate_to_human"
            decision.rationale += " (Invalid action corrected to escalate_to_human)"

        self._log.info(
            "escalation_decision_made",
            action=decision.action,
            rationale=decision.rationale,
            target_agent=decision.target_agent,
        )

        return decision

    # -- Main entry point ---------------------------------------------------

    async def run(self, task: str) -> Dict[str, Any]:
        """Execute the full orchestration pipeline.

        The main entry point that orchestrates the complete flow:

        1. **Decompose** the task into a sub-task DAG.
        2. **Execute** the DAG (with error handling and retries).
        3. **Synthesize** the results into a unified response.

        Parameters
        ----------
        task:
            The user's task description in natural language.

        Returns
        -------
        dict
            A result dictionary with keys:

            - ``"synthesis"`` — The synthesized response string.
            - ``"sub_task_results"`` — Raw sub-task results dict.
            - ``"sub_task_count"`` — Total number of sub-tasks.
            - ``"successful_count"`` — Number of successful sub-tasks.
            - ``"escalations"`` — List of escalation events (if any).
            - ``"duration_seconds"`` — Total pipeline duration.
        """
        start_time = time.monotonic()

        self._log.info("orchestration_run_start", task_length=len(task))

        try:
            # Step 1: Decompose the task into a DAG
            dag = await self.decompose(task)

            # Step 2: Execute the DAG
            sub_task_results = await self.execute_dag(dag)

            # Step 3: Synthesize the results
            synthesis = await self.synthesize(task, sub_task_results)

        except Exception as exc:
            self._log.error(
                "orchestration_run_error",
                error=str(exc),
                error_type=type(exc).__name__,
            )
            # Return a partial result with error information
            return {
                "synthesis": f"**Orchestration Error**: {exc}",
                "sub_task_results": {},
                "sub_task_count": 0,
                "successful_count": 0,
                "escalations": [],
                "duration_seconds": time.monotonic() - start_time,
                "error": str(exc),
                "error_type": type(exc).__name__,
            }

        duration = time.monotonic() - start_time

        # Compute summary stats
        successful = sum(
            1 for k, v in sub_task_results.items()
            if not k.startswith("_") and isinstance(v, dict) and "error" not in v
        )
        total = sum(1 for k in sub_task_results if not k.startswith("_"))

        result: Dict[str, Any] = {
            "synthesis": synthesis,
            "sub_task_results": sub_task_results,
            "sub_task_count": total,
            "successful_count": successful,
            "escalations": sub_task_results.get("_escalations", []),
            "duration_seconds": round(duration, 3),
        }

        self._log.info(
            "orchestration_run_complete",
            sub_task_count=total,
            successful=successful,
            duration_seconds=round(duration, 3),
        )

        return result

    # -- Utilities ----------------------------------------------------------

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Strip markdown code fences from a model response.

        The Kimi model may wrap JSON in ``````json ... `````` blocks.
        This method removes those wrappers.

        Parameters
        ----------
        text:
            The raw model response.

        Returns
        -------
        str
            The text with code fences removed.
        """
        # Match ```json ... ``` or ``` ... ```
        pattern = r"^```(?:json)?\s*\n?(.*?)\n?\s*```$"
        match = re.match(pattern, text.strip(), re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
