/**
 * Obsidian Sync API — Live knowledge source management
 *
 * Endpoints:
 *   GET  ?action=stats        — Get Obsidian connector stats
 *   GET  ?action=sources      — List all indexed sources
 *   GET  ?action=search&q=... — Search Obsidian knowledge
 *   POST ?action=reindex      — Trigger full re-index
 *   GET  ?action=moc          — Generate Obsidian MOC (Map of Content) as .md
 */

import { NextRequest, NextResponse } from 'next/server';
import {
  getObsidianStats,
  getObsidianSources,
  searchObsidian,
  reindexObsidian,
  getObsidianContext,
} from '@/lib/obsidian-connector';
import { audit } from '@/lib/audit-log';
import {
  checkAuth, checkRateLimit, RATE_LIMIT_VAULT, sanitizeInput,
} from '@/lib/safety-gate';

const CATEGORY_EMOJI: Record<string, string> = {
  seo: '\U0001f50d', 'web-design': '\U0001f3a8', 'google-api': '\u2601\ufe0f', scraping: '\U0001f577\ufe0f',
  social: '\U0001f4f1', 'ai-agent': '\U0001f916', obsidian: '\U0001f4dd', saas: '\U0001f4bc',
  automation: '\u26a1', 'eli-core': '\U0001f9e0', content: '\u270d\ufe0f', infra: '\U0001f5a5\ufe0f',
  ecommerce: '\U0001f6d2', crm: '\U0001f465', security: '\U0001f512', database: '\U0001f5c4\ufe0f',
  knowledge: '\U0001f4da', 'project-mgmt': '\U0001f4cb',
};

function getClientIp(request: NextRequest): string {
  return request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
}

