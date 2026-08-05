/**
 * Knowledge Search Engine v2 — Upgraded
 * Broader search with synonym expansion, more results, bigger snippets.
 * Includes a pre-built Knowledge Map for persistent background awareness.
 */

import { readdir, readFile, stat } from 'fs/promises';
import { join } from 'path';

const UPLOAD_DIR = '/home/z/my-project/upload';

export interface KnowledgeChunk {
  source: string;
  sourcePath: string;
  title: string;
  content: string;
  category: string;
  url?: string;
  charCount: number;
}

export interface SearchResult {
  chunk: KnowledgeChunk;
  score: number;
  matchedTerms: string[];
}

// In-memory cache
let cachedChunks: KnowledgeChunk[] | null = null;
let cacheTimestamp = 0;
const CACHE_TTL = 5 * 60 * 1000;

// Synonym expansion for broader search coverage
const SYNONYMS: Record<string, string[]> = {
  'scraping': ['crawl', 'extract', 'harvest', 'parse', 'spider'],
  'seo': ['search engine', 'ranking', 'serp', 'organic', 'backlink', 'keyword'],
  'design': ['ui', 'ux', 'layout', 'style', 'css', 'component', 'frontend'],
  'ai': ['artificial intelligence', 'llm', 'machine learning', 'gpt', 'claude', 'gemini', 'agent', 'automation'],
  'saas': ['software as a service', 'subscription', 'multi-tenant', 'b2b'],
  'automation': ['workflow', 'integration', 'zapier', 'no-code', 'trigger'],
  'youtube': ['video', 'channel', 'tags', 'thumbnail', 'yt'],
  'google': ['search', 'maps', 'drive', 'cloud', 'indexing', 'api'],
  'crm': ['customer relationship', 'salesforce', 'hubspot', 'lead management', 'pipeline', 'contact'],
  'project': ['kanban', 'agile', 'scrum', 'sprint', 'jira', 'asana', 'trello', 'gantt', 'task board'],
  'cloud': ['aws', 'azure', 'gcp', 'kubernetes', 'k8s', 'docker', 'terraform', 'devops', 'serverless'],
  'security': ['cybersecurity', 'pentest', 'vulnerability', 'malware', 'firewall', 'encryption', 'owasp'],
  'database': ['sql', 'postgres', 'mysql', 'mongodb', 'redis', 'sqlite', 'orm', 'query'],
  'vps': ['hosting', 'self-host', 'selfhost', 'homelab', 'server provisioning', 'dedicated server'],
  'copywriting': ['content generation', 'ai writing', 'humanizer', 'paraphrase', 'rewriting', 'ghostwriter', 'jasper'],
  'backend': ['server', 'api', 'database', 'schema', 'architecture'],
  'productivity': ['notion', 'task', 'project', 'collaboration', 'notes'],
  'marketing': ['growth', 'campaign', 'content', 'brand', 'audience'],
  'website': ['web', 'site', 'page', 'landing', 'blog', 'cms'],
  'code': ['programming', 'developer', 'algorithm', 'rust', 'python', 'javascript'],
  'obsidian': ['vault', 'note', 'markdown', 'frontmatter', 'wikilink', 'plugin'],
  'eli': ['agent eli', 'eli os', 'virtuallab', 'command center', 'growth intelligence'],
  'skill': ['capability', 'harness', 'stack', 'agent skill', 'skill registry'],
  'workflow': ['automation', 'pipeline', 'dag', 'execution', 'rewiring'],
  'authority': ['human order', 'operator', 'policy', 'governance', 'approval'],
  'google': ['google api', 'gcloud', 'gcp', 'workspace', 'gmail', 'drive', 'calendar', 'sheets', 'docs', 'gemini', 'maps', 'places', 'oauth'],
};

