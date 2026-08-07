/**
 * Omni Route v2 — Self-healing API key rotation via Open Claw
 * 
 * Wired patterns from:
 *   OmniKey — dynamic penalty tracker with decay, fallback chain, response headers
 *   OmniRoute (diegosouzapw) — 19-strategy naming, decision transparency
 *   LoopX — typed failure kinds, repair vs replan
 *   OmniMail — retryable vs non-retryable error classification
 * 
 * Architecture:
 *   Open Claw Engine → multi-provider email gen + reader
 *   Omni Route (coordinator) → key lifecycle + penalty + fallback + routing
 * 
 * Modes:
 *   CLAW-AUTO  — Open Claw generates + reads emails, extracts keys automatically
 *   MANUAL     — User injects keys manually via POST /api/omni?action=inject
 *   OI-PAID    — If OPENINBOX_API_KEY set, also uses OpenInbox v1 for reading
 */

import { getOpenClaw, OpenClaw, ClawInbox } from './open-claw';
import { audit } from './audit-log';

// ─── Types ────────────────────────────────────────────────────────

export interface OmniKey {
  id: string;
  service: string;
  key: string;
  inboxId: string;
  inboxEmail: string;
  provider: string;
  createdAt: number;
  expiresAt: number;
  inboxExpiresAt: number;
  usageEstimate: number;
  usageLimit: number;
  status: 'active' | 'warm' | 'expired' | 'drained';
  penalty: number;           // OmniKey: dynamic penalty score
  consecutiveFailures: number; // OmniKey: failure tracking
}

export type TurnResultKind =
  | 'validated_progress'  // Key worked, usage recorded
  | 'validated_completion' // Key still good, no action needed
  | 'repair_required'     // Retryable failure — try again
  | 'replan_required'     // Non-retryable — need new approach
  | 'user_action_required' // Needs manual intervention
  | 'quota_exhausted'     // Usage limit hit
  | 'key_expired';        // TTL expired

export interface OmniDecision {
  strategy: string;       // Routing strategy used (OmniRoute naming)
  provider: string;       // Which claw provider supplied the inbox
  fallbackAttempts: number;
  latencyMs: number;
  keySource: 'claw-auto' | 'env' | 'manual';
}

export interface OmniState {
  activeKey: OmniKey | null;
  keyHistory: OmniKey[];
  totalRotations: number;
  totalFailures: number;
  totalRepairs: number;
  lastRotationAt: number;
  lastError: string | null;
  lastDecision: OmniDecision | null;
  mode: 'claw-auto' | 'manual' | 'oi-paid';
  clawState: any;
}

// ─── Penalty Tracker (from OmniKey) ──────────────────────────────
// Dynamic penalty with time-based decay — sinks bad providers, recovers good ones

const PENALTY_PER_FAILURE = 3;
const MAX_PENALTY = 10;
const PENALTY_DECAY_INTERVAL_MS = 120_000; // 2 min
const PENALTY_DECAY_AMOUNT = 1;
const SUCCESS_RECOVERY = 1;

interface PenaltyEntry {
  penalty: number;
  lastUpdated: number;
  consecutiveFailures: number;
}

class PenaltyTracker {
  private entries = new Map<string, PenaltyEntry>();

  recordFailure(provider: string) {
    const entry = this.getOrCreate(provider);
    entry.penalty = Math.min(MAX_PENALTY, entry.penalty + PENALTY_PER_FAILURE);
    entry.consecutiveFailures++;
    entry.lastUpdated = Date.now();
    console.log(`[PENALTY] ${provider} +${PENALTY_PER_FAILURE} → ${entry.penalty}/${MAX_PENALTY} (${entry.consecutiveFailures} failures)`);
  }

  recordSuccess(provider: string) {
    const entry = this.getOrCreate(provider);
    entry.penalty = Math.max(0, entry.penalty - SUCCESS_RECOVERY);
    entry.consecutiveFailures = 0;
    entry.lastUpdated = Date.now();
  }

  getPenalty(provider: string): number {
    this.decay(provider);
    return this.entries.get(provider)?.penalty || 0;
  }

  private decay(provider: string) {
    const entry = this.entries.get(provider);
    if (!entry) return;
    const elapsed = Date.now() - entry.lastUpdated;
    const decaySteps = Math.floor(elapsed / PENALTY_DECAY_INTERVAL_MS);
    if (decaySteps > 0) {
      entry.penalty = Math.max(0, entry.penalty - (decaySteps * PENALTY_DECAY_AMOUNT));
      entry.lastUpdated += decaySteps * PENALTY_DECAY_INTERVAL_MS;
    }
  }

