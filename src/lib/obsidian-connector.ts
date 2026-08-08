/**
 * Obsidian Knowledge Connector v1
 *
 * Bridges raw Obsidian knowledge sources into Eli's vault-search engine.
 * Handles:
 *   - Markdown files from knowledge-sources/ (171 files, 6.8MB)
 *   - .docx files from docs/
 *   - Eli OS skill templates from eli-os-delivery/
 *   - Live sync & re-indexing
 *
 * Architecture:
 *   1. Scanner — discovers all ingestible files
 *   2. Parser — extracts text from .md, .docx, .txt
 *   3. Chunker — splits into micro-chunks with metadata
 *   4. Indexer — builds a term→file search index for fast retrieval
 *   5. Retriever — provides RAG-style context for chat queries
 */

import { readFile, readdir, stat, writeFile, mkdir } from 'fs/promises';
import { join, relative, extname } from 'path';
import { existsSync } from 'fs';

// ─── Config ──────────────────────────────────────────────────────

const KNOWLEDGE_DIR = join(process.cwd(), 'data', 'uploads', 'knowledge-sources');
const DOCS_DIR = join(process.cwd(), 'data', 'uploads', 'docs');
const ELOS_TEMPLATES_DIR = join(process.cwd(), 'data', 'eli-os-delivery', 'skill-templates');
const ELOS_NOTES_DIR = join(process.cwd(), 'data', 'eli-os-delivery', 'integration-notes');
const OBSIDIAN_INDEX_DIR = join(process.cwd(), 'data', 'eli-vault', '03-Index');
const OBSIDIAN_INDEX_PATH = join(OBSIDIAN_INDEX_DIR, 'obsidian-live-index.json');

// ─── Types ──────────────────────────────────────────────────────

export interface ObsidianSource {
  id: string;
  title: string;
  filePath: string;
  relativePath: string;
  category: string;
  size: number;
  modified: number;
  sourceType: 'knowledge-source' | 'doc' | 'elos-template' | 'elos-note';
  chunkCount: number;
}

export interface ObsidianChunk {
  id: string;
  content: string;
  title: string;
  source: string;
  category: string;
  sourceType: string;
  chunkIndex: number;
  totalChunks: number;
}

export interface ObsidianSearchResult {
  chunk: ObsidianChunk;
  score: number;
  matchedTerms: string[];
}

export interface ObsidianContextResult {
  context: string;
  sources: Array<{ title: string; source: string; category: string; sourceType: string }>;
  totalAvailable: number;
}

// ─── Category Detection ──────────────────────────────────────────

const FILENAME_CATEGORIES: Record<string, string[]> = {
  'seo': ['seo', 'serp', 'ranking', 'keyword', 'backlink', 'aeo', 'geo', 'parasite', 'on-page', 'technical-seo', 'ahrefs', 'semrush'],
  'ai-agent': ['ai', 'agent', 'llm', 'gpt', 'claude', 'gemini', 'chatgpt', 'prompt', 'eliza'],
  'automation': ['automation', 'n8n', 'zapier', 'activepieces', 'workflow', 'trigger'],
  'web-design': ['design', 'ui', 'ux', 'css', 'frontend', 'component', 'theme', 'template', 'uswds', 'material', 'ant-design', 'tailwind'],
  'google-api': ['google', 'api', 'oauth', 'maps', 'drive', 'cloud', 'workspace'],
  'scraping': ['scrap', 'crawl', 'extract', 'harvest', 'spider', 'browser'],
  'social': ['social', 'instagram', 'twitter', 'facebook', 'linkedin', 'tiktok', 'youtube', 'yt'],
  'content': ['copywriting', 'content', 'writing', 'blog', 'article', 'copy', 'headline', 'claude-repurpose'],
  'saas': ['saas', 'gohighlevel', 'ghl', 'agency', 'funnel', 'publii'],
  'obsidian': ['obsidian', 'vault', 'note', 'markdown', 'frontmatter', 'wikilink', 'appflowy', 'notion'],
  'infra': ['cloud', 'vps', 'hosting', 'server', 'deploy', 'docker', 'kubernetes', 'devops'],
  'eli-core': ['eli', 'skill', 'harness', 'agent-eli', 'identity', 'claw', 'omni', 'openclaw', 'safety'],
  'ecommerce': ['ecommerce', 'shopify', 'woocommerce'],
  'knowledge': ['awesome', 'curated', 'list', 'directory', 'tools', 'resources', 'fmhy', 'repository'],
  'database': ['database', 'sql', 'postgres', 'sqlite', 'supabase'],
  'crm': ['crm', 'sales', 'hubspot', 'pipedrive'],
  'project-mgmt': ['project', 'github', 'git', 'kanban', 'agile'],
  'security': ['security', 'auth', 'password', 'encryption', 'pentest'],
};

