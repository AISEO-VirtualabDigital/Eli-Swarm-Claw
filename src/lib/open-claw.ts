/**
 * Open Claw Engine v2 — Infinite Email Generator + Autonomous Reader
 * 
 * "Open Claw" = self-sufficient, zero-cost, multi-provider email system.
 * 
 * Wired patterns:
 *   OmniKey — penalty tracker with decay, round-robin, skip-set on failure
 *   OmniMail — provider resolution chain, retryable error classification
 *   Agent-Reach — probe-don't-guess health checks
 *   OmniRoute (diegosouzapw) — provider adapter abstraction
 *   browser-use — decoupled browser task generation
 * 
 * Providers:
 *   1. Guerrilla Mail (primary) — session-based, instant, 1hr TTL, no registration
 *   2. mail.tm (secondary) — account-based, JWT auth, @web-library.net
 *   3. OpenInbox (tertiary) — creation-only (free), can't read without paid key
 * 
 * Provider resolution chain (OmniMail pattern):
 *   probe all → filter by skip-set → sort by penalty+latency → round-robin tiebreak
 */

import { audit } from './audit-log';
import { KEY_PATTERNS as CENTRALIZED_KEY_PATTERNS, MAX_PENDING_KEYS, INBOX_TTL_MS } from './safety-gate';

// ─── Types ────────────────────────────────────────────────────────

export interface ClawInbox {
  id: string;
  email: string;
  provider: 'guerrilla' | 'mailtm' | 'openinbox';
  expiresAt: number;        // epoch ms
  createdAt: number;
  sessionData: any;         // provider-specific session (sid_token, jwt, etc.)
  emailCount: number;
  status: 'fresh' | 'polling' | 'expired' | 'error';
}

export interface ClawEmail {
  id: string;
  from: string;
  subject: string;
  bodyText: string;
  bodyHtml: string;
  receivedAt: number;
}

export interface ClawConfig {
  pollIntervalMs: number;
  maxInboxes: number;
  maxPollAttempts: number;
  pollDelayMs: number;
  inboxTtlMs: number;
}

export type ProviderName = 'guerrilla' | 'mailtm' | 'openinbox';

// Agent-Reach: probe-don't-guess + OmniKey: penalty system
export interface ProviderHealth {
  status: 'ok' | 'missing' | 'broken' | 'timeout' | 'error';
  latencyMs: number;
  lastProbeAt: number;
  consecutiveFailures: number;
  penalty: number;       // OmniKey: +3 per failure, -1 per success, max 10
  tier: 0 | 1 | 2;     // Agent-Reach: zero-config / free-key / complex
}

export interface PendingKey {
  id: string;
  service: string;
  key: string;
  envVar: string;
  extractedAt: number;
  inboxId: string;
  inboxEmail: string;
  status: 'pending' | 'approved' | 'rejected';
  validatedAt?: number;
  validationError?: string;
}

export interface ClawState {
  inboxes: ClawInbox[];
  totalGenerated: number;
  totalEmailsRead: number;
  totalKeysExtracted: number;
  lastKeyExtracted: string | null;
  providerStats: Record<string, { generated: number; errors: number; emailsRead: number }>;
  providerHealth: Record<ProviderName, ProviderHealth>;  // from Agent-Reach: probe-don't-guess
  pendingKeys: PendingKey[];
}

// ─── Browser Automation Types (browser-use pattern) ─────────────

export interface ClawBrowserStep {
  action: 'goto' | 'click' | 'fill' | 'wait' | 'screenshot';
  url?: string;
  selector?: string;
  value?: string;
  ms?: number;
  timeout?: number;
}

export interface ClawBrowserTask {
  service: string;
  email: string;
  inboxId: string;
  steps: ClawBrowserStep[];
  postAction: string;    // e.g. "poll-inbox:gm-xxx:30" = poll inbox 30 times
  keyPattern: string | null;  // regex to extract from email, null if no key
}

// ─── Default Config ──────────────────────────────────────────────

const DEFAULT_CONFIG: ClawConfig = {
  pollIntervalMs: 5000,
  maxInboxes: 10,
  maxPollAttempts: 12,
  pollDelayMs: 5000,
  inboxTtlMs: INBOX_TTL_MS,
};

// ─── Provider Base URLs (must be before probes) ──────────────────

