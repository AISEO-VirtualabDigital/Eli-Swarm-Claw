#!/usr/bin/env python3
"""Phase 2: Read fetched data from JSON and generate knowledge source files."""

import json, re
from pathlib import Path

KS_DIR = Path('/home/z/my-project/upload/knowledge-sources')
TMP_DIR = Path('/tmp/gh-batch3')

def write_ks(filename, content):
    path = KS_DIR / filename
    path.write_text(content, encoding='utf-8')
    print(f'  OK {filename} ({len(content):,} chars)')
    return filename

def clean_readme(text):
    if not text:
        return ''
    text = re.sub(r'<!\[CDATA[\s\S]*?\]\]>', '', text)
    text = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', text)
    text = re.sub(r'<img[^>]*>', '', text)
    text = re.sub(r'\n{4,}', '\n\n', text)
    return text.strip()

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
    readme = clean_readme(repo.get('_readme', ''))
    text = '## ' + name + ' Stars:' + format(stars, ',') + '\n\n'
    text += '**URL**: ' + url + '  \n'
    text += '**Language**: ' + lang + '  \n'
    text += '**Description**: ' + desc + '\n\n'
    if readme:
        text += readme[:max_chars]
    text += '\n\n---\n\n'
    return text

def categorize(repo):
    fn = repo['full_name'].lower()
    desc = (repo.get('description') or '').lower()
    topics = [t.lower() for t in repo.get('topics', [])]
    queries = repo.get('queries', [])
    combined = fn + ' ' + desc + ' ' + ' '.join(topics) + ' ' + ' '.join(queries)

    scores = {}

    crm_kw = ['crm', 'salesforce', 'hubspot', 'erp', 'customer', 'lead generation', 'pipeline', 'contact management']
    scores['crm-sales'] = sum(3 for kw in crm_kw if kw in combined)
    if 'crm' in queries:
        scores['crm-sales'] += 5

    pm_kw = ['project management', 'kanban', 'agile', 'scrum', 'sprint', 'jira', 'asana', 'trello', 'todo', 'gantt', 'task board']
    scores['project-mgmt'] = sum(3 for kw in pm_kw if kw in combined)
    if 'project-management' in queries or 'asana' in queries:
        scores['project-mgmt'] += 5

    seo_kw = ['seo', 'serp', 'ranking', 'keyword', 'backlink', 'ahrefs', 'semrush', 'search engine', 'organic', 'analytics', 'audit', 'crawl', 'site audit']
    scores['seo-marketing'] = sum(3 for kw in seo_kw if kw in combined)
    if any(q in queries for q in ['ahrefs', 'semrush', 'youtube-seo', 'social-media-seo']):
        scores['seo-marketing'] += 5

    copy_kw = ['copywriting', 'copywriter', 'content generation', 'ai writing', 'humanizer', 'paraphrase', 'rewriting', 'jasper', 'ghostwriter']
    scores['copywriting-ai'] = sum(3 for kw in copy_kw if kw in combined)
    if any(q in queries for q in ['humanizer', 'jasper']):
        scores['copywriting-ai'] += 5
    if 'copywriterpro' in fn or 'claude-scientific-writer' in fn or 'whisper-writer' in fn:
        scores['copywriting-ai'] += 8

    cloud_kw = ['cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'k8s', 'docker', 'terraform', 'infrastructure', 'devops', 'serverless']
    scores['cloud-infra'] = sum(3 for kw in cloud_kw if kw in combined)
    if 'cloud' in queries:
        scores['cloud-infra'] += 5

    cyber_kw = ['cybersecurity', 'cyber security', 'security', 'vulnerability', 'penetration', 'pentest', 'exploit', 'malware', 'firewall', 'encryption']
    scores['cybersecurity'] = sum(3 for kw in cyber_kw if kw in combined)
    if 'cyber-security' in queries:
        scores['cybersecurity'] += 5

    design_kw = ['adobe', 'webflow', 'figma', 'sketch', 'creative', 'photoshop', 'illustrator', 'design system', 'ui kit', 'component library']
    scores['design-uiux'] = sum(3 for kw in design_kw if kw in combined)
    if any(q in queries for q in ['adobe', 'webflow', 'ux-ui-promax']):
        scores['design-uiux'] += 5

    llm_kw = ['llm', 'large language model', 'gpt', 'claude', 'gemini', 'llama', 'transformer', 'nlp', 'language model', 'openai', 'anthropic', 'mistral']
    scores['llm-ai'] = sum(3 for kw in llm_kw if kw in combined)
    if 'llm' in queries:
        scores['llm-ai'] += 5
    if 'claude-scientific-writer' in fn:
        scores['llm-ai'] += 3

    vps_kw = ['vps', 'virtual private server', 'hosting', 'self-host', 'selfhost', 'homelab', 'server provisioning']
    scores['vps-hosting'] = sum(3 for kw in vps_kw if kw in combined)
    if 'vps' in queries:
        scores['vps-hosting'] += 5

    db_kw = ['database', 'sql', 'postgres', 'mysql', 'mongodb', 'redis', 'sqlite', 'orm', 'query builder', 'data store']
    scores['database'] = sum(3 for kw in db_kw if kw in combined)
    if 'database' in queries:
        scores['database'] += 5

    best_cat = max(scores, key=scores.get)
    if scores[best_cat] == 0:
        return None
    return best_cat

CATEGORY_LABELS = {
    'crm-sales': 'CRM & Sales Tools',
    'project-mgmt': 'Project Management',
    'seo-marketing': 'SEO & Marketing (Ahrefs/Semrush/YouTube/Social)',
    'copywriting-ai': 'Copywriting & AI Content',
    'cloud-infra': 'Cloud & Infrastructure',
    'cybersecurity': 'Cybersecurity',
    'design-uiux': 'Design & UI/UX (Adobe/Webflow)',
    'llm-ai': 'LLM & AI Frameworks',
    'vps-hosting': 'VPS & Hosting',
    'database': 'Database',
}

# Load data
print('Loading data from Phase 1...')
with open(TMP_DIR / 'batch3-all-data.json', 'r') as f:
    all_repos_raw = json.load(f)

print('Loaded ' + str(len(all_repos_raw)) + ' repos')

# Categorize
categorized = {cat: [] for cat in CATEGORY_LABELS}
uncategorized = []

for repo in all_repos_raw:
    cat = categorize(repo)
    if cat:
        categorized[cat].append(repo)
    else:
        uncategorized.append(repo)

for cat in categorized:
    categorized[cat].sort(key=lambda r: r.get('stars', 0), reverse=True)

print('\nCategory distribution:')
for cat, repos in categorized.items():
    label = CATEGORY_LABELS[cat]
    print('  ' + label + ': ' + str(len(repos)) + ' repos')
print('  Uncategorized: ' + str(len(uncategorized)) + ' repos')

# Generate files
print('\nGenerating knowledge source files...')
files_created = []

# File 1: Master Directory
dir_parts = ['# GitHub Multi-Topic Repository Directory', '']
dir_parts.append('Source: 22 GitHub URLs (17 search queries + 4 direct repos + 1 duplicate).')
dir_parts.append('Queries: crm, project management, asana, ahrefs, semrush, cloud, cyber security, adobe, webflow, youtube seo, social media seo, humanizer, ux ui promax, llm, VPS, database, jasper.')
dir_parts.append('')
dir_parts.append('Total unique repositories indexed: ' + str(len(all_repos_raw)))
dir_parts.append('')

for cat_key, repos in categorized.items():
    if repos:
        label = CATEGORY_LABELS[cat_key]
        dir_parts.append('## ' + label + ' (' + str(len(repos)) + ' repos)')
        dir_parts.append('')
        for repo in repos[:25]:
            dir_parts.append(make_entry(repo))
        if len(repos) > 25:
            dir_parts.append('*... and ' + str(len(repos) - 25) + ' more*')
            dir_parts.append('')

dir_parts.append('## Uncategorized (' + str(len(uncategorized)) + ' repos)')
dir_parts.append('')
for repo in uncategorized[:30]:
    dir_parts.append(make_entry(repo))

fname = write_ks('github-multi-topic-directory.md', '\n'.join(dir_parts))
files_created.append(fname)

# Category-specific files
CATEGORY_FILES = {
    'crm-sales': ('github-crm-sales-tools.md', 'CRM & Sales Tools', 'Open-source CRM, sales automation, lead management, and customer relationship platforms.'),
    'project-mgmt': ('github-project-management-tools.md', 'Project Management Tools', 'Project management, task tracking, Kanban boards, agile/scrum tools, and team collaboration platforms.'),
    'seo-marketing': ('github-seo-marketing-tools.md', 'SEO & Marketing Tools', 'SEO analysis, keyword research, SERP tracking, YouTube SEO, social media optimization, and digital marketing tools.'),
    'copywriting-ai': ('github-copywriting-ai-content.md', 'Copywriting & AI Content', 'AI-powered copywriting, content humanizers, text generators, scientific writing, and AI content frameworks.'),
    'cloud-infra': ('github-cloud-infrastructure-tools.md', 'Cloud & Infrastructure', 'Cloud platforms, DevOps tools, IaC, container orchestration, and cloud management.'),
    'cybersecurity': ('github-cybersecurity-tools.md', 'Cybersecurity Tools', 'Security auditing, pentesting, vulnerability scanners, and cybersecurity frameworks.'),
    'design-uiux': ('github-design-ui-ux-tools.md', 'Design & UI/UX Tools', 'Design systems, UI/UX frameworks, Adobe integrations, Webflow tools, and creative workflows.'),
    'llm-ai': ('github-llm-ai-frameworks.md', 'LLM & AI Frameworks', 'LLM frameworks, AI agents, prompt engineering, and AI application development.'),
    'vps-hosting': ('github-vps-hosting-tools.md', 'VPS & Hosting', 'VPS management, server provisioning, self-hosting, and hosting automation.'),
    'database': ('github-database-tools.md', 'Database Tools', 'Database management, ORMs, database UIs, migration frameworks, and data storage.'),
}

for cat_key, repos in categorized.items():
    if not repos:
        continue
    filename, title, intro = CATEGORY_FILES[cat_key]
    parts = ['# ' + title + ' — GitHub Repositories', '', intro, '']
    for repo in repos[:20]:
        parts.append(make_readme_entry(repo, 3000))
    fname = write_ks(filename, '\n'.join(parts))
    files_created.append(fname)

# Summary
print('\n' + '=' * 60)
print('BATCH 3 FILE GENERATION COMPLETE')
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