function detectCategory(filename: string, content: string): string {
  const lower = filename.toLowerCase();
  const contentLower = content.slice(0, 500).toLowerCase();

  let bestCategory = 'knowledge';
  let bestScore = 0;

  for (const [cat, keywords] of Object.entries(FILENAME_CATEGORIES)) {
    let score = 0;
    for (const kw of keywords) {
      if (lower.includes(kw)) score += 2;
      if (contentLower.includes(kw)) score += 1;
    }
    if (score > bestScore) {
      bestScore = score;
      bestCategory = cat;
    }
  }

  return bestCategory;
}

// ─── Simple hash for IDs ──────────────────────────────────────────

function simpleHash(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return Math.abs(hash).toString(36);
}

// ─── Scanner ─────────────────────────────────────────────────────

async function scanDirectory(
  dir: string,
  sourceType: ObsidianSource['sourceType'],
  extensions: string[]
): Promise<ObsidianSource[]> {
  const sources: ObsidianSource[] = [];

  async function walk(currentDir: string) {
    try {
      const entries = await readdir(currentDir);
      for (const entry of entries) {
        const fullPath = join(currentDir, entry);
        try {
          const s = await stat(fullPath);
          if (s.isDirectory()) {
            await walk(fullPath);
          } else if (extensions.some(ext => entry.toLowerCase().endsWith(ext))) {
            const relPath = relative(dir, fullPath);
            sources.push({
              id: `obs-${simpleHash(relPath)}`,
              title: entry.replace(/\.[^.]+$/, '').replace(/[-_]/g, ' '),
              filePath: fullPath,
              relativePath: relPath,
              category: 'knowledge', // will be updated after parsing
              size: s.size,
              modified: s.mtimeMs,
              sourceType,
              chunkCount: 0,
            });
          }
        } catch {}
      }
    } catch {}
  }

  await walk(dir);
  return sources;
}

export async function scanAllSources(): Promise<ObsidianSource[]> {
  const allSources: ObsidianSource[] = [];

  // Knowledge sources (171 .md files)
  if (existsSync(KNOWLEDGE_DIR)) {
    const ks = await scanDirectory(KNOWLEDGE_DIR, 'knowledge-source', ['.md']);
    allSources.push(...ks);
  }

  // Docs (.md, .txt, .docx)
  if (existsSync(DOCS_DIR)) {
    const docs = await scanDirectory(DOCS_DIR, 'doc', ['.md', '.txt', '.docx']);
    allSources.push(...docs);
  }

  // Eli OS skill templates
  if (existsSync(ELOS_TEMPLATES_DIR)) {
    const templates = await scanDirectory(ELOS_TEMPLATES_DIR, 'elos-template', ['.md']);
    allSources.push(...templates);
  }

  // Eli OS integration notes
  if (existsSync(ELOS_NOTES_DIR)) {
    const notes = await scanDirectory(ELOS_NOTES_DIR, 'elos-note', ['.md']);
    allSources.push(...notes);
  }

  return allSources;
}

// ─── Parser ──────────────────────────────────────────────────────

async function parseMarkdown(content: string): Promise<string> {
  // Strip YAML frontmatter
  let cleaned = content.replace(/^---[\s\S]*?---\n?/, '');
  // Strip Obsidian wikilinks but keep text: [[link|display]] → display, [[link]] → link
  cleaned = cleaned.replace(/\[\[([^|\]]+)\|([^\]]+)\]\]/g, '$2');
  cleaned = cleaned.replace(/\[\[([^\]]+)\]\]/g, '$1');
  // Strip callouts: > [!note] → just keep the content
  cleaned = cleaned.replace(/> \[![a-z]+\]\s*/gi, '> ');
  // Strip tags: #tag
  cleaned = cleaned.replace(/(?:^|\s)#\w+/g, '');
  // Strip embeds: ![[file]]
  cleaned = cleaned.replace(/!\[\[([^\]]+)\]\]/g, '');
  return cleaned.trim();
}

