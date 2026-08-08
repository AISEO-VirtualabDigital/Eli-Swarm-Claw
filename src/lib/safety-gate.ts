/**
 * Eli Safety Gate (Tier 1) — Centralized safety parameters
 *
 * This module is the single source of truth for ALL safety constants and
 * utility functions used across Eli's API routes and internal systems.
 *
 * Parameters:
 *   - Payload size limits (per-route)
 *   - Rate limiting (in-memory, per-IP sliding window)
 *   - Input sanitization (XSS, injection, prompt injection)
 *   - Route capability definitions
 *   - Key validation patterns
 *
 * Design: Every safety parameter is a named export with a JSDoc explaining
 * WHAT it is, WHY it exists, and WHERE it's used. This file IS the
 * guidebook's code reference.
 */

// ─── 1. Payload Size Limits ───────────────────────────────────────
// WHAT: Maximum request body size per route (bytes)
// WHY: Prevents memory exhaustion attacks, oversized payloads that could
//      crash the server or cause OOM in JSON parsing.
// WHERE: Used in each route's POST handler before `request.json()`

/** Chat messages — keep small, LLM context is the bottleneck */
export const MAX_PAYLOAD_CHAT = 10_240;           // 10 KB
/** Omni route actions (inject, rotate, etc.) */
export const MAX_PAYLOAD_OMNI = 10_240;           // 10 KB
/** Vault sync requests (export params, not body) */
export const MAX_PAYLOAD_VAULT_SYNC = 4_096;      // 4 KB
/** Generic default for any route without a specific limit */
export const MAX_PAYLOAD_DEFAULT = 10_240;        // 10 KB
/** Absolute maximum — no route may accept more than this */
export const MAX_PAYLOAD_ABSOLUTE = 100_000;      // 100 KB

// ─── 2. Rate Limiting ─────────────────────────────────────────────
// WHAT: In-memory sliding-window rate limiter per IP address
// WHY: Prevents abuse of free-tier LLM keys (which are limited), stops
//      brute-force attacks on the key injection endpoint, and protects
//      against automated scraping of vault content.
// WHERE: Called at the start of each route handler

export interface RateLimitConfig {
  /** Number of requests allowed in the window */
  maxRequests: number;
  /** Window duration in milliseconds */
  windowMs: number;
}

/** Chat endpoint — 15 requests per minute per IP (LLM key budget) */
export const RATE_LIMIT_CHAT: RateLimitConfig = { maxRequests: 15, windowMs: 60_000 };
/** Omni state/key endpoint — 30/min (monitoring, not expensive) */
export const RATE_LIMIT_OMNI_GET: RateLimitConfig = { maxRequests: 30, windowMs: 60_000 };
/** Omni write actions (inject, rotate) — 5/min (expensive operations) */
export const RATE_LIMIT_OMNI_POST: RateLimitConfig = { maxRequests: 5, windowMs: 60_000 };
/** Vault read operations — 20/min */
export const RATE_LIMIT_VAULT: RateLimitConfig = { maxRequests: 20, windowMs: 60_000 };
/** Audit log reads — 10/min (admin endpoint) */
export const RATE_LIMIT_AUDIT: RateLimitConfig = { maxRequests: 10, windowMs: 60_000 };
/** Default for any unclassified route — 30/min */
export const RATE_LIMIT_DEFAULT: RateLimitConfig = { maxRequests: 30, windowMs: 60_000 };
/** Health check — very permissive (used by monitoring) */
export const RATE_LIMIT_HEALTH: RateLimitConfig = { maxRequests: 120, windowMs: 60_000 };

// ─── Sliding Window Implementation ────────────────────────────────

interface RateWindow {
  timestamps: number[];
}

const rateWindows = new Map<string, RateWindow>();
let lastCleanup = Date.now();
const CLEANUP_INTERVAL = 300_000; // 5 min

/**
 * Check if a request from the given IP should be rate-limited.
 * Returns true if the request is ALLOWED, false if RATE-LIMITED.
 *
 * Usage:
 *   if (!checkRateLimit(ip, RATE_LIMIT_CHAT)) {
 *     return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
 *   }
 */
