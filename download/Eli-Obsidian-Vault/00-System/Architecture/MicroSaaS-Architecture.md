# Eli MicroSaaS Architecture

## Overview

Eli runs as a lightweight MicroSaaS deployed on a single Ubuntu VPS, accessible at **eli.virtualabdigital.com**. The stack prioritizes simplicity, speed, and minimal operational overhead.

## Runtime & Framework

- **Framework:** Next.js 16 in standalone output mode
- **Runtime:** Bun (replaces Node.js for faster startup and lower memory footprint)
- **Build:** `next build` produces a self-contained `standalone/` directory with all dependencies bundled

## Database & ORM

- **Database:** SQLite — zero-configuration, file-based, perfect for single-server deployments
- **ORM:** Prisma with the SQLite adapter for type-safe queries and schema migrations
- **Schema:** Manages knowledge entries, conversation logs, and caching metadata

## Reverse Proxy & TLS

- **Caddy** serves as the reverse proxy, handling automatic HTTPS via Let's Encrypt
- Routes external traffic to the Bun/Next.js process on a local port
- Provides gzip compression and static asset caching out of the box

## Process Management

- **systemd** service file manages the Eli process lifecycle
- Auto-restarts on crash, logs to journald, starts on boot
- No Docker overhead — direct process execution for minimal latency

## RAG Pipeline

Core retrieval-augmented generation lives in `knowledge-search.ts`:

- **TF-IDF scoring** ranks knowledge entries by term frequency inverse document frequency
- **Bigram matching** catches two-word phrases that unigram search misses
- **Synonym expansion** broadens recall using a curated synonym map
- **5-minute cache** avoids redundant DB queries for repeated similar queries within a short window

The pipeline returns ranked results that are injected into the LLM context window before generation.

## LLM Abstraction Layer

Eli uses a provider abstraction that decouples the core logic from any single model:

- **Primary:** Google Gemini (see [[LLM-Backend]])
- **Fallback:** z-ai-web-dev-sdk sandbox endpoint for development and resilience
- Switchover is automatic — if the primary provider fails, the fallback is invoked transparently

## Deployment Topology

```
Internet → Caddy (443/80) → Bun + Next.js 16 (localhost) → SQLite + Prisma
                                                         ↓
                                                    RAG Pipeline
                                                         ↓
                                                    LLM Provider(s)
```

Single-server, single-process, zero-docker. Built to be maintained by one person with minimal DevOps burden.