function expandQuery(query: string): string {
  const lower = query.toLowerCase();
  let expanded = query;
  for (const [term, syns] of Object.entries(SYNONYMS)) {
    if (lower.includes(term)) {
      expanded += ' ' + syns.join(' ');
    }
  }
  return expanded;
}

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
  if (lower.includes('brand') || lower.includes('tokens') || lower.includes('voice')) return 'brand';
  if (lower.includes('design_screenshot') || lower.includes('screencapture')) return 'screenshot';
  if (lower.includes('design_analysis')) return 'analysis';
  if (lower.includes('eliclaw') || lower.includes('zed-main') || lower.includes('kimi_agent')) return 'codebase';
  if (lower.includes('strategic') || lower.includes('prompt') || lower.includes('chatgpt') || lower.includes('first.docx')) return 'strategy';
  if (lower.includes('all_docs')) return 'strategy';
  if (lower.includes('seo') || lower.includes('searchfit') || lower.includes('backlink') || lower.includes('geo-') || lower.includes('ecommerce') || lower.includes('youtube') || lower.includes('yt-') || lower.includes('google-dork') || lower.includes('indexing-api')) return 'seo';
  if (lower.includes('eliza') || lower.includes('browseros') || lower.includes('chatgpt-prompts') || lower.includes('ai-tools') || lower.includes('llm-scraper') || lower.includes('youmind')) return 'ai-agent';
  if (lower.includes('webstudio') || lower.includes('webflow') || lower.includes('instatic') || lower.includes('getpublii') || lower.includes('wp-cpt') || lower.includes('design-resources') || lower.includes('ant-design') || lower.includes('material-web') || lower.includes('material-components') || lower.includes('responsive-web') || lower.includes('awesome-web-design') || lower.includes('uswds') || lower.includes('frontend-design-checklist') || lower.includes('goindex-theme')) return 'web-design';
  if (lower.includes('appflowy') || lower.includes('activepieces')) return 'productivity';
  if (lower.includes('saas') || lower.includes('serverless') || lower.includes('ghl')) return 'saas';
  if (lower.includes('algorithm') || lower.includes('testing-tools') || lower.includes('scraper') || lower.includes('scrapegraph') || lower.includes('social-analyzer') || lower.includes('goindex') || lower.includes('google-drive-index') || lower.includes('google-maps-scraper') || lower.includes('schemacrawler')) return 'codebase';
  if (lower.includes('fmhy') || lower.includes('virtuallab-strategy') || lower.includes('googleapis-repo') || lower.includes('google-research') || lower.includes('google-services-samples') || lower.includes('google-api-python-docs') || lower.includes('googleapis-nodejs') || lower.includes('low-level-design')) return 'reference';
  // --- Google API (client libs, workspace, maps, AI, auth, scraping) ---
  if (lower.includes('github-google-api-topic') || lower.includes('google-api-client-libraries') || lower.includes('google-workspace-api') || lower.includes('google-maps-places') || lower.includes('google-ai-gemini') || lower.includes('google-auth-oauth') || lower.includes('google-scraping-automation')) return 'google-api';
  // --- SEO tools, frameworks, libraries ---
  if (lower.includes('github-seo-tools') || lower.includes('awesome-seo') || lower.includes('claude-seo') || lower.includes('next-seo') || lower.includes('laravel-seo') || lower.includes('seo-tools-yoast') || lower.includes('image-seo') || lower.includes('github-seo-marketing')) return 'seo';
  // --- Batch 3: Multi-topic GitHub repos ---
  if (lower.includes('github-crm-sales')) return 'crm-sales';
  if (lower.includes('github-project-management')) return 'project-mgmt';
  if (lower.includes('github-copywriting-ai')) return 'copywriting-ai';
  if (lower.includes('github-cloud-infrastructure')) return 'cloud-infra';
  if (lower.includes('github-cybersecurity')) return 'cybersecurity';
  if (lower.includes('github-design-ui-ux')) return 'design-uiux';
  if (lower.includes('github-llm-ai-frameworks')) return 'llm-ai';
  if (lower.includes('github-vps-hosting')) return 'vps-hosting';
  if (lower.includes('github-database-tools')) return 'database';
  if (lower.includes('github-multi-topic-directory')) return 'github-multi';
  // --- Eli identity, architecture, skills ---
  if (lower.includes('eli-core-identity') || lower.includes('eli-obsidian-agent-skills') || lower.includes('eli-obsidian-architecture') || lower.includes('eli-obsidian-manual-rewiring')) return 'eli-core';
  // --- Obsidian vault, importer, skill harness ---
  if (lower.includes('eli-obsidian') || lower.includes('obsidian-importer') || lower.includes('skill-harness-manager')) return 'obsidian';
  // --- Agent Eli v1 specific ---
  if (lower.includes('agent-eli-v1')) return 'agent-eli';
  return 'strategy';
}

