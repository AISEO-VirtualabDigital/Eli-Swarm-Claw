/**
 * Obsidian Micro-Chunk Engine with Skill Containment
 * 
 * Architecture:
 * - Dissolves ALL knowledge into tiny semantic chunks (~200-500 chars)
 * - Each chunk gets: hash, embedding signature, skill tags, containment metadata
 * - Skill Containment: chunks are NEVER deleted, only marked as "dissolved"
 *   → they persist in a hidden `.containment/` layer even if removed from active vault
 * - Air LLM: lightweight Gemini-powered retrieval with semantic scoring
 * 
 * Storage format: Obsidian-flavored markdown in a structured vault
 * - 00-Containment/ — deletion-proof skill memory (hidden layer)
 * - 01-Active/     — currently active knowledge chunks
 * - 02-Skills/     — extracted patterns, processes, capabilities
 * - 03-Index/      — JSON index files for fast retrieval
 */

import { readdir, readFile, writeFile, mkdir, stat, copyFile, rm, access } from 'fs/promises';
import { join, basename, dirname, relative } from 'path';
import { createHash } from 'crypto';

// ─── Types ──────────────────────────────────────────────────────────

export interface MicroChunk {
  id: string;              // sha256 hash of content
  content: string;         // the actual text (200-500 chars)
  meta: ChunkMeta;
}

export interface ChunkMeta {
  source: string;          // original filename
  sourcePath: string;      // original full path
  title: string;           // extracted title
  category: string;        // topic category
  skillTags: string[];     // extracted skill/pattern tags
  containmentHash: string; // hash for containment tracking
  createdAt: number;       // timestamp
  dissolved: boolean;      // marked as dissolved (still in containment)
  links: string[];         // [[wikilinks]] to related chunks
  embeddingSig: string;    // lightweight semantic signature (not full embedding)
}

export interface SkillRecord {
  id: string;
  name: string;
  pattern: string;         // the pattern/process description
  chunks: string[];        // chunk IDs that form this skill
  category: string;
 strength: number;        // 0-1 how reinforced this skill is
  lastUsed: number;
  containmentProof: string; // merkle-like proof of existence
}

export interface ContainmentIndex {
  totalChunks: number;
  activeChunks: number;
  dissolvedChunks: number;
  skills: number;
  categories: Record<string, number>;
  lastIngestion: number;
  vaultPath: string;
}

// ─── Config ──────────────────────────────────────────────────────────

const CHUNK_TARGET_SIZE = 350;     // target chars per chunk
const CHUNK_MIN_SIZE = 100;        // minimum chars
const CHUNK_MAX_SIZE = 600;        // hard max
const OVERLAP_SIZE = 50;           // overlap between chunks for context preservation
const CONTAINMENT_DIR = '.containment';