const GM_BASE = 'https://api.guerrillamail.com';
const MT_BASE = 'https://api.mail.tm';
const OI_BASE = 'https://api.openinbox.io';

// ─── Provider Health Probes (Agent-Reach: probe-don't-guess) ──────
// Actually test each provider before using it. Catches stale endpoints.

const PROBE_TIMEOUT = 10_000;

// Service patterns — use centralized patterns from safety-gate for consistency
const SERVICES_MAP: Record<string, { pattern: RegExp }> = {
  gemini:    { pattern: CENTRALIZED_KEY_PATTERNS.gemini.pattern },
  openai:    { pattern: CENTRALIZED_KEY_PATTERNS.openai.pattern },
  anthropic: { pattern: CENTRALIZED_KEY_PATTERNS.anthropic.pattern },
};

async function probeGuerrilla(): Promise<ProviderHealth> {
  const start = Date.now();
  try {
    const res = await fetch(`${GM_BASE}/ajax.php?f=get_email_address&lang=en`, {
      signal: AbortSignal.timeout(PROBE_TIMEOUT),
    });
    const latency = Date.now() - start;
    return { status: res.ok ? 'ok' : 'error', latencyMs: latency, lastProbeAt: Date.now(), consecutiveFailures: 0, penalty: 0, tier: 0 };
  } catch (err) {
    return { status: (err as Error).name === 'TimeoutError' ? 'timeout' : 'broken', latencyMs: Date.now() - start, lastProbeAt: Date.now(), consecutiveFailures: 1, penalty: 3, tier: 0 };
  }
}

async function probeMailTm(): Promise<ProviderHealth> {
  const start = Date.now();
  try {
    const res = await fetch(`${MT_BASE}/domains`, { signal: AbortSignal.timeout(PROBE_TIMEOUT) });
    const latency = Date.now() - start;
    return { status: res.ok ? 'ok' : 'error', latencyMs: latency, lastProbeAt: Date.now(), consecutiveFailures: 0, penalty: 0, tier: 0 };
  } catch (err) {
    return { status: (err as Error).name === 'TimeoutError' ? 'timeout' : 'broken', latencyMs: Date.now() - start, lastProbeAt: Date.now(), consecutiveFailures: 1, penalty: 3, tier: 0 };
  }
}

async function probeOpenInbox(): Promise<ProviderHealth> {
  const start = Date.now();
  try {
    const res = await fetch(OI_BASE, { signal: AbortSignal.timeout(PROBE_TIMEOUT) });
    const latency = Date.now() - start;
    return { status: res.ok ? 'ok' : 'error', latencyMs: latency, lastProbeAt: Date.now(), consecutiveFailures: 0, penalty: 0, tier: 1 };
  } catch (err) {
    return { status: (err as Error).name === 'TimeoutError' ? 'timeout' : 'broken', latencyMs: Date.now() - start, lastProbeAt: Date.now(), consecutiveFailures: 1, penalty: 3, tier: 1 };
  }
}

// ─── Provider: Guerrilla Mail ─────────────────────────────────────

async function gmCreate(): Promise<ClawInbox> {
  const res = await fetch(`${GM_BASE}/ajax.php?f=get_email_address&lang=en`);
  if (!res.ok) throw new Error(`Guerrilla create failed: ${res.status}`);
  const data = await res.json();
  return {
    id: `gm-${data.alias || Date.now()}`,
    email: data.email_addr,
    provider: 'guerrilla',
    expiresAt: Date.now() + DEFAULT_CONFIG.inboxTtlMs,
    createdAt: Date.now(),
    sessionData: { sidToken: data.sid_token, alias: data.alias },
    emailCount: 0,
    status: 'fresh',
  };
}

async function gmCheck(inbox: ClawInbox): Promise<ClawEmail[]> {
  const { sidToken } = inbox.sessionData;
  const res = await fetch(
    `${GM_BASE}/ajax.php?f=check_email&lang=en&sid_token=${sidToken}&seq=0`
  );
  if (!res.ok) throw new Error(`Guerrilla check failed: ${res.status}`);
  const data = await res.json();
  const list = data.list || [];
  return list.map((m: any) => ({
    id: `gm-${m.mail_id}`,
    from: m.mail_from,
    subject: m.mail_subject || '',
    bodyText: m.mail_body || m.mail_excerpt || '',
    bodyHtml: m.mail_body || '',
    receivedAt: (m.mail_timestamp || Date.now() / 1000) * 1000,
  }));
}