function extractUrl(content: string): string | undefined {
  const fmMatch = content.match(/^---[\s\S]*?Source:\s*(.+?)[\r\n]/);
  if (fmMatch) {
    const url = fmMatch[1].trim();
    if (url.startsWith('http')) return url;
  }
  return undefined;
}

function stripFrontmatter(content: string): string {
  return content.replace(/^---[\s\S]*?---\n?/, '');
}

async function buildIndex(): Promise<KnowledgeChunk[]> {
  const chunks: KnowledgeChunk[] = [];
  const textExtensions = ['.md', '.txt', '.json', '.docx'];
  const skipDirs = ['node_modules', '.git', '.next'];

  async function scanDir(dir: string, depth: number = 0) {
    if (depth > 2) return;
    try {
      const entries = await readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.name.startsWith('.') && skipDirs.includes(entry.name)) continue;
        const fullPath = join(dir, entry.name);
        if (entry.isDirectory()) {
          await scanDir(fullPath, depth + 1);
        } else if (entry.isFile()) {
          const ext = entry.name.split('.').pop()?.toLowerCase() ?? '';
          if (!textExtensions.includes(ext) && ext !== 'md') continue;
          if (['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.zip'].includes(ext)) continue;
          try {
            const fileContent = await readFile(fullPath, 'utf-8');
            if (!fileContent || fileContent.length < 20) continue;
            if (ext === 'json' && fileContent.length > 50000) continue;
            let cleanContent = fileContent;
            if (ext === 'json') {
              try {
                const parsed = JSON.parse(fileContent);
                if (parsed.data?.html) {
                  cleanContent = parsed.data.html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
                } else {
                  cleanContent = JSON.stringify(parsed, null, 2);
                }
              } catch {
                cleanContent = fileContent;
              }
            }
            const noFrontmatter = stripFrontmatter(cleanContent);
            chunks.push({
              source: entry.name,
              sourcePath: fullPath,
              title: extractTitle(cleanContent, entry.name),
              content: noFrontmatter.slice(0, 8000),
              category: extractCategory(cleanContent, entry.name),
              url: extractUrl(cleanContent),
              charCount: noFrontmatter.length,
            });
          } catch {}
        }
      }
    } catch {}
  }

  await scanDir(UPLOAD_DIR);
  return chunks;
}

export async function getKnowledgeIndex(forceRefresh = false): Promise<KnowledgeChunk[]> {
  const now = Date.now();
  if (!forceRefresh && cachedChunks && (now - cacheTimestamp) < CACHE_TTL) {
    return cachedChunks;
  }
  cachedChunks = await buildIndex();
  cacheTimestamp = now;
  return cachedChunks;
}

/**
 * Build a Knowledge Map — compact category-level index of all sources.
 * Injected as persistent background so Eli always knows what's available.
 */
