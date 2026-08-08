const { Document, Packer, Paragraph, TextRun, Header, Footer, Table, TableRow, TableCell,
        AlignmentType, HeadingLevel, PageNumber, WidthType, ShadingType, PageBreak,
        TableOfContents, NumberFormat, SectionType, BorderStyle } = require('docx');
const fs = require('fs');

// ─── Palette: Tech/Security (Cool + Heavy + Active) ───
const P = {
  primary: "#0D1B2A",
  body: "#1B2838",
  secondary: "#5A6B7E",
  accent: "#00B4D8",
  surface: "#F0F4F8"
};

const c = (hex) => hex.replace('#', '');
const NB = { style: BorderStyle.NONE, size: 0, color: '000000' };
const allNoBorders = { top: NB, bottom: NB, left: NB, right: NB,
  insideHorizontal: NB, insideVertical: NB };

// ─── Helpers ───────────────────────────────────────

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 480, after: 200 },
    children: [new TextRun({ text, bold: true, size: 32, color: c(P.primary), font: { ascii: 'Calibri', eastAsia: 'SimHei' } })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 360, after: 160 },
    children: [new TextRun({ text, bold: true, size: 28, color: c(P.primary), font: { ascii: 'Calibri', eastAsia: 'SimHei' } })]
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 24, color: c(P.accent), font: { ascii: 'Calibri', eastAsia: 'SimHei' } })]
  });
}

function body(text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 312, after: 100 },
    children: [new TextRun({ text, size: 22, color: c(P.body), font: { ascii: 'Calibri', eastAsia: 'Microsoft YaHei' } })]
  });
}

function bodyBold(label, text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 312, after: 100 },
    children: [
      new TextRun({ text: label, bold: true, size: 22, color: c(P.primary), font: { ascii: 'Calibri', eastAsia: 'Microsoft YaHei' } }),
      new TextRun({ text, size: 22, color: c(P.body), font: { ascii: 'Calibri', eastAsia: 'Microsoft YaHei' } }),
    ]
  });
}

function code(text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 276, after: 60 },
    indent: { left: 360 },
    shading: { type: ShadingType.CLEAR, fill: c(P.surface) },
    children: [new TextRun({ text, size: 20, color: c(P.body), font: { name: 'Consolas', ascii: 'Consolas' } })]
  });
}

function note(text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 312, after: 120 },
    indent: { left: 360, right: 360 },
    border: { left: { style: BorderStyle.SINGLE, size: 6, color: c(P.accent), space: 10 } },
    children: [
      new TextRun({ text: 'NOTE: ', bold: true, size: 20, color: c(P.accent), font: { ascii: 'Calibri' } }),
      new TextRun({ text, size: 20, color: c(P.secondary), font: { ascii: 'Calibri', eastAsia: 'Microsoft YaHei' } }),
    ]
  });
}

function paramTable(rows) {
  const headerRow = new TableRow({
    tableHeader: true,
    cantSplit: true,
    children: ['Parameter', 'Value', 'Purpose'].map(t =>
      new TableCell({
        width: { size: t === 'Purpose' ? 50 : t === 'Parameter' ? 30 : 20, type: WidthType.PERCENTAGE },
        shading: { type: ShadingType.CLEAR, fill: c(P.primary) },
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: t, bold: true, size: 20, color: 'FFFFFF', font: { ascii: 'Calibri' } })
        ]})]
      })
    )
  });

  const dataRows = rows.map((r, i) =>
    new TableRow({
      cantSplit: true,
      children: r.map((t, j) =>
        new TableCell({
          width: { size: j === 2 ? 50 : j === 0 ? 30 : 20, type: WidthType.PERCENTAGE },
          shading: i % 2 === 1 ? { type: ShadingType.CLEAR, fill: c(P.surface) } : undefined,
          children: [new Paragraph({ alignment: j === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
            spacing: { line: 276 },
            children: [new TextRun({ text: String(t), size: 20, color: c(P.body), font: { ascii: 'Consolas', eastAsia: 'Microsoft YaHei' } })]
          })]
        })
      )
    })
  );

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.SINGLE, size: 2, color: c(P.secondary) },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: c(P.secondary) },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: c(P.secondary) } },
    rows: [headerRow, ...dataRows]
  });
}

function spacer(twips = 200) {
  return new Paragraph({ spacing: { before: twips } });
}

// ─── Cover (R1: Pure Paragraph Left, adapted for tech) ───

function buildCover() {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [new TableRow({
      height: { value: 16838, rule: 'exact' },
      children: [new TableCell({
        width: { size: 100, type: WidthType.PERCENTAGE },
        verticalAlign: 'top',
        borders: allNoBorders,
        children: [
          spacer(5000),
          new Paragraph({ spacing: { line: 600, lineRule: 'atLeast' }, children: [
            new TextRun({ text: 'Eli Safety Guidebook', bold: true, size: 64, color: c(P.primary), font: { ascii: 'Calibri' } })
          ]}),
          new Paragraph({ spacing: { before: 200 }, children: [
            new TextRun({ text: 'Tier 1 Safety Parameters', size: 28, color: c(P.secondary), font: { ascii: 'Calibri' } })
          ]}),
          new Paragraph({ spacing: { before: 100 }, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: c(P.accent), space: 8 } }, children: [] }),
          new Paragraph({ spacing: { before: 300 }, children: [
            new TextRun({ text: 'Every safety parameter implemented in Eli, documented with code references,', size: 22, color: c(P.secondary), font: { ascii: 'Calibri' } })
          ]}),
          new Paragraph({ spacing: { before: 60 }, children: [
            new TextRun({ text: 'plus a standalone learning guide for your personal projects.', size: 22, color: c(P.secondary), font: { ascii: 'Calibri' } })
          ]}),
          spacer(2000),
          new Paragraph({ children: [
            new TextRun({ text: 'VirtuaLab Digital  |  August 2026', size: 20, color: c(P.secondary), font: { ascii: 'Calibri' } })
          ]}),
        ]
      })]
    })]
  });
}