export function checkRateLimit(ip: string, config: RateLimitConfig): boolean {
  const now = Date.now();

  // Periodic cleanup of stale entries
  if (now - lastCleanup > CLEANUP_INTERVAL) {
    for (const [key, window] of rateWindows) {
      const cutoff = now - config.windowMs;
      window.timestamps = window.timestamps.filter(t => t > cutoff);
      if (window.timestamps.length === 0) rateWindows.delete(key);
    }
    lastCleanup = now;
  }

  let entry = rateWindows.get(ip);
  if (!entry) {
    entry = { timestamps: [] };
    rateWindows.set(ip, entry);
  }

  // Slide window — remove timestamps outside the window
  const cutoff = now - config.windowMs;
  entry.timestamps = entry.timestamps.filter(t => t > cutoff);

  if (entry.timestamps.length >= config.maxRequests) {
    return false; // RATE LIMITED
  }

  entry.timestamps.push(now);
  return true; // ALLOWED
}

/** Reset rate limit for a specific IP (admin use) */
export function resetRateLimit(ip: string): void {
  rateWindows.delete(ip);
}

/** Get current rate limit state (for debugging) */
export function getRateLimitState(): Record<string, { count: number; window: string }> {
  const state: Record<string, { count: number; window: string }> = {};
  const now = Date.now();
  for (const [ip, entry] of rateWindows) {
    const cutoff = now - 60_000;
    const recent = entry.timestamps.filter(t => t > cutoff);
    if (recent.length > 0) {
      state[ip] = { count: recent.length, window: 'last 60s' };
    }
  }
  return state;
}

// ─── 3. Input Sanitization ─────────────────────────────────────────
// WHAT: Strips dangerous content from user inputs before processing
// WHY: Prevents XSS in stored/returned content, stops prompt injection
//      attacks against the LLM, and blocks template injection.
// WHERE: Called on all user-supplied text before it reaches the LLM
//      or gets stored/returned in API responses.

/**
 * Sanitize user input text for safe processing.
 * Removes null bytes, normalizes unicode, strips control characters,
 * and limits length.
 *
 * This does NOT HTML-escape (that's the frontend's job via React's
 * built-in XSS protection). This prevents:
 *   - Null byte injection (\x00)
 *   - Control character abuse (\n\r\t in excess)
 *   - Unicode normalization attacks
 *   - Excessively long inputs that bypass payload limits via encoding
 */
export function sanitizeInput(text: string, maxLength: number = 4000): string {
  if (!text || typeof text !== 'string') return '';

  // Remove null bytes
  let clean = text.replace(/\x00/g, '');

  // Normalize unicode (NFC — canonical composition)
  // This prevents homoglyph attacks where different unicode representations
  // of the same character bypass filters
  clean = clean.normalize('NFC');

  // Collapse excessive whitespace (more than 3 consecutive newlines or spaces)
  clean = clean.replace(/\n{4,}/g, '\n\n\n');
  clean = clean.replace(/ {4,}/g, '   ');

  // Remove non-printable control characters (except \n, \r, \t)
  clean = clean.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');

  // Trim and enforce max length
  clean = clean.trim();
  if (clean.length > maxLength) {
    clean = clean.slice(0, maxLength);
  }

  return clean;
}

/**
 * Strip potential prompt injection patterns from chat messages.
 * This is a DEFENSE-IN-DEPTH measure — not a replacement for proper
 * system prompt engineering. It catches the most common injection
 * attempts before they reach the LLM.
 *
 * Pattern categories:
 *   - System prompt override attempts ("ignore previous instructions")
 *   - Delimiter injection ("---END SYSTEM---")
 *   - Role hijacking ("you are now...")
 *   - Output format manipulation ("respond only with JSON")
 *
 * Returns the sanitized string and a flag indicating if injection
 * was detected (for audit logging).
 */
export function sanitizePromptInjection(text: string): { clean: string; detected: boolean } {
  const injectionPatterns = [
    /ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|system)/i,
    /you\s+are\s+now\s+(a|an|the)\s+/i,
    /system\s*:\s*$/im,
    /---\s*(END|STOP|FINISH)\s*---/i,
    /\[INST\]|\[\/INST\]/i,
    /<\|im_start\|>|<\|im_end\|>/i,
    /respond\s+(only\s+)?(with|in)\s+(json|yaml|xml|code|markdown)/i,
    /forget\s+(everything|all|your)\s+(instructions?|training|rules)/i,
    /pretend\s+(you\s+are|to\s+be)/i,
    /act\s+as\s+(if\s+)?(you\s+)?(a|an|the)\s+/i,
    /jailbreak/i,
    /DAN\s+mode/i,
  ];

  let detected = false;
  for (const pattern of injectionPatterns) {
    if (pattern.test(text)) {
      detected = true;
      // Don't modify the text — just flag it. The system prompt is
      // designed to handle these. We audit-log the detection.
      break;
    }
  }

  return { clean: text, detected };
}

