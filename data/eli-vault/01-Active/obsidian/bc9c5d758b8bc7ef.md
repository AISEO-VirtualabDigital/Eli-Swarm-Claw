---
id: bc9c5d758b8bc7ef
source: "eli-obsidian-architecture.md"
"title: Eli-OS Architecture & Binding Decisions"
category: obsidian
skillTags: ["tool"]
containmentHash: 4a2cc47e2c8038fe7192
createdAt: 1786051353889
embeddingSig: "2026:phase:binding|accepted:authority:binding|authority:binding:project|authority:human:obsidian|binding:decisions:command|binding:project:date|command:authority:human|date:2026:phase|decisions:command:authority|human:obsidian:agent|phase:binding:decisions|project:date:2026"
---
s: accepted
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