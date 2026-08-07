/**
 * /api/omni — Eli's self-healing API key rotation endpoint
 * 
 * OpenInbox-powered. Two modes:
 *   creation-only (no OPENINBOX_API_KEY): create inboxes, track state, manual inject
 *   full-auto (with OPENINBOX_API_KEY): also reads emails + auto-extracts keys
 * 
 * GET  /api/omni              → omni state (active key, pool, mode)
 * GET  /api/omni?action=key    → raw active key (internal use)
 * GET  /api/omni?action=test   → test current key
 * GET  /api/omni?action=signup → get signup instructions (email + URL)
 * POST /api/omni              → force rotation
 * POST /api/omni?action=inject → manually inject an API key
 * POST /api/omni?action=inbox  → create a fresh temp inbox
 * POST /api/omni?action=check  → check inbox for new keys
 * POST /api/omni?action=usage  → record usage
 */

import { NextRequest, NextResponse } from 'next/server';
import { getOmniRoute } from '@/lib/omni-route';
import { getOpenClaw } from '@/lib/open-claw';
import { audit } from '@/lib/audit-log';
import {
  MAX_PAYLOAD_OMNI, validateKeyFormat,
  checkAuth, checkRateLimit,
  RATE_LIMIT_OMNI_GET, RATE_LIMIT_OMNI_POST,
  OMNI_CAPABILITIES, hasCapability, CapabilityLevel,
} from '@/lib/safety-gate';

const MAX_PAYLOAD_SIZE = MAX_PAYLOAD_OMNI;

function getClientIp(request: NextRequest): string {
  return request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
}

function enforcePayloadLimit(request: NextRequest): boolean {
  const len = parseInt(request.headers.get('content-length') || '0', 10);
  if (len > MAX_PAYLOAD_SIZE) return false;
  return true;
}

// ─── Helpers ────────────────────────────────────────────────

function maskKey(key: string): string {
  if (!key || key.length < 12) return '***';
  return `${key.slice(0, 8)}...${key.slice(-4)}`;
}

// ─── GET ────────────────────────────────────────────────────

