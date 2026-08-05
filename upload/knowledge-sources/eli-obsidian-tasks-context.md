# Eli-OS Tasks & Context Snapshots

## CTX-001-Task-Context-Snapshot.md

---
id: ctx-001
type: context_snapshot
status: active
project_id: eli-os
task_id: task-001
created_at: 2026-08-01T20:17:00+04:00
---

# CTX-001 — Task Context Snapshot

## Binding Sources

- [[../01-HUMAN-ORDERS/ORDER-001-Phase-1]]
- [[../03-ARCHITECTURE/ADR/ADR-001-Phase-1-Binding-Decisions]]
- [[../03-ARCHITECTURE/Phase-1-Research-Framework]]
- [[../04-SPRINTS/SPRINT-001-Phase-1]]
- [[../05-REPOSITORY/MIGRATION-BOUNDARIES]]
- [[../05-REPOSITORY/PHASE-1-CONFLICT-REPORT]]

## Current Scope

Phase 1, Step 1 only.

## Staleness Rule

This context becomes stale if:
- the human order changes;
- the ADR is superseded;
- migration boundaries change;
- task acceptance criteria change.


## TASK-001-Phase-1-Core-Identifiers.md

---
id: task-001
type: task
status: active
project_id: eli-os
order_id: order-001
phase: 1
step: 1
assigned_agent: qwen
context_snapshot: ctx-001
required_skill_stack:
  - skill-001
  - skill-002
  - skill-003
  - skill-004
  - skill-005
  - skill-006
  - skill-007
  - skill-008
manual_rewiring_policy: manual-rewiring-policy
---

# TASK-001 — Core Identifiers and Domain Types

## Objective

Create the foundational Rust types all later Eli-OS modules depend on.

## Agent STACK

The assigned agent must load the approved skill stack before execution:

- Task Anchoring
- Human Order Compliance
- Obsidian Relay Reading
- Rust Workspace Engineering
- Repository Preservation
- Manual Rewiring Compliance
- Evidence and Logs
- Stop on Conflict

## Manual Rewiring Requirement

Any human-authored change to task flow, file boundaries, type relationships, or implementation order overrides the agent's generated plan.

## Required Types

- Strongly typed identifiers
- Shared timestamps
- Version types
- Organization
- User
- Project
- Website
- Asset
- Page
- Image
- Entity
- Schema
- Plugin
- Workflow
- Workflow node
- Workflow run
- Task
- Agent task anchor
- Human order
- Knowledge source
- Context snapshot
- Validation result
- Recommendation
- Indexing request
- Telemetry event
- Human review item
- Domain errors

## Identifier Requirements

- Newtype wrappers
- Serde support
- Display and FromStr
- Database compatibility
- OpenAPI schema support
- No panics for invalid external input
- Stable prefixes
- ULID or UUIDv7 internally
- Unit tests for parsing and serialization

## Output Contract

1. Exact files created
2. Full folder tree
3. Cargo check output
4. Cargo test output
5. Clippy output
6. Design decisions
7. Known limitations
8. Commit SHA