export async function GET(request: NextRequest) {
  const ip = getClientIp(request);

  if (!checkAuth(request)) {
    audit('auth.blocked', `Obsidian-sync auth failed from ${ip}`, { ip });
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  if (!checkRateLimit(ip, RATE_LIMIT_VAULT)) {
    audit('obsidian.ratelimited', `Obsidian rate limited from ${ip}`, { ip });
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
  }

  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action') || 'stats';

  try {
    // ─── Stats ─────────────────────────────────────────
    if (action === 'stats') {
      const stats = await getObsidianStats();
      return NextResponse.json({
        action: 'stats',
        connector: 'obsidian-live',
        ...stats,
        timestamp: Date.now(),
      });
    }

    // ─── Sources list ──────────────────────────────────
    if (action === 'sources') {
      const sources = await getObsidianSources();
      const type = searchParams.get('type');
      const filtered = type ? sources.filter(s => s.sourceType === type) : sources;
      return NextResponse.json({
        action: 'sources',
        total: filtered.length,
        sources: filtered.map(s => ({
          id: s.id,
          title: s.title,
          category: s.category,
          sourceType: s.sourceType,
          size: s.size,
          modified: s.modified,
          chunkCount: s.chunkCount,
        })),
      });
    }

    // ─── Search ────────────────────────────────────────
    if (action === 'search') {
      const query = searchParams.get('q') || '';
      if (!query || query.length < 2) {
        return NextResponse.json({ error: 'Query parameter "q" is required (min 2 chars)' }, { status: 400 });
      }
      const cleanQuery = sanitizeInput(query, 200);
      const maxResults = Math.min(parseInt(searchParams.get('limit') || '8'), 20);
      const results = await searchObsidian(cleanQuery, { maxResults });

      return NextResponse.json({
        action: 'search',
        query: cleanQuery,
        results: results.map(r => ({
          id: r.chunk.id,
          title: r.chunk.title,
          content: r.chunk.content.slice(0, 300),
          source: r.chunk.source,
          category: r.chunk.category,
          sourceType: r.chunk.sourceType,
          score: r.score,
          matchedTerms: r.matchedTerms,
        })),
        totalResults: results.length,
      });
    }

    // ─── Context preview (like what Eli sees) ─────────
    if (action === 'context') {
      const query = searchParams.get('q') || '';
      if (!query || query.length < 2) {
        return NextResponse.json({ error: 'Query parameter "q" is required' }, { status: 400 });
      }
      const cleanQuery = sanitizeInput(query, 200);
      const ctx = await getObsidianContext(cleanQuery, { maxResults: 5 });
      return NextResponse.json({
        action: 'context',
        query: cleanQuery,
        context: ctx.context,
        sources: ctx.sources,
        totalAvailable: ctx.totalAvailable,
      });
    }

    // ─── Map of Content (Obsidian .md export) ──────────
    if (action === 'moc') {
      const sources = await getObsidianSources();
      const stats = await getObsidianStats();

      let md = '# \U0001f4d6 Obsidian Live Knowledge \u2014 Map of Content\n\n';
      md += `> Auto-generated from ${stats.totalSources} live sources | ${new Date().toISOString()}\n\n`;

      // Group by category
      const byCategory: Record<string, typeof sources> = {};
      for (const s of sources) {
        if (!byCategory[s.category]) byCategory[s.category] = [];
        byCategory[s.category].push(s);
      }

      md += '## Knowledge Categories\n\n';
      md += '| Category | Sources | Chunks |\n|----------|---------|--------|\n';
      for (const [cat, count] of Object.entries(stats.categories).sort((a: any, b: any) => b[1] - a[1])) {
        const emoji = CATEGORY_EMOJI[cat] || '\U0001f4c1';
        const srcCount = byCategory[cat]?.length || 0;
        md += `| ${emoji} ${cat} | ${srcCount} | ${count} |\n`;
      }

      md += `\n**Total**: ${stats.totalSources} sources, ${stats.totalChunks} chunks\n`;

      md += '\n## All Sources\n\n';
      for (const [cat, items] of Object.entries(byCategory).sort((a, b) => b[1].length - a[1].length)) {
        const emoji = CATEGORY_EMOJI[cat] || '\U0001f4c1';
        md += `### ${emoji} ${cat}\n\n`;
        for (const s of items.sort((a, b) => b.modified - a.modified)) {
          const typeLabel = s.sourceType === 'knowledge-source' ? 'KS' :
            s.sourceType === 'elos-template' ? 'EOS' :
              s.sourceType === 'elos-note' ? 'EON' : 'DOC';
          md += `- [${typeLabel}] **${s.title}** \u2014 ${s.chunkCount} chunks (${(s.size / 1024).toFixed(1)}KB)\n`;
        }
        md += '\n';
      }

      md += `\n---\n*Connector: obsidian-live v1 | Engine: term-index | Index age: ${Math.round(stats.indexAge / 1000)}s*\n`;

      return new NextResponse(md, {
        headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
      });
    }

    return NextResponse.json(
      { error: 'Unknown action. Use: stats, sources, search, context, moc' },
      { status: 400 }
    );
  } catch (error) {
    console.error('[OBSIDIAN-SYNC] Error:', error);
    audit('obsidian.error', `Unhandled: ${(error as Error).message?.slice(0, 100)}`, { ip });
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  const ip = getClientIp(request);

  if (!checkAuth(request)) {
    audit('auth.blocked', `Obsidian-sync POST auth failed from ${ip}`, { ip });
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const action = body.action || 'reindex';

    if (action === 'reindex') {
      audit('obsidian.reindex', `Reindex triggered from ${ip}`, { ip });
      const index = await reindexObsidian();
      return NextResponse.json({
        action: 'reindex',
        totalSources: index.totalSources,
        totalChunks: index.totalChunks,
        categories: index.categories,
        timestamp: Date.now(),
      });
    }

    return NextResponse.json({ error: 'Unknown POST action. Use: reindex' }, { status: 400 });
  } catch (error) {
    console.error('[OBSIDIAN-SYNC] POST Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
