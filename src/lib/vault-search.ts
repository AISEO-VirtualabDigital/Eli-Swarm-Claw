
/**
 * Vault Search v4 — Pre-built index lookup
 * 
 * Uses search-index.json (built at ingestion time) for instant term→file mapping.
 */

import { readdir, readFile } from 'fs/promises';
import { join } from 'path';

const VAULT_PATH = process.env.OBSIDIAN_VAULT_PATH || '/home/z/my-project/data/eli-vault';
const ACTIVE_DIR = join(VAULT_PATH, '01-Active');
const INDEX_PATH = join(VAULT_PATH, '03-Index', 'vault-index.json');
const SEARCH_INDEX_DIR = join(VAULT_PATH, '03-Index');
const SEARCH_INDEX_PATTERN = /^search-index-
+\.json$/;

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

let vaultIndex: any = null;
let searchIndex: Record<string, string[]> = {};
let indexLoadTime = 0;
const INDEX_TTL = 60_000;

const CATEGORY_TERMS: Record<string, string[]> = {
  'seo': ['seo','search','ranking','serp','organic','backlink','keyword','parasite','aeo','geo'],
  'web-design': ['design','ui','ux','layout','css','frontend','component','theme','template'],
  'google-api': ['google','api','oauth','maps','drive','cloud','workspace','gemini'],
  'scraping': ['scrap','crawl','extract','harvest','parse','spider'],
  'social': ['social','instagram','twitter','facebook','linkedin','tiktok','youtube'],
  'ai-agent': ['ai','agent','llm','gpt','claude','gemini','eliza','chatgpt'],
  'obsidian': ['obsidian','vault','note','markdown','frontmatter','wikilink'],
  'saas': ['saas','serverless','ghl','gohighlevel','agency','funnel'],
  'automation': ['automation','workflow','n8n','activepieces','zapier','trigger'],
  'eli-core': ['eli','skill','harness','agent-eli','identity'],
  'content': ['copywriting','content','writing','blog','article','copy','headline'],
  'infra': ['cloud','vps','hosting','server','deploy','docker','kubernetes'],
};

async function loadIndexes(): Promise<void> {
  const now = Date.now();
  if (vaultIndex && (now - indexLoadTime) < INDEX_TTL) return;
  try {
    const vaultData = await readFile(INDEX_PATH, 'utf-8');
    vaultIndex = JSON.parse(vaultData);
  } catch {}
  // Load search index parts
  searchIndex = {};
  try {
    const files = await readdir(SEARCH_INDEX_DIR);
    for (const pf of files) {
      try {
        const data = await readFile(join(SEARCH_INDEX_DIR, pf), 'utf-8');
        const parsed = JSON.parse(data);
        Object.assign(searchIndex, parsed.terms || {});
      } catch {}
  }
  indexLoadTime = now;
}

async function parseChunkFile(filePath: string): Promise<VaultChunk | null> {
  try {
    const content = await readFile(filePath, 'utf-8');
    const sections = content.split(/
/);
    const body = sections[1] || content;
    if (sections.length < 2) return null;
    const fm = sections[0];
    if (!fm || !fm[1].includes('---')) return null;
    const body = body.slice(fm[0].length).trim();
    const fm = fmMatch[1];
    const getField = (field: string): string => {
      const m = fm.match(new RegExp(`^${field}:
+`, 'm'));
      return m ? m[1].trim().replace(/^[