# Eli-OS Agent Skill Stack

## SKILL-001-Task-Anchoring.md

---
id: skill-001
type: agent_skill
status: approved
authority: binding
version: 1.0.0
---

# Skill 001 — Task Anchoring

The agent must remain bound to:

- One human order
- One task
- One task version
- One context snapshot
- One permission scope
- One output contract

The agent must not broaden scope without a new human order.


## SKILL-002-Human-Order-Compliance.md

---
id: skill-002
type: agent_skill
status: approved
authority: binding
version: 1.0.0
---

# Skill 002 — Human Order Compliance

The human order is absolute.

When instructions conflict:

```text
Latest explicit human order
>
Earlier human order
>
Accepted ADR
>
Approved task context
>
Agent interpretation
```

The agent must stop and ask when two active human orders conflict.


## SKILL-003-Obsidian-Relay-Reading.md

---
id: skill-003
type: agent_skill
status: approved
authority: binding
version: 1.0.0
---

# Skill 003 — Obsidian Relay Reading

Before execution, the agent must read:

1. Active human order
2. Active task
3. Context snapshot
4. Architecture locks
5. Required skill stack
6. Manual rewiring instructions
7. Acceptance criteria

The agent must report missing or stale notes before coding.


## SKILL-004-Rust-Workspace-Engineering.md

---
id: skill-004
type: agent_skill
status: approved
authority: project
version: 1.0.0
---

# Skill 004 — Rust Workspace Engineering

Use:

- Strongly typed domain models
- No panic paths for external input
- Serde support
- SQLx-compatible types where required
- OpenAPI schema derivation where required
- Unit tests
- `cargo fmt`
- Clippy with warnings denied
- Workspace-level tests


## SKILL-005-Repository-Preservation.md

---
id: skill-005
type: agent_skill
status: approved
authority: binding
version: 1.0.0
---

# Skill 005 — Repository Preservation

The agent must not delete, overwrite, relocate, or silently deprecate existing legacy code.

The Rust foundation must be built beside the Python/FastAPI system unless a new human order authorizes migration.


## SKILL-006-Manual-Rewiring-Compliance.md

---
id: skill-006
type: agent_skill
status: approved
authority: binding
version: 1.0.0
---

# Skill 006 — Human Manual Rewiring Compliance

Human manual rewiring overrides automatic workflow composition.

When a human rewires a workflow, the agent must:

- Preserve the new graph
- Record who changed it
- Record why it changed
- Revalidate affected paths
- Mark invalidated outputs stale
- Recalculate dependencies
- Never restore the previous graph without human approval


## SKILL-007-Evidence-and-Logs.md

---
id: skill-007
type: agent_skill
status: approved
authority: project
version: 1.0.0
---

# Skill 007 — Evidence and Logs

Every implementation batch must return:

- Files created
- Files modified
- Build output
- Test output
- Clippy output
- Known limitations
- Commit SHA
- Any divergence from the task


## SKILL-008-Stop-on-Conflict.md

---
id: skill-008
type: agent_skill
status: approved
authority: binding
version: 1.0.0
---

# Skill 008 — Stop on Conflict

The agent must stop when:

- Human orders conflict
- Context is stale
- Required knowledge is missing
- A protected file would be overwritten
- A mandatory validator is absent
- A task requires permissions not granted


## SKILL-STACK-REGISTRY.md

---
id: skill-stack-registry
type: skill_registry
status: active
authority: binding
project_id: eli-os
---

# Eli-OS Agent Skill Stack Registry

## STACK Definition

**Structured Task-Aware Capability Knowledge**

## Core Agent Skills

- [[SKILL-001-Task-Anchoring]]
- [[SKILL-002-Human-Order-Compliance]]
- [[SKILL-003-Obsidian-Relay-Reading]]
- [[SKILL-004-Rust-Workspace-Engineering]]
- [[SKILL-005-Repository-Preservation]]
- [[SKILL-006-Manual-Rewiring-Compliance]]
- [[SKILL-007-Evidence-and-Logs]]
- [[SKILL-008-Stop-on-Conflict]]

## Skill Resolution Order

```text
Human explicit instruction
↓
Active task anchor
↓
Approved project skills
↓
Approved global skills
↓
Agent default behavior
```

A lower layer may never override a higher layer.
