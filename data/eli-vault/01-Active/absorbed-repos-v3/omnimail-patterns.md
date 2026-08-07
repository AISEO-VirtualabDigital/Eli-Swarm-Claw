---
id: absorbed-omnimail-20250808
source: https://github.com/mibgb65-cloud/OmniMail
title: OmniMail — Email Provider Patterns
category: automation
skillTags: ["pattern", "code", "process"]
containmentHash: sha256-absorbed-omnimail
embeddingSig: trigram:provider:chain:retry
---

# OmniMail — Absorbed Patterns

## 1. Provider Resolution Chain
- Explicit priority ordering: SendFlare domain → Resend domain → SendFlare global
- Domain-scoped JSON config per provider
- fail-fast config validation before any provider call

→ WIRED into: open-claw.ts getBestProvider(skipProviders) with skip-set filtering

## 2. Attachment-Aware Provider Fallback
- SendFlare lacks attachments → auto-falls back to Resend
- If no capable fallback → explicit non-retryable error (no silent data loss)

→ PATTERN NOTED: applies to open-claw.ts (OpenInbox can't read emails → falls back to Guerrilla/mailtm)

## 3. Retryable vs Non-Retryable Error Classification
- Custom error class with `retryable` boolean flag
- 408, 409, 429, 5xx = retryable
- 4xx config errors = non-retryable
- Queue-level: exponential backoff with cap (30s, 60s, 120s, 240s, 300s max)
- After 3 total attempts → permanent failure

→ WIRED into: open-claw.ts _clawRetryable flag + omni-route.ts isRetryableError()

## 4. Version-Based Conditional Polling
- Client polls with version token
- Server returns { unchanged: true, version } if no changes — zero DB queries
- Cross-tab dedup: only one tab polls at a time

→ PATTERN NOTED: could optimize open-claw.ts polling to skip unchanged inboxes

## 5. TTL via purge_after Column
- Set at creation time (not just on trash)
- Workflow-based batched cleanup with claim/release for concurrency
- Multiple retention policies: trash, temporary accounts, audit logs, failed messages

→ ALREADY EXISTS in: open-claw.ts inboxTtlMs + purgeExpired()

## 6. Idempotency Keys
- Client sends idempotencyKey with every operation
- Server checks for existing operation before executing
- Failed idempotent requests auto-requeue on retry

→ NOT YET WIRED: could add to omni API for rotation idempotency

## 7. Compensating Transactions
- On failure: delete partial writes + release quota atomically
- Prevents orphaned state from partial operations

→ PATTERN NOTED: for future open-claw.ts multi-step operations

## 8. Rate Limiting via Atomic UPSERT
- Sliding window implemented as single SQL UPSERT
- Per-user overrides, idempotent retries don't re-count
- Returns 429 + Retry-After header when limited

→ NOT YET WIRED: could add to omni-route.ts for rotation rate limiting
