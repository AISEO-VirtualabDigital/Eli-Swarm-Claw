/**
 * Omni Route — Self-healing API key rotation via OpenInbox
 * 
 * OpenInbox API (tested 2026-08-07):
 *   POST /api/inbox              → Create inbox (NO auth needed)
 *   GET  /api/inbox/:id          → Get inbox status (NO auth needed)
 *   GET  /api/v1/inboxes/:id/emails  → List emails (REQUIRES X-API-Key)
 *   GET  /api/v1/emails/:id      → Get email body (REQUIRES X-API-Key)
 * 
 * Two modes:
 *   1. CREATION-ONLY (no OPENINBOX_API_KEY): Can create inboxes, monitor expiry,
 *      track keys. User manually injects keys or reads emails externally.
 *   2. FULL AUTO (with OPENINBOX_API_KEY): Can also read emails and auto-extract keys.
 * 
 * Flow:
 *   create inbox → use email to signup for API service → poll/read inbox
 *   → extract API key from email → inject into process.env → Eli is LIVE
 */

// ─── Types ────────────────────────────────────────────────────────

export interface OmniKey {
  id: string;
  service: string;
  key: string;
  inboxId: string;
  inboxEmail: string;
  createdAt: number;
  expiresAt: number;
  inboxExpiresAt: number;
  usageEstimate: number;
  usageLimit: number;
  status: 'active' | 'warm' | 'expired' | 'drained';
}

export interface OmniInbox {
  id: string;
  email: string;
  expiresAt: string;
  createdAt: string;
  emailCount: number;
  isExisting: boolean;
  registeredAt?: number;  // when omni became aware of it
}

export interface OmniServiceConfig {
  service: string;
  signupUrl: string;
  keyPattern: RegExp;
  keyHeader: string;
  usageLimit: number;
  modelName: string;
  // How to extract key from various email formats
  keyExtractFrom: 'body' | 'subject' | 'both';
}

export interface OmniState {
  activeKey: OmniKey | null;
  keyHistory: OmniKey[];
  totalRotations: number;
  lastRotationAt: number;
  lastError: string | null;
  inboxPool: OmniInbox[];
  mode: 'full-auto' | 'creation-only';
  openInboxApiKeySet: boolean;
}

// ─── Config ──────────────────────────────────────────────────────

const OI_BASE = 'https://api.openinbox.io';
const INBOX_TTL_MS = 10 * 60 * 1000;  // OpenInbox inboxes last ~10 min

const SERVICES: OmniServiceConfig[] = [
  {
    service: 'gemini',
    signupUrl: 'https://aistudio.google.com/apikey',
    keyPattern: /AIza[0-9A-Za-z_-]{35}/,
    keyHeader: 'GEMINI_API_KEY',
    usageLimit: -1,
    modelName: 'gemini-2.0-flash',
    keyExtractFrom: 'both',
  },
  {
    service: 'openai',
    signupUrl: 'https://platform.openai.com/api-keys',
    keyPattern: /sk-[a-zA-Z0-9]{20,}/,
    keyHeader: 'OPENAI_API_KEY',
    usageLimit: -1,
    modelName: 'gpt-4o-mini',
    keyExtractFrom: 'both',
  },
  {
    service: 'anthropic',
    signupUrl: 'https://console.anthropic.com/settings/keys',
    keyPattern: /sk-ant-[a-zA-Z0-9-]{20,}/,
    keyHeader: 'ANTHROPIC_API_KEY',
    usageLimit: -1,
    modelName: 'claude-sonnet-4-20250514',
    keyExtractFrom: 'both',
  },
];

// ─── OpenInbox API Client ────────────────────────────────────────

async function oiCreateInbox(prefix?: string): Promise<OmniInbox> {
  const body = prefix ? { prefix } : {};
  const res = await fetch(`${OI_BASE}/api/inbox`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`OpenInbox create failed (${res.status}): ${text}`);
  }
  const data = await res.json();
  return {
    id: data.id,
    email: data.email,
    expiresAt: data.expiresAt,
    createdAt: data.createdAt,
    emailCount: data.emailCount || 0,
    isExisting: data.isExisting || false,
  };
}

