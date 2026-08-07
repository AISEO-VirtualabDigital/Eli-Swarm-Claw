/**
 * Eli API Authentication Middleware (Tier 1 Safety)
 * 
 * Enforces bearer token auth on all /api/* routes.
 * Static pages and assets are exempt.
 * 
 * Env vars:
 *   ELI_API_KEY — required bearer token (set this in .env and on VPS)
 *   ELI_AUTH_DISABLED — set to 'true' to bypass (dev only)
 */

import { NextRequest, NextResponse } from 'next/server';

const PUBLIC_PATHS = ['/_next', '/logo.svg', '/favicon.ico', '/api/health'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip non-API and public paths
  if (!pathname.startsWith('/api/') || PUBLIC_PATHS.some(p => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Dev bypass
  if (process.env.ELI_AUTH_DISABLED === 'true') {
    return NextResponse.next();
  }

  const apiKey = process.env.ELI_API_KEY;
  if (!apiKey) {
    console.warn('[AUTH] ELI_API_KEY not set — API routes are UNPROTECTED. Set ELI_API_KEY immediately.');
    return NextResponse.next();
  }

  const authHeader = request.headers.get('authorization');
  const queryToken = request.nextUrl.searchParams.get('token');
  const token = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : queryToken;

  if (!token || token !== apiKey) {
    console.warn(`[AUTH] Blocked unauthorized request to ${pathname} from ${request.headers.get('x-forwarded-for') || 'unknown'}`);
    return NextResponse.json(
      { error: 'Unauthorized', message: 'Valid Bearer token required' },
      { status: 401 }
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/api/:path*'],
};
