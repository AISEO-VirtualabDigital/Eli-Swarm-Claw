---
absorbedFrom: https://github.com/mibgb65-cloud/OmniMail
absorbedAt: 2026-08-08
chunkType: email-architecture-pattern
tags: [omnimail, email-engine, queue-processing, cursor-pagination, idempotent-send, mime-parsing, provider-abstraction, quota-system, cloudflare-workers]
---

# OmniMail — Multi-Domain Webmail on Cloudflare Workers

## Core Concept
Self-hosted webmail built entirely on Cloudflare's serverless stack. Wraps Cloudflare Email Routing (inbound catch-all) with React frontend + Hono API Worker. NOT IMAP/SMTP — uses D1 (SQLite), R2 (object storage), and Queues.

## Pattern 1: Queue-Based Async Processing with Typed Jobs
Single queue, discriminated union on `kind`, separate consumer handlers. 3 job types:
- `parse` — MIME parsing via postal-mime (3 retries, dead letter queue)
- `outbound` — Email delivery via Resend/SendFlare (exponential backoff: 30s→60s→120s→300s)
- `index` — Full-text search index backfill

```typescript
type MailQueueJob = ParseJob | OutboundJob | SearchIndexJob
```

**Absorb into Eli**: Open Claw's email processing could use a job queue pattern for reliability. Currently it polls synchronously — a queue would make it resilient to failures.

## Pattern 2: Idempotent Send with Client-Supplied Keys
Every send requires `idempotencyKey` (`/^[a-zA-Z0-9_-]{8,100}$/`). Server checks before writing — duplicate keys return existing message without re-sending. Retry-safe.

```typescript
const existing = await db.query(
  'SELECT id, status FROM messages WHERE client_request_id = ? AND mailbox_address = ?',
  [idempotencyKey, mailboxAddress]
)
if (existing) return existing;
```

**Absorb into Eli**: Add idempotency keys to Omni Route's rotation — prevent double-rotation from race conditions.

## Pattern 3: Cursor-Based Pagination with Version Sync
Opaque base64url cursors encoding `[sortTime, id]`. DB triggers auto-increment version on INSERT/UPDATE/DELETE. Client sends `?version=N`; if DB version matches, returns `{ unchanged: true }` — eliminates redundant queries.

**Absorb into Eli**: Apply to vault-search API for efficient chunk pagination with conditional sync.

## Pattern 4: Storage Quota Reservation Pattern
Atomic check+update: `reserveStorage()` claims bytes before write, `releaseStorage()` returns them on failure. Prevents quota races.

## Pattern 5: Provider Abstraction with Domain-Based Routing
Per-domain provider resolution from environment config: SendFlare domain-specific → Resend domain-specific → SendFlare global.

```typescript
export function outboundProviderForAddress(env, address): OutboundProviderConfig | null {
  // SendFlare domain → Resend domain → SendFlare global
  return { provider: 'resend' | 'sendflare', apiKey, from? }
}
```

**Absorb into Eli**: This is exactly how Open Claw's provider routing works (guerrilla → mailtm → openinbox). Validate the pattern matches. The OmniMail pattern adds domain-based resolution which could extend to service-based routing in Omni Route.

## Pattern 6: Search Index as Separate Table
Denormalized `message_search` table with pre-indexed content (subject + sender + recipients + body, truncated at 200K chars). `LIKE` queries with proper escaping. Updated via queue.

**Absorb into Eli**: Eli's vault-search already has a search index. This pattern validates the denormalized approach for SQLite-backed search.

## Pattern 7: Self-Evolving Schema with Version Tracking
No migration files — schema evolves in code via `ALTER TABLE` on every request if version mismatch. Works for single-tenant D1.

## Pattern 8: Anti-Bot Detection in Content
HTML emails rendered in sandboxed iframe with scripts/forms/remote network blocked. Remote images blocked by default. Security-first approach.

## Pattern 9: Attachment Handling
Individual R2 objects at `attachments/{messageId}/{index}`. Metadata in D1 with `content_id` for inline/CID references. Max 5 per message, 5 MiB each, 10 MiB total.

## Pattern 10: Security — PBKDF2-SHA256 with 100K iterations
Per-user random salt, Web Crypto API. Tokens stored as SHA-256 hashes only. Sessions: HttpOnly + Secure + SameSite=Lax cookies. Rate limiting: IP + email compound keys.