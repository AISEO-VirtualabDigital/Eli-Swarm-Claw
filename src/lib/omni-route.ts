/**
 * Omni Route — Self-healing API key rotation via OpenInbox
 * 
 * Architecture:
 * 1. Creates temp inboxes via OpenInbox (no auth needed for creation)
 * 2. Registers the inbox for webhooks (requires API key)
 * 3. Signs up for API services using the temp email
 * 4. Receives the API key in the temp inbox
 * 5. Extracts the key from the email body
 * 6. Swaps it into Eli's runtime config
 * 7. Proactively rotates BEFORE the key drains/expires
 * 
 * The "Omni" part: one endpoint handles ALL key lifecycle management.
 */

// ─── Types ────────────────────────────────────────────────────────

export interface OmniKey {
  id: string;
  service: string;          // 'gemini', 'openai', 'anthropic', etc.
  key: string;
  inboxId: string;
  inboxEmail: string;
  createdAt: number;
  expiresAt: number;
  inboxExpiresAt: number;   // OpenInbox inbox expiry
  usageEstimate: number;      // estimated calls made
  usageLimit: number;        // known limit or -1
  status: 'active' | 'warm' | 'expired' | 'drained';
}

export interface OmniConfig {
  openInboxApiKey?: string;   // For reading emails + webhooks (v1 endpoints)
  rotationThreshold: number; // Rotate when usage reaches this % of limit
  preRotateMinutes: number;   // Rotate this many minutes before inbox expires
  services: OmniServiceConfig[];
}

export interface OmniServiceConfig {
  service: string;
  signupUrl?: string;        // URL to trigger API key email
  signupBody?: string;       // POST body template ({{email}} placeholder)
  keyPattern: RegExp;        // Regex to extract API key from email body
  keyHeader?: string;        // env var name to set
  usageLimit?: number;        // -1 = unknown
  modelName?: string;        // For logging
}

export interface OmniState {
  activeKey: OmniKey | null;
  keyHistory: OmniKey[];
  totalRotations: number;
  lastRotationAt: number;
  lastError: string | null;
  inboxPool: Array<{ id: string; email: string; expiresAt: string; createdAt: string }>;
}

// ─── Default Config ──────────────────────────────────────────────

const DEFAULT_CONFIG: OmniConfig = {
  openInboxApiKey: process.env.OPENINBOX_API_KEY || '',
  rotationThreshold: 0.7,  // rotate at 70% usage
  preRotateMinutes: 10,     // rotate 10min before inbox expires
  services: [
    {
      service: 'gemini',
      signupUrl: 'https://aistudio.google.com/apikey',
      keyPattern: /AIza[0-9A-Za-z_-]{35}/,
      keyHeader: 'GEMINI_API_KEY',
      usageLimit: -1,
      modelName: 'gemini-2.0-flash',
    },
    {
      service: 'openai',
      keyPattern: /sk-[a-zA-Z0-9]{48}/,
      keyHeader: 'OPENAI_API_KEY',
      usageLimit: -1,
    },
  ],
};

// ─── OpenInbox API Client ────────────────────────────────────────

const OI_BASE = 'https://api.openinbox.io';

async function oiCreateInbox(prefix?: string): Promise<{ id: string; email: string; expiresAt: string }> {
  const body = prefix ? { prefix } : {};
  const res = await fetch(`${OI_BASE}/api/inbox`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`OpenInbox create failed: ${res.status}`);
  const data = await res.json();
  return { id: data.id, email: data.email, expiresAt: data.expiresAt };
}

