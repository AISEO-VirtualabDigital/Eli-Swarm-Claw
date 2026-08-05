# Eli-OS Architecture & Binding Decisions

# Architecture

Binding architecture decisions and research framework.

Accepted ADRs override research notes.
Superseded ADRs must remain for history.


# Authority Model

## Absolute Order

```text
HUMAN
↓
OBSIDIAN
↓
AGENT
```

## Rules

- Human gives the order.
- Obsidian relays and versions the message.
- Agent is task-bound.
- Agents may not expand scope.
- Conflicts return to human.


---
id: phase-1-research
type: architecture_reference
status: reviewed
authority: reference
project_id: eli-os
---

# Eli-OS Phase 1 Research Framework

Paste the final cleaned research framework here.

Binding decisions belong in ADR-001.


---
id: adr-001
type: architecture_decision
status: accepted
authority: binding
project_id: eli-os
date: 2026-08-01
---

# ADR-001 — Phase 1 Binding Decisions

## Command Authority

Human → Obsidian → Agent

## Plugin Isolation

- gRPC: primary boundary
- WASM: lightweight sandbox
- Native Rust: trusted internal modules

## API Versioning

- URL-based
- `/api/v1`

## Degradation Policy

- Auto-publish minimum confidence: 0.90
- Human review below: 0.80
- Fallback drift maximum: 0.10
- Hard validator failure: block
- Sensitive actions: human approval

## Human Review

- PostgreSQL: source of truth
- Redis: realtime coordination
- Approved with edits: revalidate affected nodes

## OpenAPI

- Code-first generation
- Drift check
- Breaking-change check
- Contract testing
