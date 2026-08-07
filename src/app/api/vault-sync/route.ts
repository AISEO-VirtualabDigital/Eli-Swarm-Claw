import { NextRequest, NextResponse } from 'next/server';
import { readFile, readdir, stat } from 'fs/promises';
import { join } from 'path';
import { parseChunkFile } from '@/lib/vault-search';
import { audit } from '@/lib/audit-log';
import {
  checkAuth, checkRateLimit, RATE_LIMIT_VAULT,
} from '@/lib/safety-gate';

const VAULT_PATH = process.env.OBSIDIAN_VAULT_PATH || join(process.cwd(), 'data', 'eli-vault');
const ACTIVE_DIR = join(VAULT_PATH, '01-Active');
const INDEX_PATH = join(VAULT_PATH, '03-Index', 'vault-index.json');

const CATEGORY_EMOJI: Record<string, string> = {
  seo: '🔍', 'web-design': '🎨', 'google-api': '☁️', scraping: '🕷️',
  social: '📱', 'ai-agent': '🤖', obsidian: '📝', saas: '💼',
  automation: '⚡', 'eli-core': '🧠', content: '✍️', infra: '🖥️',
  ecommerce: '🛒', crm: '👥', security: '🔒', database: '🗄️',
  knowledge: '📚', 'project-mgmt': '📋',
};

function getClientIp(request: NextRequest): string {
  return request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
}

export async function GET(request: NextRequest) {
  const ip = getClientIp(request);

  // ─── Auth + Rate limit (Tier 1) ──────────────────────────────
  if (!checkAuth(request)) {
    audit('auth.blocked', `Vault-sync auth failed from ${ip}`, { ip });
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  if (!checkRateLimit(ip, RATE_LIMIT_VAULT)) {
    audit('vault.ratelimited', `Vault rate limited from ${ip}`, { ip });
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
  }

  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action') || 'stats';

  try {
    if (action === 'stats') {
      const indexData = JSON.parse(await readFile(INDEX_PATH, 'utf-8'));
      return NextResponse.json({
        action: 'stats', vault: indexData,
        categories: Object.keys(CATEGORY_EMOJI),
        timestamp: Date.now(),
      });
    }

    if (action === 'export') {
      const category = searchParams.get('category') || '';
      const limit = parseInt(searchParams.get('limit') || '50');
      const offset = parseInt(searchParams.get('offset') || '0');
      const format = searchParams.get('format') || 'obsidian';

      const targetDir = category ? join(ACTIVE_DIR, category) : ACTIVE_DIR;
      const chunks: Array<Record<string, any>> = [];

      async function walkDir(dir: string) {
        const entries = await readdir(dir);
        for (const entry of entries) {
          if (chunks.length >= offset + limit) return;
          const fullPath = join(dir, entry);
          const s = await stat(fullPath).catch(() => null);
          if (!s) continue;
          if (s.isDirectory()) {
            await walkDir(fullPath);
          } else if (entry.endsWith('.md')) {
            const chunk = await parseChunkFile(fullPath);
            if (chunk) chunks.push(chunk);
          }
        }
      }

      await walkDir(targetDir);
      const page = chunks.slice(offset, offset + limit);

      if (format === 'obsidian') {
        const emoji = CATEGORY_EMOJI[category] || '📁';
        let md = `# ${emoji} ${category || 'All'} — Export\n\n`;
        md += `> Exported from Eli Vault on ${new Date().toISOString()}\n`;
        md += `> Showing ${page.length} chunks (offset ${offset})\n\n---\n\n`;
        for (const c of page) {
          md += `## ${c.title || c.id}\n\n`;
          md += `**Source**: ${c.source} | **Category**: ${c.category} | **Skills**: ${(c.skillTags || []).join(', ')}\n\n`;
          md += `${c.content}\n\n---\n\n`;
        }
        return new NextResponse(md, {
          headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
        });
      }

      return NextResponse.json({
        action: 'export', category, total: chunks.length,
        offset, limit, chunks: page,
      });
    }

    if (action === 'moc') {
      const indexData = JSON.parse(await readFile(INDEX_PATH, 'utf-8'));
      const cats = indexData.categories || {};
      let md = '# 🧠 Eli Vault — Live Map of Content\n\n';
      md += `> Auto-generated from live vault | ${new Date().toISOString()}\n\n`;
      md += '## Knowledge Categories\n\n| Category | Chunks |\n|----------|--------|\n';
      for (const [cat, count] of Object.entries(cats).sort((a: any, b: any) => b[1] - a[1])) {
        const emoji = CATEGORY_EMOJI[cat] || '📁';
        md += `| ${emoji} ${cat} | ${count} |\n`;
      }
      md += `\n**Total**: ${indexData.totalChunks} chunks from ${indexData.totalFiles} sources\n`;
      md += '\n## Skill Tags\n\n';
      const tags = indexData.skillTags || {};
      for (const [tag, count] of Object.entries(tags).sort((a: any, b: any) => b[1] - a[1])) {
        md += `- **${tag}**: ${count} chunks\n`;
      }
      md += `\n---\n*Engine: ${indexData.engine} | Avg chunk: ${indexData.avgChunkSize} chars*\n`;
      return new NextResponse(md, {
        headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
      });
    }

    if (action === 'categories') {
      const entries = await readdir(ACTIVE_DIR);
      const categories = [];
      for (const e of entries) {
        const p = join(ACTIVE_DIR, e);
        const s = await stat(p).catch(() => null);
        if (s?.isDirectory()) {
          const files = await readdir(p);
          categories.push({ name: e, emoji: CATEGORY_EMOJI[e] || '📁', chunks: files.length });
        }
      }
      return NextResponse.json({ action: 'categories', categories });
    }

    return NextResponse.json({ error: 'Unknown action. Use: stats, export, moc, categories' }, { status: 400 });
  } catch (error) {
    console.error('[VAULT-SYNC] Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}