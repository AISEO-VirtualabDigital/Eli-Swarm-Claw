---
id: abs-kos-f01a8493
title: "Knowledge OS Starter Kit — Markdown-Driven Agent Knowledge System"
source: https://github.com/kravetech/kos-starter-kit
category: knowledge-system
skillTags: ["obsidian", "agent-knowledge", "markdown", "memory-system"]
createdAt: 2026-08-07T15:24:11.126Z
absorbedFrom: github-research
---

Knowledge OS Starter Kit is an open-source, Markdown-driven installer for creating a portable Knowledge OS for business, projects, personal work, research, learning, and AI-assisted execution.

## What It Generates
- Numbered Obsidian-compatible domain structure
- Canonical AGENTS.md router with thin Claude and Codex adapters
- Durable memory.md and current-state handoff.md
- Context, metadata, privacy, token, archive, and automation policies
- Optional examples, Git initialization, and migration-safe conflict files

## Key Design Decisions
- **Privacy Model**: Reference system used only to derive reusable architecture. Private notes, identities, credentials NOT included in shared templates
- **Agent Adapters**: Thin adapters for Claude Code and Codex CLI — agents can read/write the knowledge base
- **Handoff Protocol**: handoff.md tracks current state so agents can resume work across sessions
- **Token Policies**: Built-in token management for context window optimization
- **Conflict Files**: Migration-safe — handles conflicts when updating existing systems

## Project Structure
- KOS-INSTALLER.md: canonical agent-executable installer contract
- QUESTIONNAIRE.md: interactive and answer-file questions
- installer/: schema, examples, state template, installation engine
- templates/: neutral source templates
- scripts/: validation, privacy, and manifest utilities

## Relevance to Eli
KOS validates Eli's vault-based knowledge architecture. Eli's micro-chunk-containment-v2 engine IS a Knowledge OS. The AGENTS.md router pattern maps to Eli's eli-chat route. The handoff.md concept maps to Eli's conversation history. KOS's privacy model informs how Eli should handle user data in the vault. The token policy system maps to Eli's context window management in air-llm.ts.