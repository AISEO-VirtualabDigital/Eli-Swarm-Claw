/**
 * Omni Route — Self-healing API key rotation via Open Claw
 * 
 * Architecture:
 *   Open Claw Engine (primary) — multi-provider infinite email gen + reader
 *     ├─ Guerrilla Mail (session, 1hr TTL, free read)
 *     ├─ mail.tm (account, JWT, @web-library.net, free read)
 *     └─ OpenInbox (creation-only free, read needs paid key)
 *   
 *   Omni Route (coordinator) — key lifecycle management
 *     ├─ Tracks active key, history, usage
 *     ├─ Auto-rotates before inbox expiry
 *     ├─ Extracts keys from email content
 *     └─ Injects keys into process.env + notifies Air LLM
 * 
 * Modes:
 *   CLAW-AUTO  — Open Claw generates + reads emails, extracts keys automatically
 *   MANUAL     — User injects keys manually via POST /api/omni?action=inject
 *   OI-PAID    — If OPENINBOX_API_KEY set, also uses OpenInbox v1 for reading
 */

import { getOpenClaw, OpenClaw, ClawInbox } from './open-claw';

// ─── Types ────────────────────────────────────────────────────────

export interface OmniKey {
  id: string;
  service: string;
  key: string;
  inboxId: string;
  inboxEmail: string;
  provider: string;         // which claw provider generated the inbox
  createdAt: number;
  expiresAt: number;
  inboxExpiresAt: number;
  usageEstimate: number;
  usageLimit: number;
  status: 'active' | 'warm' | 'expired' | 'drained';
}

export interface OmniState {
  activeKey: OmniKey | null;
  keyHistory: OmniKey[];
  totalRotations: number;
  lastRotationAt: number;
  lastError: string | null;
  mode: 'claw-auto' | 'manual' | 'oi-paid';
  clawState: any;
}

// ─── Service Config ──────────────────────────────────────────────

const SERVICES = {
  gemini: {
    signupUrl: 'https://aistudio.google.com/apikey',
    keyHeader: 'GEMINI_API_KEY',
    modelName: 'gemini-2.0-flash',
  },
  openai: {
    signupUrl: 'https://platform.openai.com/api-keys',
    keyHeader: 'OPENAI_API_KEY',
    modelName: 'gpt-4o-mini',
  },
  anthropic: {
    signupUrl: 'https://console.anthropic.com/settings/keys',
    keyHeader: 'ANTHROPIC_API_KEY',
    modelName: 'claude-sonnet-4-20250514',
  },
};

// ─── Omni Route Engine ───────────────────────────────────────────

export class OmniRoute {
  private claw: OpenClaw;
  private state: OmniState;
  private rotationTimer: ReturnType<typeof setInterval> | null = null;
  private checkInterval: number;
  private preRotateMinutes: number;

  constructor(opts: {
    openInboxApiKey?: string;
    checkIntervalMs?: number;
    preRotateMinutes?: number;
    seedInbox?: string;
  } = {}) {
    this.checkInterval = opts.checkIntervalMs || 60_000;
    this.preRotateMinutes = opts.preRotateMinutes || 5;

    // Initialize the Claw
    this.claw = getOpenClaw();

    // When the claw extracts a key, auto-inject it into omni
    this.claw.onKey((service, key, envVar) => {
      console.log(`[OMNI] Claw delivered key [${service}] → injecting into omni`);
      this.injectKey(service, key, `${envVar}`);
    });

    this.state = {
      activeKey: null,
      keyHistory: [],
      totalRotations: 0,
      lastRotationAt: 0,
      lastError: null,
      mode: 'claw-auto',
      clawState: null,
    };

    // Bootstrap with env key if valid
    const envKey = process.env.GEMINI_API_KEY || '';
    if (envKey && !envKey.startsWith('Astralform') && (envKey.match(/AIza/) || envKey.match(/^AQ\./))) {
      this.state.activeKey = {
        id: `env-${Date.now()}`,
        service: 'gemini',
        key: envKey,
        inboxId: 'env',
        inboxEmail: 'env-injection',
        provider: 'env',
        createdAt: Date.now(),
        expiresAt: Date.now() + 24 * 60 * 60 * 1000,
        inboxExpiresAt: Date.now() + 24 * 60 * 60 * 1000,
        usageEstimate: 0,
        usageLimit: -1,
        status: 'active',
      };
    }
  }

