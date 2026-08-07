---
title: Eli System Architecture
created: 2026-08-07
tags:
  - "system"
  - "architecture"
  - "map"
type: dashboard
---

# Eli System Architecture

> Complete system map of Eli MicroSaaS — VirtuaLab Digital's AI Growth Intelligence

## Backend Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| Runtime | Bun + Next.js 16.1.1 | ✅ Active |
| Frontend | React 19 + Tailwind CSS 4 + shadcn/ui | ✅ Active |
| Knowledge Engine | Micro-Chunk Containment v2 | ✅ 24,331 chunks |
| LLM Backend | Google Gemini 2.0 Flash (Air LLM) | ⚠️ Needs API Key |
| Database | SQLite (Prisma) | ⚠️ Unused scaffold |
| Reverse Proxy | Caddy (auto-HTTPS) | ✅ Production |
| Vault Storage | Obsidian-flavored markdown | ✅ 208 MB |

## API Routes

| Route | Method | Purpose | Status |
|-------|--------|---------|--------|
| `/api/eli-chat` | POST/GET | Core chat with vault retrieval | ✅ Fixed |
| `/api/health` | GET | System health + vault stats | ✅ Fixed |
| `/api/knowledge-stats` | GET | Knowledge base statistics | ✅ Fixed |
| `/api/eli-intro` | GET | Introduction config | ✅ Working |
| `/api/keywords` | GET | Keyword research datasets | ✅ Working |
| `/api/skills` | GET | Skill templates | ✅ Working |

## Knowledge Architecture

```
eli-vault/
├── 00-Containment/    ← Deletion-proof memory (Skill Contain)
├── 01-Active/         ← 24,331 active micro-chunks
│   ├── seo/           ← 2,841 chunks
│   ├── web-design/    ← 7,724 chunks
│   ├── google-api/    ← 3,211 chunks
│   ├── knowledge/     ← 3,640 chunks
│   ├── scraping/      ← 2,749 chunks
│   ├── social/        ← 1,205 chunks
│   ├── ai-agent/      ← 808 chunks
│   ├── obsidian/      ← 681 chunks
│   ├── saas/          ← 644 chunks
│   └── ... (9 more categories)
├── 02-Skills/         ← Extracted patterns & processes
└── 03-Index/          ← Fast term→file lookup indexes
```

## Skill Contain System

> **Every chunk is permanent.** When knowledge is updated or removed from active vault, it moves to `00-Containment/` — Eli retains the patterns forever.

- **Total chunks**: 24,331
- **Active**: 24,331 | **Dissolved**: 0
- **Skill tags**: process (1,018) · capability (1,053) · metric (2,251) · pattern (846) · tool (4,466) · strategy (285) · code (1,015) · warning (204)
- **Sources ingested**: 171 files (7.2M chars)
- **Avg chunk size**: 298 chars (100-600 range)

## Air LLM Pipeline

```
User Query
    ↓
searchVault() → pre-built index lookup (O(1) term→file)
    ↓
parseChunkFile() → read top 10-12 chunks
    ↓
buildVaultKnowledgeMap() → category awareness
    ↓
Gemini 2.0 Flash → generate response with sources
    ↓
Response + source tracking + containment hits
```

## Obsidian Sync

This vault connects to Eli's live system via the sync API.
See [[Sync Setup]] for configuration.