async function parseFile(filePath: string): Promise<string> {
  const ext = extname(filePath).toLowerCase();

  if (ext === '.md' || ext === '.txt') {
    const raw = await readFile(filePath, 'utf-8');
    return parseMarkdown(raw);
  }

  if (ext === '.docx') {
    // For .docx, try to use mammoth if available, otherwise skip
    try {
      // Dynamic import for optional dependency
      // @ts-expect-error — mammoth is an optional dependency
      const mammoth: any = await import('mammoth');
      const buffer = await readFile(filePath);
      const result = await mammoth.extractRawText({ buffer });
      return result.value;
    } catch {
      // mammoth not available — return placeholder
      return `[DOCX file: ${filePath}. Install mammoth package for full parsing.]`;
    }
  }

  // JSON files — extract meaningful text
  if (ext === '.json') {
    try {
      const raw = await readFile(filePath, 'utf-8');
      const parsed = JSON.parse(raw);
      return jsonToText(parsed);
    } catch {
      return '';
    }
  }

  return '';
}

function jsonToText(obj: any, depth = 0): string {
  if (depth > 3 || !obj) return '';
  const parts: string[] = [];
  if (typeof obj === 'string') return obj;
  if (Array.isArray(obj)) {
    for (const item of obj.slice(0, 20)) {
      const t = jsonToText(item, depth + 1);
      if (t) parts.push(t);
    }
  } else if (typeof obj === 'object') {
    for (const [k, v] of Object.entries(obj)) {
      if (['title', 'name', 'description', 'content', 'text', 'body', 'summary'].includes(k)) {
        const t = jsonToText(v, depth + 1);
        if (t) parts.push(t);
      }
    }
  }
  return parts.join('\n');
}

// ─── Chunker ─────────────────────────────────────────────────────

const CHUNK_SIZE = 800;   // chars per chunk
const CHUNK_OVERLAP = 100; // overlap between chunks
const MIN_CHUNK_SIZE = 100;

function chunkText(text: string, source: ObsidianSource): ObsidianChunk[] {
  if (!text || text.length < MIN_CHUNK_SIZE) {
    return [];
  }

  // Auto-detect category from filename + content
  const category = detectCategory(source.title, text);

  const chunks: ObsidianChunk[] = [];
  const sentences = text.split(/(?<=[.!?\n])\s+/);

  let buffer = '';
  let chunkIndex = 0;

  for (const sentence of sentences) {
    buffer += (buffer ? ' ' : '') + sentence;

    if (buffer.length >= CHUNK_SIZE) {
      chunks.push({
        id: `${source.id}-c${chunkIndex}`,
        content: buffer.trim(),
        title: source.title,
        source: source.relativePath,
        category,
        sourceType: source.sourceType,
        chunkIndex,
        totalChunks: 0, // filled later
      });
      chunkIndex++;

      // Keep overlap
      const words = buffer.split(' ');
      const overlapWords = words.slice(Math.max(0, words.length - Math.ceil(CHUNK_OVERLAP / 5)));
      buffer = overlapWords.join(' ');
    }
  }

  // Remaining buffer
  if (buffer.trim().length >= MIN_CHUNK_SIZE) {
    chunks.push({
      id: `${source.id}-c${chunkIndex}`,
      content: buffer.trim(),
      title: source.title,
      source: source.relativePath,
      category,
      sourceType: source.sourceType,
      chunkIndex,
      totalChunks: 0,
    });
  }

  // Set total chunks
  const total = chunks.length;
  for (const c of chunks) c.totalChunks = total;

  return chunks;
}

// ─── Indexer ─────────────────────────────────────────────────────

interface ObsidianLiveIndex {
  version: number;
  lastBuilt: number;
  totalSources: number;
  totalChunks: number;
  sources: Record<string, { title: string; category: string; chunkCount: number; sourceType: string; modified: number }>;
  terms: Record<string, string[]>; // term → [chunkId, ...]
  categories: Record<string, number>;
}

let liveIndex: ObsidianLiveIndex | null = null;
let indexCacheTime = 0;
const INDEX_CACHE_TTL = 120_000; // 2 min

/**
 * Build or rebuild the Obsidian live search index.
 * Scans all sources, parses, chunks, and creates term→chunk mappings.
 */
