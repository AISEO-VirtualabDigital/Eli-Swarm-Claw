import { readFile } from 'fs/promises';
import { join } from 'path';

const SEARCH_INDEX_DIR = '/home/z/my-project/data/eli-vault/03-Index';

async function debug() {
  // Check if 'parasite' exists in any index
  const { readdir } = await import('fs/promises');
  const files = await readdir(SEARCH_INDEX_DIR);
  const indexFiles = files.filter(f => /^search-index-\d+\.json$/.test(f));
  
  for (const f of indexFiles) {
    const data = await readFile(join(SEARCH_INDEX_DIR, f), 'utf-8');
    const parsed = JSON.parse(data);
    const terms = parsed.terms || {};
    if (terms['parasite']) {
      console.log(f, '-> parasite found:', terms['parasite'].length, 'files');
      console.log('  first file:', terms['parasite'][0]);
    }
    if (terms['seo']) {
      console.log(f, '-> seo found:', terms['seo'].length, 'files');
    }
  }
  
  // Also test the exact tokenization
  const query = 'parasite seo';
  const queryTerms = query
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 2);
  console.log('\nQuery terms:', queryTerms);
  
  // Check if they exist in merged index
  let merged = {} as Record<string, string[]>;
  for (const f of indexFiles) {
    const data = await readFile(join(SEARCH_INDEX_DIR, f), 'utf-8');
    const parsed = JSON.parse(data);
    for (const [term, paths] of Object.entries(parsed.terms || {})) {
      if (!merged[term]) merged[term] = [];
      merged[term].push(...(paths as string[]));
    }
  }
  console.log('parasite in merged:', !!merged['parasite'], merged['parasite']?.length || 0);
  console.log('seo in merged:', !!merged['seo'], merged['seo']?.length || 0);
}

debug().catch(console.error);
