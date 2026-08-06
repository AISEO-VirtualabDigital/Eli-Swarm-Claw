# Eli-OS Repository Inventory & Migration

## MIGRATION-BOUNDARIES.md

---
id: migration-boundaries
type: migration_policy
status: binding
project_id: eli-os
---

# Migration Boundaries

## Preserve

- Existing Python/FastAPI application
- Existing Next.js frontend
- Existing Celery workers
- Existing Redis configuration
- Existing database models
- Existing Docker files
- Existing tests

## New Rust Foundation

Preferred location:

```text
eli-os/
├── Cargo.toml
├── crates/
├── apps/
├── proto/
├── migrations/
├── docs/
└── tests/
```

Migration or removal requires a new human order.


## PHASE-1-CONFLICT-REPORT.md

# Phase 1 Conflict Report

## Conflict

Existing implementation is Python/FastAPI.
Phase 1 introduces a Rust workspace.

## Resolution

Build side by side.
Do not replace the legacy system.
Treat the legacy system as the operational reference until migration is explicitly ordered.


## REPOSITORY-INVENTORY.md

---
id: repository-inventory
type: repository_inventory
status: draft
project_id: eli-os
---

# Repository Inventory

## Existing System

- Python / FastAPI backend
- SQLAlchemy
- 55+ database tables
- Celery workers
- Redis queue
- Next.js frontend
- Docker Compose
- 44 passing tests

## Required Agent Action

Qwen must replace this summary with an exact tree from the repository.