// ─── Content Sections ─────────────────────────────

function buildContent() {
  const children = [];

  // ── Section 1: Overview ──
  children.push(h1('1. Safety Architecture Overview'));
   children.push(body('Eli runs as a Next.js 16 SPA with multiple API routes that handle chat, API key rotation, vault search, and email inbox management. Because the system uses free-tier, temporary API keys generated by the Open Claw Engine, security is not optional — it is the difference between a working system and a compromised one. This guidebook documents every safety parameter, why it exists, how it works, and where in the codebase it lives.'));
  children.push(body('The safety system is organized into three tiers. Tier 1, which is fully implemented and documented here, covers the essentials: authentication gates, payload limits, rate limiting, input sanitization, prompt injection detection, key validation, and audit logging. Tier 2, planned for the future, will add per-session authentication, rate limits tied to user identity, and a persistent audit log. Tier 3 will introduce per-resource permissions, external call gating, and key expiry management.'));
  children.push(body('Every safety constant lives in a single file: src/lib/safety-gate.ts. This is the central source of truth. No magic numbers are scattered across routes. When you need to adjust a limit, you change it in one place. The middleware in src/middleware.ts handles authentication and rate limiting. Individual routes handle their own payload validation, input sanitization, and domain-specific safety checks.'));

  // ── Section 2: Parameter 1 — API Authentication Gate ──
  children.push(h1('2. Parameter: API Authentication Gate'));
  children.push(h2('2.1 What It Does'));
  children.push(body('The authentication gate enforces Bearer token authentication on every /api/* route. When ELI_API_KEY is set in the environment, all API requests must include a valid Authorization: Bearer <token> header, or pass the token as a ?token= query parameter. Without a valid token, the request is rejected with a 401 Unauthorized response. The health check endpoint (/api/health) is exempt from authentication so that monitoring probes can reach it.'));
  children.push(h2('2.2 Why It Matters'));
  children.push(body('Without authentication, anyone who discovers Eli\'s URL can call /api/omni?action=inject to inject their own API keys, call /api/eli-chat to burn through your Gemini quota, or access /api/audit to read your system logs. The omni endpoint can force-rotate keys, create email inboxes, and extract API keys from email. All of these are destructive or sensitive operations that must be gated. The middleware also logs blocked attempts with the caller\'s IP address, giving you visibility into who is probing your system.'));
  children.push(h2('2.3 How It Works'));
  children.push(body('The middleware runs in Next.js edge runtime, which means it executes before any route handler. It checks the request path against a list of public paths (/_next for static assets, /api/health for monitoring). For all other /api/* routes, it extracts the token from the Authorization header or query parameter and compares it against process.env.ELI_API_KEY. If the environment variable is not set, it allows all requests but logs a warning — this prevents breaking a fresh deploy where the key has not been configured yet.'));
  children.push(body('There is also a dev bypass: if ELI_AUTH_DISABLED is set to "true", all routes are open. This is for local development only and should never be set in production. The middleware returns 401 with a JSON body containing an error message, never exposing whether the key exists or not.'));
  children.push(h2('2.4 Code Reference'));
  children.push(code('File: src/middleware.ts'));
  children.push(code('Key check: const token = authHeader?.startsWith("Bearer ") ? authHeader.slice(7) : queryToken;'));
  children.push(code('Reject: return NextResponse.json({ error: "Unauthorized" }, { status: 401 });'));
  children.push(code('Env vars: ELI_API_KEY (required), ELI_AUTH_DISABLED (dev only)'));
  children.push(h2('2.5 Configuration'));
  children.push(paramTable([
    ['ELI_API_KEY', 'string', 'Bearer token for API authentication. Set in .env and on VPS.'],
    ['ELI_AUTH_DISABLED', '"true"', 'Bypass auth in dev. NEVER set in production.'],
    ['PUBLIC_PATHS', 'string[]', 'Routes exempt from auth: /_next, /api/health.'],
  ]));

  // ── Section 3: Parameter 2 — Payload Size Limits ──
  children.push(h1('3. Parameter: Payload Size Limits'));
  children.push(h2('3.1 What It Does'));
  children.push(body('Every POST endpoint enforces a maximum request body size before parsing JSON. The limits are defined per-route in safety-gate.ts, with a global absolute maximum of 100KB that no route may exceed. If a request\'s Content-Length header exceeds the limit, the server returns a 413 Payload Too Large response immediately, without ever reading or parsing the body. This is a critical optimization: it prevents the server from allocating memory for an oversized payload, which could lead to OOM (out of memory) crashes under attack.'));
  children.push(h2('3.2 Why It Matters'));
  children.push(body('A payload size limit is the most basic defense against denial-of-service attacks. Without it, an attacker could send a 500MB JSON body to /api/eli-chat, forcing the server to allocate memory, parse the entire string, and then fail. On a VPS with limited RAM, this could crash the entire application. Even without malicious intent, a buggy client sending oversized requests can cause the same outcome. The per-route limits are calibrated to what each endpoint actually needs: chat messages need 10KB (messages are short), vault sync reads are 4KB (they use query params, not body), and nothing needs more than 100KB.'));
  children.push(h2('3.3 How It Works'));
  children.push(body('Each route reads the Content-Length header from the incoming request and compares it against its configured maximum. This check happens before any JSON parsing or file reading. If the header is missing or zero, the check passes (the body will be validated by JSON.parse anyway). The Content-Length check is a fast-path optimization that avoids parsing entirely for obviously oversized requests.'));
  children.push(h2('3.4 Code Reference'));
  children.push(paramTable([
    ['MAX_PAYLOAD_CHAT', '10,240 B', 'eli-chat POST — chat messages are short'],
    ['MAX_PAYLOAD_OMNI', '10,240 B', 'omni POST — action params are small'],
    ['MAX_PAYLOAD_VAULT_SYNC', '4,096 B', 'vault-sync uses query params, not body'],
    ['MAX_PAYLOAD_DEFAULT', '10,240 B', 'Any route without a specific limit'],
    ['MAX_PAYLOAD_ABSOLUTE', '100,000 B', 'No route may accept more than this'],
  ]));
  children.push(code('File: src/lib/safety-gate.ts → Section 1: Payload Size Limits'));
  children.push(code('Usage: const contentLen = parseInt(request.headers.get("content-length") || "0", 10);'));
  children.push(code('if (contentLen > MAX_PAYLOAD_CHAT) return 413;'));

  // ── Section 4: Parameter 3 — Rate Limiting ──
  children.push(h1('4. Parameter: Rate Limiting'));
  children.push(h2('4.1 What It Does'));
  children.push(body('The rate limiter enforces a maximum number of requests per IP address within a sliding time window. Each route group has its own limit configuration. When an IP exceeds its limit, the server returns a 429 Too Many Requests response with a Retry-After header indicating when the client can try again. The rate limiter is implemented as an in-memory sliding window: it stores timestamps of each request and prunes entries that have fallen outside the window.'));
  children.push(h2('4.2 Why It Matters'));
  children.push(body('Eli uses free-tier API keys from the Open Claw Engine. These keys have rate limits imposed by the provider (for example, Google limits free Gemini keys to roughly 15 requests per minute). If a single user or bot sends 100 requests per minute, they will exhaust the key\'s quota, causing failures for all users. Rate limiting protects the shared key budget. It also mitigates brute-force attacks on the key injection endpoint and prevents automated scraping of vault content. The sliding window approach ensures smooth enforcement without the "burst at window boundary" problem that fixed-window rate limiters have.'));
  children.push(h2('4.3 How It Works'));
  children.push(body('The checkRateLimit(ip, config) function in safety-gate.ts maintains a Map of IP addresses to arrays of request timestamps. On each call, it first prunes timestamps outside the current window (e.g., older than 60 seconds), then checks if the remaining count exceeds the maximum. If not, it adds the current timestamp and returns true (allowed). If yes, it returns false (rate limited). A periodic cleanup runs every 5 minutes to remove stale entries from memory, preventing memory leaks from accumulated IPs.'));
  children.push(body('Rate limiting is applied at two levels. The middleware applies per-route limits based on the URL path. For example, /api/eli-chat gets 15 requests per minute, while /api/health gets 120 per minute (monitoring needs higher throughput). POST requests to /api/omni get an even tighter limit of 5 per minute because write operations like key injection and rotation are expensive.'));
  children.push(h2('4.4 Code Reference'));
  children.push(paramTable([
    ['RATE_LIMIT_CHAT', '15 / 60s', 'Chat endpoint — protects LLM key budget'],
    ['RATE_LIMIT_OMNI_GET', '30 / 60s', 'Omni read operations — state, probe'],
    ['RATE_LIMIT_OMNI_POST', '5 / 60s', 'Omni write operations — inject, rotate'],
    ['RATE_LIMIT_VAULT', '20 / 60s', 'Vault read operations'],
    ['RATE_LIMIT_AUDIT', '10 / 60s', 'Audit log reads — admin endpoint'],
    ['RATE_LIMIT_HEALTH', '120 / 60s', 'Health checks — monitoring probes'],
    ['RATE_LIMIT_DEFAULT', '30 / 60s', 'Any unclassified route'],
  ]));
  children.push(code('File: src/lib/safety-gate.ts → Section 2: Rate Limiting'));
  children.push(code('File: src/middleware.ts → Layer 2: Rate Limiting'));
  children.push(note('The rate limiter is in-memory only. If the server restarts, all rate limit counters reset. For production with multiple instances, use Redis. For Eli\'s single-instance VPS deployment, in-memory is sufficient.'));

  // ── Section 5: Parameter 4 — Input Sanitization ──
  children.push(h1('5. Parameter: Input Sanitization'));
  children.push(h2('5.1 What It Does'));
  children.push(body('The sanitizeInput() function processes all user-supplied text before it reaches the LLM, gets stored, or is returned in API responses. It performs four operations: removes null bytes (which can cause string truncation in downstream systems), normalizes Unicode to NFC form (preventing homoglyph attacks where different Unicode representations of the same character bypass filters), collapses excessive whitespace (more than 3 consecutive newlines or spaces), and removes non-printable control characters while preserving newlines, tabs, and carriage returns. It also enforces a maximum length, truncating anything that exceeds it.'));
  children.push(h2('5.2 Why It Matters'));
  children.push(body('User input reaches three downstream systems: the Gemini LLM, the vault search engine, and the audit log. Each of these can be disrupted by malicious input. Null bytes (ASCII 0x00) can cause C-style string functions to truncate, potentially splitting a malicious payload across what appears to be two separate strings. Unicode normalization attacks exploit the fact that some characters have multiple representations — for example, the letter "e" with an acute accent can be one codepoint or two (e + combining accent). A filter that blocks the single-codepoint version might miss the two-codepoint version. By normalizing to NFC (canonical composition), all equivalent representations are converted to the same form before filtering.'));
  children.push(h2('5.3 Code Reference'));
  children.push(paramTable([
    ['MAX_MESSAGE_LENGTH', '4,000 chars', 'Max single chat message after sanitization'],
    ['MAX_HISTORY_MESSAGES', '20', 'Max chat history messages accepted from client'],
    ['sanitizeInput()', '—', 'Main sanitization function'],
    ['sanitizePromptInjection()', '—', 'Prompt injection detection (audit-only)'],
  ]));
  children.push(code('File: src/lib/safety-gate.ts → Section 3: Input Sanitization'));
  children.push(code('Usage (eli-chat): const clean = sanitizeInput(message, MAX_MESSAGE_LENGTH);'));

  // ── Section 6: Parameter 5 — Prompt Injection Detection ──
  children.push(h1('6. Parameter: Prompt Injection Detection'));
  children.push(h2('6.1 What It Does'));
  children.push(body('The sanitizePromptInjection() function scans chat messages for patterns commonly used in prompt injection attacks. It checks against 12 regex patterns that match system prompt override attempts ("ignore previous instructions"), role hijacking ("you are now..."), delimiter injection ("---END SYSTEM---"), output format manipulation ("respond only with JSON"), and known jailbreak names ("DAN mode", "jailbreak"). When a pattern matches, the function does NOT block the message — instead, it flags the detection and logs it to the audit trail with the caller\'s IP and a preview of the message.'));
  children.push(h2('6.2 Why It Matters'));
  children.push(body('Eli\'s system prompt contains identity information ("You are Eli"), knowledge about VirtuaLab Digital\'s strategies, and instructions on how to behave. A successful prompt injection could cause Eli to reveal internal knowledge, change her behavior, or produce harmful content. The detection is defense-in-depth: the system prompt itself is designed to resist manipulation, but the detection layer adds an audit trail so you can see when someone is attempting attacks. This is important for understanding threat patterns and deciding whether to implement stricter filtering in the future.'));
  children.push(h2('6.3 Design Decision: Audit-Only, Not Blocking'));
  children.push(body('The current implementation detects but does not block. This is intentional. False positives are common in legitimate marketing conversations — phrases like "ignore previous instructions" might appear in a discussion about email marketing compliance, and "act as if you are" appears naturally in role-play brainstorming. Blocking these would create a terrible user experience. Instead, the detection feeds the audit log, giving you data to make informed decisions about whether to escalate to blocking in a future tier.'));
  children.push(h2('6.4 Code Reference'));
  children.push(code('File: src/lib/safety-gate.ts → sanitizePromptInjection()'));
  children.push(code('File: src/app/api/eli-chat/route.ts → Prompt injection detection section'));
  children.push(code('Audit event: prompt.injection.detected'));

  // ── Section 7: Parameter 6 — Key Validation ──
  children.push(h1('7. Parameter: Key Validation Before Injection'));
  children.push(h2('7.1 What It Does'));
  children.push(body('Before any API key is injected into the system (whether from manual injection via /api/omni?action=inject or from the Open Claw\'s email extraction pipeline), the key must pass format validation. The validateKeyFormat() function in safety-gate.ts checks the key against service-specific regex patterns that match the exact format of legitimate keys. For Gemini, this means keys must start with "AIza" followed by 33+ alphanumeric characters, or "AQ." followed by 30+ characters. For OpenAI, keys must start with "sk-" and be at least 25 characters long. For Anthropic, keys must start with "sk-ant-" and be at least 30 characters long. Keys that fail format validation are rejected before they ever reach process.env.'));
  children.push(h2('7.2 Why It Matters'));
  children.push(body('Injecting a malformed key into process.env causes cascading failures. The next LLM call will use the bad key, receive an authentication error from the API provider, and the OmniRoute penalty tracker will flag the key as failed. If the key was auto-injected from the Claw\'s email extraction, this creates a cycle: extract bad key, inject it, fail, rotate, extract another bad key. Format validation catches obviously wrong keys before they enter the system. It also prevents a subtle attack: an attacker who gains access to the inject endpoint could try to inject a key that looks valid but points to their own proxy server, intercepting all LLM traffic.'));
  children.push(h2('7.3 Code Reference'));
  children.push(paramTable([
    ['KEY_PATTERNS.gemini', 'AIza...|AQ....', 'Google AI Studio key format'],
    ['KEY_PATTERNS.openai', 'sk-...', 'OpenAI API key format'],
    ['KEY_PATTERNS.anthropic', 'sk-ant-...', 'Anthropic API key format'],
    ['validateKeyFormat()', '{valid, reason}', 'Returns validation result with reason'],
  ]));
  children.push(code('File: src/lib/safety-gate.ts → Section 5: Key Validation Patterns'));
  children.push(code('Usage (omni): const v = validateKeyFormat(service, key); if (!v.valid) return 400;'));

  // ── Section 8: Parameter 7 — Key Approval Queue ──
  children.push(h1('8. Parameter: Key Approval Queue'));
  children.push(h2('8.1 What It Does'));
  children.push(body('When the Open Claw Engine extracts an API key from an email, it does not automatically inject the key into process.env. Instead, the key enters a "pending" queue with status "pending". It stays there until a human operator explicitly approves it via POST /api/omni?action=approve (passing the pendingId), or rejects it via POST /api/omni?action=reject. The auto-approve mode exists but is disabled by default (autoApproveKeys = false). When a key is approved, the validateAndInject() function runs a format check and, for Gemini keys, makes a test API call ("Say OK") to verify the key actually works before injecting it into the environment.'));
  children.push(h2('8.2 Why It Matters'));
  children.push(body('Automatic key injection is dangerous because extracted keys can be malformed, expired, or fraudulent. The Claw\'s regex-based extraction can match strings that look like API keys but are not (for example, a license key in a promotional email, or a base64-encoded string that happens to start with "AIza"). The approval queue gives a human operator a checkpoint: they can review the key\'s source email, the inbox it came from, and the key preview before deciding to activate it. This prevents poisoned keys from entering the system.'));
  children.push(h2('8.3 Code Reference'));
  children.push(paramTable([
    ['MAX_PENDING_KEYS', '20', 'Max keys in queue before oldest auto-rejected'],
    ['autoApproveKeys', 'false (default)', 'Auto-approve mode — OFF by default'],
    ['approvePendingKey(id)', '—', 'Validate + approve a pending key'],
    ['rejectPendingKey(id)', '—', 'Reject a pending key'],
    ['getPendingKeys()', '—', 'List all pending keys'],
  ]));
  children.push(code('File: src/lib/open-claw.ts → PendingKey queue + validateAndInject()'));
  children.push(code('API: POST /api/omni?action=approve { pendingId }'));
  children.push(code('API: POST /api/omni?action=reject { pendingId }'));

  // ── Section 9: Parameter 8 — Audit Logging ──
  children.push(h1('9. Parameter: Audit Logging'));
  children.push(h2('9.1 What It Does'));
  children.push(body('The audit log records every sensitive operation in the system with a structured JSON entry containing: timestamp (ISO 8601), event type (e.g., "key.injected", "llm.call", "auth.blocked"), human-readable description, optional metadata (key preview, IP address, error messages), and caller IP. Events are stored in two places: an in-memory ring buffer (MAX_AUDIT_MEMORY = 500 entries, oldest discarded) for fast API access, and a JSONL file at data/audit/audit.jsonl for persistent post-mortem analysis. The file write is fire-and-forget (non-blocking) to avoid slowing down request handling.'));
  children.push(h2('9.2 Why It Matters'));
  children.push(body('Without audit logging, you have no visibility into what happened after an incident. When a key gets exhausted, when an unauthorized request is blocked, when the Claw extracts a suspicious key — these events need to be recorded so you can reconstruct the timeline. The in-memory buffer provides instant access for the /api/audit endpoint (useful for dashboards), while the JSONL file provides durability across restarts and can be analyzed with standard tools (grep, jq, Python). The audit log is the single most important tool for understanding system behavior after the fact.'));
  children.push(h2('9.3 Event Types'));
  children.push(paramTable([
    ['key.extracted', 'Claw pulled key from email', 'Source inbox, key preview, pendingId'],
    ['key.approved', 'Key passed validation', 'pendingId'],
    ['key.rejected', 'Key failed validation', 'pendingId, error reason'],
    ['key.injected', 'Manual key injection', 'IP, service, key preview'],
    ['key.inject.blocked', 'Invalid key format', 'IP, service, reason'],
    ['llm.call', 'Gemini API called', 'IP, message preview'],
    ['llm.failure', 'Gemini call failed', 'IP, error message'],
    ['auth.blocked', 'Unauthorized access', 'IP, route path'],
    ['prompt.injection.detected', 'Injection pattern found', 'IP, message preview'],
    ['chat.blocked', 'Payload too large', 'IP, payload size'],
    ['claw.spawn', 'New inbox created', 'Provider, email, TTL'],
  ]));
  children.push(code('File: src/lib/audit-log.ts'));
  children.push(code('API: GET /api/audit?event=key.injected&limit=50'));

  // ── Section 10: Parameter 9 — Route Capability Scoping ──
  children.push(h1('10. Parameter: Route Capability Scoping'));
  children.push(h2('10.1 What It Does'));
  children.push(body('The capability map defines four access levels (public, user, operator, admin) and maps every /api/omni action to a required level. For example, viewing the omni state is "user" level, forcing a key rotation is "operator" level, and getting the raw API key is "admin" level. The hasCapability() function checks if a user\'s level meets or exceeds the required level using a numeric hierarchy (public=0, user=1, operator=2, admin=3). This system is currently defined and documented but not yet enforced in the middleware — it is a declaration of the intended access control structure for Tier 2 implementation.'));
  children.push(h2('10.2 Why It Matters'));
  children.push(body('Not every authenticated user should be able to do everything. A client using Eli\'s chat should not be able to inject API keys or read the raw key. An operator monitoring the system should not be able to read audit logs or toggle auto-approve mode. Capability scoping implements the principle of least privilege: each session gets exactly the permissions it needs, and nothing more. By defining the map now, you have a clear migration path when Tier 2 authentication is implemented — just add the capability check to the middleware and wire it to the session.'));
  children.push(h2('10.3 Code Reference'));
  children.push(paramTable([
    ['public (0)', 'Health check', 'No auth needed'],
    ['user (1)', 'Chat, state, signup', 'Any authenticated session'],
    ['operator (2)', 'Rotate, check inbox, reject', 'Can modify system state'],
    ['admin (3)', 'Raw key, inject, approve, audit', 'Full system access'],
  ]));
  children.push(code('File: src/lib/safety-gate.ts → Section 4: Route Capability Map'));
  children.push(note('This parameter is declared for Tier 2. It is currently documentation-only. No enforcement exists yet.'));

  // ── Section 11: Parameter 10 — Key Masking ──
  children.push(h1('11. Parameter: Key Masking in Responses'));
  children.push(h2('11.1 What It Does'));
  children.push(body('Every API response that includes an API key displays only a masked preview: the first 8 characters followed by "..." followed by the last 4 characters. The raw key is never included in any JSON response. The maskKey() function in the omni route and the key redaction in OpenClaw\'s getState() both apply this masking. The only way to retrieve a raw key is through the /api/omni?action=key endpoint, which is classified as "admin" capability level.'));
  children.push(h2('11.2 Why It Matters'));
  children.push(body('API keys are the most sensitive data in the system. If a log aggregator, error tracking service, or browser extension intercepts an API response, the raw key would be exposed. Masking ensures that even if a response is leaked, the key cannot be used. The first-8-and-last-4 format is enough to identify which key is being referenced (useful for debugging) without exposing enough to authenticate.'));
  children.push(h2('11.3 Code Reference'));
  children.push(code('File: src/app/api/omni/route.ts → maskKey() function'));
  children.push(code('File: src/lib/open-claw.ts → getState() key redaction'));
  children.push(code('Format: key.slice(0, 8) + "..." + key.slice(-4)'));

  // ── Section 12: Safety Summary ──
  children.push(h1('12. Safety Summary — /api/health Endpoint'));
  children.push(body('The /api/health endpoint now includes a "safety" object in its response that summarizes all active safety parameters. This gives you a single endpoint to verify that all safety systems are operational. The response includes payload limits, rate limit configurations, validation settings, whether authentication is enabled, and whether auto-approve is active. You can use this in your monitoring stack to alert on safety configuration drift (e.g., if authEnabled becomes false, something is wrong).'));
  children.push(code('API: GET /api/health → response.safety'));
  children.push(code('Source: getSafetySummary() in src/lib/safety-gate.ts'));

  // ═══════════════════════════════════════════════════
  // PART 2: LEARNING GUIDE
  // ═══════════════════════════════════════════════════

  children.push(h1('Part 2: Learning Guide'));
  children.push(body('This section contains standalone practice exercises for each safety pattern. Each exercise is designed to be implemented in a fresh project (not Eli) so you can internalize the patterns by building them from scratch. The exercises are progressive: start with Exercise 1 and work through them in order. Each exercise includes the concept, a step-by-step implementation guide, and verification steps.'));

  // Exercise 1
  children.push(h2('Exercise 1: Build an API Key Authentication Middleware'));
  children.push(h3('Concept'));
  children.push(body('Create a Next.js middleware that enforces Bearer token authentication on all /api/* routes, with configurable public paths and a dev bypass. This is the foundation of API security — without it, every endpoint is open to the world.'));
  children.push(h3('Step-by-Step'));
  children.push(bodyBold('Step 1: ', 'Create a new Next.js project (npx create-next-app@latest) and create src/middleware.ts.'));
  children.push(bodyBold('Step 2: ', 'Define a PUBLIC_PATHS array. Start with just ["/_next", "/api/health"]. These routes will skip auth.'));
  children.push(bodyBold('Step 3: ', 'In the middleware function, extract the pathname from request.nextUrl. If it does not start with "/api/" or matches a public path, call NextResponse.next() to pass through.'));
  children.push(bodyBold('Step 4: ', 'Read process.env.API_KEY. If it is not set, log a warning and allow the request (for safe initial deploys). If it IS set, extract the token from the Authorization header (strip "Bearer ") or from ?token= query param.'));
  children.push(bodyBold('Step 5: ', 'Compare the token to API_KEY. If they do not match, return a 401 JSON response. Log the blocked IP and path.'));
  children.push(bodyBold('Step 6: ', 'Export the config matcher: export const config = { matcher: ["/api/:path*"] };'));
  children.push(h3('Verification'));
  children.push(body('Start the dev server. Set API_KEY=test123 in .env. Test that curl localhost:3000/api/health returns 200 (public), curl localhost:3000/api/test returns 401 (no token), and curl -H "Authorization: Bearer test123" localhost:3000/api/test returns the actual response.'));

  // Exercise 2
  children.push(h2('Exercise 2: Implement Payload Size Limits'));
  children.push(h3('Concept'));
  children.push(body('Add a pre-parse payload size check to a POST endpoint. The check reads the Content-Length header and rejects oversized requests before JSON parsing, protecting against memory exhaustion.'));
  children.push(h3('Step-by-Step'));
  children.push(bodyBold('Step 1: ', 'Create a POST endpoint in app/api/submit/route.ts that accepts a JSON body.'));
  children.push(bodyBold('Step 2: ', 'Before calling request.json(), read the Content-Length header: const len = parseInt(request.headers.get("content-length") || "0", 10);'));
  children.push(bodyBold('Step 3: ', 'Define a MAX_PAYLOAD constant (start with 1024 bytes for testing). If len > MAX_PAYLOAD, return 413 with a JSON error.'));
  children.push(bodyBold('Step 4: ', 'Create a centralized safety module (lib/safety.ts) that exports all payload limits as named constants. Import them in your route instead of hardcoding.'));
  children.push(bodyBold('Step 5: ', 'Test with curl: send a small JSON body (should work) and a body larger than MAX_PAYLOAD (should return 413).'));
  children.push(h3('Verification'));
  children.push(body('Use curl -d "$(python3 -c "print(\"x\"*2000)")" -H "Content-Type: application/json" to send an oversized payload. Verify it returns 413. Check that the server did not log a JSON parse error (which would mean the body was parsed despite being oversized).'));

  // Exercise 3
  children.push(h2('Exercise 3: Build a Sliding-Window Rate Limiter'));
  children.push(h3('Concept'));
  children.push(body('Implement an in-memory rate limiter using the sliding window algorithm. Track requests per IP, prune old entries, and return 429 when the limit is exceeded. This is the most important exercise — rate limiting protects every shared resource.'));
  children.push(h3('Step-by-Step'));
  children.push(bodyBold('Step 1: ', 'Create a Map<string, number[]> to store IP addresses and their request timestamps.'));
  children.push(bodyBold('Step 2: ', 'Write a function checkRateLimit(ip, maxRequests, windowMs) that: (a) gets or creates the entry for the IP, (b) filters out timestamps older than Date.now() - windowMs, (c) checks if remaining count >= maxRequests → return false, (d) pushes current timestamp and returns true.'));
  children.push(bodyBold('Step 3: ', 'Add periodic cleanup: every 5 minutes, iterate the Map and delete entries with no recent timestamps.'));
  children.push(bodyBold('Step 4: ', 'Integrate into your middleware or route handler. Extract IP from x-forwarded-for header (split on comma, take first, trim). Call checkRateLimit before processing the request.'));
  children.push(bodyBold('Step 5: ', 'Return 429 with a Retry-After header when rate limited.'));
  children.push(h3('Verification'));
  children.push(body('Write a quick loop script that sends 20 requests in 5 seconds to your rate-limited endpoint (limit = 10/minute). Verify that the first 10 succeed and the next 10 return 429. Wait 60 seconds and verify requests succeed again.'));

  // Exercise 4
  children.push(h2('Exercise 4: Input Sanitization Function'));
  children.push(h3('Concept'));
  children.push(body('Build a sanitizeInput(text, maxLength) function that handles null bytes, Unicode normalization, control characters, whitespace collapsing, and length truncation. This function should be applied to ALL user input before processing.'));
  children.push(h3('Step-by-Step'));
  children.push(bodyBold('Step 1: ', 'Create the function signature: function sanitizeInput(text: string, maxLength = 4000): string.'));
  children.push(bodyBold('Step 2: ', 'Handle edge cases: if text is not a string or is empty, return empty string.'));
  children.push(bodyBold('Step 3: ', 'Remove null bytes: text.replace(/\\x00/g, ""). This prevents C-style string truncation attacks.'));
  children.push(bodyBold('Step 4: ', 'Normalize Unicode: text.normalize("NFC"). This converts all equivalent character sequences to the same form.'));
  children.push(bodyBold('Step 5: ', 'Collapse excessive whitespace: replace 4+ consecutive newlines with 3, and 4+ consecutive spaces with 3.'));
  children.push(bodyBold('Step 6: ', 'Remove control characters: replace chars in the 0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F, 0x7F ranges with empty string. Preserve newlines, tabs, and carriage returns.'));
  children.push(bodyBold('Step 7: ', 'Trim and truncate: text.trim().slice(0, maxLength).'));
  children.push(h3('Verification'));
  children.push(body('Test with: null byte injection (a string containing ASCII 0x00), homoglyph test (e + combining accent vs. e-acute), control char test (a string containing ASCII 0x01), and length test (5000-char string with maxLength=100).'));

  // Exercise 5
  children.push(h2('Exercise 5: Pattern-Based Detection with Audit Logging'));
  children.push(h3('Concept'));
  children.push(body('Build a simple pattern scanner that checks user input against a list of regex patterns, logs matches to an audit trail, but does NOT block the input. This teaches you the audit-only detection pattern: observe and record, do not prematurely block.'));
  children.push(h3('Step-by-Step'));
  children.push(bodyBold('Step 1: ', 'Define an array of detection patterns: [{ name: "injection", pattern: /ignore previous instructions/i }, ...]. Start with 3-5 patterns relevant to your application.'));
  children.push(bodyBold('Step 2: ', 'Write a scanInput(text) function that tests the text against each pattern and returns { detected: boolean, matches: string[] }. Do not modify the text.'));
  children.push(bodyBold('Step 3: ', 'Create a simple audit log: an array of { timestamp, event, detail } objects with a max size (e.g., 100). On new entries, shift the oldest if the array is full.'));
  children.push(bodyBold('Step 4: ', 'Persist the audit log to a file using appendFile (fire-and-forget, do not await). Use JSONL format (one JSON object per line).'));
  children.push(bodyBold('Step 5: ', 'Wire it together: in your route handler, call scanInput(), and if detected, push an entry to the audit log.'));
  children.push(h3('Verification'));
  children.push(body('Send normal text (no detections). Send text containing "ignore previous instructions" (should log but not block). Check the audit log file to verify entries are being written. Verify the in-memory buffer stays at max size.'));

  // Exercise 6
  children.push(h2('Exercise 6: Key Validation with Format + Test Call'));
  children.push(h3('Concept'));
  children.push(body('Build a two-stage key validation function: first check format with a regex, then make a test API call to verify the key actually works. This is the same pattern used in Eli\'s Open Claw engine.'));
  children.push(h3('Step-by-Step'));
  children.push(bodyBold('Step 1: ', 'Define service-specific key patterns: { gemini: /^(AIza|AQ\.)/, openai: /^sk-/ }. Store them in a centralized object.'));
  children.push(bodyBold('Step 2: ', 'Write validateKeyFormat(service, key) that checks: (a) key is a non-empty string, (b) key length >= minimum for the service, (c) key matches the service pattern regex. Return { valid: boolean, reason: string }.'));
  children.push(bodyBold('Step 3: ', 'Write validateKeyLive(service, key) that makes a minimal test API call (e.g., for Gemini, call generateContent with "Say OK"). If the call succeeds, the key is valid. If it fails, return the error.'));
  children.push(bodyBold('Step 4: ', 'Create a validateAndInject(pendingKey) function that calls validateKeyFormat first (cheap), then validateKeyLive (expensive). Only inject into process.env if both pass.'));
  children.push(h3('Verification'));
  children.push(body('Test with a valid key (both checks pass). Test with a malformed key (format check fails). Test with a valid-looking but expired key (format passes, live check fails). Verify that process.env is only modified when both checks pass.'));

  // Exercise 7
  children.push(h2('Exercise 7: Approval Queue Pattern'));
  children.push(h3('Concept'));
  children.push(body('Build an approval queue where items enter a "pending" state and require explicit approval before activation. This pattern is used in Eli for extracted API keys but applies to any system where automated actions need human oversight.'));
  children.push(h3('Step-by-Step'));
  children.push(bodyBold('Step 1: ', 'Define a PendingItem interface: { id, type, value, status: "pending" | "approved" | "rejected", createdAt, validatedAt?, rejectionReason? }. Create an array to hold pending items.'));
  children.push(bodyBold('Step 2: ', 'Write submitForApproval(type, value) that creates a PendingItem with status "pending", adds it to the array, and returns the item with the ID.'));
  children.push(bodyBold('Step 3: ', 'Write approve(id) and reject(id, reason) functions that find the item by ID and change its status. approve() should run validation before approving. reject() should record the reason.'));
  children.push(bodyBold('Step 4: ', 'Enforce a maximum queue size. When a new item is submitted and the queue is full, auto-reject the oldest pending item.'));
  children.push(bodyBold('Step 5: ', 'Create API endpoints: POST /api/approve, POST /api/reject, GET /api/pending. Wire them to the queue functions.'));
  children.push(h3('Verification'));
  children.push(body('Submit 5 items. Approve 2. Reject 1. Verify GET /api/pending shows 2 remaining. Submit items until the queue overflows and verify the oldest is auto-rejected.'));

  return children;
}

