import { NextResponse } from 'next/server';
import { getVaultStats } from '@/lib/vault-search';

export async function GET() {
  const start = Date.now();
  let vaultOk = false;
  let vaultStats: any = null;

  try {
    vaultStats = await getVaultStats();
    vaultOk = (vaultStats?.totalChunks || 0) > 0;
  } catch {
    vaultOk = false;
  }

  return NextResponse.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime_ms: Date.now() - start,
    vault: {
      ok: vaultOk,
      totalChunks: vaultStats?.totalChunks || 0,
      activeChunks: vaultStats?.activeChunks || 0,
      skills: vaultStats?.skills || 0,
      categories: Object.keys(vaultStats?.categories || {}).length,
      engine: vaultStats?.engine || 'unknown',
    },
    provider: process.env.GEMINI_API_KEY ? 'gemini-2.0-flash' : 'vault-fallback',
  });
}
