---
title: Sync Setup
tags:
  - "sync"
  - "setup"
  - "api"
  - "bridge"
type: setup-guide
---

# Obsidian ↔ Eli Sync Setup

> Connect your local Obsidian vault to Eli's live system

## Overview

This vault syncs with Eli's knowledge engine on `eli.virtualabdigital.com`.
The sync is **one-way pull** — Eli's server is the source of truth.

## Sync API Endpoints

### Pull Vault Stats
```
GET https://eli.virtualabdigital.com/api/health
```
Returns vault statistics, chunk counts, category breakdown.

### Pull Knowledge Stats
```
GET https://eli.virtualabdigital.com/api/knowledge-stats
```
Returns detailed knowledge base statistics.

### Chat with Eli
```
POST https://eli.virtualabdigital.com/api/eli-chat
Body: { "message": "your question", "history": [] }
```
Returns Eli's response with vault sources and containment hits.

### Pull Skill Templates
```
GET https://eli.virtualabdigital.com/api/skills
```
Returns all available SEO agent skill templates.

### Pull Keyword Data
```
GET https://eli.virtualabdigital.com/api/keywords
```
Returns keyword research datasets.

## Obsidian Sync Plugin

For automated sync, use the **Obsidian Git** plugin or **Periodic Notes**:

1. Install "Obsidian Git" community plugin
2. Point the git repo to Eli's vault on your VPS
3. Set auto-pull interval (e.g., every 5 minutes)

Alternatively, use the `/api/health` endpoint with a simple cron/scheduled task
to periodically export fresh vault data.

## Vault Structure

```
Eli-Vault/                    ← This vault
├── 00-System/                ← System architecture & maps
├── 01-Categories/            ← One dashboard per knowledge category
├── 02-Skill-Contain/         ← Skill Contain system & records
├── 03-Sources/               ← Source file inventory
├── 04-Sync/                  ← Sync configuration & logs
└── .obsidian/                ← Obsidian app settings
```

## Related

- [[Eli-System-Architecture]]
- [[Skill-Contain-System]]
