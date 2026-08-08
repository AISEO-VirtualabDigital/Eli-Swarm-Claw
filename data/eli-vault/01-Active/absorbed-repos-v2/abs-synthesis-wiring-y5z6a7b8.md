---
absorbedAt: 2026-08-08
chunkType: synthesis-wiring-plan
tags: [synthesis, wiring-plan, open-claw-v2, omni-route-v2, dashboard-v2, seo-v2, eli-v3]
---

# Absorption Synthesis — Wiring Plan for Eli v3

## What Was Absorbed

| Source | Key Patterns Extracted | Target Module |
|--------|----------------------|---------------|
| **OmniKey** | Penalty system, round-robin, health checking, Zod validation, sticky sessions | omni-route.ts, open-claw.ts |
| **OmniMail** | Queue-based processing, idempotent operations, cursor pagination, version sync | open-claw.ts, vault-search.ts |
| **OmniDash** | Generic DataTable, cmdk palette, server component fetching, cookie-persisted panels | Dashboard page.tsx |
| **LoopX** | Typed enums, handler-chain dispatch, dry-run safety, capability catalog, boundary enforcement | All API routes, skill system |
| **Agent-Reach** | Two-phase backend selection, probe-don't-guess, symlink safety, URL hardening, sensitive redaction | open-claw.ts, omni-route.ts |
| **SomnusAI** | Full meta stack, schema markup, heading hierarchy, stats bar, internal linking, SEO mistakes to avoid | layout.tsx, public pages |

## Immediate Code Changes (Priority Order)

### 1. Open Claw v2 — Provider Health Probes + Two-Phase Selection
- Add `probe()` method to each provider (lightweight test before use)
- Change `generate()` from sequential failover to two-phase: probe all, select best
- Add provider tier tagging (0/1/2)
- Add penalty scoring from OmniKey pattern

### 2. Omni Route v2 — Penalty System + Health Checks + Dry-Run
- Add `penalty` field per provider (from OmniKey)
- Record success/failure per provider, adjust penalty scores
- Add `healthCheck()` that validates active key against provider
- Add `dryRun` option to rotate and inject
- Add idempotency key to rotation (from OmniMail)
- Add sensitive redaction to getState() (from Agent-Reach)

### 3. Dashboard — SEO Meta Stack + Schema Markup
- Add full meta tag stack to layout.tsx (from SomnusAI pattern)
- Add Organization + WebSite + SoftwareApplication JSON-LD
- Fix heading hierarchy
- Add stats bar with Eli's KPIs

### 4. API Routes — Typed Enums + Dry-Run + Handler Chain
- Define TurnResult enum for chat processing (from LoopX)
- Add dry-run mode to mutation endpoints
- Apply handler-chain dispatch pattern

## Future Absorptions (Deferred)
- OmniKey's AES-256-GCM encryption for persistent key storage
- OmniDash's generic DataTable component (needs shadcn/ui install)
- LoopX's extension system with TOML manifests for skills
- Agent-Reach's symlink-hardened file operations
- OmniMail's queue-based email processing

## Vault Chunks Created
1. `abs-omnikey-arch-a1b2c3d4.md` — 10 patterns
2. `abs-omnimail-email-e5f6g7h8.md` — 10 patterns
3. `abs-omnidash-ui-i9j0k1l2.md` — 10 patterns
4. `abs-loopx-control-m3n4o5p6.md` — 10 patterns
5. `abs-agent-reach-deep-q7r8s9t0.md` — 10 patterns
6. `abs-somnusai-seo-u1v2w3x4.md` — 10 patterns + 10 anti-patterns
7. `abs-synthesis-wiring-y5z6a7b8.md` — this file

**Total: 60 patterns absorbed, 10 anti-patterns documented**