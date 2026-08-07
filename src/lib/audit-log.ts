/**
 * Eli Audit Log (Tier 1 Safety)
 * 
 * Structured in-memory audit trail for all sensitive operations.
 * Persists to a JSONL file for post-mortem analysis.
 * 
 * Logged events:
 *   - key.extracted   — Open Claw pulled a key from email
 *   - key.pending     — Key awaiting validation
 *   - key.approved    — Key passed validation and went active
 *   - key.rejected    — Key failed validation
 *   - key.injected    — Manual key injection via API
 *   - key.rotation    — OmniRoute rotated to new inbox
 *   - claw.spawn      — New email inbox created
 *   - claw.poll       — Inbox polled, emails found
 *   - llm.call        — Gemini API called
 *   - llm.failure     — Gemini API call failed
 *   - auth.blocked    — Unauthorized API access attempt
 *   - vault.query     — Vault search executed
 */

import { appendFile, mkdir } from 'fs/promises';
import { join } from 'path';

const LOG_DIR = join(process.cwd(), 'data', 'audit');
const LOG_FILE = join(LOG_DIR, 'audit.jsonl');
const MAX_IN_MEMORY = 500;

export interface AuditEntry {
  ts: string;           // ISO timestamp
  event: string;        // event type (see above)
  detail: string;       // human-readable description
  meta?: Record<string, any>; // structured context
  ip?: string;          // caller IP (if available)
}

const buffer: AuditEntry[] = [];
let initialized = false;

async function ensureDir() {
  if (!initialized) {
    await mkdir(LOG_DIR, { recursive: true }).catch(() => {});
    initialized = true;
  }
}

export async function audit(
  event: string,
  detail: string,
  meta?: Record<string, any>,
  ip?: string
): Promise<void> {
  const entry: AuditEntry = {
    ts: new Date().toISOString(),
    event,
    detail,
    meta,
    ip,
  };

  buffer.push(entry);
  if (buffer.length > MAX_IN_MEMORY) buffer.shift();

  // Persist to JSONL (fire-and-forget, don't block the caller)
 ensureDir().then(() => {
    appendFile(LOG_FILE, JSON.stringify(entry) + '\n').catch((err) => {
      console.error('[AUDIT] Write failed:', (err as Error).message);
    });
  });

  console.log(`[AUDIT] ${entry.ts} ${event}: ${detail}`);
}

export function getAuditLog(options: { limit?: number; event?: string } = {}): AuditEntry[] {
  const { limit = 100, event } = options;
  let entries = [...buffer].reverse(); // newest first
  if (event) entries = entries.filter(e => e.event === event);
  return entries.slice(0, limit);
}