  /**
   * Start auto-rotation
   */
  startAutoRotation() {
    if (this.rotationTimer) return;
    console.log('[OMNI] Auto-rotation started (Open Claw powered)');
    this.rotationTimer = setInterval(() => this.checkAndRotate(), this.checkInterval);
    this.checkAndRotate();
  }

  stopAutoRotation() {
    if (this.rotationTimer) {
      clearInterval(this.rotationTimer);
      this.rotationTimer = null;
    }
    this.claw.stopPolling();
    console.log('[OMNI] Stopped');
  }

  /**
   * Main rotation loop
   */
  async checkAndRotate(): Promise<void> {
    try {
      const key = this.state.activeKey;

      // No active key → spawn claw inbox
      if (!key || !key.key) {
        console.log('[OMNI] No active key — spawning claw inbox...');
        await this.rotate();
        return;
      }

      const now = Date.now();
      const timeLeft = key.inboxExpiresAt - now;
      const preRotateMs = this.preRotateMinutes * 60_000;

      if (timeLeft < preRotateMs) {
        console.log(`[OMNI] Inbox expires in ${Math.round(timeLeft / 60000)}min — pre-rotating`);
        await this.rotate();
        return;
      }

      // Usage threshold check
      if (key.usageLimit > 0) {
        const pct = key.usageEstimate / key.usageLimit;
        if (pct >= 0.7) {
          console.log(`[OMNI] Usage at ${Math.round(pct * 100)}% — rotating`);
          await this.rotate();
        }
      }
    } catch (err) {
      this.state.lastError = (err as Error).message;
      console.error('[OMNI] Check error:', (err as Error).message);
    }
  }

  /**
   * Full rotation: claw generates inbox → return signup info
   */
  async rotate(service?: string): Promise<OmniKey | null> {
    const targetService = service || 'gemini';
    console.log(`[OMNI] Rotating ${targetService} via Open Claw...`);

    try {
      // 1. Claw spawns a new inbox (auto-picks best provider)
      const clawInbox = await this.claw.spawn();

      // 2. Create the omni key record (warm — waiting for email)
      const newKey: OmniKey = {
        id: `claw-${Date.now()}`,
        service: targetService,
        key: '',
        inboxId: clawInbox.id,
        inboxEmail: clawInbox.email,
        provider: clawInbox.provider,
        createdAt: Date.now(),
        expiresAt: clawInbox.expiresAt,
        inboxExpiresAt: clawInbox.expiresAt,
        usageEstimate: 0,
        usageLimit: -1,
        status: 'warm',
      };

      // 3. Archive old key
      if (this.state.activeKey) {
        this.state.activeKey.status = this.state.activeKey.key ? 'expired' : 'drained';
        this.state.keyHistory.push(this.state.activeKey);
        if (this.state.keyHistory.length > 20) {
          this.state.keyHistory = this.state.keyHistory.slice(-20);
        }
      }

      // 4. Set active
      this.state.activeKey = newKey;
      this.state.totalRotations++;
      this.state.lastRotationAt = Date.now();
      this.state.lastError = null;

      console.log(`[OMNI] Rotation done | inbox=${clawInbox.email} | provider=${clawInbox.provider}`);
      return newKey;
    } catch (err) {
      this.state.lastError = (err as Error).message;
      console.error('[OMNI] Rotation failed:', (err as Error).message);
      return null;
    }
  }

