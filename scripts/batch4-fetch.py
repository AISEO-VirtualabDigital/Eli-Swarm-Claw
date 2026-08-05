#!/usr/bin/env python3
"""Batch 4: 8 new search queries + merge with existing batch3 data."""

import json, time, urllib.request, urllib.parse, re, base64
from pathlib import Path

KS_DIR = Path('/home/z/my-project/upload/knowledge-sources')
TMP = Path('/tmp/gh-batch4')
TMP.mkdir(exist_ok=True)

def gh_get(url):
    h = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Eli'}
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f'  FAIL: {e}')
        return None

SEARCHES = [
    ('backlink', 'backlink', 1),
    ('automation', 'automation', 1),
    ('automation-p3', 'automation', 3),
    ('executive-assistant', 'executive assistant', 1),
    ('social-media-manager', 'social media manager', 1),
    ('shopify-seo', 'shopify SEO', 1),
    ('notion', 'notion', 1),
    ('gohighlevel', 'gohighlevel', 1),
]

# Load existing repos from batch 3
existing_path = Path('/tmp/gh-batch3/batch3-all-data.json')
if existing_path.exists():
    existing = json.load(open(existing_path))
    existing_fns = {r['full_name'] for r in existing}
    print(f'Loaded {len(existing)} existing repos from batch 3')
else:
    existing = []
    existing_fns = set()
    print('No existing data, starting fresh')

# Fetch searches
all_new = []
for label, query, page in SEARCHES:
    encoded = urllib.parse.quote(query)
    url = f'https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page=30&page={page}'
    print(f'  {query} (p{page}) ...', end=' ', flush=True)
    data = gh_get(url)
    if data and 'items' in data:
        new_count = 0
        for item in data['items']:
            fn = item['full_name']
            if fn not in existing_fns:
                item['_queries'] = [label]
                all_new.append(item)
                existing_fns.add(fn)
                new_count += 1
        print(f'{data["total_count"]:,} total, {new_count} new')
    else:
        print('no results')
    time.sleep(0.8)

print(f'\nNew unique repos: {len(all_new)}')

# Save raw new data
raw = []
for r in all_new:
    raw.append({
        'full_name': r['full_name'],
        'stars': r.get('stargazers_count', 0),
        'description': r.get('description', ''),
        'language': r.get('language', ''),
        'topics': r.get('topics', []),
        'html_url': r.get('html_url', ''),
        'queries': r.get('_queries', []),
    })
with open(TMP / 'batch4-new-repos.json', 'w') as f:
    json.dump(raw, f, indent=2, ensure_ascii=False)

# Fetch READMEs for top 25 new repos
print(f'\nFetching READMEs for top 25...')
def fetch_readme(fn):
    data = gh_get(f'https://api.github.com/repos/{fn}/readme')
    if data and 'content' in data:
        try: return base64.b64decode(data['content']).decode('utf-8', errors='replace')
        except: return ''
    return ''

def clean(t):
    if not t: return ''
    t = re.sub(r'<!\[CDATA[\s\S]*?\]\]>', '', t)
    t = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', t)
    t = re.sub(r'<img[^>]*>', '', t)
    t = re.sub(r'\n{4,}', '\n\n', t)
    return t.strip()

sorted_new = sorted(all_new, key=lambda r: r.get('stargazers_count', 0), reverse=True)[:25]
for i, repo in enumerate(sorted_new):
    fn = repo['full_name']
    readme = fetch_readme(fn)
    if readme:
        repo['_readme'] = clean(readme)[:5000]
        print(f'  OK {fn}')
    else:
        repo['_readme'] = ''
        print(f'  -- {fn}')
    time.sleep(0.5)

# Save enriched new data
enriched = []
for r in sorted(all_new, key=lambda r: r.get('stargazers_count', 0), reverse=True):
    enriched.append({
        'full_name': r['full_name'],
        'stars': r.get('stargazers_count', 0),
        'description': r.get('description', ''),
        'language': r.get('language', ''),
        'topics': r.get('topics', []),
        'html_url': r.get('html_url', ''),
        'queries': r.get('_queries', []),
        '_readme': r.get('_readme', ''),
    })
with open(TMP / 'batch4-enriched.json', 'w') as f:
    json.dump(enriched, f, indent=2, ensure_ascii=False)
print(f'\nSaved {len(enriched)} enriched repos')
print('Phase 1 complete!')
