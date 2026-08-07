/**
 * /api/audit — Eli audit trail endpoint (Tier 1 Safety)
 * 
 * GET /api/audit              → recent 100 entries
 * GET /api/audit?event=KEY    → filter by event type
 * GET /api/audit?limit=50     → custom limit
 */

import { NextRequest, NextResponse } from 'next/server';
import { getAuditLog } from '@/lib/audit-log';
import { audit } from '@/lib/audit-log';
import { checkAuth, checkRateLimit, RATE_LIMIT_AUDIT } from '@/lib/safety-gate';

function getClientIp(request: NextRequest): string {
  return request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
}

export async function GET(request: NextRequest) {
  const ip = getClientIp(request);

  // ─── Auth + Rate limit (Tier 1) — audit is admin-only ─────────
  if (!checkAuth(request)) {
    audit('auth.blocked', `Audit read failed from ${ip}`, { ip });
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  if (!checkRateLimit(ip, RATE_LIMIT_AUDIT)) {
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
  }

  const { searchParams } = new URL(request.url);
  const event = searchParams.get('event') || undefined;
  const limit = parseInt(searchParams.get('limit') || '100', 10);

  const entries = getAuditLog({ event, limit });

  return NextResponse.json({
    total: entries.length,
    entries,
  });
}
