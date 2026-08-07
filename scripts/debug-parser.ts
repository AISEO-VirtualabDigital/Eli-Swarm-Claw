import { readFile } from 'fs/promises';
import { join } from 'path';

const ACTIVE_DIR = '/home/z/my-project/data/eli-vault/01-Active';

async function debug() {
  const filePath = join(ACTIVE_DIR, 'seo', '0ad7764ebbcf2b2f.md');
  const content = await readFile(filePath, 'utf-8');
  
  console.log('=== Raw content (first 300 chars) ===');
  console.log(JSON.stringify(content.slice(0, 300)));
  
  // My parser logic
  const fmEnd = content.indexOf('---', 3);
  console.log('\nfmEnd position:', fmEnd);
  
  if (fmEnd === -1) {
    console.log('ERROR: No closing --- found');
    return;
  }
  
  const fmRaw = content.slice(3, fmEnd).trim();
  const body = content.slice(fmEnd + 3).trim();
  
  console.log('\n=== Frontmatter ===');
  console.log(fmRaw);
  
  console.log('\n=== Body (first 200) ===');
  console.log(body.slice(0, 200));
  
  // Test field extraction
  const idRegex = /^id:\s*"?([^"]*)"?$/m;
  const idMatch = fmRaw.match(idRegex);
  console.log('\nID match:', idMatch?.[1]);
  
  const titleRegex = /^title:\s*"?([^"]*)"?$/m;
  const titleMatch = fmRaw.match(titleRegex);
  console.log('Title match:', titleMatch?.[1]);
  
  // Check the actual format more carefully
  const lines = fmRaw.split('\n');
  console.log('\nFM lines:');
  lines.forEach((l, i) => console.log(`  ${i}: ${JSON.stringify(l)}`));
}

debug().catch(console.error);
