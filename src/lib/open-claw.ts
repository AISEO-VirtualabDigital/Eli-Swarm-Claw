/**
 * Open Claw Engine — Infinite Email Generator + Autonomous Reader
 * 
 * "Open Claw" = self-sufficient, zero-cost, multi-provider email system.
 * The claw reaches out through multiple free services to generate and read
 * temporary emails without any API keys or payment.
 * 
 * Providers:
 *   1. Guerrilla Mail (primary) — session-based, instant, 1hr TTL, no registration
 *   2. mail.tm (secondary) — account-based, JWT auth, @web-library.net
 *   3. OpenInbox (tertiary) — creation-only (free), can't read without paid key
 * 
 * The claw auto-failovers between providers. If one fails, it slices to the next.
 */

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

export interface ClawState {
  inboxes: ClawInbox[];
  totalGenerated: number;
  totalEmailsRead: number;
  totalKeysExtracted: number;
  lastKeyExtracted: string | null;
  providerStats: Record<string, { generated: number; errors: number; emailsRead: number }>;
}

// ─── Default Config ──────────────────────────────────────────────

const DEFAULT_CONFIG: ClawConfig = {
  pollIntervalMs: 5000,      // poll every 5s
  maxInboxes: 10,            // keep 10 inboxes in pool
  maxPollAttempts: 12,       // try 12 times (60s total)
  pollDelayMs: 5000,         // 5s between polls
  inboxTtlMs: 55 * 60 * 1000, // 55 min (safety margin under 1hr)
};

// ─── Provider: Guerrilla Mail ─────────────────────────────────────

const GM_BASE = 'https://api.guerrillamail.com';

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

const MT_BASE = 'https://api.mail.tm';

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

const OI_BASE = 'https://api.openinbox.io';

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
  private keyCallback: ((service: string, key: string, envVar: string) => void) | null = null;

  constructor(config: Partial<ClawConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.stats = {
      guerrilla: { generated: 0, errors: 0, emailsRead: 0 },
      mailtm: { generated: 0, errors: 0, emailsRead: 0 },
      openinbox: { generated: 0, errors: 0, emailsRead: 0 },
    };
  }

  /**
   * Register a callback for when a key is extracted
   */
  onKey(callback: (service: string, key: string, envVar: string) => void) {
    this.keyCallback = callback;
  }

  /**
   * Generate a new inbox. Tries providers in order: guerrilla → mailtm → openinbox
   */
  async generate(provider?: 'guerrilla' | 'mailtm' | 'openinbox'): Promise<ClawInbox> {
    const providers = provider
      ? [provider]
      : ['guerrilla', 'mailtm', 'openinbox'] as const;

    for (const p of providers) {
      try {
        let inbox: ClawInbox;
        switch (p) {
          case 'guerrilla': inbox = await gmCreate(); break;
          case 'mailtm':   inbox = await mtCreate(); break;
          case 'openinbox': inbox = await oiCreate(); break;
        }

        this.inboxes.push(inbox);
        this.totalGenerated++;
        this.stats[p].generated++;

        // Trim pool
        if (this.inboxes.length > this.config.maxInboxes) {
          this.inboxes = this.inboxes.slice(-this.config.maxInboxes);
        }

        console.log(`[CLAW] Generated ${p} inbox: ${inbox.email} (expires in ${Math.round((inbox.expiresAt - Date.now()) / 60000)}min)`);
        return inbox;
      } catch (err) {
        this.stats[p].errors++;
        console.warn(`[CLAW] ${p} generation failed:`, (err as Error).message);
      }
    }

    throw new Error('All email providers failed');
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

      // Auto-extract keys from new emails
      for (const email of emails) {
        const keys = extractKeysFromEmail(email);
        for (const k of keys) {
          console.log(`[CLAW] KEY EXTRACTED [${k.service}]: ${k.key.slice(0, 12)}... from ${inbox.email}`);
          this.totalKeysExtracted++;
          this.lastKeyExtracted = k.key;
          process.env[k.envVar] = k.key;
          this.keyCallback?.(k.service, k.key, k.envVar);
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
   * Get full state
   */
  getState(): ClawState {
    return {
      inboxes: this.inboxes.map(i => ({
        ...i,
        sessionData: { /* strip sensitive session data */ },
      })),
      totalGenerated: this.totalGenerated,
      totalEmailsRead: this.totalEmailsRead,
      totalKeysExtracted: this.totalKeysExtracted,
      lastKeyExtracted: this.lastKeyExtracted,
      providerStats: { ...this.stats },
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
