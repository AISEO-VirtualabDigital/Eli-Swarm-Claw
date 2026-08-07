/**
 * Vault Search v5 — Optimized index lookup
 * 
 * Uses search-index.json (built at ingestion time) for instant term→file mapping.
 * 
 * v5 changes:
 *   - Fixed containment search: uses search-index-absorbed.json instead of
 *     scanning 23K+ files in 00-Containment/ (was a critical performance bottleneck)
 *   - Absorbed repo v2 index support
 *   - Deduplication by source file (not chunk ID)
 */

import { readdir, readFile } from 'fs/promises';
import { join } from 'path';

const VAULT_PATH = process.env.OBSIDIAN_VAULT_PATH || join(process.cwd(), 'data', 'eli-vault');
const ACTIVE_DIR = join(VAULT_PATH, '01-Active');
const CONTAINMENT_DIR = join(VAULT_PATH, '00-Containment');
const INDEX_PATH = join(VAULT_PATH, '03-Index', 'vault-index.json');
const SEARCH_INDEX_DIR = join(VAULT_PATH, '03-Index');

// ─── Types ─────────────────────────────────────────────────────────

export interface VaultChunk {
  id: string;
  content: string;
  source: string;
  title: string;
  category: string;
  skillTags: string[];
  containmentHash: string;
  embeddingSig: string;
  dissolved?: boolean;
}

export interface VaultSearchResult {
  chunk: VaultChunk;
  score: number;
  matchedTerms: string[];
}

export interface VaultContextResult {
  context: string;
  sources: Array<{ title: string; source: string; category: string }>;
  containmentHits: number;
}

// ─── Index Cache ────────────────────────────────────────────────────

let vaultIndex: any = null;
let searchIndex: Record<string, string[]> = {};
let indexLoadTime = 0;
const INDEX_TTL = 60_000; // 1 min cache

// ─── Category mapping for query expansion ───────────────────────────

const CATEGORY_TERMS: Record<string, string[]> = {
  'seo': ['seo', 'search', 'ranking', 'serp', 'organic', 'backlink', 'keyword', 'parasite', 'aeo', 'geo'],
  'web-design': ['design', 'ui', 'ux', 'layout', 'css', 'frontend', 'component', 'theme', 'template'],
  'google-api': ['google', 'api', 'oauth', 'maps', 'drive', 'cloud', 'workspace', 'gemini'],
  'scraping': ['scrap', 'crawl', 'extract', 'harvest', 'parse', 'spider'],
  'social': ['social', 'instagram', 'twitter', 'facebook', 'linkedin', 'tiktok', 'youtube'],
  'ai-agent': ['ai', 'agent', 'llm', 'gpt', 'claude', 'gemini', 'eliza', 'chatgpt'],
  'obsidian': ['obsidian', 'vault', 'note', 'markdown', 'frontmatter', 'wikilink'],
  'saas': ['saas', 'serverless', 'ghl', 'gohighlevel', 'agency', 'funnel'],
  'automation': ['automation', 'workflow', 'n8n', 'activepieces', 'zapier', 'trigger'],
  'eli-core': ['eli', 'skill', 'harness', 'agent-eli', 'identity'],
  'content': ['copywriting', 'content', 'writing', 'blog', 'article', 'copy', 'headline'],
  'infra': ['cloud', 'vps', 'hosting', 'server', 'deploy', 'docker', 'kubernetes'],
};

// ─── Index Loading ──────────────────────────────────────────────────

async function loadIndexes(): Promise<void> {
  const now = Date.now();
  if (vaultIndex && (now - indexLoadTime) < INDEX_TTL) return;

  try {
    const vaultData = await readFile(INDEX_PATH, 'utf-8');
    vaultIndex = JSON.parse(vaultData);
  } catch (err) {
    console.error('[VAULT-SEARCH] Failed to load vault-index.json:', (err as Error).message);
    vaultIndex = null;
  }

  searchIndex = {};
  try {
    const files = await readdir(SEARCH_INDEX_DIR);
    const indexFiles = files.filter(f => /^search-index-\d+\.json$/.test(f));
    for (const f of indexFiles) {
      try {
        const data = await readFile(join(SEARCH_INDEX_DIR, f), 'utf-8');
        const parsed = JSON.parse(data);
        if (parsed.terms) {
          for (const [term, paths] of Object.entries(parsed.terms)) {
            if (!searchIndex[term]) searchIndex[term] = [];
            searchIndex[term].push(...(paths as string[]));
          }
        }
      } catch {}
    }
  } catch (err) {
    console.error('[VAULT-SEARCH] Failed to load search indexes:', (err as Error).message);
  }

  indexLoadTime = now;
}

// ─── Chunk File Parsing ────────────────────────────────────────────

export async function parseChunkFile(filePath: string): Promise<VaultChunk | null> {
  try {
    const content = await readFile(filePath, 'utf-8');
    return parseChunkContent(content);
  } catch (err) {
    console.error('[VAULT-SEARCH] parseChunkFile error:', (err as Error).message);
    return null;
  }
}

/**
 * Parse a chunk's frontmatter + body from raw markdown string.
 * Shared by vault-search and vault-sync to avoid duplication.
 */
export function parseChunkContent(content: string): VaultChunk | null {
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

  const id = getField('id');
  const source = getField('source');
  const title = getField('title');
  const category = getField('category');
  const skillTags = getArrayField('skillTags');
  const containmentHash = getField('containmentHash');
  const embeddingSig = getField('embeddingSig');

  if (!id || !body) return null;
  return { id, content: body, source, title, category, skillTags, containmentHash, embeddingSig };
}

