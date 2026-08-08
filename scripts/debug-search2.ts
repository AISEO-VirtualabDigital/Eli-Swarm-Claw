import { searchVault } from '../src/lib/vault-search';

async function debug() {
  const results = await searchVault('parasite seo', { maxResults: 3 });
  console.log('Results:', results.length);
  for (const r of results) {
    console.log(' -', r.chunk?.title, '| score:', r.score);
  }
}

debug().catch(e => {
  console.error('Error:', e.message);
  console.error(e.stack);
});