  private getOrCreate(provider: string): PenaltyEntry {
    if (!this.entries.has(provider)) {
      this.entries.set(provider, { penalty: 0, lastUpdated: Date.now(), consecutiveFailures: 0 });
    }
    return this.entries.get(provider)!;
  }

  getState() {
    const out: Record<string, number> = {};
    for (const [k, v] of this.entries) out[k] = v.penalty;
    return out;
  }
}

// ─── Error Classification (from OmniMail) ────────────────────────

function isRetryableError(err: any): boolean {
  if (!err) return false;
  const msg = (err.message || err.toString()).toLowerCase();
  const status = err.status || err.statusCode || 0;
  // 429 rate limit, 5xx server errors, timeouts, connection issues
  if (status === 429 || status === 408 || status === 503 || status === 500 || status === 502 || status === 504) return true;
  // Pattern matching for common retryable error messages
  const retryablePatterns = ['rate limit', 'quota', 'timeout', 'econnrefused', 'econnreset', 'socket hang up', 'too many requests', 'temporarily unavailable', 'overloaded'];
  return retryablePatterns.some(p => msg.includes(p));
}

// ─── Service Config ──────────────────────────────────────────────

const SERVICES: Record<string, { signupUrl: string; keyHeader: string; modelName: string; keyPattern: RegExp }> = {
  gemini: { signupUrl: 'https://aistudio.google.com/apikey', keyHeader: 'GEMINI_API_KEY', modelName: 'gemini-2.0-flash', keyPattern: /^(AIza|AQ\.)/ },
  openai: { signupUrl: 'https://platform.openai.com/api-keys', keyHeader: 'OPENAI_API_KEY', modelName: 'gpt-4o-mini', keyPattern: /^sk-/ },
  anthropic: { signupUrl: 'https://console.anthropic.com/settings/keys', keyHeader: 'ANTHROPIC_API_KEY', modelName: 'claude-sonnet-4-20250514', keyPattern: /^sk-ant-/ },
};

// ─── Omni Route Engine v2 ────────────────────────────────────────

export class OmniRoute {
  private claw: OpenClaw;
  private state: OmniState;
  private penalties: PenaltyTracker;
  private rotationTimer: ReturnType<typeof setInterval> | null = null;
  private checkInterval: number;
  private preRotateMinutes: number;
  private skipProviders = new Set<string>(); // OmniKey: skip set for failed providers

  constructor(opts: {
    openInboxApiKey?: string;
    checkIntervalMs?: number;
    preRotateMinutes?: number;
    seedInbox?: string;
  } = {}) {
    this.checkInterval = opts.checkIntervalMs || 60_000;
    this.preRotateMinutes = opts.preRotateMinutes || 5;
    this.penalties = new PenaltyTracker();

    this.claw = getOpenClaw();

    // Claw key delivery — notify but don't auto-inject (Tier 1: approval queue)
    this.claw.onKey((service, key, envVar, pendingId) => {
      console.log(`[OMNI] Claw extracted key [${service}] → pending approval (${pendingId})`);
      this.skipProviders.clear();
    });

    this.state = {
      activeKey: null,
      keyHistory: [],
      totalRotations: 0,
      totalFailures: 0,
      totalRepairs: 0,
      lastRotationAt: 0,
      lastError: null,
      lastDecision: null,
      mode: 'claw-auto',
      clawState: null,
    };

    // Bootstrap with env key if valid
    const envKey = process.env.GEMINI_API_KEY || '';
    const geminiPattern = SERVICES.gemini?.keyPattern;
    if (envKey && geminiPattern?.test(envKey)) {
      this.state.activeKey = {
        id: `env-${Date.now()}`,
        service: 'gemini', key: envKey,
        inboxId: 'env', inboxEmail: 'env-injection', provider: 'env',
        createdAt: Date.now(),
        expiresAt: Date.now() + 24 * 60 * 60 * 1000,
        inboxExpiresAt: Date.now() + 24 * 60 * 60 * 1000,
        usageEstimate: 0, usageLimit: -1, status: 'active',
        penalty: 0, consecutiveFailures: 0,
      };
    }
  }

  startAutoRotation() {
    if (this.rotationTimer) return;
    console.log('[OMNI] Auto-rotation started (Open Claw + Penalty Tracker)');
    this.rotationTimer = setInterval(() => this.checkAndRotate(), this.checkInterval);
    // Note: PenaltyTracker.decay() runs automatically on every getPenalty() call.
    // No separate decay timer needed — it's time-based and self-healing.
    this.checkAndRotate();
  }