// ─── Assemble Document ─────────────────────────────

async function main() {
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: { ascii: 'Calibri', eastAsia: 'Microsoft YaHei' }, size: 22, color: c(P.body) },
          paragraph: { spacing: { line: 312 } },
        }
      }
    },
    sections: [
      // Section 1: Cover (no page numbers)
      {
        properties: {
          page: { margin: { top: 0, bottom: 0, left: 0, right: 0 }, size: { width: 11906, height: 16838 } }
        },
        children: [buildCover()]
      },
      // Section 2: TOC + Body
      {
        properties: {
          page: {
            margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
            size: { width: 11906, height: 16838 },
            pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL }
          }
        },
        footers: {
          default: new Footer({ children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: c(P.secondary) })]
          })] })
        },
        children: [
          new Paragraph({ spacing: { before: 200, after: 200 }, children: [
            new TextRun({ text: 'Table of Contents', bold: true, size: 32, color: c(P.primary), font: { ascii: 'Calibri' } })
          ]}),
          new TableOfContents('Table of Contents', {
            hyperlink: true,
            headingStyleRange: '1-3',
          }),
          new Paragraph({ spacing: { before: 100 }, children: [
            new TextRun({ text: 'Right-click the TOC and select "Update Field" to refresh page numbers.', italics: true, size: 18, color: c(P.secondary), font: { ascii: 'Calibri' } })
          ]}),
          new Paragraph({ children: [new PageBreak()] }),
          ...buildContent(),
        ]
      }
    ]
  });

  const buffer = await Packer.toBuffer(doc);
  const outPath = '/home/z/my-project/download/Eli-Safety-Guidebook.docx';
  fs.writeFileSync(outPath, buffer);
  console.log('Written to:', outPath);
}

main().catch(console.error);
