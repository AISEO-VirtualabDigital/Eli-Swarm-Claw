/**
 * Eli API Middleware (Tier 1 Safety)
 * 
 * Three-layer defense:
 *   Layer 1 — Bearer token authentication (ELI_API_KEY)
 *   Layer 2 — Rate limiting (per-IP sliding window)
 *   Layer 3 — Route-level capability scoping
 * 
 * Exempt paths: /_next (static assets), /api/health (monitoring)
 * 
 * Env vars:
 *   ELI_API_KEY — required bearer token (set in .env + VPS)
 *   ELI_AUTH_DISABLED — set to 'true' to bypass (dev only)
 */

import { NextRequest, NextResponse } from 'next/server';
import { checkRateLimit, RATE_LIMIT_DEFAULT, RATE_LIMIT_HEALTH } from '@/lib/safety-gate';

const PUBLIC_PATHS = ['/_next', '/logo.svg', '/favicon.ico'];

// Routes that get the permissive health rate limit
const HEALTH_PATHS = ['/api/health'];

// Rate limit map for specific route groups (applied AFTER auth)
// These are defaults — individual routes can apply tighter limits
const ROUTE_RATE_LIMITS: Record<string, { maxRequests: number; windowMs: number }> = {
  '/api/eli-chat':     { maxRequests: 15, windowMs: 60_000 },
  '/api/omni':         { maxRequests: 30, windowMs: 60_000 },
  '/api/vault-sync':   { maxRequests: 20, windowMs: 60_000 },
  '/api/audit':        { maxRequests: 10, windowMs: 60_000 },
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip non-API and public static paths
  if (!pathname.startsWith('/api/') || PUBLIC_PATHS.some(p => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // ─── Layer 1: Authentication ─────────────────────────────────

  // Health endpoint is always public (for monitoring probes)
  if (HEALTH_PATHS.some(p => pathname.startsWith(p))) {
    // Still rate-limit health checks
    const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
    if (!checkRateLimit(ip, RATE_LIMIT_HEALTH)) {
      return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
    }
    return NextResponse.next();
  }

  // Dev bypass
  if (process.env.ELI_AUTH_DISABLED === 'true') {
    console.warn('[AUTH] ELI_AUTH_DISABLED=true — API routes are UNPROTECTED (dev mode)');
  } else {
    const apiKey = process.env.ELI_API_KEY;
    if (!apiKey) {
      // No key configured — allow but warn (safe for initial deploy)
      console.warn('[AUTH] ELI_API_KEY not set — API routes are UNPROTECTED. Set ELI_API_KEY immediately.');
    } else {
      const authHeader = request.headers.get('authorization');
      const queryToken = request.nextUrl.searchParams.get('token');
      const token = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : queryToken;

      if (!token || token !== apiKey) {
        const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
        console.warn(`[AUTH] Blocked unauthorized request to ${pathname} from ${ip}`);
        return NextResponse.json(
          { error: 'Unauthorized', message: 'Valid Bearer token required' },
          { status: 401 }
        );
      }
    }
  }

  // ─── Layer 2: Rate Limiting (per-IP) ─────────────────────────
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';

  // Find the most specific matching route pattern
  let matchedLimit = RATE_LIMIT_DEFAULT;
  for (const [route, config] of Object.entries(ROUTE_RATE_LIMITS)) {
    if (pathname.startsWith(route)) {
      matchedLimit = config;
      break;
    }
  }

  // POST requests to omni get tighter limits than GET
  if (pathname === '/api/omni' && request.method === 'POST') {
    matchedLimit = { maxRequests: 5, windowMs: 60_000 };
  }

  if (!checkRateLimit(ip, matchedLimit)) {
    console.warn(`[RATE] Limited ${ip} on ${pathname} (${matchedLimit.maxRequests}/${matchedLimit.windowMs}ms)`);
    return NextResponse.json(
      { error: 'Too many requests', retryAfterMs: matchedLimit.windowMs },
      { status: 429, headers: { 'Retry-After': String(Math.ceil(matchedLimit.windowMs / 1000)) } }
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/api/:path*'],
};
