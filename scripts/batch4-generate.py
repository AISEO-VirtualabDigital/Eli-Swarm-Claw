#!/usr/bin/env python3
"""Batch 4 Phase 2: Categorize 230 new repos and generate knowledge files."""

import json, re
from pathlib import Path

KS_DIR = Path('/home/z/my-project/upload/knowledge-sources')
TMP = Path('/tmp/gh-batch4')

def write_ks(filename, content):
    path = KS_DIR / filename
    path.write_text(content, encoding='utf-8')
    print(f'  OK {filename} ({len(content):,} chars)')
    return filename

def make_entry(repo):
    name = repo['full_name']
    stars = repo.get('stars', 0)
    desc = repo.get('description') or 'No description'
    lang = repo.get('language') or 'N/A'
    topics = repo.get('topics', [])
    url = repo.get('html_url', 'https://github.com/' + name)
    lines = [
        '### [' + name + '](' + url + ') Stars:' + format(stars, ','),
        '- **Language**: ' + lang,
        '- **Description**: ' + desc,
        '- **Topics**: ' + ', '.join(topics[:10]),
        ''
    ]
    return '\n'.join(lines)

def make_readme_entry(repo, max_chars=3500):
    name = repo['full_name']
    stars = repo.get('stars', 0)
    desc = repo.get('description') or 'No description'
    lang = repo.get('language') or 'N/A'
    url = repo.get('html_url', 'https://github.com/' + name)
    readme = repo.get('_readme', '')
    text = '## ' + name + ' Stars:' + format(stars, ',') + '\n\n'
    text += '**URL**: ' + url + '  \n'
    text += '**Language**: ' + lang + '  \n'
    text += '**Description**: ' + desc + '\n\n'
    if readme:
        text += readme[:max_chars]
    text += '\n\n---\n\n'
    return text

# Categorization
def categorize(repo):
    fn = repo['full_name'].lower()
    desc = (repo.get('description') or '').lower()
    topics = [t.lower() for t in repo.get('topics', [])]
    queries = repo.get('queries', [])
    combined = fn + ' ' + desc + ' ' + ' '.join(topics) + ' ' + ' '.join(queries)

    scores = {}

    # Notion ecosystem
    notion_kw = ['notion', 'notes', 'workspace', 'knowledge management', 'wiki', 'document collaboration']
    scores['notion'] = sum(3 for kw in notion_kw if kw in combined)
    if 'notion' in queries: scores['notion'] += 5

    # GoHighLevel / agency tools
    ghl_kw = ['gohighlevel', 'highlevel', 'agency', 'saas platform', 'crm', 'marketing automation', 'funnel', 'landing page']
    scores['gohighlevel-agency'] = sum(3 for kw in ghl_kw if kw in combined)
    if 'gohighlevel' in queries: scores['gohighlevel-agency'] += 5

    # Automation
    auto_kw = ['automation', 'workflow', 'zapier', 'n8n', 'make', 'ifttt', 'trigger', 'integration', 'no-code', 'low-code', 'rpa', 'bot']
    scores['automation'] = sum(3 for kw in auto_kw if kw in combined)
    if 'automation' in queries or 'automation-p3' in queries: scores['automation'] += 5

    # Backlink
    bl_kw = ['backlink', 'link building', 'seo', 'serp', 'keyword', 'rank', 'organic search', 'link analysis']
    scores['backlink-seo'] = sum(3 for kw in bl_kw if kw in combined)
    if 'backlink' in queries: scores['backlink-seo'] += 5

    # Executive assistant
    ea_kw = ['executive assistant', 'virtual assistant', 'scheduling', 'calendar', 'meeting', 'email management', 'personal assistant', 'productivity']
    scores['exec-assistant'] = sum(3 for kw in ea_kw if kw in combined)
    if 'executive-assistant' in queries: scores['exec-assistant'] += 5

    # Social media manager
    smm_kw = ['social media', 'instagram', 'twitter', 'facebook', 'linkedin', 'content calendar', 'social posting', 'social scheduling', 'influencer']
    scores['social-media'] = sum(3 for kw in smm_kw if kw in combined)
    if 'social-media-manager' in queries: scores['social-media'] += 5

    # Shopify SEO
    shopify_kw = ['shopify', 'ecommerce', 'e-commerce', 'store', 'product listing', 'commerce', 'woocommerce']
    scores['shopify-ecommerce'] = sum(3 for kw in shopify_kw if kw in combined)
    if 'shopify-seo' in queries: scores['shopify-ecommerce'] += 5

    best_cat = max(scores, key=scores.get)
    if scores[best_cat] == 0:
        return None
    return best_cat

