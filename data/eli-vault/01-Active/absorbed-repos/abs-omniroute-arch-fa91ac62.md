---
id: abs-omniroute-arch-fa91ac62
title: "OmniRoute — AI Gateway Architecture (290+ providers, 500+ models)"
source: https://github.com/diegosouzapw/OmniRoute
category: omniroute
skillTags: ["api-routing", "llm-gateway", "multi-provider", "auto-fallback"]
createdAt: 2026-08-07T15:24:11.124Z
absorbedFrom: github-research
---

OmniRoute is a local AI routing gateway and dashboard built on Next.js. It provides a single OpenAI-compatible endpoint (/v1/*) that aggregates 290+ LLM providers (90+ free) and 500+ models into one unified API.

## Core Architecture
- **Request Flow**: CLI/tools (226 providers, 60 executors) → Request/response translation → Model combo fallback → Account-level fallback → Quota-aware selection → Provider connection
- **Combo System**: Chain of models that auto-fallback. When quota runs out, provider fails, or costs spike, the combo silently slides to the next model. This is what makes OmniRoute "unbreakable."
- **Zero-config**: Works out of the box with model="auto" — no API keys needed for 90+ free providers
- **Free Tier Aggregation**: ~1.53B free tokens/month by stacking free tiers across 43 provider pools

## Key Components
- 226 provider integrations, 60 executors
- Quota preflight and quota-aware account selection
- OAuth + API-key management (16 OAuth modules)
- Multi-modal: embeddings (6 providers), image gen (10+ providers), audio (7 providers), TTS (10 providers), video gen, music gen, web search (5 providers), moderations, reranking
- Think tag parsing for reasoning models
- RTK + Caveman compression (saves 15-95% tokens)
- MCP Server (87 tools) with 3 transports (stdio/SSE/Streamable HTTP)
- A2A Server (JSON-RPC 2.0 + SSE)
- Memory system, Skills system, Prompt compression pipeline
- Circuit breaker pattern, anti-thundering herd protection
- Per-account rate limiting with provider-specific profiles
- IP allowlist/blocklist, compliance audit logging

## Relevance to Eli
The OmniRoute combo system is directly applicable to Eli's omni-route: instead of routing to different LLM providers, Eli routes to different EMAIL providers (Guerrilla Mail, mail.tm, OpenInbox). The same "combo fallback" pattern applies — if one email provider fails, slide to the next. The quota-aware selection maps to Eli's inbox TTL tracking. The zero-config approach maps to Eli's claw-auto mode.