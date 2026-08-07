import { NextRequest, NextResponse } from 'next/server';
import { readFile, readdir, stat } from 'fs/promises';
import { join } from 'path';

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

async function parseChunkFile(filePath: string): Promise<Record<string, any> | null> {
  try {
    const content = await readFile(filePath, 'utf-8');
    const fmEnd = content.indexOf('---', 3);
    if (fmEnd === -1) return null;
    const fmRaw = content.slice(3, fmEnd).trim();
    const body = content.slice(fmEnd + 3).trim();
    const getField = (field: string): string => {
      const regex = new RegExp(`^"?${field}:\s*"?([^"(\n)]*)"?$`, 'm');
      const m = fmRaw.match(regex);
      return m ? m[1].trim() : '';
    };
    const getArrayField = (field: string): string[] => {
      const escaped = field.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`^${escaped}:\\s*\\[([^\\]]*)\\]`, 'm');
      const m = fmRaw.match(regex);
      if (!m) return [];
      return m[1].match(/"([^"]+)"/g)?.map(s => s.replace(/"/g, '')) || [];
    };
    return {
      id: getField('id'), source: getField('source'), title: getField('title'),
      category: getField('category'), skillTags: getArrayField('skillTags'),
      containmentHash: getField('containmentHash'), content: body,
    };
  } catch { return null; }
}

export async function GET(request: NextRequest) {
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
      const chunks: Record<string, any>[] = [];

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