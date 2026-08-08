---
absorbedFrom: https://github.com/huangruiteng/loopx
absorbedAt: 2026-08-08
chunkType: control-plane-pattern
tags: [loopx, agent-orchestration, control-plane, durable-state, typed-enums, handler-chain, capability-catalog, extension-system, zero-deps, dry-run-safety]
---

# LoopX — Lightweight Agent Control Plane

## Core Concept
LoopX is a state kernel and agent-agnostic local control plane for **loop engineering** — governing long-running AI agent work (multi-day tasks, cross-agent handoffs). Six durable layers: Registry, Goal State, Run Log, Run History, Status Queue, Compute Quota.

**Key insight**: "Keep the loop moving. Keep the judgment human."

Zero runtime dependencies (stdlib only). MIT license. Python 3.11+.

## Pattern 1: Four Runtime Responsibilities (Strict Separation)

| Role | Owns | Must NOT Own |
|------|------|------------|
| **Agent** | Planning, analysis, tool use, one bounded execution | Durable goal lifecycle |
| **Provider** | External calls, observations, effect results | Domain transition policy |
| **Capability** | Outcome contract, domain policy, validation | Durable scheduling |
| **LoopX Kernel** | Goal, todo, claim, gate, monitor, quota, writeback | Domain-specific reasoning |

**Absorb into Eli**: This maps to Eli's architecture: Agent = eli-chat, Provider = vault-search + open-claw, Capability = omni-route + skill-contain, Kernel = the coordination layer. Validate that Eli's modules respect these boundaries.

## Pattern 2: Typed Turn Decisions (Enum States)
Explicit enumeration of ALL possible outcomes — no string comparisons for control flow.

```python
class LoopXTurnResultKind(Enum):
    validated_progress = "validated_progress"
    validated_completion = "validated_completion"
    repair_required = "repair_required"
    replan_required = "replan_required"
    user_action_required = "user_action_required"
    wait = "wait"
    host_failure = "host_failure"
    validation_failed = "validation_failed"
    writeback_failed = "writeback_failed"
    quota_spend_failed = "quota_spend_failed"
```

**Absorb into Eli**: Define a `TurnResult` enum for Eli's chat processing — instead of returning strings, return typed results (success, key_needed, quota_exceeded, etc.)

## Pattern 3: Handler-Chain Dispatch with None Sentinel
Flat handler chain with `None` return-early for 60+ commands. Simpler than subclass dispatch.

```python
starter_result = handle_starter_command(args, print_payload)
if starter_result is not None:
    return starter_result
```

**Absorb into Eli**: Apply to Eli's API route handlers — chain action handlers with early return pattern.

## Pattern 4: Declarative Capability Catalog
Capabilities as a tuple of dicts — type-safe, immutable, serializable.

```python
BUILTIN_CAPABILITIES: tuple[dict[str, Any], ...] = (
    {"id": "integration-branch-reconcile", "origin": "builtin", "status": "active-preview"},
    ...
)
```

**Absorb into Eli**: Eli's skill templates in the vault could use this pattern — a `SKILL_REGISTRY` tuple that defines all available skills with metadata.

## Pattern 5: Default-Dry-Run Mutation Safety
Almost every state-mutating command is dry-run first. `--execute` flag required for actual writes.

**Absorb into Eli**: Add dry-run mode to Omni Route's rotation and key injection. POST /api/omni?action=rotate&dryRun=true shows what would happen without doing it.

## Pattern 6: Public/Private Boundary Enforcement
Recursive payload scanning prevents accidental credential leaks. String obfuscation in regex patterns (e.g., `"la"+"rk"+"office"` for "larkoffice").

**Absorb into Eli**: Add a `sanitizeForLog()` function that strips API keys from log output. Already partially done with `.slice(0, 12)...` but could be more systematic.

## Pattern 7: Dual Output Format (JSON + Markdown)
Every command returns structured dicts; rendering is a separate concern. Both JSON (machine) and Markdown (human) outputs supported.

**Absorb into Eli**: API routes already return JSON. Add markdown rendering option for the vault-sync export.

## Pattern 8: Per-Goal File-Based State
No database needed. State stored as local files: `.loopx/registry.json`, `ACTIVE_GOAL_STATE.md`, `runs/index.jsonl`. Clear separation of public fixtures, private state, and shared history.

## Pattern 9: Extension System with TOML Manifests
TOML manifests with semantic versioning constraints for extensions.

```toml
schema_version = "loopx_extension_manifest_v0"
id = "loopx-lark"
requires_loopx_api = ">=1,<2"
permissions = ["read_status", "read_todos", "external_write"]
```

**Absorb into Eli**: Eli's skill templates could have YAML frontmatter with `requires_eli_version` and `permissions` fields.

## Pattern 10: Zero-Dependency CLI
Proves powerful tools can be built with stdlib only. argparse, json, pathlib, subprocess, re.