  /**
   * Manually inject a key
   */
  injectKey(service: string, key: string, source?: string): OmniKey {
    const svc = SERVICES[service as keyof typeof SERVICES];
    const now = Date.now();

    const newKey: OmniKey = {
      id: `${source || 'manual'}-${now}`,
      service,
      key,
      inboxId: source || 'manual',
      inboxEmail: source ? `via-claw-${source}` : 'manual-injection',
      provider: source || 'manual',
      createdAt: now,
      expiresAt: now + 24 * 60 * 60 * 1000,
      inboxExpiresAt: now + 24 * 60 * 60 * 1000,
      usageEstimate: 0,
      usageLimit: -1,
      status: 'active',
    };

    // Archive old
    if (this.state.activeKey) {
      this.state.activeKey.status = this.state.activeKey.key ? 'expired' : 'drained';
      this.state.keyHistory.push(this.state.activeKey);
      if (this.state.keyHistory.length > 20) {
        this.state.keyHistory = this.state.keyHistory.slice(-20);
      }
    }

    this.state.activeKey = newKey;
    this.state.lastRotationAt = now;
    this.state.lastError = null;

    // Inject into env
    if (svc?.keyHeader) {
      process.env[svc.keyHeader] = key;
      console.log(`[OMNI] Injected ${svc.keyHeader} into process.env`);
    }

    return newKey;
  }

  /**
   * Create a standalone inbox via claw (no rotation)
   */
  async createInbox(provider?: 'guerrilla' | 'mailtm' | 'openinbox') {
    return this.claw.spawn(provider);
  }

  /**
   * Check a specific claw inbox for keys
   */
  async checkInboxForKeys(inboxId: string, service?: string): Promise<string | null> {
    const inbox = this.claw.getState().inboxes.find(i => i.id === inboxId);
    if (!inbox) return null;

    const emails = await this.claw.checkInbox(inbox as ClawInbox);
    if (emails.length > 0) {
      // Keys are auto-extracted by the claw's checkInbox method
      // Check if the active key was updated
      if (this.state.activeKey?.key) {
        return this.state.activeKey.key;
      }
    }
    return null;
  }

  /**
   * Get active key for a service
   */
  getActiveKey(service?: string): string {
    const target = service || 'gemini';
    if (this.state.activeKey?.service === target && this.state.activeKey.key) {
      return this.state.activeKey.key;
    }
    // Fallback to env
    const svc = SERVICES[target as keyof typeof SERVICES];
    if (svc?.keyHeader) return process.env[svc.keyHeader] || '';
    return '';
  }

  getGeminiKey(): string {
    return this.getActiveKey('gemini');
  }

  hasValidKey(service?: string): boolean {
    const key = this.getActiveKey(service);
    if (!key) return false;
    const s = service || 'gemini';
    if (s === 'gemini') return key.match(/AIza|AQ\./) ? true : false;
    if (s === 'openai') return key.startsWith('sk-');
    if (s === 'anthropic') return key.startsWith('sk-ant-');
    return true;
  }

  recordUsage(calls: number = 1) {
    if (this.state.activeKey) {
      this.state.activeKey.usageEstimate += calls;
    }
  }

  /**
   * Get full state for dashboard
   */
  getState(): OmniState {
    return {
      ...this.state,
      clawState: this.claw.getState(),
    };
  }

  /**
   * Get signup instructions for the freshest claw inbox
   */
  async getSignupInstructions(service?: string): Promise<{ email: string; url: string; provider: string; service: string } | null> {
    return this.claw.getSignupInstructions(service);
  }

  /**
   * Purge expired claw inboxes
   */
  purgeExpired(): number {
    return this.claw.purgeExpired();
  }
}

// ─── Singleton ──────────────────────────────────────────────────────

let omniInstance: OmniRoute | null = null;

export function getOmniRoute(): OmniRoute {
  if (!omniInstance) {
    omniInstance = new OmniRoute({
      preRotateMinutes: 5,
    });
    omniInstance.startAutoRotation();
  }
  return omniInstance;
}

/**
 * Convenience: get current Gemini key from omni.
 */
export function getOmniGeminiKey(): string {
  return getOmniRoute().getGeminiKey();
}