async function oiGetInbox(inboxId: string): Promise<OmniInbox> {
  const res = await fetch(`${OI_BASE}/api/inbox/${inboxId}`);
  if (!res.ok) throw new Error(`OpenInbox get failed: ${res.status}`);
  const data = await res.json();
  return {
    id: data.id,
    email: data.email,
    expiresAt: data.expiresAt,
    createdAt: data.createdAt,
    emailCount: data.emailCount || 0,
    isExisting: false,
  };
}

async function oiListEmails(inboxId: string, apiKey: string): Promise<any[]> {
  const res = await fetch(`${OI_BASE}/api/v1/inboxes/${inboxId}/emails`, {
    headers: { 'X-API-Key': apiKey },
  });
  if (!res.ok) return [];
  const data = await res.json();
  return Array.isArray(data) ? data : (data.emails || data.data || []);
}

async function oiGetEmail(emailId: string, apiKey: string): Promise<any> {
  const res = await fetch(`${OI_BASE}/api/v1/emails/${emailId}`, {
    headers: { 'X-API-Key': apiKey },
  });
  if (!res.ok) throw new Error(`OpenInbox get email failed: ${res.status}`);
  return res.json();
}

// ─── Key Extraction ──────────────────────────────────────────────

function extractKeyFromText(text: string, pattern: RegExp): string | null {
  const match = text.match(pattern);
  return match ? match[0] : null;
}