export async function buildObsidianIndex(force = false): Promise<ObsidianLiveIndex> {
  const now = Date.now();
  if (!force && liveIndex && (now - indexCacheTime) < INDEX_CACHE_TTL) {
    return liveIndex;
  }

  // Try loading from disk first (unless forced)
  if (!force && existsSync(OBSIDIAN_INDEX_PATH)) {
    try {
      const cached = JSON.parse(await readFile(OBSIDIAN_INDEX_PATH, 'utf-8'));
      if (cached && cached.terms && Object.keys(cached.terms).length > 0) {
        liveIndex = cached as ObsidianLiveIndex;
        indexCacheTime = now;
        return liveIndex;
      }
    } catch {}
  }

  console.log('[OBSIDIAN-CONNECTOR] Building live index from scratch...');
  const startTime = Date.now();

  const sources = await scanAllSources();
  const index: ObsidianLiveIndex = {
    version: 1,
    lastBuilt: now,
    totalSources: 0,
    totalChunks: 0,
    sources: {},
    terms: {},
    categories: {},
  };

  for (const source of sources) {
    try {
      const text = await parseFile(source.filePath);
      if (!text || text.length < MIN_CHUNK_SIZE) continue;

      const category = detectCategory(source.title, text);
      source.category = category;

      const chunks = chunkText(text, source);
      if (chunks.length === 0) continue;

      source.chunkCount = chunks.length;
      index.totalSources++;
      index.totalChunks += chunks.length;
      index.categories[category] = (index.categories[category] || 0) + chunks.length;

      // Store source metadata
      index.sources[source.id] = {
        title: source.title,
        category,
        chunkCount: chunks.length,
        sourceType: source.sourceType,
        modified: source.modified,
      };

      // Index each chunk's terms
      for (const chunk of chunks) {
        const terms = extractTerms(chunk.content);
        for (const term of terms) {
          if (!index.terms[term]) index.terms[term] = [];
          // Ensure it's always an array (guard against type corruption)
          if (Array.isArray(index.terms[term])) {
            (index.terms[term] as string[]).push(chunk.id);
          } else {
            index.terms[term] = [chunk.id];
          }
        }
      }
    } catch (err: any) {
      console.warn(`[OBSIDIAN-CONNECTOR] Failed to index ${source.relativePath}: ${err.message}`);
    }
  }

  // Deduplicate term mappings
  for (const term of Object.keys(index.terms)) {
    index.terms[term] = [...new Set(index.terms[term])];
  }

  const elapsed = Date.now() - startTime;
  console.log(`[OBSIDIAN-CONNECTOR] Index built: ${index.totalSources} sources, ${index.totalChunks} chunks, ${Object.keys(index.terms).length} terms in ${elapsed}ms`);

  // Save to disk
  try {
    await writeFile(OBSIDIAN_INDEX_PATH, JSON.stringify(index), 'utf-8');
  } catch (err: any) {
    console.warn(`[OBSIDIAN-CONNECTOR] Failed to save index: ${err.message}`);
  }

  liveIndex = index;
  indexCacheTime = now;
  return index;
}

// ─── Term Extraction ─────────────────────────────────────────────

const STOP_WORDS = new Set([
  'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
  'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
  'and', 'but', 'or', 'nor', 'for', 'yet', 'so', 'both', 'either',
  'neither', 'not', 'only', 'own', 'same', 'than', 'too', 'very',
  'just', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'from',
  'with', 'about', 'against', 'between', 'through', 'during', 'before',
  'after', 'above', 'below', 'to', 'up', 'down', 'in', 'out', 'on',
  'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
  'there', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
  'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not',
  'also', 'into', 'which', 'their', 'this', 'that', 'these', 'those',
  'what', 'who', 'whom', 'its', 'your', 'his', 'her', 'our', 'my',
]);

function extractTerms(text: string): string[] {
  const words = text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2 && !STOP_WORDS.has(w));

  // Also extract bigrams for better matching
  const terms: string[] = [];
  for (const w of words) terms.push(w);
  for (let i = 0; i < words.length - 1; i++) {
    terms.push(`${words[i]} ${words[i + 1]}`);
  }
  return [...new Set(terms)];
}

// ─── Retriever (RAG-style) ───────────────────────────────────────

// In-memory chunk cache for fast retrieval
let chunkCache: Map<string, ObsidianChunk> = new Map();

/**
 * Search Obsidian knowledge sources for relevant context.
 * Returns ranked chunks matching the query.
 */
