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

// ─── Helpers ────────────────────────────────────────────────

function maskKey(key: string): string {
  if (!key || key.length < 12) return '***';
  return `${key.slice(0, 8)}...${key.slice(-4)}`;
}

// ─── GET ────────────────────────────────────────────────────

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action') || 'state';
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

    return NextResponse.json(
      { error: 'Unknown action. Use: state, key, test, signup, claw' },
      { status: 400 }
    );
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

// ─── POST ───────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const { action } = body as { action?: string };
  const omni = getOmniRoute();

  try {
    // ── Force rotation ──
    if (!action || action === 'rotate') {
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

    // ── Manual key injection ──
    if (action === 'inject') {
      const { service, key } = body as { service: string; key: string };
      if (!service || !key) {
        return NextResponse.json({ error: 'service and key are required' }, { status: 400 });
      }
      const newKey = omni.injectKey(service, key);
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

    return NextResponse.json(
      { error: `Unknown action: ${action}. Use: rotate, inject, inbox, check, usage` },
      { status: 400 }
    );
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
