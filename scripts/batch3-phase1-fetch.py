#!/usr/bin/env python3
"""Phase 1: Fetch all repos from GitHub search queries + direct repos. Save to JSON."""

import json, time, urllib.request, urllib.parse, base64
from pathlib import Path

TMP_DIR = Path('/tmp/gh-batch3')
TMP_DIR.mkdir(exist_ok=True)

def gh_get(url, retries=2):
    headers = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Eli-Knowledge-Absorber'}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f'  FAIL: {e}')
                return None

def fetch_readme(full_name):
    url = 'https://api.github.com/repos/' + full_name + '/readme'
    data = gh_get(url)
    if not data or 'content' not in data:
        return ''
    try:
        return base64.b64decode(data['content']).decode('utf-8', errors='replace')
    except Exception:
        return ''

SEARCH_QUERIES = [
    ('crm', 'crm'),
    ('project-management', 'project management'),
    ('asana', 'asana'),
    ('ahrefs', 'ahrefs'),
    ('semrush', 'semrush'),
    ('cloud', 'cloud'),
    ('cyber-security', 'cyber security'),
    ('adobe', 'adobe'),
    ('webflow', 'webflow'),
    ('youtube-seo', 'youtube seo'),
    ('social-media-seo', 'social media seo'),
    ('humanizer', 'humanizer'),
    ('ux-ui-promax', 'ux ui promax'),
    ('llm', 'llm'),
    ('vps', 'VPS'),
    ('database', 'database'),
    ('jasper', 'jasper'),
]

DIRECT_REPOS = [
    'CopywriterPro-ai/copywriterproai-backend',
    'garmeeh/next-seo',
    'K-Dense-AI/claude-scientific-writer',
    'savbell/whisper-writer',
]

print('PHASE 1: Fetching search results...')
all_repos = {}
query_assignments = {}

for label, query in SEARCH_QUERIES:
    encoded = urllib.parse.quote(query)
    url = 'https://api.github.com/search/repositories?q=' + encoded + '&sort=stars&order=desc&per_page=30'
    print('  ' + query + ' ...', end=' ', flush=True)
    data = gh_get(url)
    if not data or 'items' not in data:
        print('no results')
    else:
        print(str(data['total_count']) + ' total, got ' + str(len(data['items'])))
        for item in data['items']:
            fn = item['full_name']
            if fn not in all_repos:
                all_repos[fn] = item
            if fn not in query_assignments:
                query_assignments[fn] = []
            if label not in query_assignments[fn]:
                query_assignments[fn].append(label)
    time.sleep(1.2)

print('\nDirect repos...')
for full_name in DIRECT_REPOS:
    print('  ' + full_name + ' ...', end=' ', flush=True)
    if full_name not in all_repos:
        url = 'https://api.github.com/repos/' + full_name
        repo = gh_get(url)
        if repo:
            all_repos[full_name] = repo
            query_assignments[full_name] = ['direct-repo']
            print('OK (' + str(repo.get('stargazers_count', 0)) + ' stars)')
        else:
            print('FAILED')
    else:
        print('already in results')
    time.sleep(0.8)

# Fetch READMEs for top 80
print('\nFetching READMEs for top 80...')
sorted_repos = sorted(all_repos.values(), key=lambda r: r.get('stargazers_count', 0), reverse=True)
for i, repo in enumerate(sorted_repos[:80]):
    fn = repo['full_name']
    if '_readme' in repo:
        continue
    if (i + 1) % 20 == 0:
        print('  Progress: ' + str(i + 1) + '/80')
    readme = fetch_readme(fn)
    repo['_readme'] = readme
    all_repos[fn]['_readme'] = readme
    time.sleep(0.6)

# Save everything
output = []
for fn, repo in all_repos.items():
    output.append({
        'full_name': fn,
        'stars': repo.get('stargazers_count', 0),
        'description': repo.get('description', ''),
        'language': repo.get('language', ''),
        'topics': repo.get('topics', []),
        'html_url': repo.get('html_url', ''),
        'queries': query_assignments.get(fn, []),
        '_readme': repo.get('_readme', '')[:6000],
    })

outpath = TMP_DIR / 'batch3-all-data.json'
with open(outpath, 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print('\nSaved ' + str(len(output)) + ' repos to ' + str(outpath))
print('Phase 1 complete!')