function stripHtml(html: string): string {
  return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

// ─── Omni Route Engine ───────────────────────────────────────────

export class OmniRoute {
  private oiApiKey: string;
  private state: OmniState;
  private rotationTimer: ReturnType<typeof setInterval> | null = null;
  private checkInterval: number;
  private preRotateMinutes: number;

  constructor(opts: {
    openInboxApiKey?: string;
    checkIntervalMs?: number;
    preRotateMinutes?: number;
    seedInbox?: string;  // pre-existing inbox email to register
  } = {}) {
    this.oiApiKey = opts.openInboxApiKey || process.env.OPENINBOX_API_KEY || '';
    this.checkInterval = opts.checkIntervalMs || 60_000;
    this.preRotateMinutes = opts.preRotateMinutes || 2;  // rotate 2min before inbox dies

    this.state = {
      activeKey: null,
      keyHistory: [],
      totalRotations: 0,
      lastRotationAt: 0,
      lastError: null,
      inboxPool: [],
      mode: this.oiApiKey ? 'full-auto' : 'creation-only',
      openInboxApiKeySet: !!this.oiApiKey,
    };

    // Register seed inbox if provided
    if (opts.seedInbox) {
      this.state.inboxPool.push({
        id: 'seed',
        email: opts.seedInbox,
        expiresAt: new Date(Date.now() + INBOX_TTL_MS).toISOString(),
        createdAt: new Date().toISOString(),
        emailCount: 0,
        isExisting: true,
        registeredAt: Date.now(),
      });
    }

    // Try to bootstrap with existing env key
    const envKey = process.env.GEMINI_API_KEY || '';
    if (envKey && !envKey.startsWith('Astralform') && envKey.match(/AIza/)) {
      this.state.activeKey = {
        id: `env-${Date.now()}`,
        service: 'gemini',
        key: envKey,
        inboxId: 'env',
        inboxEmail: 'env-injection',
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
   * Start the auto-rotation background loop
   */
  startAutoRotation() {
    if (this.rotationTimer) return;
    console.log(
      `[OMNI] Auto-rotation started | mode=${this.state.mode} | interval=${this.checkInterval / 1000}s | ` +
      `seed inbox=${this.state.inboxPool.length > 0 ? this.state.inboxPool[0].email : 'none'}`
    );
    this.rotationTimer = setInterval(() => this.checkAndRotate(), this.checkInterval);
    this.checkAndRotate();
  }

  stopAutoRotation() {
    if (this.rotationTimer) {
      clearInterval(this.rotationTimer);
      this.rotationTimer = null;
    }
    console.log('[OMNI] Auto-rotation stopped');
  }

  /**
   * Main rotation check — called periodically
   */
  async checkAndRotate(): Promise<void> {
    try {
      const key = this.state.activeKey;

      // No active key → create inbox + prepare for rotation
      if (!key || !key.key) {
        console.log('[OMNI] No active key — ensuring fresh inbox exists...');
        await this.ensureFreshInbox();
        return;
      }

      const now = Date.now();
      const inboxExpiryMs = key.inboxExpiresAt;
      const timeUntilExpiry = inboxExpiryMs - now;
      const preRotateMs = this.preRotateMinutes * 60_000;

      // Check if inbox is about to expire → pre-rotate
      if (timeUntilExpiry < preRotateMs && timeUntilExpiry > 0) {
        console.log(`[OMNI] Inbox expires in ${Math.round(timeUntilExpiry / 60000)}min, pre-rotating...`);
        await this.rotate();
        return;
      }

      // Inbox already expired
      if (timeUntilExpiry <= 0) {
        console.log('[OMNI] Inbox expired, rotating...');
        await this.rotate();
        return;
      }

      // If we have an API key, poll the active inbox for new keys
      if (this.oiApiKey && key.inboxId !== 'env' && key.inboxId !== 'manual') {
        await this.pollInboxForKeys(key.inboxId, key.service);
      }

      // Check usage threshold (if limit is known)
      if (key.usageLimit > 0) {
        const usagePct = key.usageEstimate / key.usageLimit;
        if (usagePct >= 0.7) {
          console.log(`[OMNI] Usage at ${Math.round(usagePct * 100)}%, rotating...`);
          await this.rotate();
        }
      }
    } catch (err) {
      this.state.lastError = (err as Error).message;
      console.error('[OMNI] Check error:', (err as Error).message);
    }
  }

  /**
   * Ensure at least one fresh (non-expired) inbox exists in the pool
   */
  async ensureFreshInbox(): Promise<OmniInbox | null> {
    const now = Date.now();
    const fresh = this.state.inboxPool.find(
      inbox => new Date(inbox.expiresAt).getTime() - now > 3 * 60_000
    );
    if (fresh) return fresh;

    console.log('[OMNI] No fresh inbox — creating new one...');
    return this.createInbox();
  }

  /**
   * Full rotation: create inbox → prepare signup → poll for key → swap
   */
  async rotate(service?: string): Promise<OmniKey | null> {
    const targetService = service || 'gemini';
    const svcConfig = SERVICES.find(s => s.service === targetService);
    if (!svcConfig) {
      this.state.lastError = `Unknown service: ${targetService}`;
      return null;
    }

    console.log(`[OMNI] Rotating ${targetService} key...`);

    try {
      // 1. Create temp inbox
      const prefix = `eli-${targetService}-${Date.now().toString(36)}`;
      const inbox = await oiCreateInbox(prefix);
      console.log(`[OMNI] Inbox created: ${inbox.email} (expires ${inbox.expiresAt})`);

      // 2. Add to pool
      this.addToPool(inbox);

      // 3. If full-auto mode, poll for existing emails that might contain a key
      let extractedKey: string | null = null;
      if (this.oiApiKey) {
        console.log('[OMNI] Polling inbox for API key emails...');
        extractedKey = await this.pollInboxForKeys(inbox.id, targetService);
      }

      // 4. Create the key record
      const newKey: OmniKey = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        service: targetService,
        key: extractedKey || '',
        inboxId: inbox.id,
        inboxEmail: inbox.email,
        createdAt: Date.now(),
        expiresAt: new Date(inbox.expiresAt).getTime(),
        inboxExpiresAt: new Date(inbox.expiresAt).getTime(),
        usageEstimate: 0,
        usageLimit: svcConfig.usageLimit,
        status: extractedKey ? 'active' : 'warm',
      };

      // 5. Archive old key
      if (this.state.activeKey) {
        this.state.activeKey.status = this.state.activeKey.key ? 'expired' : 'drained';
        this.state.keyHistory.push(this.state.activeKey);
        if (this.state.keyHistory.length > 20) {
          this.state.keyHistory = this.state.keyHistory.slice(-20);
        }
      }

      // 6. Set as active
      this.state.activeKey = newKey;
      this.state.totalRotations++;
      this.state.lastRotationAt = Date.now();
      this.state.lastError = null;

      // 7. Inject into process.env if key was extracted
      if (extractedKey && svcConfig.keyHeader) {
        process.env[svcConfig.keyHeader] = extractedKey;
        console.log(`[OMNI] Injected ${svcConfig.keyHeader} into process.env`);
      }

      console.log(`[OMNI] Rotation complete | status=${newKey.status} | email=${inbox.email}`);
      return newKey;
    } catch (err) {
      this.state.lastError = (err as Error).message;
      console.error('[OMNI] Rotation failed:', (err as Error).message);
      return null;
    }
  }

  /**
   * Poll an inbox for emails containing API keys
   * Returns extracted key or null
   */
  async pollInboxForKeys(inboxId: string, service: string, maxAttempts = 6): Promise<string | null> {
    if (!this.oiApiKey) return null;

    const svcConfig = SERVICES.find(s => s.service === service);
    if (!svcConfig) return null;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        await new Promise(r => setTimeout(r, 5000)); // 5s between polls
        const emails = await oiListEmails(inboxId, this.oiApiKey);
        console.log(`[OMNI] Poll ${attempt + 1}: ${emails.length} email(s) in ${inboxId.slice(0, 8)}`);

        for (const email of emails) {
          try {
            const fullEmail = await oiGetEmail(email.id, this.oiApiKey);
            const subject = fullEmail.subject || '';
            const textBody = fullEmail.textBody || fullEmail.text || '';
            const htmlBody = fullEmail.htmlBody || fullEmail.html || '';
            const plainText = stripHtml(htmlBody);

            let searchText = '';
            if (svcConfig.keyExtractFrom === 'body') searchText = `${textBody} ${plainText}`;
            else if (svcConfig.keyExtractFrom === 'subject') searchText = subject;
            else searchText = `${subject} ${textBody} ${plainText}`;

            const key = extractKeyFromText(searchText, svcConfig.keyPattern);
            if (key) {
              console.log(`[OMNI] KEY EXTRACTED from email "${subject.slice(0, 50)}": ${key.slice(0, 10)}...`);

              // Auto-inject
              this.injectKey(service, key);
              return key;
            }
          } catch (emailErr) {
            console.warn(`[OMNI] Error reading email ${email.id}:`, (emailErr as Error).message);
          }
        }
      } catch (err) {
        console.warn(`[OMNI] Poll attempt ${attempt + 1} error:`, (err as Error).message);
      }
    }

    return null;
  }

  /**
   * Manually inject a key
   */
  injectKey(service: string, key: string): OmniKey {
    const svcConfig = SERVICES.find(s => s.service === service);
    const now = Date.now();

    const newKey: OmniKey = {
      id: `manual-${now}`,
      service,
      key,
      inboxId: 'manual',
      inboxEmail: 'manual-injection',
      createdAt: now,
      expiresAt: now + 24 * 60 * 60 * 1000,
      inboxExpiresAt: now + 24 * 60 * 60 * 1000,
      usageEstimate: 0,
      usageLimit: svcConfig?.usageLimit || -1,
      status: 'active',
    };

    // Archive old key
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

    // Inject into process.env
    if (svcConfig?.keyHeader) {
      process.env[svcConfig.keyHeader] = key;
      console.log(`[OMNI] Injected ${svcConfig.keyHeader} into process.env`);
    }

    return newKey;
  }

  /**
   * Create a fresh inbox (without full rotation)
   */
  async createInbox(prefix?: string): Promise<OmniInbox> {
    const p = prefix || `eli-omni-${Date.now().toString(36)}`;
    const inbox = await oiCreateInbox(p);
    this.addToPool(inbox);
    return inbox;
  }

  /**
   * Check a specific inbox for keys (manual trigger)
   */
  async checkInboxForKeys(inboxId: string, service?: string): Promise<string | null> {
    return this.pollInboxForKeys(inboxId, service || 'gemini', 1);
  }

  /**
   * Get the active API key for a service.
   * This is what air-llm.ts calls.
   */
  getActiveKey(service?: string): string {
    const target = service || 'gemini';
    if (this.state.activeKey?.service === target && this.state.activeKey.key) {
      return this.state.activeKey.key;
    }
    // Fallback to env
    if (target === 'gemini') return process.env.GEMINI_API_KEY || '';
    if (target === 'openai') return process.env.OPENAI_API_KEY || '';
    if (target === 'anthropic') return process.env.ANTHROPIC_API_KEY || '';
    return '';
  }

  /**
   * Get the Gemini key specifically (for air-llm compatibility)
   */
  getGeminiKey(): string {
    return this.getActiveKey('gemini');
  }

  /**
   * Check if we have a valid (non-placeholder) key
   */
  hasValidKey(service?: string): boolean {
    const key = this.getActiveKey(service);
    if (!key) return false;
    if (service === 'gemini' || !service) return key.startsWith('AIza');
    if (service === 'openai') return key.startsWith('sk-');
    if (service === 'anthropic') return key.startsWith('sk-ant-');
    return true;
  }

  /**
   * Record usage
   */
  recordUsage(calls: number = 1) {
    if (this.state.activeKey) {
      this.state.activeKey.usageEstimate += calls;
    }
  }

  /**
   * Get full state (for dashboard)
   */
  getState(): OmniState {
    return {
      ...this.state,
      inboxPool: this.state.inboxPool.map(inbox => ({
        ...inbox,
        // Check if expired
        _expired: new Date(inbox.expiresAt).getTime() < Date.now(),
      })) as any,
    };
  }

  /**
   * Get signup instructions for a service
   */
  getSignupInstructions(service?: string): { email: string; url: string; service: string } | null {
    const target = service || 'gemini';
    const svc = SERVICES.find(s => s.service === target);
    const freshInbox = this.state.inboxPool.find(
      i => new Date(i.expiresAt).getTime() - Date.now() > 3 * 60_000
    );
    if (!svc || !freshInbox) return null;
    return {
      email: freshInbox.email,
      url: svc.signupUrl,
      service: target,
    };
  }

  // ─── Private ──────────────────────────────────────────────

  private addToPool(inbox: OmniInbox) {
    // Avoid duplicates
    const exists = this.state.inboxPool.find(i => i.id === inbox.id);
    if (!exists) {
      this.state.inboxPool.push({
        ...inbox,
        registeredAt: Date.now(),
      });
    }
    // Keep pool manageable
    if (this.state.inboxPool.length > 15) {
      this.state.inboxPool = this.state.inboxPool.slice(-15);
    }
  }
}

// ─── Singleton ──────────────────────────────────────────────────────

let omniInstance: OmniRoute | null = null;

export function getOmniRoute(): OmniRoute {
  if (!omniInstance) {
    omniInstance = new OmniRoute({
      openInboxApiKey: process.env.OPENINBOX_API_KEY || '',
      seedInbox: '70ew6zebmoxg@inboxfly.space',
      preRotateMinutes: 2,
    });
    omniInstance.startAutoRotation();
  }
  return omniInstance;
}

/**
 * Convenience: get the current Gemini key from omni.
 * Use this in air-llm.ts instead of reading process.env directly.
 */
export function getOmniGeminiKey(): string {
  return getOmniRoute().getGeminiKey();
}