async function gmFetchEmail(inbox: ClawInbox, emailId: string): Promise<ClawEmail | null> {
  const { sidToken } = inbox.sessionData;
  const numericId = emailId.replace('gm-', '');
  const res = await fetch(
    `${GM_BASE}/ajax.php?f=fetch_email&lang=en&sid_token=${sidToken}&email_id=${numericId}`
  );
  if (!res.ok) return null;
  const data = await res.json();
  return {
    id: emailId,
    from: data.mail_from || '',
    subject: data.mail_subject || '',
    bodyText: data.mail_body || '',
    bodyHtml: data.mail_body || '',
    receivedAt: (data.mail_timestamp || Date.now() / 1000) * 1000,
  };
}

// ─── Provider: mail.tm ─────────────────────────────────────────────

let mtDomains: string[] = [];

async function mtGetDomains(): Promise<string[]> {
  if (mtDomains.length > 0) return mtDomains;
  const res = await fetch(`${MT_BASE}/domains`);
  if (!res.ok) return ['web-library.net']; // fallback
  const data = await res.json();
  mtDomains = (data['hydra:member'] || []).map((d: any) => d.domain);
  return mtDomains;
}

async function mtCreate(): Promise<ClawInbox> {
  const domains = await mtGetDomains();
  const domain = domains[0] || 'web-library.net';
  const localPart = `eli-claw-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
  const address = `${localPart}@${domain}`;
  const password = `Claw${Date.now().toString(36)}!X${Math.random().toString(36).slice(2, 8)}`;

  // Create account
  const accRes = await fetch(`${MT_BASE}/accounts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address, password }),
  });
  if (!accRes.ok) throw new Error(`mail.tm create account failed: ${accRes.status}`);
  const accData = await accRes.json();

  // Get JWT
  const tokRes = await fetch(`${MT_BASE}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address, password }),
  });
  if (!tokRes.ok) throw new Error(`mail.tm get token failed: ${tokRes.status}`);
  const tokData = await tokRes.json();

  return {
    id: `mt-${accData.id}`,
    email: address,
    provider: 'mailtm',
    expiresAt: Date.now() + DEFAULT_CONFIG.inboxTtlMs,
    createdAt: Date.now(),
    sessionData: { token: tokData.token, accountId: accData.id, password },
    emailCount: 0,
    status: 'fresh',
  };
}

async function mtCheck(inbox: ClawInbox): Promise<ClawEmail[]> {
  const { token } = inbox.sessionData;
  const res = await fetch(`${MT_BASE}/messages`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`mail.tm check failed: ${res.status}`);
  const data = await res.json();
  const members = data['hydra:member'] || [];
  return members.map((m: any) => ({
    id: `mt-${m.id}`,
    from: m.from?.address || m.from?.name || '',
    subject: m.subject || '',
    bodyText: m.intro || '',
    bodyHtml: '',
    receivedAt: new Date(m.createdAt).getTime(),
  }));
}

async function mtFetchEmail(inbox: ClawInbox, emailId: string): Promise<ClawEmail | null> {
  const { token } = inbox.sessionData;
  const numericId = emailId.replace('mt-', '');
  const res = await fetch(`${MT_BASE}/messages/${numericId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) return null;
  const data = await res.json();
  // mail.tm returns HTML in data.html[].content
  const htmlParts = data.html || [];
  const textParts = data.text || [];
  return {
    id: emailId,
    from: data.from?.address || '',
    subject: data.subject || '',
    bodyText: textParts.map((p: any) => p.content).join('\n'),
    bodyHtml: htmlParts.map((p: any) => p.content).join('\n'),
    receivedAt: new Date(data.createdAt).getTime(),
  };
}

// ─── Provider: OpenInbox (creation-only) ───────────────────────────