async function oiGetInbox(inboxId: string): Promise<any> {
  const res = await fetch(`${OI_BASE}/api/inbox/${inboxId}`);
  if (!res.ok) throw new Error(`OpenInbox get failed: ${res.status}`);
  return res.json();
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

// ─── Omni Route Engine ───────────────────────────────────────────

export class OmniRoute {
  private config: OmniConfig;
  private state: OmniState;
  private rotationTimer: ReturnType<typeof setInterval> | null = null;
  private checkInterval: number;

  constructor(config: Partial<OmniConfig> = {}, checkIntervalMs = 60_000) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.checkInterval = checkIntervalMs;
    this.state = {
      activeKey: null,
      keyHistory: [],
      totalRotations: 0,
      lastRotationAt: 0,
      lastError: null,
      inboxPool: [],
    };
  }

  /**
   * Start the auto-rotation background loop
   */
  startAutoRotation() {
    if (this.rotationTimer) return;
    console.log('[OMNI] Auto-rotation started, checking every', this.checkInterval / 1000, 's');
    this.rotationTimer = setInterval(() => this.checkAndRotate(), this.checkInterval);
    // Also check immediately
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
      if (!key) {
        console.log('[OMNI] No active key, rotating...');
        await this.rotate();
        return;
      }

      const now = Date.now();
      const inboxExpiryMs = new Date(key.inboxExpiresAt).getTime();
      const timeUntilExpiry = inboxExpiryMs - now;
      const preRotateMs = this.config.preRotateMinutes * 60_000;

      // Check if inbox is about to expire
      if (timeUntilExpiry < preRotateMs) {
        console.log(`[OMNI] Inbox expires in ${Math.round(timeUntilExpiry / 60000)}min, pre-rotating...`);
        await this.rotate();
        return;
      }

      // Check usage threshold (if limit is known)
      if (key.usageLimit > 0) {
        const usagePct = key.usageEstimate / key.usageLimit;
        if (usagePct >= this.config.rotationThreshold) {
          console.log(`[OMNI] Usage at ${Math.round(usagePct * 100)}%, rotating...`);
          await this.rotate();
          return;
        }
      }
    } catch (err) {
      this.state.lastError = (err as Error).message;
      console.error('[OMNI] Check error:', (err as Error).message);
    }
  }

  /**
   * Full rotation: create inbox → signup → poll for key → swap
   */
  async rotate(service?: string): Promise<OmniKey | null> {
    const targetService = service || this.config.services[0]?.service || 'gemini';
    const svcConfig = this.config.services.find(s => s.service === targetService);
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

      // 2. If there's a signup URL, trigger it (fire and forget — the email comes async)
      if (svcConfig.signupUrl) {
        // We can't actually automate Google AI Studio signup from server-side
        // (it requires browser interaction, CAPTCHA, etc.)
        // Instead, we log the email so the user (or a browser automation) can use it
        console.log(`[OMNI] SIGNUP EMAIL: ${inbox.email}`);
        console.log(`[OMNI] Use this email at: ${svcConfig.signupUrl}`);
      }

      // 3. Try to poll for existing API key in the inbox
      let extractedKey: string | null = null;
      if (this.config.openInboxApiKey) {
        console.log('[OMNI] Polling inbox for API key emails...');
        for (let attempt = 0; attempt < 6; attempt++) {
          await new Promise(r => setTimeout(r, 5000)); // 5s between polls
          const emails = await oiListEmails(inbox.id, this.config.openInboxApiKey);
          console.log(`[OMNI] Poll ${attempt + 1}: ${emails.length} emails`);
          
          for (const email of emails) {
            const fullEmail = await oiGetEmail(email.id, this.config.openInboxApiKey);
            const searchText = `${fullEmail.subject || ''} ${fullEmail.textBody || ''} ${fullEmail.htmlBody || ''}`;
            extractedKey = extractKeyFromText(searchText, svcConfig.keyPattern);
            if (extractedKey) {
              console.log(`[OMNI] KEY EXTRACTED: ${extractedKey.slice(0, 10)}...`);
              break;
            }
          }
          if (extractedKey) break;
        }
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
        usageLimit: svcConfig.usageLimit || -1,
        status: extractedKey ? 'active' : 'warm',
      };

      // 5. Archive old key
      if (this.state.activeKey) {
        this.state.activeKey.status = 'expired';
        this.state.keyHistory.push(this.state.activeKey);
        // Keep only last 20 keys
        if (this.state.keyHistory.length > 20) {
          this.state.keyHistory = this.state.keyHistory.slice(-20);
        }
      }

      // 6. Set as active
      this.state.activeKey = newKey;
      this.state.totalRotations++;
      this.state.lastRotationAt = Date.now();
      this.state.lastError = null;

      // 7. If key was extracted, inject into process.env
      if (extractedKey && svcConfig.keyHeader) {
        process.env[svcConfig.keyHeader] = extractedKey;
        console.log(`[OMNI] Injected ${svcConfig.keyHeader} into process.env`);
      }

      // 8. Add inbox to pool for monitoring
      this.state.inboxPool.push({
        id: inbox.id,
        email: inbox.email,
        expiresAt: inbox.expiresAt,
        createdAt: new Date().toISOString(),
      });
      if (this.state.inboxPool.length > 10) {
        this.state.inboxPool = this.state.inboxPool.slice(-10);
      }

      console.log(`[OMNI] Rotation complete. Status: ${newKey.status}`);
      return newKey;
    } catch (err) {
      this.state.lastError = (err as Error).message;
      console.error('[OMNI] Rotation failed:', (err as Error).message);
      return null;
    }
  }

  /**
   * Manually inject a key (e.g., user provides one)
   */
  injectKey(service: string, key: string): OmniKey {
    const svcConfig = this.config.services.find(s => s.service === service);
    const newKey: OmniKey = {
      id: `manual-${Date.now()}`,
      service,
      key,
      inboxId: 'manual',
      inboxEmail: 'manual-injection',
      createdAt: Date.now(),
      expiresAt: Date.now() + 24 * 60 * 60 * 1000, // 24h default
      inboxExpiresAt: Date.now() + 24 * 60 * 60 * 1000,
      usageEstimate: 0,
      usageLimit: svcConfig?.usageLimit || -1,
      status: 'active',
    };

    if (this.state.activeKey) {
      this.state.activeKey.status = 'expired';
      this.state.keyHistory.push(this.state.activeKey);
    }
    this.state.activeKey = newKey;
    this.state.lastRotationAt = Date.now();
    this.state.lastError = null;

    if (svcConfig?.keyHeader) {
      process.env[svcConfig.keyHeader] = key;
    }

    return newKey;
  }

  /**
   * Get current state (for dashboard / API)
   */
  getState(): OmniState {
    return { ...this.state };
  }

  /**
   * Get the current active API key for a service
   */
  getActiveKey(service?: string): string {
    const target = service || this.config.services[0]?.service;
    if (this.state.activeKey && this.state.activeKey.service === target) {
      return this.state.activeKey.key;
    }
    return process.env.GEMINI_API_KEY || '';
  }

  /**
   * Record usage (call after each LLM API call)
   */
  recordUsage(calls: number = 1) {
    if (this.state.activeKey) {
      this.state.activeKey.usageEstimate += calls;
    }
  }

  /**
   * Create a fresh inbox without full rotation (for manual use)
   */
  async createInbox(prefix?: string) {
    const inbox = await oiCreateInbox(prefix);
    this.state.inboxPool.push({
      id: inbox.id,
      email: inbox.email,
      expiresAt: inbox.expiresAt,
      createdAt: new Date().toISOString(),
    });
    return inbox;
  }

  /**
   * Check a specific inbox for new emails and extract keys
   */
  async checkInboxForKeys(inboxId: string, service?: string): Promise<string | null> {
    if (!this.config.openInboxApiKey) {
      console.warn('[OMNI] No OpenInbox API key — cannot read emails');
      return null;
    }
    const targetService = service || this.config.services[0]?.service || 'gemini';
    const svcConfig = this.config.services.find(s => s.service === targetService);
    if (!svcConfig) return null;

    try {
      const emails = await oiListEmails(inboxId, this.config.openInboxApiKey);
      for (const email of emails) {
        const fullEmail = await oiGetEmail(email.id, this.config.openInboxApiKey);
        const searchText = `${fullEmail.subject || ''} ${fullEmail.textBody || ''} ${fullEmail.htmlBody || ''}`;
        const key = extractKeyFromText(searchText, svcConfig.keyPattern);
        if (key) return key;
      }
    } catch (err) {
      console.error('[OMNI] Inbox check error:', (err as Error).message);
    }
    return null;
  }
}

// ─── Singleton ──────────────────────────────────────────────────────

let omniInstance: OmniRoute | null = null;

export function getOmniRoute(): OmniRoute {
  if (!omniInstance) {
    omniInstance = new OmniRoute({
      openInboxApiKey: process.env.OPENINBOX_API_KEY || '',
      services: [
        {
          service: 'gemini',
          signupUrl: 'https://aistudio.google.com/apikey',
          keyPattern: /AIza[0-9A-Za-z_-]{35}/,
          keyHeader: 'GEMINI_API_KEY',
          usageLimit: -1,
          modelName: 'gemini-2.0-flash',
        },
        {
          service: 'openai',
          keyPattern: /sk-[a-zA-Z0-9]{20,}/,
          keyHeader: 'OPENAI_API_KEY',
          usageLimit: -1,
        },
        {
          service: 'anthropic',
          keyPattern: /sk-ant-[a-zA-Z0-9-]{20,}/,
          keyHeader: 'ANTHROPIC_API_KEY',
          usageLimit: -1,
        },
      ],
    });
    omniInstance.startAutoRotation();
  }
  return omniInstance;
}
