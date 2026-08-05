#!/usr/bin/env python3
"""Fetch READMEs in batches of 10, saving progress after each batch."""

import json, time, base64, urllib.request
from pathlib import Path

TMP = Path('/tmp/gh-batch3')

def gh_get(url):
    h = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Eli'}
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except:
        return None

def fetch_readme(fn):
    data = gh_get('https://api.github.com/repos/' + fn + '/readme')
    if data and 'content' in data:
        try:
            return base64.b64decode(data['content']).decode('utf-8', errors='replace')
        except:
            return ''
    return ''

import re
def clean(t):
    if not t: return ''
    t = re.sub(r'<!\[CDATA[\s\S]*?\]\]>', '', t)
    t = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', t)
    t = re.sub(r'<img[^>]*>', '', t)
    t = re.sub(r'\n{4,}', '\n\n', t)
    return t.strip()

# Load data
with open(TMP / 'batch3-all-data.json') as f:
    repos = json.load(f)

# Load progress
progress_file = TMP / 'readme-progress.json'
if progress_file.exists():
    done = set(json.load(open(progress_file)))
    print(f'Resuming: {len(done)} already done')
else:
    done = set()

# Sort by stars, take top 80
repos_sorted = sorted(repos, key=lambda r: r.get('stars', 0), reverse=True)
target_repos = [r['full_name'] for r in repos_sorted[:80] if r['full_name'] not in done]

def get_repo_obj(fn):
    for r in repos:
        if r['full_name'] == fn:
            return r
    return None

print(f'Need to fetch {len(target_repos)} READMEs')

BATCH = 10
for i in range(0, len(target_repos), BATCH):
    batch = target_repos[i:i+BATCH]
    for fn in batch:
        print(f'  {fn} ...', end=' ', flush=True)
        readme = fetch_readme(fn)
        if readme:
            obj = get_repo_obj(fn)
            if obj:
                obj['_readme'] = clean(readme)[:5000]
            print(f'OK ({len(readme):,} chars)')
        else:
            print('empty')
        done.add(fn)
        time.sleep(0.6)
    
    # Save progress
    with open(progress_file, 'w') as f:
        json.dump(list(done), f)
    
    # Save enriched data
    with open(TMP / 'batch3-all-data.json', 'w') as f:
        json.dump(repos, f, ensure_ascii=False)
    
    print(f'  Batch done: {len(done)}/80')
    time.sleep(1)

print(f'\nComplete! {len(done)} READMEs fetched')