export async function GET(request: NextRequest) {
  const ip = getClientIp(request);
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action') || 'state';

  // ─── Auth + Rate limit (Tier 1) ──────────────────────────────
  const cap = OMNI_CAPABILITIES.find(c => c.method === 'GET' && c.action === action);
  const requiredLevel = (cap?.level || 'user') as CapabilityLevel;
  if (!checkCapability(request, requiredLevel)) {
    audit('auth.blocked', `Omni GET ${action} auth failed from ${ip}`, { ip, action });
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  if (!checkRateLimit(ip, RATE_LIMIT_OMNI_GET)) {
    audit('omni.ratelimited', `Omni GET rate limited from ${ip}`, { ip });
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
  }

  const omni = getOmniRoute();

  try {
    // ── State ──
    if (action === 'state') {
      const state = omni.getState();
      return NextResponse.json({
        action: 'state',
        mode: state.mode,
        hasValidKey: omni.hasValidKey(),
        activeKey: state.activeKey
          ? { ...state.activeKey, key: maskKey(state.activeKey.key) }
          : null,
        keyHistory: state.keyHistory.map(k => ({ ...k, key: maskKey(k.key) })),
        claw: state.clawState
          ? {
              totalGenerated: state.clawState.totalGenerated,
              totalEmailsRead: state.clawState.totalEmailsRead,
              totalKeysExtracted: state.clawState.totalKeysExtracted,
              lastKeyExtracted: state.clawState.lastKeyExtracted
                ? maskKey(state.clawState.lastKeyExtracted) : null,
              inboxes: (state.clawState.inboxes || []).map((i: any) => ({
                id: i.id,
                email: i.email,
                provider: i.provider,
                status: i.status,
                emailCount: i.emailCount,
                expiresAt: i.expiresAt,
                ttlMinutes: Math.max(0, Math.round((i.expiresAt - Date.now()) / 60000)),
              })),
              providerStats: state.clawState.providerStats,
              providerHealth: state.clawState.providerHealth,
            }
          : null,
        totalRotations: state.totalRotations,
        lastRotationAt: state.lastRotationAt,
        lastError: state.lastError,
      });
    }

    // ── Raw key (internal) ──
    if (action === 'key') {
      const key = omni.getActiveKey(searchParams.get('service') || undefined);
      return NextResponse.json({ key, source: 'omni-route', valid: omni.hasValidKey(searchParams.get('service') || undefined) });
    }

    // ── Test key ──
    if (action === 'test') {
      const service = searchParams.get('service') || 'gemini';
      const key = omni.getActiveKey(service);

      if (!key || (service === 'gemini' && !key.match(/AIza|^AQ\./))) {
        return NextResponse.json({
          action: 'test', service, status: 'invalid',
          message: key ? 'Key format invalid — not a standard API key' : 'No active key',
        });
      }

      try {
        const { GoogleGenerativeAI } = await import('@google/generative-ai');
        const genAI = new GoogleGenerativeAI(key);
        const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });
        const result = await model.generateContent({
          contents: [{ role: 'user', parts: [{ text: 'Say OK' }] }],
        });
        const text = result.response.text();
        omni.recordUsage(1);
        return NextResponse.json({
          action: 'test', service, status: 'valid',
          response: text.slice(0, 50),
        });
      } catch (err: any) {
        return NextResponse.json({
          action: 'test', service, status: 'error',
          message: err.message?.slice(0, 200),
        });
      }
    }

    // ── Signup instructions ──
    if (action === 'signup') {
      const instructions = omni.getSignupInstructions(searchParams.get('service') || undefined);
      if (!instructions) {
        return NextResponse.json({
          action: 'signup', status: 'no-inbox',
          message: 'No fresh inbox available. Call POST /api/omni?action=inbox first.',
        });
      }
      return NextResponse.json({
        action: 'signup',
        ...instructions,
        steps: [
          `1. Go to ${instructions.url}`,
          `2. Sign up / create API key using email: ${instructions.email}`,
          `3. The key email will arrive in the inbox`,
          `4. Call POST /api/omni?action=check with inboxId to extract the key`,
          `5. Or manually inject: POST /api/omni?action=inject { service, key }`,
        ],
      });
    }

    // ── Claw: direct claw operations ──
    if (action === 'claw') {
      const { getOpenClaw } = await import('@/lib/open-claw');
      const claw = getOpenClaw();
      const sub = searchParams.get('sub') || 'state';

      if (sub === 'generate') {
        const provider = (searchParams.get('provider') as any) || undefined;
        const inbox = await claw.generate(provider);
        return NextResponse.json({
          action: 'claw-generate',
          id: inbox.id,
          email: inbox.email,
          provider: inbox.provider,
          ttlMinutes: Math.round((inbox.expiresAt - Date.now()) / 60000),
        });
      }

      if (sub === 'poll') {
        const purged = claw.purgeExpired();
        const results = await claw.pollAll();
        const summary: Record<string, number> = {};
        for (const [email, emails] of results) {
          summary[email] = emails.length;
        }
        return NextResponse.json({
          action: 'claw-poll',
          purgedExpired: purged,
          inboxesWithMail: summary,
          clawState: claw.getState(),
        });
      }

      // Default: claw state
      return NextResponse.json({ action: 'claw-state', ...claw.getState() });
    }

    // ── Probe: health-check all email providers (Agent-Reach) ──
    if (action === 'probe') {
      const { getOpenClaw } = await import('@/lib/open-claw');
      const clawProbe = getOpenClaw();
      await clawProbe.probeAllProviders();
      const state = clawProbe.getState();
      return NextResponse.json({
        action: 'probe',
        providerHealth: state.providerHealth,
        bestProvider: await clawProbe.getBestProvider(),
      });
    }

    // ── Browser task: get browser-use instructions for a service signup ──
    if (action === 'browser-task') {
      const { getOpenClaw } = await import('@/lib/open-claw');
      const clawBt = getOpenClaw();
      const service = searchParams.get('service') || 'gemini';
      const task = await clawBt.generateBrowserTask(service);
      if (!task) {
        return NextResponse.json({ error: `No browser task for service: ${service}` }, { status: 400 });
      }
      return NextResponse.json({
        action: 'browser-task',
        ...task,
        note: 'Execute these steps with browser-use/Playwright. After completion, the claw will auto-poll the inbox for the API key.',
        supportedServices: clawBt.getSupportedBrowserServices(),
      });
    }

    return NextResponse.json(
      { error: 'Unknown action. Use: state, key, test, signup, claw, probe, browser-task' },
      { status: 400 }
    );
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

// ─── POST ───────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  const ip = getClientIp(request);

  // ─── Auth + Rate limit (Tier 1) ──────────────────────────────
  if (!checkAuth(request)) {
    audit('auth.blocked', `Omni POST auth failed from ${ip}`, { ip });
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  if (!checkRateLimit(ip, RATE_LIMIT_OMNI_POST)) {
    audit('omni.ratelimited', `Omni POST rate limited from ${ip}`, { ip });
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
  }

  if (!enforcePayloadLimit(request)) {
    return NextResponse.json({ error: 'Payload too large (max 10KB)' }, { status: 413 });
  }

  const body = await request.json().catch(() => ({}));
  const { action } = body as { action?: string };

  // Per-action capability check
  const cap = OMNI_CAPABILITIES.find(c => c.method === 'POST' && c.action === action);
  if (cap && !hasCapability('admin', cap.level)) {
    audit('auth.blocked', `Omni POST ${action} capability denied from ${ip}`, { ip, action, required: cap.level });
    return NextResponse.json({ error: 'Insufficient permissions' }, { status: 403 });
  }

  const omni = getOmniRoute();

  try {
    // ── Force rotation ──
    if (!action || action === 'rotate') {
      audit('key.rotation', `Force rotate requested`, { ip });
      const service = (body as { service?: string }).service || 'gemini';
      const newKey = await omni.rotate(service);
      if (!newKey) {
        return NextResponse.json({
          error: 'Rotation failed', lastError: omni.getState().lastError,
        }, { status: 500 });
      }
      return NextResponse.json({
        action: 'rotated',
        service: newKey.service,
        inboxEmail: newKey.inboxEmail,
        inboxExpiresAt: new Date(newKey.inboxExpiresAt).toISOString(),
        keyExtracted: !!newKey.key,
        keyPreview: newKey.key ? maskKey(newKey.key) : null,
        status: newKey.status,
        message: newKey.key
          ? `Key extracted and injected. Eli is LIVE.`
          : `Inbox created: ${newKey.inboxEmail}. Use this email to get an API key, then POST /api/omni?action=check`,
      });
    }

    // ── Manual key injection (with format validation) ──
    if (action === 'inject') {
      const { service, key } = body as { service: string; key: string };
      if (!service || !key) {
        return NextResponse.json({ error: 'service and key are required' }, { status: 400 });
      }
      // Tier 1: Validate key format before injection
      const validation = validateKeyFormat(service, key);
      if (!validation.valid) {
        audit('key.inject.blocked', `Invalid key format for ${service}: ${validation.reason}`, { ip, service });
        return NextResponse.json({ error: `Invalid key: ${validation.reason}` }, { status: 400 });
      }
      const newKey = omni.injectKey(service, key);
      audit('key.injected', `Validated ${service} key injected`, { ip, service, keyPreview: maskKey(key) });
      return NextResponse.json({
        action: 'injected',
        service: newKey.service,
        keyPreview: maskKey(newKey.key),
        status: newKey.status,
      });
    }

    // ── Create inbox only ──
    if (action === 'inbox') {
      const inbox = await omni.createInbox((body as { prefix?: string }).prefix);
      return NextResponse.json({
        action: 'inbox-created',
        id: inbox.id,
        email: inbox.email,
        expiresAt: inbox.expiresAt,
        ttlMinutes: Math.round((new Date(inbox.expiresAt).getTime() - Date.now()) / 60000),
      });
    }

    // ── Check inbox for keys ──
    if (action === 'check') {
      const { inboxId, service } = body as { inboxId: string; service?: string };
      if (!inboxId) {
        return NextResponse.json({ error: 'inboxId is required' }, { status: 400 });
      }
      const extractedKey = await omni.checkInboxForKeys(inboxId, service);
      if (extractedKey) {
        const svc = service || 'gemini';
        return NextResponse.json({
          action: 'key-found',
          service: svc,
          keyPreview: maskKey(extractedKey),
          message: 'Key extracted and injected into Eli!',
        });
      }
      return NextResponse.json({
        action: 'no-key',
        message: 'No API key found in inbox yet. The email might not have arrived.',
      });
    }

    // ── Record usage ──
    if (action === 'usage') {
      const { calls } = body as { calls?: number };
      omni.recordUsage(calls || 1);
      return NextResponse.json({ action: 'usage-recorded' });
    }

    // ── Tier 1: Approve pending key ──
    if (action === 'approve') {
      const { pendingId } = body as { pendingId: string };
      if (!pendingId) {
        return NextResponse.json({ error: 'pendingId is required' }, { status: 400 });
      }
      const claw = getOpenClaw();
      const valid = await claw.approvePendingKey(pendingId);
      if (!valid) {
        return NextResponse.json({ action: 'approve-failed', message: 'Key not found, already processed, or failed validation' }, { status: 400 });
      }
      return NextResponse.json({ action: 'approved', pendingId });
    }

    // ── Tier 1: Reject pending key ──
    if (action === 'reject') {
      const { pendingId } = body as { pendingId: string };
      if (!pendingId) {
        return NextResponse.json({ error: 'pendingId is required' }, { status: 400 });
      }
      const claw = getOpenClaw();
      const rejected = claw.rejectPendingKey(pendingId);
      if (!rejected) {
        return NextResponse.json({ action: 'reject-failed', message: 'Key not found or already processed' }, { status: 400 });
      }
      return NextResponse.json({ action: 'rejected', pendingId });
    }

    // ── Tier 1: Get pending keys ──
    if (action === 'pending') {
      const claw = getOpenClaw();
      const pending = claw.getPendingKeys();
      return NextResponse.json({
        action: 'pending-keys',
        count: pending.length,
        keys: pending.map(k => ({
          id: k.id,
          service: k.service,
          keyPreview: k.key.slice(0, 8) + '...',
          inboxEmail: k.inboxEmail,
          extractedAt: k.extractedAt,
        })),
      });
    }

    // ── Tier 1: Toggle auto-approve mode ──
    if (action === 'auto-approve') {
      const { enabled } = body as { enabled: boolean };
      const claw = getOpenClaw();
      claw.setAutoApprove(enabled !== false);
      audit('key.auto-approve', `Auto-approve ${enabled !== false ? 'enabled' : 'disabled'}`, { ip });
      return NextResponse.json({ action: 'auto-approve-set', enabled: enabled !== false });
    }

    return NextResponse.json(
      { error: `Unknown action: ${action}. Use: rotate, inject, inbox, check, usage, approve, reject, pending, auto-approve` },
      { status: 400 }
    );
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