export async function searchObsidian(
  query: string,
  options: { maxResults?: number } = {}
): Promise<ObsidianSearchResult[]> {
  const { maxResults = 8 } = options;
  const index = await buildObsidianIndex();

  const queryTerms = extractTerms(query);
  if (queryTerms.length === 0) return [];

  // Score chunks by term overlap
  const chunkScores: Record<string, { score: number; matchedTerms: string[] }> = {};

  for (const term of queryTerms) {
    let chunkIds = index.terms[term];
    if (!chunkIds) continue;
    // Ensure array type (disk-loaded index may have string values)
    if (!Array.isArray(chunkIds)) {
      chunkIds = [String(chunkIds)];
    }
    for (const chunkId of chunkIds) {
      if (!chunkScores[chunkId]) chunkScores[chunkId] = { score: 0, matchedTerms: [] };
      chunkScores[chunkId].score += 1;
      if (queryTerms.includes(term)) {
        chunkScores[chunkId].score += 2;
        chunkScores[chunkId].matchedTerms.push(term);
      }
    }
  }

  // Sort by score, take top N
  const sorted = Object.entries(chunkScores)
    .sort((a, b) => b[1].score - a[1].score)
    .slice(0, maxResults);

  // Resolve chunk IDs to full chunks
  const results: ObsidianSearchResult[] = [];
  for (const [chunkId, scoring] of sorted) {
    const chunk = await resolveChunk(chunkId);
    if (chunk) {
      results.push({ chunk, score: scoring.score, matchedTerms: scoring.matchedTerms });
    }
  }

  return results;
}

/**
 * Get Obsidian context for chat — returns formatted context string + sources.
 */
export async function getObsidianContext(
  query: string,
  options: { maxResults?: number } = {}
): Promise<ObsidianContextResult> {
  const results = await searchObsidian(query, options);
  const index = await buildObsidianIndex();

  const sources: ObsidianContextResult['sources'] = [];
  const contextParts: string[] = [];
  const seenSources = new Set<string>();

  for (const r of results) {
    if (!seenSources.has(r.chunk.source)) {
      seenSources.add(r.chunk.source);
      sources.push({
        title: r.chunk.title,
        source: r.chunk.source,
        category: r.chunk.category,
        sourceType: r.chunk.sourceType,
      });
    }
    contextParts.push(`[OBSIDIAN:${r.chunk.sourceType}] ${r.chunk.content}`);
  }

  return {
    context: contextParts.join('\n---\n'),
    sources,
    totalAvailable: index.totalChunks,
  };
}

/**
 * Resolve a chunk ID to its full content by re-parsing the source file.
 * Uses in-memory cache to avoid repeated file reads.
 */
async function resolveChunk(chunkId: string): Promise<ObsidianChunk | null> {
  // Check cache
  if (chunkCache.has(chunkId)) return chunkCache.get(chunkId)!;

  // Parse the chunk ID: obs-{hash}-c{index}
  const match = chunkId.match(/^(obs-[a-z0-9]+)-c(\d+)$/);
  if (!match) return null;

  const sourceId = match[1];
  const chunkIndex = parseInt(match[2], 10);

  // Find the source
  const sources = await scanAllSources();
  const source = sources.find(s => s.id === sourceId);
  if (!source) return null;

  try {
    const text = await parseFile(source.filePath);
    if (!text) return null;

    const chunks = chunkText(text, source);
    const chunk = chunks[chunkIndex];
    if (!chunk) return null;

    // Cache it
    if (chunkCache.size < 500) {
      chunkCache.set(chunkId, chunk);
    }

    return chunk;
  } catch {
    return null;
  }
}

// ─── Diagnostics & Stats ─────────────────────────────────────────

export async function getObsidianStats(): Promise<{
  totalSources: number;
  totalChunks: number;
  categories: Record<string, number>;
  sourceTypes: Record<string, number>;
  indexAge: number;
}> {
  const index = await buildObsidianIndex();
  const sourceTypes: Record<string, number> = {};

  for (const src of Object.values(index.sources)) {
    sourceTypes[src.sourceType] = (sourceTypes[src.sourceType] || 0) + 1;
  }

  return {
    totalSources: index.totalSources,
    totalChunks: index.totalChunks,
    categories: index.categories,
    sourceTypes,
    indexAge: Date.now() - index.lastBuilt,
  };
}

export async function getObsidianSources(): Promise<ObsidianSource[]> {
  const sources = await scanAllSources();
  const index = await buildObsidianIndex();

  // Enrich with index metadata
  for (const source of sources) {
    const meta = index.sources[source.id];
    if (meta) {
      source.category = meta.category;
      source.chunkCount = meta.chunkCount;
    }
  }

  return sources;
}

/**
 * Trigger a full re-index (clears cache, rebuilds from scratch).
 */
export async function reindexObsidian(): Promise<ObsidianLiveIndex> {
  liveIndex = null;
  chunkCache.clear();
  indexCacheTime = 0;
  return buildObsidianIndex(true);
}
