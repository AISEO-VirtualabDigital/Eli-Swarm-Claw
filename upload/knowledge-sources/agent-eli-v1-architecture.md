# Agent Eli v1 — Architecture & Documentation

# Agent Eli Architecture

## Public layer

- Portfolio
- Work
- Agent Eli
- Systems
- Skills
- Services
- Case studies
- Contact

The operator portrait and professional identity belong in the public viewer experience, not inside the private dashboard.

## Private layer

- Dashboard
- Leads
- Audits
- Campaigns
- Content Engine
- Rank Tracking
- Approvals
- Activity Logs
- Integrations
- Workflows
- Sentinel Scrapers
- Open SEO Skills
- Crew Registry
- Databases
- Knowledge Vault
- Orange Orbit Legacy
- Settings

## Core runtime

Orange Orbit is preserved as Agent Eli's legacy core:

- FastAPI
- owner authentication
- knowledge search
- memory create/search/forget
- OpenRouter model routing
- crew registry
- PostgreSQL
- Redis
- Docker
- safe mode

## State machine

OBSERVE → ANALYZE → PLAN → PREVIEW → APPROVAL → EXECUTE → VERIFY → RECORD

## Prime directive

The operator is final authority.

Eli does not exist to agree.
Eli exists to make the operator faster without lying.


# Implementation Roadmap

## Phase 1 — Foundation
- Preserve Orange Orbit archive
- Move owner authentication into Eli Core
- Migrate memory and knowledge
- Add integration and skill registries
- Add policy engine and audit logging
- Build Baserow-inspired workspace

## Phase 2 — First-party SEO intelligence
- SiteOne adapter
- Search Console and GA4 adapters
- Content decay
- Cannibalization
- Local recon
- AI citation monitoring
- White-label parasite strategy
- Authority link acquisition

## Phase 3 — Execution
- n8n workflows
- WordPress staging
- outreach staging
- reports and deliverables
- approval queue
- verification jobs

## Phase 4 — Persistent knowledge
- Obsidian vault
- Google Drive ingestion
- source-of-truth rules
- semantic retrieval
- provenance and version history


# Orange Orbit → Agent Eli Migration Map

| Orange Orbit capability | Agent Eli destination |
|---|---|
| FastAPI application | Eli Core API |
| Owner token authentication | Security / operator authentication |
| OpenRouter client | Model Router |
| Knowledge store | Knowledge Vault + RAG |
| Memory create/search/forget | Persistent Memory |
| Crew registry | Agent / Crew Registry |
| Director and specialists | Skills and specialist agents |
| PostgreSQL | Structured state |
| Redis | Queue, cache and jobs |
| Docker deployment | Infrastructure |
| Safe mode | Policy engine |
| Manual learning feed | Knowledge intake approval |
| Collab / Connect | Integration registry |
| Missions | Workflow and task engine |

An untouched Orange Orbit archive should be retained before production migration.


# Security and Governance

- Secrets remain server-side only.
- Never put API keys in frontend code, prompts or logs.
- Deny by default for unknown tools.
- Read-only and staging actions may run automatically.
- Publishing, deleting, sending, purchasing, deploying and production writes require owner approval.
- Every action records actor, tool, input summary, decision, result and timestamp.
- Unofficial token/session wrappers are quarantined.
- Redistributed or unlicensed premium plugins are excluded.
- Bulk indexing never implies guaranteed indexing.
- Backlink automation must not create spam, PBNs, hacked links or deceptive placements.