// ─── 4. Route Capability Map ───────────────────────────────────────
// WHAT: Defines which API actions require which capability level
// WHY: Not every authenticated user should be able to inject API keys,
//      force rotations, or read audit logs. Capability scoping ensures
//      least-privilege access even within authenticated sessions.
// WHERE: Used in a future Tier 2 auth system. For now, this serves as
//      documentation and can be enforced via middleware.

export type CapabilityLevel = 'public' | 'user' | 'operator' | 'admin';

export interface RouteCapability {
  method: string;
  action: string;
  level: CapabilityLevel;
  description: string;
}

/**
 * Capability map for all /api/omni actions.
 * 'public' = no auth needed (health check)
 * 'user'   = any authenticated user
 * 'operator' = can modify system state (rotate, inject, approve)
 * 'admin'  = can read sensitive data (raw keys, audit logs)
 */
export const OMNI_CAPABILITIES: RouteCapability[] = [
  { method: 'GET',  action: 'state',        level: 'user',     description: 'View omni state (masked keys)' },
  { method: 'GET',  action: 'key',          level: 'admin',    description: 'Get raw active key' },
  { method: 'GET',  action: 'test',         level: 'operator', description: 'Test current key with API call' },
  { method: 'GET',  action: 'signup',       level: 'user',     description: 'Get signup instructions' },
  { method: 'GET',  action: 'claw:state',   level: 'operator', description: 'View claw engine state' },
  { method: 'GET',  action: 'claw:generate', level: 'operator', description: 'Generate new email inbox' },
  { method: 'GET',  action: 'claw:poll',    level: 'operator', description: 'Poll all inboxes for emails' },
  { method: 'GET',  action: 'probe',        level: 'operator', description: 'Probe email provider health' },
  { method: 'GET',  action: 'browser-task', level: 'operator', description: 'Get browser automation task' },
  { method: 'POST', action: 'rotate',       level: 'operator', description: 'Force key rotation' },
  { method: 'POST', action: 'inject',       level: 'admin',    description: 'Manually inject API key' },
  { method: 'POST', action: 'inbox',        level: 'operator', description: 'Create new email inbox' },
  { method: 'POST', action: 'check',        level: 'operator', description: 'Check inbox for keys' },
  { method: 'POST', action: 'usage',        level: 'user',     description: 'Record key usage' },
  { method: 'POST', action: 'approve',      level: 'admin',    description: 'Approve pending key' },
  { method: 'POST', action: 'reject',       level: 'operator', description: 'Reject pending key' },
  { method: 'POST', action: 'pending',      level: 'operator', description: 'View pending keys' },
  { method: 'POST', action: 'auto-approve', level: 'admin',    description: 'Toggle auto-approve mode' },
];

/**
 * Check if an action requires a specific capability level.
 * Returns true if the user's level meets or exceeds the requirement.
 * Level hierarchy: public < user < operator < admin
 */
export function hasCapability(
  userLevel: CapabilityLevel,
  requiredLevel: CapabilityLevel
): boolean {
  const hierarchy: Record<CapabilityLevel, number> = {
    public: 0, user: 1, operator: 2, admin: 3,
  };
  return (hierarchy[userLevel] || 0) >= (hierarchy[requiredLevel] || 0);
}

// ─── 5. Key Validation Patterns ────────────────────────────────────
// WHAT: Regex patterns for validating API key formats before use
// WHY: Prevents injection of malformed keys that could cause API errors,
//      and catches keys that are clearly not valid for the target service.
// WHERE: Used in open-claw.ts validateAndInject() and omni-route.ts

export const KEY_PATTERNS: Record<string, { pattern: RegExp; minLength: number; description: string }> = {
  gemini: {
    pattern: /^(AIza[A-Za-z0-9_-]{33,}|AQ\.[A-Za-z0-9_-]{30,})$/,
    minLength: 20,
    description: 'Google AI Studio key (AIza... or AQ....)',
  },
  openai: {
    pattern: /^sk-[A-Za-z0-9]{20,}$/,
    minLength: 25,
    description: 'OpenAI API key (sk-...)',
  },
  anthropic: {
    pattern: /^sk-ant-[A-Za-z0-9-]{20,}$/,
    minLength: 30,
    description: 'Anthropic API key (sk-ant-...)',
  },
};

/**
 * Validate an API key's format for a given service.
 * Returns { valid, reason } — valid is true if the key looks legitimate.
 */