const SKILL_PATTERNS: Record<string, RegExp[]> = {
  'process': [/step \d/i, /first[,\.]/i, /then[,\.]/i, /next[,\.]/i, /finally[,\.]/i, /workflow/i, /pipeline/i, /\d+\.\s/],
  'pattern': [/pattern/i, /whenever/i, /always/i, /never/i, /rule/i, /principle/i, /framework/i],
  'capability': [/can\s/i, /able to/i, /supports/i, /integrates/i, /provides/i, /enables/i, /allows?\s/i],
  'tool': [/tool/i, /api\b/i, /library/i, /plugin/i, /extension/i, /sdk\b/i, /cli\b/i, /package\b/i],
  'strategy': [/strategy/i, /approach/i, /tactic/i, /methodology/i, /playbook/i, /framework/i],
  'metric': [/\d+%/, /\$\d+/, /\d+x\b/, /score/i, /rate/i, /volume/i, /traffic/i, /conversion/i],
  'code': [/function\s/, /const\s/, /import\s/, /class\s/, /async\s/, /return\s/, /=>\s/, /```/],
  'warning': [/warning/i, /caution/i, /avoid/i, /don'?t\s/i, /risk/i, /critical/i, /important/i],
};

// ─── Hashing ──────────────────────────────────────────────────────────

function contentHash(content: string): string {
  return createHash('sha256').update(content.trim()).digest('hex').slice(0, 16);
}

function containmentHash(content: string, source: string, timestamp: number): string {
  return createHash('sha256')
    .update(`${content}|${source}|${timestamp}`)
    .digest('hex').slice(0, 20);
}

// ─── Semantic Signature (lightweight, no external API) ──────────────

function buildSemanticSig(content: string): string {
  const words = content.toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 3);
  
  // Build a bloom-filter-like signature from word trigrams
  const trigrams = new Set<string>();
  for (let i = 0; i < words.length - 2; i++) {
    trigrams.add(`${words[i]}:${words[i+1]}:${words[i+2]}`);
  }
  
  // Create a compact signature string (first 8 trigrams sorted)
  return Array.from(trigrams).slice(0, 12).sort().join('|');
}

// ─── Chunking ──────────────────────────────────────────────────────

function dissolveIntoChunks(content: string, source: string, sourcePath: string): MicroChunk[] {
  const chunks: MicroChunk[] = [];
  const title = extractTitle(content, source);
  const category = extractCategory(content, source);
  const now = Date.now();
  
  // Strip frontmatter
  const clean = content.replace(/^---[\s\S]*?---\n?/, '');
  
  if (clean.length <= CHUNK_MAX_SIZE) {
    // Small file → single chunk
    const sig = buildSemanticSig(clean);
    const ch = containmentHash(clean, source, now);
    chunks.push({
      id: contentHash(clean),
      content: clean,
      meta: {
        source,
        sourcePath,
        title,
        category,
        skillTags: extractSkillTags(clean),
        containmentHash: ch,
        createdAt: now,
        dissolved: false,
        links: [],
        embeddingSig: sig,
      },
    });
    return chunks;
  }
  
  // Large file → split by paragraphs/sections with overlap
  const sections = splitIntoSections(clean);
  let buffer = '';
  
  for (const section of sections) {
    buffer += (buffer ? '\n' : '') + section;
    
    while (buffer.length >= CHUNK_TARGET_SIZE) {
      // Find a good split point near target size
      let splitAt = findSplitPoint(buffer, CHUNK_TARGET_SIZE);
      
      const chunkText = buffer.slice(0, splitAt).trim();
      if (chunkText.length >= CHUNK_MIN_SIZE) {
        const sig = buildSemanticSig(chunkText);
        const ch = containmentHash(chunkText, source, now);
        chunks.push({
          id: contentHash(chunkText + chunks.length.toString()), // unique per position
          content: chunkText,
          meta: {
            source,
            sourcePath,
            title,
            category,
            skillTags: extractSkillTags(chunkText),
            containmentHash: ch,
            createdAt: now,
            dissolved: false,
            links: [],
            embeddingSig: sig,
          },
        });
      }
      
      // Keep overlap for context
      buffer = buffer.slice(Math.max(0, splitAt - OVERLAP_SIZE));
    }
  }
  
  // Don't forget remaining buffer
  if (buffer.trim().length >= CHUNK_MIN_SIZE) {
    const chunkText = buffer.trim();
    const sig = buildSemanticSig(chunkText);
    const ch = containmentHash(chunkText, source, now);
    chunks.push({
      id: contentHash(chunkText + chunks.length.toString()),
      content: chunkText,
      meta: {
        source,
        sourcePath,
        title,
        category,
        skillTags: extractSkillTags(chunkText),
        containmentHash: ch,
        createdAt: now,
        dissolved: false,
        links: [],
        embeddingSig: sig,
      },
    });
  }
  
  // Wire up wikilinks between consecutive chunks from same source
  for (let i = 0; i < chunks.length - 1; i++) {
    chunks[i].meta.links.push(chunks[i + 1].id);
    chunks[i + 1].meta.links.push(chunks[i].id);
  }
  
  return chunks;
}

function splitIntoSections(content: string): string[] {
  // Split by headings, double newlines, or code blocks
  const parts: string[] = [];
  let current = '';
  const lines = content.split('\n');
  
  for (const line of lines) {
    if (line.match(/^#{1,4}\s/) && current.trim()) {
      parts.push(current.trim());
      current = line + '\n';
    } else if (line.trim() === '' && current.trim().length > 100) {
      parts.push(current.trim());
      current = '';
    } else {
      current += line + '\n';
    }
  }
  if (current.trim()) parts.push(current.trim());
  
  return parts.length > 0 ? parts : [content];
}

function findSplitPoint(text: string, target: number): number {
  // Try to split at sentence or paragraph boundary near target
  const searchStart = Math.max(0, target - 80);
  const searchEnd = Math.min(text.length, target + 80);
  const window = text.slice(searchStart, searchEnd);
  
  // Priority 1: double newline (paragraph)
  let idx = window.lastIndexOf('\n\n');
  if (idx > 20) return searchStart + idx + 2;
  
  // Priority 2: sentence end
  idx = window.lastIndexOf('. ');
  if (idx > 20) return searchStart + idx + 2;
  idx = window.lastIndexOf('! ');
  if (idx > 20) return searchStart + idx + 2;
  idx = window.lastIndexOf('? ');
  if (idx > 20) return searchStart + idx + 2;
  
  // Priority 3: newline
  idx = window.lastIndexOf('\n');
  if (idx > 10) return searchStart + idx + 1;
  
  // Priority 4: space near target
  idx = window.lastIndexOf(' ', target - searchStart);
  if (idx > 10) return searchStart + idx + 1;
  
  return Math.min(target, text.length);
}

// ─── Skill Tag Extraction ──────────────────────────────────────────

function extractSkillTags(content: string): string[] {
  const tags: string[] = [];
  const lower = content.toLowerCase();
  
  for (const [tag, patterns] of Object.entries(SKILL_PATTERNS)) {
    for (const pattern of patterns) {
      if (pattern.test(lower)) {
        if (!tags.includes(tag)) tags.push(tag);
        break;
      }
    }
  }
  
  return tags;
}

// ─── Title & Category (reuse from knowledge-search logic) ──────────

function extractTitle(content: string, filename: string): string {
  const fmMatch = content.match(/^---[\s\S]*?title:\s*(.+?)[\r\n]/);
  if (fmMatch) return fmMatch[1].trim().replace(/^['"]|['"]$/g, '');
  const h1Match = content.match(/^#\s+(.+)$/m);
  if (h1Match) return h1Match[1].trim();
  return filename.replace(/[-_]/g, ' ').replace(/\.(md|txt|json)$/i, '').replace(/\b\w/g, c => c.toUpperCase());
}

function extractCategory(content: string, filename: string): string {
  const fmMatch = content.match(/^---[\s\S]*?Category:\s*(.+?)[\r\n]/);
  if (fmMatch) return fmMatch[1].trim().toLowerCase();
  const lower = filename.toLowerCase();
  if (lower.includes('seo') || lower.includes('backlink') || lower.includes('keyword') || lower.includes('indexing')) return 'seo';
  if (lower.includes('ai') || lower.includes('agent') || lower.includes('llm') || lower.includes('claude') || lower.includes('gemini')) return 'ai-agent';
  if (lower.includes('design') || lower.includes('ui') || lower.includes('ux') || lower.includes('frontend')) return 'web-design';
  if (lower.includes('saas') || lower.includes('ghl') || lower.includes('agency')) return 'saas';
  if (lower.includes('google') || lower.includes('api') || lower.includes('oauth')) return 'google-api';
  if (lower.includes('obsidian') || lower.includes('vault') || lower.includes('note')) return 'obsidian';
  if (lower.includes('eli') || lower.includes('skill') || lower.includes('harness')) return 'eli-core';
  if (lower.includes('automation') || lower.includes('workflow') || lower.includes('n8n')) return 'automation';
  if (lower.includes('cloud') || lower.includes('vps') || lower.includes('hosting') || lower.includes('server')) return 'infra';
  if (lower.includes('social') || lower.includes('instagram') || lower.includes('youtube')) return 'social';
  if (lower.includes('copy') || lower.includes('content') || lower.includes('writing')) return 'content';
  if (lower.includes('shopify') || lower.includes('ecommerce')) return 'ecommerce';
  return 'knowledge';
}

// ─── Vault Manager ──────────────────────────────────────────────────

export class ObsidianVault {
  private vaultPath: string;
  private activeDir: string;
  private containmentDir: string;
  private skillsDir: string;
  private indexDir: string;
  private chunkCache: Map<string, MicroChunk> = new Map();
  private skillCache: Map<string, SkillRecord> = new Map();
  private loaded = false;

  constructor(vaultPath: string) {
    this.vaultPath = vaultPath;
    this.activeDir = join(vaultPath, '01-Active');
    this.containmentDir = join(vaultPath, '00-Containment');
    this.skillsDir = join(vaultPath, '02-Skills');
    this.indexDir = join(vaultPath, '03-Index');
  }

  async init(): Promise<void> {
    // Create vault structure
    for (const dir of [this.activeDir, this.containmentDir, this.skillsDir, this.indexDir]) {
      await mkdir(dir, { recursive: true });
    }
    
    // Create vault metadata
    const metaPath = join(this.vaultPath, '.vault-meta.json');
    try {
      await access(metaPath);
    } catch {
      await writeFile(metaPath, JSON.stringify({
        name: 'Eli Skill Vault',
        version: '2.0',
        engine: 'micro-chunk-containment',
        created: Date.now(),
        lastUpdated: Date.now(),
      }, null, 2));
    }
    
    this.loaded = true;
  }

  // ─── Ingest: dissolve files into micro-chunks ──────────────────

  async ingestDirectory(sourceDir: string, depth = 0, maxDepth = 3): Promise<number> {
    if (!this.loaded) await this.init();
    
    let totalChunks = 0;
    const entries = await readdir(sourceDir, { withFileTypes: true });
    
    for (const entry of entries) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;
      const fullPath = join(sourceDir, entry.name);
      
      if (entry.isDirectory() && depth < maxDepth) {
        totalChunks += await this.ingestDirectory(fullPath, depth + 1, maxDepth);
      } else if (entry.isFile()) {
        const ext = entry.name.split('.').pop()?.toLowerCase() ?? '';
        if (!['.md', '.txt', '.json'].includes(ext)) continue;
        
        try {
          const content = await readFile(fullPath, 'utf-8');
          if (!content || content.length < 20) continue;
          
          let cleanContent = content;
          if (ext === 'json') {
            try {
              const parsed = JSON.parse(content);
              if (parsed.data?.html) {
                cleanContent = parsed.data.html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
              } else {
                cleanContent = JSON.stringify(parsed, null, 2);
              }
            } catch { cleanContent = content; }
            if (cleanContent.length > 50000) cleanContent = cleanContent.slice(0, 50000);
          }
          
          const chunks = dissolveIntoChunks(cleanContent, entry.name, fullPath);
          totalChunks += chunks.length;
          
          // Store chunks
          for (const chunk of chunks) {
            await this.storeChunk(chunk);
          }
          
          // Extract and store skills
          await this.extractAndStoreSkills(chunks);
        } catch (err) {
          console.error(`Failed to ingest ${entry.name}:`, err);
        }
      }
    }
    
    // Update index
    await this.rebuildIndex();
    return totalChunks;
  }

  // ─── Store chunk to vault ─────────────────────────────────────

  private async storeChunk(chunk: MicroChunk): Promise<void> {
    this.chunkCache.set(chunk.id, chunk);
    
    // Active chunk stored as individual .md file
    const chunkPath = join(this.activeDir, chunk.meta.category, `${chunk.id}.md`);
    await mkdir(dirname(chunkPath), { recursive: true });
    
    const frontmatter = [
      '---',
      `id: ${chunk.id}`,
      `source: "${chunk.meta.source}"`,
      `category: ${chunk.meta.category}`,
      `skillTags: [${chunk.meta.skillTags.map(t => `"${t}"`).join(', ')}]`,
      `containmentHash: ${chunk.meta.containmentHash}`,
      `createdAt: ${chunk.meta.createdAt}`,
      `dissolved: false`,
      `links: [${chunk.meta.links.map(l => `"${l}"`).join(', ')}]`,
      `embeddingSig: "${chunk.meta.embeddingSig.replace(/"/g, '\\"')}"`,
      '---',
      '',
    ].join('\n');
    
    await writeFile(chunkPath, frontmatter + chunk.content);
    
    // Containment copy (deletion-proof) — stored compressed as hash-named file
    const containmentPath = join(this.containmentDir, `${chunk.meta.containmentHash}.md`);
    await writeFile(containmentPath, frontmatter + chunk.content);
  }

  // ─── Skill Extraction ─────────────────────────────────────────

  private async extractAndStoreSkills(chunks: MicroChunk[]): Promise<void> {
    // Group chunks by skill tags to form skill records
    const tagGroups: Record<string, MicroChunk[]> = {};
    
    for (const chunk of chunks) {
      for (const tag of chunk.meta.skillTags) {
        if (!tagGroups[tag]) tagGroups[tag] = [];
        tagGroups[tag].push(chunk);
      }
    }
    
    for (const [tagName, tagChunks] of Object.entries(tagGroups)) {
      if (tagChunks.length < 2) continue; // Need at least 2 chunks to form a skill
      
      // Merge content from top chunks to form skill pattern
      const mergedContent = tagChunks
        .slice(0, 5)
        .map(c => c.content.slice(0, 200))
        .join('\n---\n');
      
      const skillId = contentHash(`${tagName}:${tagChunks[0].meta.source}`);
      const now = Date.now();
      
      const skill: SkillRecord = {
        id: skillId,
        name: `${tagName}: ${tagChunks[0].meta.title}`,
        pattern: mergedContent.slice(0, 1000),
        chunks: tagChunks.map(c => c.id),
        category: tagChunks[0].meta.category,
        strength: Math.min(1, tagChunks.length / 10),
        lastUsed: now,
        containmentProof: containmentHash(mergedContent, skillId, now),
      };
      
      this.skillCache.set(skillId, skill);
      
      // Write skill file
      const skillPath = join(this.skillsDir, tagName, `${skillId}.md`);
      await mkdir(dirname(skillPath), { recursive: true });
      
      const skillContent = [
        '---',
        `id: ${skill.id}`,
        `name: "${skill.name}"`,
        `category: ${skill.category}`,
        `strength: ${skill.strength}`,
        `chunkCount: ${skill.chunks.length}`,
        `containmentProof: ${skill.containmentProof}`,
        '---',
        '',
        `# ${skill.name}`,
        '',
        `> Skill Type: ${tagName}`,
        `> Source Chunks: ${skill.chunks.length}`,
        `> Containment Proof: ${skill.containmentProof}`,
        '',
        '## Pattern',
        '',
        skill.pattern,
        '',
        '## Linked Chunks',
        '',
        ...skill.chunks.map(c => `- [[${c}]]`),
        '',
      ].join('\n');
      
      await writeFile(skillPath, skillContent);
    }
  }

  // ─── Dissolve (soft delete — moves to containment only) ───────

  async dissolveChunk(chunkId: string): Promise<void> {
    const chunk = this.chunkCache.get(chunkId);
    if (!chunk) return;
    
    // Mark as dissolved in active store
    chunk.meta.dissolved = true;
    
    // Remove from active directory
    const activePath = join(this.activeDir, chunk.meta.category, `${chunkId}.md`);
    try { await rm(activePath); } catch {}
    
    // Containment copy ALREADY exists — it's never deleted
    // Just update the index to track it as dissolved
    await this.rebuildIndex();
  }

  // ─── Search (Air LLM-ready retrieval) ────────────────────────

  async search(
    query: string,
    options?: { maxResults?: number; categories?: string[]; skillTags?: string[] }
  ): Promise<Array<{ chunk: MicroChunk; score: number; matchedTerms: string[] }>> {
    const { maxResults = 8, categories, skillTags } = options ?? {};
    
    // Ensure all chunks are loaded
    if (this.chunkCache.size === 0) await this.loadAllChunks();
    
    const queryLower = query.toLowerCase();
    const queryTerms = queryLower.replace(/[^a-z0-9\s]/g, ' ').split(/\s+/).filter(w => w.length > 2);
    const querySig = buildSemanticSig(query);
    const queryTrigrams = new Set(querySig.split('|'));
    
    const results: Array<{ chunk: MicroChunk; score: number; matchedTerms: string[] }> = [];
    
    for (const [, chunk] of this.chunkCache) {
      if (chunk.meta.dissolved) continue; // skip dissolved unless explicitly searching containment
      if (categories && categories.length > 0 && !categories.includes(chunk.meta.category)) continue;
      if (skillTags && skillTags.length > 0 && !skillTags.some(t => chunk.meta.skillTags.includes(t))) continue;
      
      const contentLower = chunk.content.toLowerCase();
      let score = 0;
      const matchedTerms: string[] = [];
      
      // Term matching (similar to old engine but on micro-chunks = more precise)
      for (const term of queryTerms) {
        const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$');
        const count = (contentLower.match(new RegExp(escaped, 'g')) || []).length;
        if (count > 0) {
          score += count * 3; // micro-chunks = higher density = lower multiplier
          if (!matchedTerms.includes(term)) matchedTerms.push(term);
        }
      }
      
      // Semantic signature overlap (trigram similarity)
      const chunkTrigrams = new Set(chunk.meta.embeddingSig.split('|'));
      let sigOverlap = 0;
      for (const tri of queryTrigrams) {
        if (chunkTrigrams.has(tri)) sigOverlap++;
      }
      if (queryTrigrams.size > 0) {
        score += (sigOverlap / queryTrigrams.size) * 10;
      }
      
      // Skill tag boost
      if (skillTags) {
        for (const tag of skillTags) {
          if (chunk.meta.skillTags.includes(tag)) score += 5;
        }
      }
      
      if (score > 0.5) {
        results.push({ chunk, score, matchedTerms });
      }
    }
    
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, maxResults);
  }

  // ─── Containment Search (searches dissolved chunks too) ───────

  async searchContainment(
    query: string,
    options?: { maxResults?: number }
  ): Promise<Array<{ chunk: MicroChunk; score: number; dissolved: boolean }>> {
    // Load ALL chunks including dissolved from containment dir
    if (this.chunkCache.size === 0) await this.loadAllChunks(true);
    
    const { maxResults = 8 } = options ?? {};
    const queryLower = query.toLowerCase();
    const queryTerms = queryLower.replace(/[^a-z0-9\s]/g, ' ').split(/\s+/).filter(w => w.length > 2);
    
    const results: Array<{ chunk: MicroChunk; score: number; dissolved: boolean }> = [];
    
    for (const [, chunk] of this.chunkCache) {
      const contentLower = chunk.content.toLowerCase();
      let score = 0;
      
      for (const term of queryTerms) {
        if (contentLower.includes(term)) score += 2;
      }
      
      if (score > 0) {
        results.push({ chunk, score, dissolved: chunk.meta.dissolved });
      }
    }
    
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, maxResults);
  }

  // ─── Get Skills ───────────────────────────────────────────────

  async getSkills(category?: string): Promise<SkillRecord[]> {
    if (this.skillCache.size === 0) await this.loadAllSkills();
    const skills = Array.from(this.skillCache.values());
    if (category) return skills.filter(s => s.category === category);
    return skills.sort((a, b) => b.strength - a.strength);
  }

  // ─── Build Context for LLM (Air LLM interface) ───────────────

  async buildAirContext(query: string): Promise<{ context: string; sources: Array<{ title: string; source: string; category: string }> }> {
    const results = await this.search(query, { maxResults: 10 });
    
    if (results.length === 0) {
      return { context: '', sources: [] };
    }
    
    // Build compact context from micro-chunks
    const sources: Array<{ title: string; source: string; category: string }> = [];
    const seenSources = new Set<string>();
    
    const contextParts = results.map((r, i) => {
      const { chunk } = r;
      if (!seenSources.has(chunk.meta.source)) {
        seenSources.add(chunk.meta.source);
        sources.push({
          title: chunk.meta.title,
          source: chunk.meta.source,
          category: chunk.meta.category,
        });
      }
      
      const tags = chunk.meta.skillTags.length > 0 
        ? ` [${chunk.meta.skillTags.join(', ')}]` 
        : '';
      return `[${chunk.meta.category}${tags}] ${chunk.content.slice(0, 400)}`;
    });
    
    const skillContext = await this.buildSkillContext(query);
    
    const context = `
---
MICRO-CHUNK RETRIEVAL (${results.length} chunks from ${seenSources.size} sources):
${contextParts.join('\n\n')}
${skillContext ? '\n---\nACTIVE SKILLS:\n' + skillContext : ''}
---
Use the above micro-chunk data and skill patterns to inform your response.`;

    return { context, sources };
  }

  private async buildSkillContext(query: string): Promise<string> {
    const skills = await this.getSkills();
    const queryLower = query.toLowerCase();
    
    // Find skills relevant to query
    const relevant = skills.filter(s => {
      const nameLower = s.name.toLowerCase();
      const patternLower = s.pattern.toLowerCase();
      return queryLower.split(/\s+/).some(term => 
        term.length > 3 && (nameLower.includes(term) || patternLower.includes(term))
      );
    }).slice(0, 3);
    
    if (relevant.length === 0) return '';
    return relevant.map(s => 
      `**${s.name}** (strength: ${(s.strength * 100).toFixed(0)}%)\n${s.pattern.slice(0, 300)}`
    ).join('\n\n');
  }

  // ─── Index Management ─────────────────────────────────────────

  async rebuildIndex(): Promise<ContainmentIndex> {
    let activeChunks = 0;
    let dissolvedChunks = 0;
    const categories: Record<string, number> = {};
    
    for (const [, chunk] of this.chunkCache) {
      if (chunk.meta.dissolved) {
        dissolvedChunks++;
      } else {
        activeChunks++;
      }
      categories[chunk.meta.category] = (categories[chunk.meta.category] || 0) + 1;
    }
    
    const index: ContainmentIndex = {
      totalChunks: this.chunkCache.size,
      activeChunks,
      dissolvedChunks,
      skills: this.skillCache.size,
      categories,
      lastIngestion: Date.now(),
      vaultPath: this.vaultPath,
    };
    
    await writeFile(
      join(this.indexDir, 'vault-index.json'),
      JSON.stringify(index, null, 2)
    );
    
    return index;
  }

  // ─── Load from disk ───────────────────────────────────────────

  async loadAllChunks(includeDissolved = false): Promise<void> {
    // Load from active directory
    await this.loadChunksFromDir(this.activeDir, includeDissolved);
    
    // If includeDissolved, also load from containment
    if (includeDissolved) {
      await this.loadChunksFromDir(this.containmentDir, true);
    }
  }

  private async loadChunksFromDir(dir: string, markAsDissolved: boolean): Promise<void> {
    try {
      await access(dir);
    } catch { return; }
    
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        await this.loadChunksFromDir(fullPath, markAsDissolved);
      } else if (entry.name.endsWith('.md') && !entry.name.startsWith('.')) {
        try {
          const content = await readFile(fullPath, 'utf-8');
          const parsed = this.parseChunkFile(content);
          if (parsed) {
            if (markAsDissolved) parsed.meta.dissolved = true;
            this.chunkCache.set(parsed.id, parsed);
          }
        } catch {}
      }
    }
  }

  private parseChunkFile(content: string): MicroChunk | null {
    const fmMatch = content.match(/^---([\s\S]*?)---/);
    if (!fmMatch) return null;
    
    const body = content.slice(fmMatch[0].length).trim();
    const fm = fmMatch[1];
    
    const get = (field: string): string => {
      const match = fm.match(new RegExp(`${field}:\s*(.+?)$`, 'm'));
      return match ? match[1].trim().replace(/^"|"$/g, '') : '';
    };
    
    const getList = (field: string): string[] => {
      const match = fm.match(new RegExp(`${field}:\s*\[([\s\S]*?)\]`, 'm'));
      if (!match) return [];
      return match[1].match(/"([^"]+)"/g)?.map(s => s.replace(/"/g, '')) || [];
    };
    
    const id = get('id');
    if (!id) return null;
    
    return {
      id,
      content: body,
      meta: {
        source: get('source'),
        sourcePath: '',
        title: get('source'), // fallback to source name
        category: get('category'),
        skillTags: getList('skillTags'),
        containmentHash: get('containmentHash'),
        createdAt: parseInt(get('createdAt')) || Date.now(),
        dissolved: get('dissolved') === 'true',
        links: getList('links'),
        embeddingSig: get('embeddingSig'),
      },
    };
  }

  async loadAllSkills(): Promise<void> {
    try {
      await access(this.skillsDir);
    } catch { return; }
    
    const entries = await readdir(this.skillsDir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(this.skillsDir, entry.name);
      if (entry.isDirectory()) {
        await this.loadSkillsFromDir(fullPath);
      }
    }
  }

  private async loadSkillsFromDir(dir: string): Promise<void> {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isFile() && entry.name.endsWith('.md')) {
        try {
          const content = await readFile(join(dir, entry.name), 'utf-8');
          const parsed = this.parseSkillFile(content);
          if (parsed) this.skillCache.set(parsed.id, parsed);
        } catch {}
      }
    }
  }

  private parseSkillFile(content: string): SkillRecord | null {
    const fmMatch = content.match(/^---([\s\S]*?)---/);
    if (!fmMatch) return null;
    
    const body = content.slice(fmMatch[0].length);
    const fm = fmMatch[1];
    
    const get = (field: string): string => {
      const match = fm.match(new RegExp(`${field}:\s*(.+?)$`, 'm'));
      return match ? match[1].trim().replace(/^"|"$/g, '') : '';
    };
    
    const id = get('id');
    if (!id) return null;
    
    // Extract pattern from body
    const patternMatch = body.match(/## Pattern\s*\n([\s\S]*?)(?=##|$)/);
    
    return {
      id,
      name: get('name'),
      pattern: patternMatch ? patternMatch[1].trim().slice(0, 1000) : body.slice(0, 500),
      chunks: [], // loaded separately if needed
      category: get('category'),
      strength: parseFloat(get('strength')) || 0.5,
      lastUsed: Date.now(),
      containmentProof: get('containmentProof'),
    };
  }

  // ─── Stats ────────────────────────────────────────────────────

  async getIndex(): Promise<ContainmentIndex | null> {
    try {
      const content = await readFile(join(this.indexDir, 'vault-index.json'), 'utf-8');
      return JSON.parse(content);
    } catch {
      return null;
    }
  }
}

// ─── Singleton ──────────────────────────────────────────────────────

let vaultInstance: ObsidianVault | null = null;

export function getVault(vaultPath?: string): ObsidianVault {
  if (!vaultInstance) {
    const path = vaultPath || process.env.OBSIDIAN_VAULT_PATH || join(process.cwd(), 'data', 'eli-vault');
    vaultInstance = new ObsidianVault(path);
  }
  return vaultInstance;
}