export async function buildKnowledgeMap(): Promise<string> {
  const chunks = await getKnowledgeIndex();
  const byCategory: Record<string, {title: string; source: string; url?: string}[]> = {};

  for (const c of chunks) {
    if (!byCategory[c.category]) byCategory[c.category] = [];
    byCategory[c.category].push({ title: c.title, source: c.source, url: c.url });
  }

  const lines: string[] = ['ELI\'S KNOWLEDGE MAP (148+ sources across 24 categories):', ''];
  const categoryLabels: Record<string, string> = {
    'seo': '🔍 SEO & Marketing',
    'codebase': '💻 Code & Scraping',
    'web-design': '🎨 Web Design & UI',
    'ai-agent': '🤖 AI Agents & Tools',
    'saas': '💰 SaaS & Business',
    'productivity': '⚡ Productivity & Automation',
    'reference': '📚 Reference & Research',
    'brand': '🏷️ VirtuaLab Brand',
    'strategy': '📋 Strategy & Planning',
    'analysis': '📊 Design Analysis',
    'screenshot': '📸 Screenshots',
    'eli-core': '🧠 Eli Core Identity & Skills',
    'obsidian': '📦 Obsidian Vault & Tools',
    'agent-eli': '⚙️ Agent Eli v1 Architecture',
    'google-api': '🔗 Google API Ecosystem',
    'crm-sales': '📊 CRM & Sales Tools',
    'project-mgmt': '📋 Project Management',
    'copywriting-ai': '✍️ Copywriting & AI Content',
    'cloud-infra': '☁️ Cloud & Infrastructure',
    'cybersecurity': '🔒 Cybersecurity',
    'design-uiux': '🎨 Design & UI/UX Tools',
    'llm-ai': '🤖 LLM & AI Frameworks',
    'vps-hosting': '🖥️ VPS & Hosting',
    'database': '🗄️ Database Tools',
    'github-multi': '📂 GitHub Multi-Topic Directory',
  };

  for (const [cat, items] of Object.entries(byCategory)) {
    const label = categoryLabels[cat] || cat;
    lines.push(`${label} (${items.length}):`);
    for (const item of items.slice(0, 15)) {
      lines.push(`  - ${item.title}${item.url ? ` — ${item.url}` : ''}`);
    }
    if (items.length > 15) lines.push(`  - ... and ${items.length - 15} more`);
    lines.push('');
  }

  return lines.join('\n');
}

export async function searchKnowledge(
  query: string,
  options?: { maxResults?: number; minScore?: number; categories?: string[] }
): Promise<SearchResult[]> {
  const { maxResults = 6, minScore = 1, categories } = options ?? {};
  const chunks = await getKnowledgeIndex();

  // Expand query with synonyms for broader coverage
  const expandedQuery = expandQuery(query);
  const queryLower = expandedQuery.toLowerCase();
  const queryTerms = queryLower
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2);

  const queryBigrams: string[] = [];
  for (let i = 0; i < queryTerms.length - 1; i++) {
    queryBigrams.push(`${queryTerms[i]} ${queryTerms[i + 1]}`);
  }

  const scored: SearchResult[] = [];

  for (const chunk of chunks) {
    if (categories && categories.length > 0 && !categories.includes(chunk.category)) continue;

    const contentLower = chunk.content.toLowerCase();
    const titleLower = chunk.title.toLowerCase();
    const combinedLower = `${titleLower} ${contentLower}`;

    let score = 0;
    const matchedTerms: string[] = [];

    for (const term of queryTerms) {
      const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const titleCount = (titleLower.match(new RegExp(escaped, 'g')) || []).length;
      if (titleCount > 0) {
        score += titleCount * 5;
        if (!matchedTerms.includes(term)) matchedTerms.push(term);
      }
      const contentCount = (contentLower.match(new RegExp(escaped, 'g')) || []).length;
      if (contentCount > 0) {
        score += contentCount;
        if (!matchedTerms.includes(term)) matchedTerms.push(term);
      }
    }

    for (const bigram of queryBigrams) {
      if (combinedLower.includes(bigram)) {
        score += 8;
      }
    }

    if (categories && categories.includes(chunk.category)) {
      score += 2;
    }

    if (score >= minScore) {
      scored.push({ chunk, score, matchedTerms });
    }
  }

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, maxResults);
}

export async function getKnowledgeContext(query: string): Promise<{
  context: string;
  sources: Array<{ title: string; source: string; url?: string; category: string }>;
}> {
  const results = await searchKnowledge(query, { maxResults: 6, minScore: 1 });

  if (results.length === 0) {
    return { context: '', sources: [] };
  }

  const sources = results.map(r => ({
    title: r.chunk.title,
    source: r.chunk.source,
    url: r.chunk.url,
    category: r.chunk.category,
  }));

  const contextParts = results.map((r, i) => {
    const snippet = r.chunk.content.slice(0, 2500);
    return `[Source ${i + 1}: ${r.chunk.title} (${r.chunk.source})]\n${snippet}`;
  });

  const context = `\n\n---\nRELEVANT KNOWLEDGE (from Eli's library):\n${contextParts.join('\n---\n')}\n---\n\nUse the above knowledge to inform your response when relevant. Cite sources by name when you reference them.`;

  return { context, sources };
}