  stopAutoRotation() {
    if (this.rotationTimer) { clearInterval(this.rotationTimer); this.rotationTimer = null; }
    this.claw.stopPolling();
    console.log('[OMNI] Stopped');
  }

  async checkAndRotate(): Promise<void> {
    const startMs = Date.now();
    try {
      const key = this.state.activeKey;

      if (!key || !key.key) {
        await this.rotate();
        this.recordDecision('claw-auto', 'none', 0, startMs, 'claw-auto');
        return;
      }

      const now = Date.now();
      const timeLeft = key.inboxExpiresAt - now;

      if (timeLeft < this.preRotateMinutes * 60_000) {
        console.log(`[OMNI] Inbox expires in ${Math.round(timeLeft / 60000)}min — pre-rotating`);
        await this.rotate();
        this.recordDecision('priority', key.provider, 0, startMs, key.provider === 'env' ? 'env' : 'claw-auto');
        return;
      }

      if (key.usageLimit > 0 && key.usageEstimate / key.usageLimit >= 0.7) {
        console.log(`[OMNI] Usage at ${Math.round(key.usageEstimate / key.usageLimit * 100)}% — rotating`);
        await this.rotate();
      }
    } catch (err) {
      const retryable = isRetryableError(err);
      this.state.totalFailures++;
      this.state.lastError = (err as Error).message;
      if (retryable) {
        this.state.totalRepairs++;
        console.log(`[OMNI] Retryable error in check — will retry next cycle`);
      } else {
        console.error(`[OMNI] Non-retryable error:`, (err as Error).message);
      }
    }
  }

