/**
 * Vault Ingestion — Plain Node.js (CJS)
 * Dissolves all knowledge files into micro-chunks
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const KNOWLEDGE_DIR = process.env.KNOWLEDGE_DIR || '/home/z/my-project/data/uploads/knowledge-sources';
const VAULT_DIR = process.env.OBSIDIAN_VAULT_PATH || '/home/z/my-project/data/eli-vault';

const CHUNK_TARGET = 350;
const CHUNK_MIN = 100;
const CHUNK_MAX = 600;
const OVERLAP = 50;

const ACTIVE_DIR = path.join(VAULT_DIR, '01-Active');
const CONTAIN_DIR = path.join(VAULT_DIR, '00-Containment');
const SKILLS_DIR = path.join(VAULT_DIR, '02-Skills');
const INDEX_DIR = path.join(VAULT_DIR, '03-Index');

// ─── Helpers ───────────────────────────────────────────────

function hash(content) {
  return crypto.createHash('sha256').update(content.trim()).digest('hex').slice(0, 16);
}

function containHash(content, source, ts) {
  return crypto.createHash('sha256').update(`${content}|${source}|${ts}`).digest('hex').slice(0, 20);
}

function semanticSig(content) {
  const words = content.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').split(/\s+/).filter(w => w.length > 3);
  const tris = new Set();
  for (let i = 0; i < words.length - 2; i++) tris.add(`${words[i]}:${words[i+1]}:${words[i+2]}`);
  return Array.from(tris).slice(0, 12).sort().join('|');
}

const SKILL_PATTERNS = {
  process: [/step \d/i, /first[,\.]/i, /then[,\.]/i, /workflow/i, /pipeline/i, /\d+\.\s/],
  pattern: [/pattern/i, /whenever/i, /always/i, /never/i, /rule/i, /framework/i],
  capability: [/can\s/i, /able to/i, /supports/i, /integrates/i, /provides/i, /enables/i],
  tool: [/tool/i, /api\b/i, /library/i, /plugin/i, /extension/i, /sdk\b/i],
  strategy: [/strategy/i, /approach/i, /tactic/i, /methodology/i, /playbook/i],
  metric: [/\d+%/, /\$\d+/, /\d+x\b/, /score/i, /rate/i, /volume/i],
  code: [/function\s/, /const\s/, /import\s/, /class\s/, /async\s/, /```/],
  warning: [/warning/i, /caution/i, /avoid/i, /risk/i, /critical/i],
};

function extractTags(content) {
  const tags = [];
  const lower = content.toLowerCase();
  for (const [tag, pats] of Object.entries(SKILL_PATTERNS)) {
    if (pats.some(p => p.test(lower)) && !tags.includes(tag)) tags.push(tag);
  }
  return tags;
}

function extractTitle(content, filename) {
  const fm = content.match(/^---[\s\S]*?title:\s*(.+?)[\r\n]/);
  if (fm) return fm[1].trim().replace(/^['"]|['"]$/g, '');
  const h1 = content.match(/^#\s+(.+)$/m);
  if (h1) return h1[1].trim();
  return filename.replace(/[-_]/g, ' ').replace(/\.(md|txt|json)$/i, '').replace(/\b\w/g, c => c.toUpperCase());
}

function extractCategory(filename) {
  const l = filename.toLowerCase();
  if (l.includes('seo') || l.includes('backlink') || l.includes('keyword') || l.includes('indexing')) return 'seo';
  if (l.includes('ai') || l.includes('agent') || l.includes('llm') || l.includes('claude') || l.includes('gemini') || l.includes('eliza')) return 'ai-agent';
  if (l.includes('design') || l.includes('ui') || l.includes('ux') || l.includes('frontend') || l.includes('material') || l.includes('ant-design')) return 'web-design';
  if (l.includes('saas') || l.includes('ghl') || l.includes('serverless') || l.includes('agency')) return 'saas';
  if (l.includes('google') || l.includes('api') || l.includes('oauth')) return 'google-api';
  if (l.includes('obsidian') || l.includes('vault') || l.includes('skill-harness')) return 'obsidian';
  if (l.includes('eli') || l.includes('skill') || l.includes('harness')) return 'eli-core';
  if (l.includes('automation') || l.includes('workflow') || l.includes('n8n') || l.includes('activepieces')) return 'automation';
  if (l.includes('cloud') || l.includes('vps') || l.includes('hosting') || l.includes('server') || l.includes('serverless')) return 'infra';
  if (l.includes('social') || l.includes('instagram') || l.includes('youtube') || l.includes('yt-')) return 'social';
  if (l.includes('copy') || l.includes('content') || l.includes('writing') || l.includes('chatgpt')) return 'content';
  if (l.includes('shopify') || l.includes('ecommerce')) return 'ecommerce';
  if (l.includes('scrape') || l.includes('rust-') || l.includes('schemacrawler')) return 'scraping';
  if (l.includes('security') || l.includes('cyber')) return 'security';
  if (l.includes('crm') || l.includes('sales')) return 'crm';
  if (l.includes('project') || l.includes('kanban')) return 'project-mgmt';
  if (l.includes('database') || l.includes('sql')) return 'database';
  return 'knowledge';
}

function findSplitPoint(text, target) {
  const start = Math.max(0, target - 80);
  const end = Math.min(text.length, target + 80);
  const window = text.slice(start, end);
  
  let idx = window.lastIndexOf('\n\n');
  if (idx > 20) return start + idx + 2;
  idx = window.lastIndexOf('. ');
  if (idx > 20) return start + idx + 2;
  idx = window.lastIndexOf('! ');
  if (idx > 20) return start + idx + 2;
  idx = window.lastIndexOf('? ');
  if (idx > 20) return start + idx + 2;
  idx = window.lastIndexOf('\n');
  if (idx > 10) return start + idx + 1;
  idx = window.lastIndexOf(' ', target - start);
  if (idx > 10) return start + idx + 1;
  return Math.min(target, text.length);
}

function dissolve(content, filename) {
  const chunks = [];
  const title = extractTitle(content, filename);
  const category = extractCategory(filename);
  const now = Date.now();
  const clean = content.replace(/^---[\s\S]*?---\n?/, '');
  
  if (clean.length <= CHUNK_MAX) {
    const ch = containHash(clean, filename, now);
    chunks.push({
      id: hash(clean),
      content: clean,
      meta: { source: filename, title, category, tags: extractTags(clean), containmentHash: ch, createdAt: now, sig: semanticSig(clean) },
    });
    return chunks;
  }
  
  // Split by headings/paragraphs
  const sections = [];
  let current = '';
  for (const line of clean.split('\n')) {
    if (line.match(/^#{1,4}\s/) && current.trim()) {
      sections.push(current.trim());
      current = line + '\n';
    } else if (line.trim() === '' && current.trim().length > 100) {
      sections.push(current.trim());
      current = '';
    } else {
      current += line + '\n';
    }
  }
  if (current.trim()) sections.push(current.trim());
  if (sections.length === 0) sections.push(clean);
  
  let buffer = '';
  let chunkIndex = 0;
  
  for (const section of sections) {
    buffer += (buffer ? '\n' : '') + section;
    
    while (buffer.length >= CHUNK_TARGET) {
      const splitAt = findSplitPoint(buffer, CHUNK_TARGET);
      const text = buffer.slice(0, splitAt).trim();
      
      if (text.length >= CHUNK_MIN) {
        const ch = containHash(text, filename, now);
        chunks.push({
          id: hash(text + chunkIndex.toString()),
          content: text,
          meta: { source: filename, title, category, tags: extractTags(text), containmentHash: ch, createdAt: now, sig: semanticSig(text) },
        });
        chunkIndex++;
      }
      buffer = buffer.slice(Math.max(0, splitAt - OVERLAP));
    }
  }
  
  if (buffer.trim().length >= CHUNK_MIN) {
    const text = buffer.trim();
    const ch = containHash(text, filename, now);
    chunks.push({
      id: hash(text + chunkIndex.toString()),
      content: text,
      meta: { source: filename, title, category, tags: extractTags(text), containmentHash: ch, createdAt: now, sig: semanticSig(text) },
    });
  }
  
  return chunks;
}

// ─── Main Ingestion ─────────────────────────────────────────

async function main() {
  console.log('═'.repeat(60));
  console.log('  ELI VAULT INGESTION — Micro-Chunk Engine v2');
  console.log('═'.repeat(60));
  console.log(`  Source: ${KNOWLEDGE_DIR}`);
  console.log(`  Vault:  ${VAULT_DIR}`);
  console.log('═'.repeat(60));
  
  // Create directories
  for (const dir of [ACTIVE_DIR, CONTAIN_DIR, SKILLS_DIR, INDEX_DIR]) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.mkdirSync(path.join(VAULT_DIR, '00-Containment'), { recursive: true });
  
  // Walk knowledge directory
  let totalChunks = 0;
  let totalFiles = 0;
  let totalChars = 0;
  const categoryCounts = {};
  const skillTagGroups = {};
  
  function walkDir(dir, depth = 0) {
    if (depth > 3) return;
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walkDir(full, depth + 1);
      } else if (entry.isFile()) {
        const ext = entry.name.split('.').pop()?.toLowerCase();
        if (!['md', 'txt', 'json'].includes(ext)) continue;
        
        try {
          let content = fs.readFileSync(full, 'utf-8');
          if (!content || content.length < 20) continue;
          
          // Clean JSON
          if (ext === 'json') {
            try {
              const p = JSON.parse(content);
              if (p.data?.html) content = p.data.html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
              else content = JSON.stringify(p, null, 2);
            } catch { /* keep raw */ }
            if (content.length > 50000) content = content.slice(0, 50000);
          }
          
          const chunks = dissolve(content, entry.name);
          totalFiles++;
          totalChars += content.length;
          
          // Write chunks
          const catDir = path.join(ACTIVE_DIR, chunks[0]?.meta.category || 'knowledge');
          fs.mkdirSync(catDir, { recursive: true });
          
          for (const chunk of chunks) {
            // Active chunk file
            const fm = [
              '---',
              `id: ${chunk.id}`,
              `source: "${chunk.meta.source}"`,
              JSON.stringify(`title: ${chunk.meta.title}`),
              `category: ${chunk.meta.category}`,
              `skillTags: [${chunk.meta.tags.map(t => `"${t}"`).join(', ')}]`,
              `containmentHash: ${chunk.meta.containmentHash}`,
              `createdAt: ${chunk.meta.createdAt}`,
              `embeddingSig: "${chunk.meta.sig.replace(/"/g, '')}"`,
              '---',
              '',
            ].join('\n');
            
            fs.writeFileSync(path.join(catDir, `${chunk.id}.md`), fm + chunk.content);
            
            // Containment copy (NEVER deleted)
            fs.writeFileSync(
              path.join(CONTAIN_DIR, `${chunk.meta.containmentHash}.md`),
              fm + chunk.content
            );
            
            // Track
            totalChunks++;
            categoryCounts[chunk.meta.category] = (categoryCounts[chunk.meta.category] || 0) + 1;
            
            for (const tag of chunk.meta.tags) {
              if (!skillTagGroups[tag]) skillTagGroups[tag] = [];
              skillTagGroups[tag].push(chunk.id);
            }
          }
          
          if (totalFiles % 20 === 0) {
            process.stdout.write(`  Processed ${totalFiles} files → ${totalChunks} chunks...\r`);
          }
        } catch (err) {
          console.error(`  FAIL: ${entry.name}: ${err.message}`);
        }
      }
    }
  }
  
  console.log('\n[1/3] Scanning and dissolving knowledge files...');
  walkDir(KNOWLEDGE_DIR);
  
  // Extract skills
  console.log('\n[2/3] Extracting skill patterns...');
  let skillCount = 0;
  for (const [tagName, chunkIds] of Object.entries(skillTagGroups)) {
    if (chunkIds.length < 2) continue;
    
    // Read first 3 chunks to form pattern
    const patternParts = [];
    for (const cid of chunkIds.slice(0, 3)) {
      const catDirs = Object.keys(categoryCounts);
      for (const cat of catDirs) {
        const fp = path.join(ACTIVE_DIR, cat, `${cid}.md`);
        if (fs.existsSync(fp)) {
          const content = fs.readFileSync(fp, 'utf-8');
          const body = content.replace(/^---[\s\S]*?---\n?/, '');
          patternParts.push(body.slice(0, 200));
          break;
        }
      }
    }
    
    if (patternParts.length > 0) {
      const skillDir = path.join(SKILLS_DIR, tagName);
      fs.mkdirSync(skillDir, { recursive: true });
      const skillId = hash(`${tagName}:${chunkIds[0]}`);
      const skillContent = [
        '---',
        `id: ${skillId}`,
        `name: "${tagName} skill (${chunkIds.length} chunks)"`,
        `category: ${tagName}`,
        `strength: ${Math.min(1, chunkIds.length / 10).toFixed(2)}`,
        `chunkCount: ${chunkIds.length}`,
        '---',
        '',
        `# ${tagName} Skill Pattern`,
        '',
        patternParts.join('\n---\n'),
        '',
      ].join('\n');
      fs.writeFileSync(path.join(skillDir, `${skillId}.md`), skillContent);
      skillCount++;
    }
  }
  
  // Build index
  console.log('[3/3] Building vault index...');
  const index = {
    totalChunks,
    activeChunks: totalChunks,
    dissolvedChunks: 0,
    skills: skillCount,
    categories: categoryCounts,
    skillTags: Object.fromEntries(Object.entries(skillTagGroups).map(([k, v]) => [k, v.length])),
    totalFiles,
    totalSourceChars: totalChars,
    avgChunkSize: totalChunks > 0 ? Math.round(totalChars / totalChunks) : 0,
    lastIngestion: Date.now(),
    vaultPath: VAULT_DIR,
    engine: 'micro-chunk-containment-v2',
  };
  
  fs.writeFileSync(path.join(INDEX_DIR, 'vault-index.json'), JSON.stringify(index, null, 2));
  
  // Print stats
  console.log('\n' + '═'.repeat(60));
  console.log('  INGESTION COMPLETE');
  console.log('═'.repeat(60));
  console.log(`  Files processed:   ${totalFiles}`);
  console.log(`  Total chunks:      ${totalChunks}`);
  console.log(`  Extracted skills:  ${skillCount}`);
  console.log(`  Avg chunk size:    ${index.avgChunkSize} chars`);
  console.log(`  Source data:       ${(totalChars / 1024).toFixed(0)} KB`);
  console.log(`  Categories:        ${Object.keys(categoryCounts).length}`);
  console.log();
  console.log('  Category breakdown:');
  for (const [cat, count] of Object.entries(categoryCounts).sort((a, b) => b[1] - a[1])) {
    const bar = '█'.repeat(Math.min(30, Math.round(count / (totalChunks / 30))));
    console.log(`    ${cat.padEnd(18)} ${String(count).padStart(5)} ${bar}`);
  }
  console.log();
  console.log('  Skill tags:');
  for (const [tag, count] of Object.entries(index.skillTags).sort((a, b) => b[1] - a[1])) {
    console.log(`    ${tag.padEnd(15)} ${count} chunks`);
  }
  console.log('═'.repeat(60));
}

main().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});