CATEGORY_LABELS = {
    'notion': 'Notion & Knowledge Management',
    'gohighlevel-agency': 'GoHighLevel & Agency Tools',
    'automation': 'Automation & Workflow',
    'backlink-seo': 'Backlink & SEO Tools',
    'exec-assistant': 'Executive & Virtual Assistant',
    'social-media': 'Social Media Management',
    'shopify-ecommerce': 'Shopify & E-Commerce',
}

# Load data
print('Loading batch 4 data...')
with open(TMP / 'batch4-enriched.json') as f:
    repos = json.load(f)
print(f'Loaded {len(repos)} repos')

# Categorize
categorized = {cat: [] for cat in CATEGORY_LABELS}
uncategorized = []

for repo in repos:
    cat = categorize(repo)
    if cat:
        categorized[cat].append(repo)
    else:
        uncategorized.append(repo)

for cat in categorized:
    categorized[cat].sort(key=lambda r: r.get('stars', 0), reverse=True)

print('\nCategory distribution:')
for cat, rlist in categorized.items():
    label = CATEGORY_LABELS[cat]
    print(f'  {label}: {len(rlist)} repos')
print(f'  Uncategorized: {len(uncategorized)} repos')

# Generate files
print('\nGenerating knowledge source files...')
files_created = []

# File 1: Master Directory
dir_parts = ['# GitHub Batch 4 — Additional Repositories', '']
dir_parts.append('Source: 8 new GitHub search queries (backlink, automation p1+p3, executive assistant, social media manager, shopify SEO, notion, gohighlevel).')
dir_parts.append('230 new unique repos not in previous batches.')
dir_parts.append('')

for cat_key, rlist in categorized.items():
    if rlist:
        label = CATEGORY_LABELS[cat_key]
        dir_parts.append('## ' + label + ' (' + str(len(rlist)) + ' repos)')
        dir_parts.append('')
        for repo in rlist[:25]:
            dir_parts.append(make_entry(repo))
        if len(rlist) > 25:
            dir_parts.append('*... and ' + str(len(rlist) - 25) + ' more*')
            dir_parts.append('')

dir_parts.append('## Uncategorized (' + str(len(uncategorized)) + ' repos)')
dir_parts.append('')
for repo in uncategorized[:30]:
    dir_parts.append(make_entry(repo))

fname = write_ks('github-batch4-directory.md', '\n'.join(dir_parts))
files_created.append(fname)

# Category-specific files
CATEGORY_FILES = {
    'notion': ('github-notion-tools.md', 'Notion & Knowledge Management Tools', 'Notion API tools, plugins, alternatives, templates, and knowledge management platforms.'),
    'gohighlevel-agency': ('github-gohighlevel-agency-tools.md', 'GoHighLevel & Agency Tools', 'GoHighLevel integrations, agency management, CRM, funnel builders, and marketing automation platforms.'),
    'automation': ('github-automation-workflow-tools.md', 'Automation & Workflow Tools', 'Automation frameworks, workflow engines, integration platforms, RPA tools, and no-code automation.'),
    'backlink-seo': ('github-backlink-seo-tools.md', 'Backlink & SEO Tools', 'Backlink analysis, link building, SEO audit tools, SERP tracking, and keyword research.'),
    'exec-assistant': ('github-executive-assistant-tools.md', 'Executive & Virtual Assistant Tools', 'AI executive assistants, virtual assistant platforms, scheduling automation, and productivity tools.'),
    'social-media': ('github-social-media-tools.md', 'Social Media Management Tools', 'Social media schedulers, content management, analytics, cross-platform posting, and influencer tools.'),
    'shopify-ecommerce': ('github-shopify-ecommerce-tools.md', 'Shopify & E-Commerce Tools', 'Shopify apps, e-commerce platforms, product management, and online store optimization.'),
}

for cat_key, rlist in categorized.items():
    if not rlist:
        continue
    filename, title, intro = CATEGORY_FILES[cat_key]
    parts = ['# ' + title + ' — GitHub Repositories', '', intro, '']
    for repo in rlist[:20]:
        parts.append(make_readme_entry(repo, 3000))
    fname = write_ks(filename, '\n'.join(parts))
    files_created.append(fname)

# Summary
print('\n' + '=' * 60)
print('BATCH 4 FILE GENERATION COMPLETE')
print('=' * 60)

total_size = 0
for fname in files_created:
    fpath = KS_DIR / fname
    if fpath.exists():
        size = fpath.stat().st_size
        total_size += size
        print('  ' + fname.ljust(50) + format(size, '>8') + ' bytes')

print('  ' + '-' * 50 + ' ' + '-' * 8)
print('  ' + str(len(files_created)) + ' new files, ' + format(total_size, ',') + ' bytes total')

all_ks = list(KS_DIR.glob('*'))
all_size = sum(f.stat().st_size for f in all_ks if f.is_file())
print('\n  Knowledge base total: ' + str(len(all_ks)) + ' files, ' + format(all_size, ',') + ' bytes')
print('Done!')