  async rotate(service?: string, maxAttempts: number = 3): Promise<OmniKey | null> {
    const targetService = service || 'gemini';
    let lastErr: Error | null = null;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        // OmniKey: pick best provider by penalty (lowest wins)
        const provider = await this.claw.getBestProvider(this.skipProviders);
        console.log(`[OMNI] Rotating ${targetService} via ${provider} (attempt ${attempt}/${maxAttempts})...`);

        const clawInbox = await this.claw.spawn(provider as any);

        const newKey: OmniKey = {
          id: `claw-${Date.now()}`,
          service: targetService, key: '',
          inboxId: clawInbox.id, inboxEmail: clawInbox.email, provider: clawInbox.provider,
          createdAt: Date.now(),
          expiresAt: clawInbox.expiresAt, inboxExpiresAt: clawInbox.expiresAt,
          usageEstimate: 0, usageLimit: -1, status: 'warm',
          penalty: 0, consecutiveFailures: 0,
        };

        this.archiveKey();
        this.state.activeKey = newKey;
        this.state.totalRotations++;
        this.state.lastRotationAt = Date.now();
        this.state.lastError = null;
        this.skipProviders.clear();

        this.recordDecision('priority', clawInbox.provider, attempt - 1, Date.now(), 'claw-auto');
        return newKey;
      } catch (err) {
        lastErr = err as Error;
        const provider = this.state.activeKey?.provider || 'unknown';
        if (isRetryableError(err)) {
          this.penalties.recordFailure(provider);
          this.skipProviders.add(provider);
          console.warn(`[OMNI] Attempt ${attempt} failed (retryable) — skipping ${provider}`);
          continue;
        } else {
          console.error(`[OMNI] Non-retryable error on rotate:`, lastErr.message);
          break;
        }
      }
    }

    this.state.lastError = lastErr?.message || 'All rotation attempts failed';
    return null;
  }

  injectKey(service: string, key: string, source?: string): OmniKey {
    audit('key.injected', `Manual ${service} key from ${source || 'manual'}`, { keyPreview: key.slice(0, 12) + '...' });
    const svc = SERVICES[service];
    const now = Date.now();

    const newKey: OmniKey = {
      id: `${source || 'manual'}-${now}`,
      service, key,
      inboxId: source || 'manual',
      inboxEmail: source ? `via-claw-${source}` : 'manual-injection',
      provider: source || 'manual',
      createdAt: now,
      expiresAt: now + 24 * 60 * 60 * 1000,
      inboxExpiresAt: now + 24 * 60 * 60 * 1000,
      usageEstimate: 0, usageLimit: -1, status: 'active',
      penalty: 0, consecutiveFailures: 0,
    };

    this.archiveKey();
    this.state.activeKey = newKey;
    this.state.lastRotationAt = now;
    this.state.lastError = null;

    if (svc?.keyHeader) {
      process.env[svc.keyHeader] = key;
      console.log(`[OMNI] Injected ${svc.keyHeader} into process.env`);
    }

    return newKey;
  }

  /**
   * Classify and handle a usage result (from LoopX typed turn results)
   * Call this after every LLM call to track key health.
   */
  recordResult(result: TurnResultKind, error?: any): void {
    const provider = this.state.activeKey?.provider || 'unknown';

    switch (result) {
      case 'validated_progress':
        this.recordUsage();
        this.penalties.recordSuccess(provider);
        break;
      case 'validated_completion':
        this.penalties.recordSuccess(provider);
        break;
      case 'repair_required':
        this.state.totalFailures++;
        this.state.totalRepairs++;
        this.penalties.recordFailure(provider);
        if (this.state.activeKey) this.state.activeKey.consecutiveFailures++;
        break;
      case 'replan_required':
      case 'quota_exhausted':
      case 'key_expired':
        this.state.totalFailures++;
        this.penalties.recordFailure(provider);
        if (this.state.activeKey) {
          this.state.activeKey.status = result === 'key_expired' ? 'expired' : 'drained';
        }
        break;
      case 'user_action_required':
        // No penalty for user-required actions
        break;
    }
  }

  async createInbox(provider?: 'guerrilla' | 'mailtm' | 'openinbox') {
    return this.claw.spawn(provider);
  }

  async checkInboxForKeys(inboxId: string, service?: string): Promise<string | null> {
    const inbox = this.claw.getState().inboxes.find(i => i.id === inboxId);
    if (!inbox) return null;
    await this.claw.checkInbox(inbox as ClawInbox);
    return this.state.activeKey?.key || null;
  }

  getActiveKey(service?: string): string {
    const target = service || 'gemini';
    if (this.state.activeKey?.service === target && this.state.activeKey.key) {
      return this.state.activeKey.key;
    }
    const svc = SERVICES[target];
    return svc?.keyHeader ? (process.env[svc.keyHeader] || '') : '';
  }

  getGeminiKey(): string { return this.getActiveKey('gemini'); }

  hasValidKey(service?: string): boolean {
    const key = this.getActiveKey(service);
    if (!key) return false;
    const svc = SERVICES[service || 'gemini'];
    return svc?.keyPattern?.test(key) || false;
  }

  recordUsage(calls: number = 1) {
    if (this.state.activeKey) this.state.activeKey.usageEstimate += calls;
  }

  /**
   * Get decision headers for response (from OmniRoute/OmniKey pattern)
   * Attach these to API responses for routing transparency.
   */
  getDecisionHeaders(): Record<string, string> {
    const d = this.state.lastDecision;
    return {
      'X-Omni-Strategy': d?.strategy || 'none',
      'X-Omni-Provider': d?.provider || 'none',
      'X-Omni-Fallback-Attempts': String(d?.fallbackAttempts || 0),
      'X-Omni-Key-Source': d?.keySource || 'none',
    };
  }

  getState(): OmniState {
    return {
      ...this.state,
      clawState: this.claw.getState(),
    };
  }

  getPenalties() { return this.penalties.getState(); }

  async getSignupInstructions(service?: string) {
    return this.claw.getSignupInstructions(service);
  }

  purgeExpired(): number { return this.claw.purgeExpired(); }

  // ─── Private ──────────────────────────────────────────────────

  private archiveKey() {
    if (this.state.activeKey) {
      this.state.activeKey.status = this.state.activeKey.key ? 'expired' : 'drained';
      this.state.keyHistory.push(this.state.activeKey);
      if (this.state.keyHistory.length > 20) {
        this.state.keyHistory = this.state.keyHistory.slice(-20);
      }
    }
  }

  private recordDecision(strategy: string, provider: string, fallbackAttempts: number, startMs: number, keySource: OmniDecision['keySource']) {
    this.state.lastDecision = {
      strategy,
      provider,
      fallbackAttempts,
      latencyMs: Date.now() - startMs,
      keySource,
    };
  }
}

// ─── Singleton ──────────────────────────────────────────────────────

let omniInstance: OmniRoute | null = null;

export function getOmniRoute(): OmniRoute {
  if (!omniInstance) {
    omniInstance = new OmniRoute({ preRotateMinutes: 5 });
    omniInstance.startAutoRotation();
  }
  return omniInstance;
}

export function getOmniGeminiKey(): string {
  return getOmniRoute().getGeminiKey();
}
