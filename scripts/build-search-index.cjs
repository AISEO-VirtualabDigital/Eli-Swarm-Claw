const fs = require('fs');
const path = require('path');

const VAULT_DIR = process.env.OBSIDIAN_VAULT_PATH || '/home/z/my-project/data/eli-vault';
const ACTIVE_DIR = path.join(VAULT_DIR, '01-Active');
const REL_PREFIX = ACTIVE_DIR + '/';
const OUTPUT = path.join(VAULT_DIR, '03-Index', 'search-index.json');

console.log('Building search index...');

const termIndex = {}; // term -> Set<relativePath>
const STOP = new Set(['that','this','with','from','have','they','been','will','would','could','should','which','their','there','about','other','into','more','some','than','also','only','then','over','such','after','before','between','through','where','when','what','your','them','these','those','being','every','most','however','using','based','including','while']);

function addTerm(term, relPath) {
  if (!term || term.length < 3) return;
  const t = term.toLowerCase();
  if (STOP.has(t)) return;
  if (!termIndex[t]) termIndex[t] = new Set();
  if (termIndex[t].size < 300) termIndex[t].add(relPath);
}

let processed = 0;
function processFile(filePath) {
  let content;
  try { content = fs.readFileSync(filePath, 'utf-8'); } catch { return; }

  const relPath = filePath.startsWith(REL_PREFIX) ? filePath.slice(REL_PREFIX.length) : filePath;

  // Extract source name from frontmatter
  const sourceMatch = content.match(/source:\s*"?([^"\n]+)["\n]?/);
  const sourceName = sourceMatch ? sourceMatch[1].toLowerCase() : '';

  // Extract body (after frontmatter)
  const bodyMatch = content.match(/^---[\s\S]*?---\n?/);
  const body = bodyMatch ? content.slice(bodyMatch[0].length) : content;

  // Index source filename terms
  const sourceTerms = sourceName.replace(/[-_.]/g, ' ').split(/\s+/).filter(w => w.length > 2);
  for (const t of sourceTerms) addTerm(t, relPath);

  // Index body terms (alpha only, length > 3)
  const words = body.toLowerCase().replace(/[^a-z\s]/g, ' ').split(/\s+/).filter(w => w.length > 3);
  for (const w of words) addTerm(w, relPath);

  // Bigrams
  for (let i = 0; i < words.length - 1; i++) {
    addTerm(words[i] + ' ' + words[i+1], relPath);
  }
}

function walkDir(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkDir(full);
    } else if (entry.name.endsWith('.md')) {
      processFile(full);
      processed++;
      if (processed % 5000 === 0) console.log(`  ${processed} files...`);
    }
  }
}

walkDir(ACTIVE_DIR);

// Convert to serializable, filter out too-common terms
const filteredTerms = {};
for (const [term, paths] of Object.entries(termIndex)) {
  if (paths.size >= 2 && paths.size <= 2000) {
    filteredTerms[term] = [...paths];
  }
}

const indexData = {
  terms: filteredTerms,
  totalUnique: Object.keys(termIndex).length,
  indexedTerms: Object.keys(filteredTerms).length,
  totalEntries: Object.values(filteredTerms).reduce((s, a) => s + a.length, 0),
  builtAt: Date.now(),
};

fs.writeFileSync(OUTPUT, JSON.stringify(indexData));

const sizeMB = (fs.statSync(OUTPUT).size / (1024 * 1024)).toFixed(1);
console.log(`Done: ${indexData.indexedTerms} indexed terms (from ${indexData.totalUnique} unique), ${sizeMB} MB`);

// Check parasite
console.log(`"parasite" -> ${JSON.stringify(filteredTerms['parasite'] || [])}`);
console.log(`"parasite seo" -> ${JSON.stringify(filteredTerms['parasite seo'] || [])}`);
console.log(`"seo" -> ${JSON.stringify(filteredTerms['seo']?.slice(0, 3) || [])}`);