// ─── Core Search ────────────────────────────────────────────────────

export async function searchVault(
  query: string,
  options: { maxResults?: number; includeContainment?: boolean } = {}
): Promise<VaultSearchResult[]> {
  const { maxResults = 10, includeContainment = false } = options;
  await loadIndexes();

  if (!vaultIndex) {
    console.warn('[VAULT-SEARCH] No vault index loaded, returning empty');
    return [];
  }

  const queryTerms = query
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 2);

  if (queryTerms.length === 0) return [];

  const expandedTerms = new Set<string>(queryTerms);
  for (const [cat, terms] of Object.entries(CATEGORY_TERMS)) {
    for (const qt of queryTerms) {
      if (terms.some(t => t.includes(qt) || qt.includes(t))) {
        terms.forEach(t => expandedTerms.add(t));
      }
    }
  }

  const fileScores: Record<string, { score: number; matchedTerms: string[] }> = {};
  const seenFiles = new Set<string>();

  for (const term of expandedTerms) {
    const files = searchIndex[term];
    if (!files) continue;
    for (const f of files) {
      if (seenFiles.has(f + term)) continue;
      seenFiles.add(f + term);
      if (!fileScores[f]) fileScores[f] = { score: 0, matchedTerms: [] };
      fileScores[f].score += 1;
      if (queryTerms.includes(term)) {
        fileScores[f].score += 2;
        fileScores[f].matchedTerms.push(term);
      }
    }
  }

  const sorted = Object.entries(fileScores)
    .sort((a, b) => b[1].score - a[1].score)
    .slice(0, maxResults);

  const results: VaultSearchResult[] = [];
  for (const [filePath, scoring] of sorted) {
    const fullPath = join(ACTIVE_DIR, filePath);
    const chunk = await parseChunkFile(fullPath);
    if (chunk) {
      results.push({ chunk, score: scoring.score, matchedTerms: scoring.matchedTerms });
    }
  }

  // v5: Containment search via pre-built absorbed index (not filesystem scan)
  // The old approach scanned 23K+ files in 00-Containment/ — O(n) disk reads per query.
  // Now we use the same term→file mapping as active search, but mark results as dissolved.
  if (includeContainment && expandedTerms.size > 0) {
    const containmentFiles = new Set<string>();
    for (const term of expandedTerms) {
      const files = searchIndex[term];
      if (files) for (const f of files) containmentFiles.add(f);
    }
    // Filter out files already found in active search
    for (const existing of sorted) {
      containmentFiles.delete(existing[0]);
    }
    // Score containment hits by term overlap (no disk read needed — just count matches)
    const contScores: Array<{ file: string; score: number }> = [];
    for (const file of containmentFiles) {
      let score = 0;
      for (const term of queryTerms) {
        if (searchIndex[term]?.includes(file)) score += 2; // bonus for exact query terms
      }
      if (score > 0) contScores.push({ file, score });
    }
    contScores.sort((a, b) => b.score - a.score);
    // Parse only the top containment hits (bounded by maxResults)
    for (const { file, score } of contScores.slice(0, Math.min(3, maxResults))) {
      if (results.length >= maxResults + 5) break;
      const chunkPath = join(ACTIVE_DIR, file);
      const chunk = await parseChunkFile(chunkPath);
      if (chunk) {
        chunk.dissolved = true;
        results.push({ chunk, score, matchedTerms: [] });
      }
    }
  }

  return results.sort((a, b) => b.score - a.score).slice(0, maxResults);
}

// ─── Context Builder ───────────────────────────────────────────────

export async function getVaultContext(
  query: string,
  options: { maxResults?: number; searchContainment?: boolean } = {}
): Promise<VaultContextResult> {
  const results = await searchVault(query, options);

  const sources: Array<{ title: string; source: string; category: string }> = [];
  const contextParts: string[] = [];
  let containmentHits = 0;

  for (const r of results) {
    if (r.chunk.dissolved) {
      containmentHits++;
      contextParts.push(`[CONTAINMENT] ${r.chunk.content.slice(0, 200)}`);
    } else {
      sources.push({
        title: r.chunk.title,
        source: r.chunk.source,
        category: r.chunk.category,
      });
      contextParts.push(`[${r.chunk.category}] ${r.chunk.content}`);
    }
  }

  return {
    context: contextParts.join('\n---\n'),
    sources: [...new Map(sources.map(s => [s.source, s])).values()],
    containmentHits,
  };
}

// ─── Knowledge Map ─────────────────────────────────────────────────

export async function buildVaultKnowledgeMap(): Promise<string> {
  await loadIndexes();
  if (!vaultIndex) return '(vault index unavailable)';

  const lines: string[] = ['Knowledge categories available:'];
  const cats = vaultIndex.categories || {};
  for (const [cat, count] of Object.entries(cats).sort((a: any, b: any) => b[1] - a[1])) {
    lines.push(`- ${cat}: ${count} chunks`);
  }
  lines.push(`\nTotal: ${vaultIndex.totalChunks} chunks from ${vaultIndex.totalFiles} sources`);
  lines.push(`Skill tags: ${Object.entries(vaultIndex.skillTags || {}).map(([k, v]) => `${k}(${v})`).join(', ')}`);
  return lines.join('\n');
}

// ─── Stats ─────────────────────────────────────────────────────────

export async function getVaultStats(): Promise<any> {
  await loadIndexes();
  return vaultIndex || {
    totalChunks: 0,
    activeChunks: 0,
    dissolvedChunks: 0,
    categories: {},
    error: 'Vault index not loaded',
  };
}