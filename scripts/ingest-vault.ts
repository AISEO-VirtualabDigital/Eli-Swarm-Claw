/**
 * Vault Ingestion Script
 * 
 * Dissolves ALL knowledge files into the Obsidian micro-chunk vault.
 * Run: npx tsx scripts/ingest-vault.ts
 * 
 * What it does:
 * 1. Creates the vault structure (00-Containment, 01-Active, 02-Skills, 03-Index)
 * 2. Reads all 167+ knowledge files
 * 3. Dissolves each into micro-chunks (~350 chars)
 * 4. Extracts skill patterns from chunks
 * 5. Stores everything with containment protection
 * 6. Builds the retrieval index
 */

import { getVault } from '../src/lib/obsidian-chunk-engine';

const KNOWLEDGE_DIR = process.env.KNOWLEDGE_DIR || '/home/z/my-project/data/uploads/knowledge-sources';
const VAULT_DIR = process.env.OBSIDIAN_VAULT_PATH || '/home/z/my-project/data/eli-vault';

async function main() {
  console.log('═'.repeat(60));
  console.log('  ELI VAULT INGESTION — Micro-Chunk Engine');
  console.log('═'.repeat(60));
  console.log(`  Knowledge source: ${KNOWLEDGE_DIR}`);
  console.log(`  Vault target:     ${VAULT_DIR}`);
  console.log('═'.repeat(60));
  console.log();

  const vault = getVault(VAULT_DIR);
  
  console.log('[1/3] Initializing vault structure...');
  await vault.init();
  console.log('  ✓ Vault directories created');
  
  console.log();
  console.log('[2/3] Dissolving knowledge files into micro-chunks...');
  console.log('  This will process all .md, .txt, .json files...');
  console.log();
  
  const startTime = Date.now();
  const totalChunks = await vault.ingestDirectory(KNOWLEDGE_DIR);
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  
  console.log();
  console.log(`  ✓ Dissolved into ${totalChunks} micro-chunks in ${elapsed}s`);
  
  console.log();
  console.log('[3/3] Building vault index...');
  const index = await vault.rebuildIndex();
  
  console.log();
  console.log('═'.repeat(60));
  console.log('  INGESTION COMPLETE');
  console.log('═'.repeat(60));
  console.log(`  Total chunks:      ${index.totalChunks}`);
  console.log(`  Active chunks:     ${index.activeChunks}`);
  console.log(`  Dissolved chunks:  ${index.dissolvedChunks}`);
  console.log(`  Extracted skills:  ${index.skills}`);
  console.log(`  Categories:        ${Object.keys(index.categories).length}`);
  console.log();
  console.log('  Category breakdown:');
  for (const [cat, count] of Object.entries(index.categories).sort((a, b) => b[1] - a[1])) {
    console.log(`    ${cat.padEnd(20)} ${count} chunks`);
  }
  console.log('═'.repeat(60));
}

main().catch(err => {
  console.error('Ingestion failed:', err);
  process.exit(1);
});