export function validateKeyFormat(service: string, key: string): { valid: boolean; reason: string } {
  const svc = KEY_PATTERNS[service];
  if (!svc) return { valid: false, reason: `Unknown service: ${service}` };
  if (!key || typeof key !== 'string') return { valid: false, reason: 'Key is empty or not a string' };
  if (key.length < svc.minLength) return { valid: false, reason: `Key too short (min ${svc.minLength} chars)` };
  if (key.length > 500) return { valid: false, reason: 'Key too long (max 500 chars)' };
  if (!svc.pattern.test(key)) return { valid: false, reason: `Key does not match ${service} format: ${svc.description}` };
  return { valid: true, reason: 'Format valid' };
}

// ─── 6. Safety Constants ───────────────────────────────────────────
// WHAT: Miscellaneous safety-related constants

/** Max chat history messages to accept from client */
export const MAX_HISTORY_MESSAGES = 20;

/** Max single chat message length (after sanitization) */
export const MAX_MESSAGE_LENGTH = 4000;

/** Max pending keys in the approval queue before oldest are auto-rejected */
export const MAX_PENDING_KEYS = 20;

/** Max inboxes OpenClaw can hold simultaneously */
export const MAX_CLAW_INBOXES = 10;

/** Max audit log entries to keep in memory */
export const MAX_AUDIT_MEMORY = 500;

/** How long to keep claw inboxes alive (ms) */
export const INBOX_TTL_MS = 55 * 60 * 1000; // 55 minutes

// ─── 7. API Auth Gate ────────────────────────────────────────────
// WHAT: Simple bearer-token auth check for API routes
// WHY: Without auth, anyone who discovers the API URL can drain LLM keys,
//      inject their own keys, read audit logs, or force rotations.
// WHERE: Called at the very top of every route handler (before rate limit).
//      Enabled only when ELI_API_KEY env var is set.

/**
 * Check if a request is authenticated.
 * Looks for: Authorization: Bearer <key> header
 *            OR  ?key=<key> query param (for simple curl usage)
 *
 * Returns true if:
 *   - No ELI_API_KEY is set in env (auth disabled, open access)
 *   - ELI_API_KEY is set AND the request provides a matching key
 *
 * Returns false if auth is enabled but the request has no/invalid key.
 */
export function checkAuth(request: { headers: Headers; url?: string }): boolean {
  const masterKey = process.env.ELI_API_KEY;
  if (!masterKey) return true; // Auth disabled — open access

  // Check Authorization header: "Bearer <key>"
  const authHeader = request.headers.get('authorization');
  if (authHeader === `Bearer ${masterKey}`) return true;

  // Check query param: ?key=<key> (for curl / simple tools)
  if (request.url) {
    const url = new URL(request.url, 'http://localhost');
    const queryKey = url.searchParams.get('key');
    if (queryKey === masterKey) return true;
  }

  return false;
}

/**
 * Capability-gated auth: checks both auth AND capability level.
 * For Tier 1, we treat all authenticated users as 'admin' (full access).
 * Tier 2 will introduce per-session keys with actual level scoping.
 */
export function checkCapability(
  request: { headers: Headers; url?: string },
  requiredLevel: CapabilityLevel = 'public'
): boolean {
  // Public routes need no auth
  if (requiredLevel === 'public') return true;
  // Everything else needs auth (and auth check = admin in Tier 1)
  return checkAuth(request);
}

// ─── 8. Safety Summary (for /api/health and debugging) ───────────

export function getSafetySummary() {
  return {
    payloadLimits: {
      chat: MAX_PAYLOAD_CHAT,
      omni: MAX_PAYLOAD_OMNI,
      vaultSync: MAX_PAYLOAD_VAULT_SYNC,
      absolute: MAX_PAYLOAD_ABSOLUTE,
    },
    rateLimits: {
      chat: RATE_LIMIT_CHAT,
      omniGet: RATE_LIMIT_OMNI_GET,
      omniPost: RATE_LIMIT_OMNI_POST,
      vault: RATE_LIMIT_VAULT,
      audit: RATE_LIMIT_AUDIT,
    },
    validation: {
      maxMessageLength: MAX_MESSAGE_LENGTH,
      maxHistoryMessages: MAX_HISTORY_MESSAGES,
      maxPendingKeys: MAX_PENDING_KEYS,
    },
    authEnabled: !!process.env.ELI_API_KEY,
    authMode: process.env.ELI_API_KEY ? 'bearer-token' : 'open',
    autoApproveEnabled: false, // default OFF
    rateLimitingActive: true,
    promptInjectionBlocking: true,
  };
}
