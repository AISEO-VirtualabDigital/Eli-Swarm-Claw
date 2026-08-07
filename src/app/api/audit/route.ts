/**
 * /api/audit — Eli audit trail endpoint (Tier 1 Safety)
 * 
 * GET /api/audit              → recent 100 entries
 * GET /api/audit?event=KEY    → filter by event type
 * GET /api/audit?limit=50     → custom limit
 */

import { NextRequest, NextResponse } from 'next/server';
import { getAuditLog } from '@/lib/audit-log';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const event = searchParams.get('event') || undefined;
  const limit = parseInt(searchParams.get('limit') || '100', 10);

  const entries = getAuditLog({ event, limit });

  return NextResponse.json({
    total: entries.length,
    entries,
  });
}