import {searchKnowledge, getKnowledgeIndex, buildKnowledgeMap} from '../src/lib/knowledge-search';

async function test() {
  const chunks = await getKnowledgeIndex(true);
  console.log(`Total indexed chunks: ${chunks.length}`);
  
  // Test 1: Knowledge Map
  const map = await buildKnowledgeMap();
  console.log(`
Knowledge Map length: ${map.length} chars`);
  console.log('First 500 chars:');
  console.log(map.slice(0, 500));
  
  // Test 2: Synonym expansion
  const queries = [
    'how to extract data from websites',
    'recommend design system',
    'automate my workflow',
    'help me rank on google',
    'build a SaaS product',
    'AI tools for productivity',
  ];
  
  console.log('\n=== SEARCH RESULTS (upgraded) ===');
  for (const q of queries) {
    const r = await searchKnowledge(q, {maxResults: 3, minScore: 1});
    console.log(`\nQuery: "${q}" → ${r.length} results`);
    r.forEach((x: any, i: number) => console.log(`  ${i+1}. [${x.score.toFixed(1)}] ${x.chunk.title} (${x.chunk.category}) [${x.matchedTerms.slice(0,5).join(',')}]`));
  }
}
test().catch(console.error);
