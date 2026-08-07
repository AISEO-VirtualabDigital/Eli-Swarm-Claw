---
id: 6e46dd09c2b236dd
source: "eli-obsidian-repository.md"
"title: Eli-OS Repository Inventory & Migration"
category: obsidian
skillTags: ["tool"]
containmentHash: 065b9fdaaaf840afc9c1
createdAt: 1786051353893
embeddingSig: "binding:project:migration|boundaries:migration:boundaries|boundaries:type:migration|inventory:migration:migration|migration:boundaries:migration|migration:boundaries:type|migration:migration:boundaries|migration:policy:status|policy:status:binding|repository:inventory:migration|status:binding:project|type:migration:policy"
---
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