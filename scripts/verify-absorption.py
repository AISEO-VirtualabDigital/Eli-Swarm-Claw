#!/usr/bin/env python3
"""
Verify the absorbed knowledge sources can be found and searched.
Mimics the TS knowledge-search logic in Python.
"""

import os, re, json
from pathlib import Path

KS_DIR = Path('/home/z/my-project/upload/knowledge-sources')

SYNONYMS = {
    'obsidian': ['vault', 'note', 'markdown', 'frontmatter', 'wikilink', 'plugin'],
    'eli': ['agent eli', 'eli os', 'virtuallab', 'command center', 'growth intelligence'],
    'skill': ['capability', 'harness', 'stack', 'agent skill', 'skill registry'],
    'workflow': ['automation', 'pipeline', 'dag', 'execution', 'rewiring'],
    'authority': ['human order', 'operator', 'policy', 'governance', 'approval'],
    'seo': ['search engine', 'ranking', 'serp', 'organic', 'backlink', 'keyword'],
}

def extract_category(filename):
    lower = filename.lower()
    if lower.startswith('eli-core-identity') or 'agent-skills' in lower or 'architecture' in lower and 'eli-obsidian' in lower or 'manual-rewiring' in lower:
        return 'eli-core'
    if 'eli-obsidian' in lower or 'obsidian-importer' in lower or 'skill-harness-manager' in lower:
        return 'obsidian'
    if 'agent-eli-v1' in lower:
        return 'agent-eli'
    return 'other'

# Index all new files
new_files = []
for f in sorted(KS_DIR.glob('eli-obsidian-*.md')):
    new_files.append(f)
for f in sorted(KS_DIR.glob('obsidian-importer-*.md')):
    new_files.append(f)
for f in sorted(KS_DIR.glob('skill-harness-*.md')):
    new_files.append(f)
for f in sorted(KS_DIR.glob('agent-eli-v1-*')):
    new_files.append(f)
if (KS_DIR / 'eli-core-identity.md').exists():
    new_files.append(KS_DIR / 'eli-core-identity.md')

print(f'New absorbed files: {len(new_files)}')
print()

# Categorize
by_cat = {}
for f in new_files:
    cat = extract_category(f.name)
    by_cat.setdefault(cat, []).append(f)

print('=== CATEGORIES ===')
for cat, files in sorted(by_cat.items()):
    print(f'  {cat}: {len(files)} files')

# Test searches
print()
print('=== SEARCH TESTS ===')

test_queries = [
    'What are my agent skills?',
    'How does the authority model work?',
    'What is the manual rewiring policy?',
    'Show me the integration registry',
    'What SEO skills do I have?',
    'How does the Obsidian importer work?',
    'What is my execution model?',
    'Tell me about the skill harness manager',
    'What is the sprint plan?',
    'How does the policy engine evaluate actions?',
]

def search(query, files):
    lower_q = query.lower()
    # Expand with synonyms
    expanded = lower_q
    for term, syns in SYNONYMS.items():
        if term in lower_q:
            expanded += ' ' + ' '.join(syns)
    terms = [w for w in re.sub(r'[^a-z0-9 ]', ' ', expanded).split() if len(w) > 2]
    
    results = []
    for f in files:
        content = f.read_text(encoding='utf-8').lower()
        filename = f.name.lower()
        title = filename.replace('-', ' ').replace('.md', '').replace('.json', '')
        
        score = 0
        matched = []
        for t in terms:
            count = content.count(t)
            if count > 0:
                score += count
                if t not in matched:
                    matched.append(t)
            title_count = title.count(t)
            if title_count > 0:
                score += title_count * 5
                if t not in matched:
                    matched.append(t)
        
        if score > 0:
            results.append((f.name, score, matched[:5]))
    
    results.sort(key=lambda x: -x[1])
    return results[:4]

for q in test_queries:
    results = search(q, new_files)
    print(f'\nQ: "{q}"')
    if results:
        for name, score, matched in results:
            print(f'  ✅ {name} (score={score}, terms={matched})')
    else:
        print(f'  ❌ No results')

# Summary
print(f'\n=== TOTAL KNOWLEDGE BASE ===')
all_files = list(KS_DIR.glob('*'))
print(f'Total files in knowledge-sources: {len(all_files)}')
total_bytes = sum(f.stat().st_size for f in all_files if f.is_file())
print(f'Total size: {total_bytes:,} bytes ({total_bytes/1024:.0f} KB)')
print(f'New absorbed files: {len(new_files)}')
print(f'New absorbed bytes: {sum(f.stat().st_size for f in new_files):,} bytes')
