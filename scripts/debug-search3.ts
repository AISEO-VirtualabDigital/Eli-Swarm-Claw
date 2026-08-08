import { readFile } from 'fs/promises';
import { join, resolve } from 'path';

const VAULT_PATH = resolve('/home/z/my-project/data/eli-vault');
const ACTIVE_DIR = join(VAULT_PATH, '01-Active');
const SEARCH_INDEX_DIR = join(VAULT_PATH, '03-Index');
const INDEX_PATH = join(VAULT_PATH, '03-Index', 'vault-index.json');

async function debug() {
  // Step 1: Load vault index
  const vaultData = await readFile(INDEX_PATH, 'utf-8');
  const vaultIndex = JSON.parse(vaultData);
  console.log('vaultIndex loaded:', vaultIndex.totalChunks);

  // Step 2: Load search indexes
  const { readdir } = await import('fs/promises');
  const files = await readdir(SEARCH_INDEX_DIR);
  const indexFiles = files.filter((f: string) => /^search-index-\d+\.json$/.test(f));
  console.log('Index files found:', indexFiles.length);

  const searchIndex: Record<string, string[]> = {};
  for (const f of indexFiles) {
    const data = await readFile(join(SEARCH_INDEX_DIR, f), 'utf-8');
    const parsed = JSON.parse(data);
    if (parsed.terms) {
      for (const [term, paths] of Object.entries(parsed.terms)) {
        if (!searchIndex[term]) searchIndex[term] = [];
        searchIndex[term].push(...(paths as string[]));
      }
    }
  }
  console.log('Total unique terms:', Object.keys(searchIndex).length);
  console.log('parasite files:', searchIndex['parasite']?.length);
  console.log('seo files:', searchIndex['seo']?.length);

  // Step 3: Score files
  const queryTerms = ['parasite', 'seo'];
  const fileScores: Record<string, { score: number; matchedTerms: string[] }> = {};
  const seenFiles = new Set<string>();

  for (const term of queryTerms) {
    const fList = searchIndex[term];
    if (!fList) { console.log('No files for term:', term); continue; }
    console.log('Term:', term, '-> files:', fList.length);
    for (const f of fList) {
      const key = f + term;
      if (seenFiles.has(key)) continue;
      seenFiles.add(key);
      if (!fileScores[f]) fileScores[f] = { score: 0, matchedTerms: [] };
      fileScores[f].score += 1;
      fileScores[f].matchedTerms.push(term);
    }
  }

  const sorted = Object.entries(fileScores)
    .sort((a, b) => b[1].score - a[1].score)
    .slice(0, 5);
  console.log('\nTop 5 files:');
  for (const [filePath, scoring] of sorted) {
    console.log(' ', filePath, '-> score:', scoring.score, 'terms:', scoring.matchedTerms);
  }

  // Step 4: Read first chunk file
  if (sorted.length > 0) {
    const firstFile = sorted[0][0];
    const fullPath = join(ACTIVE_DIR, firstFile);
    console.log('\nReading:', fullPath);
    try {
      const content = await readFile(fullPath, 'utf-8');
      const fmEnd = content.indexOf('---', 3);
      const fmRaw = content.slice(3, fmEnd).trim();
      const body = content.slice(fmEnd + 3).trim();
      console.log('Body length:', body.length);
      console.log('Body preview:', body.slice(0, 150));
    } catch (e: any) {
      console.error('Read error:', e.message);
    }
  }
}

debug().catch(console.error);
