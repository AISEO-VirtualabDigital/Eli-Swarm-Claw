/**
 * /api/omni — Eli's self-healing API key rotation endpoint
 * 
 * GET  /api/omni              → Get omni state (active key, history, pool)
 * POST /api/omni              → Force rotation for a service
 * POST /api/omni/inject       → Manually inject an API key
 * POST /api/omni/inbox        → Create a fresh temp inbox
 * POST /api/omni/check        → Check inbox for new keys
 * GET  /api/omni/test         → Test current key against a service
 */

import { NextRequest, NextResponse } from 'next/server';
import { getOmniRoute } from '@/lib/omni-route';

// ─── GET: State ─────────────────────────────────────────────

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action') || 'state';
  const omni = getOmniRoute();

  try {
    if (action === 'state') {
      const state = omni.getState();
      // Mask keys in response
      const safeState = {
        ...state,
        activeKey: state.activeKey
          ? { ...state.activeKey, key: state.activeKey.key ? `${state.activeKey.key.slice(0, 8)}...${state.activeKey.key.slice(-4)}` : '' }
          : null,
        keyHistory: state.keyHistory.map(k => ({
          ...k,
          key: k.key ? `${k.key.slice(0, 8)}...${k.key.slice(-4)}` : '',
        })),
      };
      return NextResponse.json({ action: 'state', ...safeState });
    }

    if (action === 'test') {
      const key = omni.getActiveKey(searchParams.get('service') || undefined);
      if (!key || key.startsWith('Astralform')) {
        return NextResponse.json({
          action: 'test',
          service: searchParams.get('service') || 'gemini',
          status: 'invalid',
          message: key ? 'Key format invalid — not a standard API key' : 'No active key',
        });
      }
      // Test against Gemini
      try {
        const { GoogleGenerativeAI } = await import('@google/generative-ai');
        const genAI = new GoogleGenerativeAI(key);
        const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });
        const result = await model.generateContent({ contents: [{ role: 'user', parts: [{ text: 'Say OK' }] }] });
        const text = result.response.text();
        return NextResponse.json({
          action: 'test', status: 'valid', response: text.slice(0, 50),
        });
      } catch (err: any) {
        return NextResponse.json({
          action: 'test', status: 'error',
          message: err.message?.slice(0, 200),
        });
      }
    }

    if (action === 'key') {
      // Return just the raw active key (for internal use)
      const key = omni.getActiveKey(searchParams.get('service') || undefined);
      return NextResponse.json({ key, source: 'omni-route' });
    }

    return NextResponse.json({ error: 'Unknown action. Use: state, test, key' }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

// ─── POST: Actions ───────────────────────────────────────────

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const { action } = body as { action?: string };
  const omni = getOmniRoute();

  try {
    // Force rotation
    if (!action || action === 'rotate') {
      const service = (body as { service?: string }).service || 'gemini';
      const newKey = await omni.rotate(service);
      if (!newKey) {
        return NextResponse.json({ error: 'Rotation failed', lastError: omni.getState().lastError }, { status: 500 });
      }
      return NextResponse.json({
        action: 'rotated',
        service: newKey.service,
        inboxEmail: newKey.inboxEmail,
        inboxExpiresAt: newKey.inboxExpiresAt,
        keyExtracted: !!newKey.key,
        keyPreview: newKey.key ? `${newKey.key.slice(0, 8)}...` : null,
        status: newKey.status,
        message: newKey.key
          ? `Key extracted and injected. ${newKey.status === 'active' ? 'Eli is LIVE.' : 'Key is warm — waiting for email delivery.'}`
          : `Inbox created: ${newKey.inboxEmail}. Use this email to get an API key, then check with POST /api/omni/check.`,
      });
    }

    // Manual key injection
    if (action === 'inject') {
      const { service, key } = body as { service: string; key: string };
      if (!service || !key) {
        return NextResponse.json({ error: 'service and key are required' }, { status: 400 });
      }
      const newKey = omni.injectKey(service, key);
      return NextResponse.json({
        action: 'injected',
        service: newKey.service,
        keyPreview: `${newKey.key.slice(0, 8)}...${newKey.key.slice(-4)}`,
        status: newKey.status,
      });
    }

    // Create inbox only
    if (action === 'inbox') {
      const inbox = await omni.createInbox((body as { prefix?: string }).prefix);
      return NextResponse.json({ action: 'inbox-created', ...inbox });
    }

    // Check inbox for new keys
    if (action === 'check') {
      const { inboxId, service } = body as { inboxId: string; service?: string };
      if (!inboxId) {
        return NextResponse.json({ error: 'inboxId is required' }, { status: 400 });
      }
      const extractedKey = await omni.checkInboxForKeys(inboxId, service);
      if (extractedKey) {
        const svc = service || 'gemini';
        omni.injectKey(svc, extractedKey);
        return NextResponse.json({
          action: 'key-found',
          service: svc,
          keyPreview: `${extractedKey.slice(0, 8)}...${extractedKey.slice(-4)}`,
          message: 'Key extracted and injected into Eli!',
        });
      }
      return NextResponse.json({
        action: 'no-key',
        message: 'No API key found in inbox yet. The email might not have arrived.',
      });
    }

    // Record usage
    if (action === 'usage') {
      const { calls } = body as { calls?: number };
      omni.recordUsage(calls || 1);
      return NextResponse.json({ action: 'usage-recorded' });
    }

    return NextResponse.json({ error: `Unknown action: ${action}. Use: rotate, inject, inbox, check, usage` }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