async function oiCreate(): Promise<ClawInbox> {
  const res = await fetch(`${OI_BASE}/api/inbox`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
  if (!res.ok) throw new Error(`OpenInbox create failed: ${res.status}`);
  const data = await res.json();
  return {
    id: data.id,
    email: data.email,
    provider: 'openinbox',
    expiresAt: new Date(data.expiresAt).getTime(),
    createdAt: Date.now(),
    sessionData: {},
    emailCount: 0,
    status: 'fresh',
  };
}

// Can't read emails from OpenInbox without API key, but can check count
async function oiCheck(inbox: ClawInbox): Promise<ClawEmail[]> {
  const res = await fetch(`${OI_BASE}/api/inbox/${inbox.id}`);
  if (!res.ok) throw new Error(`OpenInbox check failed: ${res.status}`);
  const data = await res.json();
  inbox.emailCount = data.emailCount || 0;
  // Can't return actual emails — just update count
  return [];
}

// ─── Key Extraction ──────────────────────────────────────────────

const KEY_PATTERNS: Array<{ name: string; pattern: RegExp; envVar: string }> = [
  { name: 'gemini', pattern: /AIza[0-9A-Za-z_-]{35}/, envVar: 'GEMINI_API_KEY' },
  { name: 'openai', pattern: /sk-[a-zA-Z0-9]{20,}/, envVar: 'OPENAI_API_KEY' },
  { name: 'anthropic', pattern: /sk-ant-[a-zA-Z0-9-]{20,}/, envVar: 'ANTHROPIC_API_KEY' },
  { name: 'google-generic', pattern: /AQ\.[a-zA-Z0-9_-]{30,}/, envVar: 'GEMINI_API_KEY' },
];

function stripHtml(html: string): string {
  return html
    .replace(/<pre[^>]*>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

function extractKeysFromEmail(email: ClawEmail): Array<{ service: string; key: string; envVar: string }> {
  const plainText = `${email.subject} ${email.bodyText} ${stripHtml(email.bodyHtml)}`;
  const results: Array<{ service: string; key: string; envVar: string }> = [];

  for (const kp of KEY_PATTERNS) {
    const matches = plainText.match(new RegExp(kp.pattern.source, 'g'));
    if (matches) {
      for (const match of matches) {
        results.push({ service: kp.name, key: match, envVar: kp.envVar });
      }
    }
  }

  return results;
}

// ─── Open Claw Engine ─────────────────────────────────────────────

export class OpenClaw {
  private config: ClawConfig;
  private inboxes: ClawInbox[] = [];
  private stats: ClawState['providerStats'];
  private totalGenerated = 0;
  private totalEmailsRead = 0;
  private totalKeysExtracted = 0;
  private lastKeyExtracted: string | null = null;
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private keyCallback: ((service: string, key: string, envVar: string, pendingId: string) => void) | null = null;
  private providerHealth: Record<ProviderName, ProviderHealth>;
  private roundRobinIdx = 0;
  private pendingKeys: PendingKey[] = [];
  private autoApproveKeys = false; // Tier 1: default OFF — keys require manual approval

  /**
   * Enable/disable auto-approval of extracted keys.
   * When OFF (default): keys go to pending queue, require POST /api/omni?action=approve
   * When ON: keys are validated and auto-injected (legacy behavior)
   */
  setAutoApprove(enabled: boolean) {
    this.autoApproveKeys = enabled;
    console.log(`[CLAW] Auto-approve ${enabled ? 'ENABLED' : 'DISABLED'} — keys will ${enabled ? 'auto-inject' : 'require approval'}`);
  }

  constructor(config: Partial<ClawConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.stats = {
      guerrilla: { generated: 0, errors: 0, emailsRead: 0 },
      mailtm: { generated: 0, errors: 0, emailsRead: 0 },
      openinbox: { generated: 0, errors: 0, emailsRead: 0 },
    };
    this.providerHealth = {
      guerrilla: { status: 'ok', latencyMs: 0, lastProbeAt: 0, consecutiveFailures: 0, penalty: 0, tier: 0 },
      mailtm: { status: 'ok', latencyMs: 0, lastProbeAt: 0, consecutiveFailures: 0, penalty: 0, tier: 0 },
      openinbox: { status: 'ok', latencyMs: 0, lastProbeAt: 0, consecutiveFailures: 0, penalty: 0, tier: 1 },
    };
  }

  // ─── Two-Phase Provider Selection (Agent-Reach + OmniKey) ──────
  // Phase 1: Probe ALL providers in parallel
  // Phase 2: Select best by ok → penalty asc → latency asc, round-robin tiebreak

  async probeAllProviders(): Promise<void> {
    const [gm, mt, oi] = await Promise.all([probeGuerrilla(), probeMailTm(), probeOpenInbox()]);

    // Penalty decay (OmniKey: -1 per 2 min)
    for (const [name, fresh] of [['guerrilla', gm], ['mailtm', mt], ['openinbox', oi]] as const) {
      const prev = this.providerHealth[name[0] as ProviderName];
      const minsSinceProbe = prev.lastProbeAt > 0 ? (Date.now() - prev.lastProbeAt) / 120_000 : 0;
      const decay = Math.floor(minsSinceProbe);
      const decayedPenalty = Math.max(0, prev.penalty - decay);

      if (fresh.status !== 'ok') {
        fresh.consecutiveFailures = prev.consecutiveFailures + 1;
        fresh.penalty = Math.min(decayedPenalty + 3, 10);
      } else {
        fresh.consecutiveFailures = 0;
        fresh.penalty = Math.max(decayedPenalty - 1, 0);
      }
    }

    this.providerHealth = { guerrilla: gm, mailtm: mt, openinbox: oi };
    console.log(`[CLAW] Probed:`, Object.entries(this.providerHealth).map(
      ([n, h]) => `${n}=${h.status}(${h.latencyMs}ms,p${h.penalty})`
    ).join(' | '));
  }

  async getBestProvider(skipProviders?: Set<string>): Promise<ProviderName> {
    const stale = Object.values(this.providerHealth).every(h => Date.now() - h.lastProbeAt > 120_000);
    if (stale) await this.probeAllProviders();

    // OmniMail: provider resolution chain — filter by skip-set, then sort
    const candidates = Object.entries(this.providerHealth)
      .filter(([name, h]) => h.status === 'ok' && h.consecutiveFailures < 3)
      .filter(([name]) => !skipProviders?.has(name))
      .sort(([, a], [, b]) => a.penalty - b.penalty || a.latencyMs - b.latencyMs);

    if (candidates.length > 0) {
      const bestPenalty = candidates[0][1].penalty;
      const topTier = candidates.filter(([, h]) => h.penalty === bestPenalty);
      const idx = this.roundRobinIdx % topTier.length;
      this.roundRobinIdx++;
      return topTier[idx][0] as ProviderName;
    }

    // OmniMail: fallback — ignore skip-set, use lowest consecutive failures
    if (skipProviders?.size) {
      console.warn(`[CLAW] All providers in skip-set, falling back to best available`);
      return this.getBestProvider();
    }

    const fallback = Object.entries(this.providerHealth)
      .sort(([, a], [, b]) => a.consecutiveFailures - b.consecutiveFailures);
    return (fallback[0]?.[0] || 'guerrilla') as ProviderName;
  }

  /**
   * Record provider success/failure for penalty scoring (OmniKey pattern)
   */
  recordProviderResult(provider: ProviderName, success: boolean) {
    const h = this.providerHealth[provider];
    if (!h) return;
    if (success) {
      h.penalty = Math.max(0, h.penalty - 1);
      h.consecutiveFailures = 0;
    } else {
      h.penalty = Math.min(h.penalty + 3, 10);
      h.consecutiveFailures++;
    }
  }

  /**
   * Register a callback for when a key is extracted
   */
  onKey(callback: (service: string, key: string, envVar: string, pendingId: string) => void) {
    this.keyCallback = callback;
  }

  /**
   * Generate a new inbox. Two-phase selection (Agent-Reach):
   * Probe all providers → select best by penalty + latency + round-robin
   */
  async generate(provider?: ProviderName): Promise<ClawInbox> {
    const targetProvider = provider || await this.getBestProvider();

    try {
      let inbox: ClawInbox;
      switch (targetProvider) {
        case 'guerrilla': inbox = await gmCreate(); break;
        case 'mailtm':   inbox = await mtCreate(); break;
        case 'openinbox': inbox = await oiCreate(); break;
      }

      this.recordProviderResult(targetProvider, true);
      this.inboxes.push(inbox);
      this.totalGenerated++;
      this.stats[targetProvider].generated++;

      // Trim pool
      if (this.inboxes.length > this.config.maxInboxes) {
        this.inboxes = this.inboxes.slice(-this.config.maxInboxes);
      }

      console.log(`[CLAW] Generated ${targetProvider} inbox: ${inbox.email} (expires in ${Math.round((inbox.expiresAt - Date.now()) / 60000)}min)`);
      return inbox;
    } catch (err) {
      this.recordProviderResult(targetProvider, false);
      this.stats[targetProvider].errors++;
      // OmniMail: classify error for upstream handling
      const errMsg = (err as Error).message || '';
      const retryable = [429, 408, 500, 502, 503, 504].some(c => errMsg.includes(String(c)))
        || /timeout|econnrefused|econnreset/i.test(errMsg);
      console.warn(`[CLAW] ${targetProvider} generation failed (${retryable ? 'retryable' : 'non-retryable'}):`, errMsg);
      (err as any)._clawRetryable = retryable;
      throw err;
    }
  }

  /**
   * Check a specific inbox for new emails
   */
  async checkInbox(inbox: ClawInbox): Promise<ClawEmail[]> {
    // Skip expired
    if (Date.now() > inbox.expiresAt) {
      inbox.status = 'expired';
      return [];
    }

    inbox.status = 'polling';

    try {
      let emails: ClawEmail[];
      switch (inbox.provider) {
        case 'guerrilla': emails = await gmCheck(inbox); break;
        case 'mailtm':   emails = await mtCheck(inbox); break;
        case 'openinbox': emails = await oiCheck(inbox); break;
        default: return [];
      }

      inbox.emailCount = emails.length;
      this.totalEmailsRead += emails.length;
      this.stats[inbox.provider].emailsRead += emails.length;

      // Auto-extract keys from new emails — Tier 1: pending queue + validation
      for (const email of emails) {
        const keys = extractKeysFromEmail(email);
        for (const k of keys) {
          console.log(`[CLAW] KEY EXTRACTED [${k.service}]: ${k.key.slice(0, 12)}... from ${inbox.email}`);
          this.totalKeysExtracted++;
          this.lastKeyExtracted = k.key;

          const pendingId = `pending-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
          const pending: PendingKey = {
            id: pendingId,
            service: k.service,
            key: k.key,
            envVar: k.envVar,
            extractedAt: Date.now(),
            inboxId: inbox.id,
            inboxEmail: inbox.email,
            status: 'pending',
          };
          this.pendingKeys.push(pending);
          if (this.pendingKeys.length > MAX_PENDING_KEYS) this.pendingKeys = this.pendingKeys.slice(-MAX_PENDING_KEYS);

          audit('key.extracted', `${k.service} key from ${inbox.email}`, {
            pendingId, keyPreview: k.key.slice(0, 12) + '...', inboxId: inbox.id,
          });

          if (this.autoApproveKeys) {
            // Auto-approve: validate then inject
            await this.validateAndInject(pending);
          }

          // Notify callback (with pendingId so caller can approve/reject)
          this.keyCallback?.(k.service, k.key, k.envVar, pendingId);
        }
      }

      return emails;
    } catch (err) {
      inbox.status = 'error';
      this.stats[inbox.provider].errors++;
      console.warn(`[CLAW] Check error [${inbox.provider}]:`, (err as Error).message);
      return [];
    }
  }

  /**
   * Fetch full email body for a specific email
   */
  async fetchEmail(inbox: ClawInbox, emailId: string): Promise<ClawEmail | null> {
    try {
      switch (inbox.provider) {
        case 'guerrilla': return gmFetchEmail(inbox, emailId);
        case 'mailtm':   return mtFetchEmail(inbox, emailId);
        default: return null; // OpenInbox can't fetch without API key
      }
    } catch (err) {
      console.warn(`[CLAW] Fetch email error:`, (err as Error).message);
      return null;
    }
  }

  /**
   * Poll ALL active inboxes for new emails
   */
  async pollAll(): Promise<Map<string, ClawEmail[]>> {
    const results = new Map<string, ClawEmail[]>();
    const now = Date.now();

    for (const inbox of this.inboxes) {
      if (inbox.status === 'expired' || now > inbox.expiresAt) {
        inbox.status = 'expired';
        continue;
      }
      const emails = await this.checkInbox(inbox);
      if (emails.length > 0) {
        results.set(inbox.email, emails);
      }
    }

    return results;
  }

  /**
   * Start background polling loop
   */
  startPolling() {
    if (this.pollTimer) return;
    console.log(`[CLAW] Polling started (every ${this.config.pollIntervalMs / 1000}s, ${this.inboxes.length} inboxes)`);
    this.pollTimer = setInterval(() => {
      this.pollAll().then(results => {
        if (results.size > 0) {
          console.log(`[CLAW] Poll: ${results.size} inbox(es) have new emails`);
        }
      }).catch(err => {
        console.error('[CLAW] Poll error:', (err as Error).message);
      });
    }, this.config.pollIntervalMs);
  }

  stopPolling() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  /**
   * Generate + immediately start polling a new inbox
   */
  async spawn(provider?: 'guerrilla' | 'mailtm' | 'openinbox'): Promise<ClawInbox> {
    const inbox = await this.generate(provider);
    // If this is the first inbox, start the poll loop
    if (!this.pollTimer) {
      this.startPolling();
    }
    return inbox;
  }

  /**
   * Get fresh (non-expired) inbox — generates one if none available
   */
  async getFreshInbox(): Promise<ClawInbox> {
    const fresh = this.inboxes.find(
      i => i.status !== 'expired' && Date.now() < i.expiresAt - 5 * 60 * 1000
    );
    if (fresh) return fresh;
    return this.spawn();
  }

  /**
   * Get signup instructions for a fresh inbox
   */
  async getSignupInstructions(service?: string): Promise<{
    email: string;
    url: string;
    provider: string;
    service: string;
  } | null> {
    const inbox = await this.getFreshInbox();
    if (!inbox) return null;

    const urls: Record<string, string> = {
      gemini: 'https://aistudio.google.com/apikey',
      openai: 'https://platform.openai.com/api-keys',
      anthropic: 'https://console.anthropic.com/settings/keys',
    };

    return {
      email: inbox.email,
      url: urls[service || 'gemini'] || urls.gemini,
      provider: inbox.provider,
      service: service || 'gemini',
    };
  }

  /**
   * Validate a key by making a test API call, then inject into process.env.
   * Returns true if valid, false if rejected.
   */
  async validateAndInject(pending: PendingKey): Promise<boolean> {
    try {
      // Quick format check first (cheaper than API call)
      const svc = SERVICES_MAP[pending.service];
      if (svc?.pattern && !svc.pattern.test(pending.key)) {
        pending.status = 'rejected';
        pending.validationError = 'Format mismatch';
        pending.validatedAt = Date.now();
        audit('key.rejected', `${pending.service} key failed format check`, { pendingId: pending.id });
        return false;
      }

      // For Gemini keys, make a test call
      if (pending.service === 'gemini' || pending.envVar === 'GEMINI_API_KEY') {
        try {
          const { GoogleGenerativeAI } = await import('@google/generative-ai');
          const genAI = new GoogleGenerativeAI(pending.key);
          const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });
          const result = await model.generateContent({
            contents: [{ role: 'user', parts: [{ text: 'Say OK' }] }],
          });
          const text = result?.response?.text();
          if (!text || text.length === 0) throw new Error('Empty response');
        } catch (err) {
          pending.status = 'rejected';
          pending.validationError = (err as Error).message?.slice(0, 200);
          pending.validatedAt = Date.now();
          audit('key.rejected', `${pending.service} key failed validation: ${(err as Error).message?.slice(0, 100)}`, {
            pendingId: pending.id,
          });
          return false;
        }
      }

      // Passed validation — inject
      pending.status = 'approved';
      pending.validatedAt = Date.now();
      process.env[pending.envVar] = pending.key;
      audit('key.approved', `${pending.service} key validated and injected`, { pendingId: pending.id });
      return true;
    } catch (err) {
      pending.status = 'rejected';
      pending.validationError = (err as Error).message;
      pending.validatedAt = Date.now();
      audit('key.rejected', `${pending.service} key validation error: ${(err as Error).message?.slice(0, 100)}`, {
        pendingId: pending.id,
      });
      return false;
    }
  }

  /** Manually approve a pending key (validates first) */
  async approvePendingKey(pendingId: string): Promise<boolean> {
    const pending = this.pendingKeys.find(k => k.id === pendingId && k.status === 'pending');
    if (!pending) return false;
    return this.validateAndInject(pending);
  }

  /** Manually reject a pending key */
  rejectPendingKey(pendingId: string): boolean {
    const pending = this.pendingKeys.find(k => k.id === pendingId && k.status === 'pending');
    if (!pending) return false;
    pending.status = 'rejected';
    pending.validatedAt = Date.now();
    pending.validationError = 'Manual rejection';
    audit('key.rejected', `${pending.service} key manually rejected`, { pendingId });
    return true;
  }

  /** Get all pending keys */
  getPendingKeys(): PendingKey[] {
    return this.pendingKeys.filter(k => k.status === 'pending');
  }

  /**
   * Get full state (Agent-Reach: sensitive key redaction)
   */
  getState(): ClawState {
    return {
      inboxes: this.inboxes.map(i => ({
        ...i,
        sessionData: { /* stripped */ },
      })),
      totalGenerated: this.totalGenerated,
      totalEmailsRead: this.totalEmailsRead,
      totalKeysExtracted: this.totalKeysExtracted,
      lastKeyExtracted: this.lastKeyExtracted
        ? `${this.lastKeyExtracted.slice(0, 8)}...${this.lastKeyExtracted.slice(-4)}`
        : null,
      providerStats: { ...this.stats },
      providerHealth: { ...this.providerHealth },
      pendingKeys: this.pendingKeys.map(k => ({
        ...k,
        key: `${k.key.slice(0, 8)}...${k.key.slice(-4)}`, // redact in state
      })),
    };
  }

  /**
   * Purge expired inboxes
   */
  purgeExpired(): number {
    const before = this.inboxes.length;
    const now = Date.now();
    this.inboxes = this.inboxes.filter(i => i.status !== 'expired' && now < i.expiresAt);
    return before - this.inboxes.length;
  }

  // ─── Browser Automation Actions (inspired by browser-use) ──────
  //
  // These methods generate the INSTRUCTIONS for browser automation.
  // The actual Playwright/browser-use execution happens on a Python
  // subprocess or a separate microservice.
  //
  // This keeps the claw (TypeScript/Next.js) decoupled from the browser
  // automation layer (Python/Playwright), following OmniRoute's provider
  // abstraction pattern.
  //

  /**
   * Generate a browser automation task for signing up at a service.
   * Returns instructions that a browser-use agent can execute.
   */
  async generateBrowserTask(service: string): Promise<ClawBrowserTask | null> {
    const inbox = await this.getFreshInbox();
    if (!inbox) return null;

    const tasks: Record<string, ClawBrowserTask> = {
      gemini: {
        service,
        email: inbox.email,
        inboxId: inbox.id,
        steps: [
          { action: 'goto', url: 'https://aistudio.google.com/apikey' },
          { action: 'wait', selector: 'input[type="email"]', timeout: 10000 },
          { action: 'fill', selector: 'input[type="email"]', value: inbox.email },
          { action: 'click', selector: 'button[type="submit"]' },
          { action: 'wait', ms: 5000 },
        ],
        postAction: `poll-inbox:${inbox.id}:30`,
        keyPattern: 'AIza[0-9A-Za-z_-]{35}',
      },
      cloudflare: {
        service,
        email: inbox.email,
        inboxId: inbox.id,
        steps: [
          { action: 'goto', url: 'https://dash.cloudflare.com/sign-up' },
          { action: 'wait', selector: 'input[name="email"]', timeout: 10000 },
          { action: 'fill', selector: 'input[name="email"]', value: inbox.email },
          { action: 'fill', selector: 'input[name="password"]', value: `Claw${Date.now().toString(36)}!S${Math.random().toString(36).slice(2, 8)}` },
          { action: 'click', selector: 'button[type="submit"]' },
          { action: 'wait', ms: 3000 },
        ],
        postAction: `poll-inbox:${inbox.id}:60`,
        keyPattern: null,
      },
    };

    return tasks[service] || null;
  }

  /**
   * Get all browser automation tasks for available services
   */
  getSupportedBrowserServices(): string[] {
    return ['gemini', 'cloudflare'];
  }
}

// ─── Singleton ──────────────────────────────────────────────────────

let clawInstance: OpenClaw | null = null;

export function getOpenClaw(): OpenClaw {
  if (!clawInstance) {
    clawInstance = new OpenClaw();
    console.log('[CLAW] Open Claw Engine initialized');
  }
  return clawInstance;
}
