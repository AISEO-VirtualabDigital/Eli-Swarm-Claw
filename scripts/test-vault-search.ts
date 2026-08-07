import { searchVault, getVaultContext, getVaultStats, buildVaultKnowledgeMap } from '../src/lib/vault-search';

async function test() {
  console.log('=== Test 1: getVaultStats ===');
  const stats = await getVaultStats();
  console.log(JSON.stringify(stats, null, 2));
  
  console.log('\n=== Test 2: searchVault ===');
  const results = await searchVault('parasite seo', { maxResults: 3 });
  console.log('Results:', results.length);
  for (const r of results) {
    console.log(' -', r.chunk.title, '| score:', r.score, '| dissolved:', r.chunk.dissolved);
  }
  
  console.log('\n=== Test 3: getVaultContext ===');
  const ctx = await getVaultContext('keyword research', { maxResults: 5, searchContainment: true });
  console.log('Sources:', ctx.sources.length);
  console.log('Containment hits:', ctx.containmentHits);
  console.log('Context length:', ctx.context.length);
  
  console.log('\n=== Test 4: buildVaultKnowledgeMap ===');
  const map = await buildVaultKnowledgeMap();
  console.log(map.slice(0, 300));
}

test().catch(e => console.error(e));
