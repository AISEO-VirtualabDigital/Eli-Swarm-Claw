#!/usr/bin/env python3
"""
Absorb GitHub Google API topic repos into Eli's knowledge base.
Creates consolidated knowledge source files from the top 50 repos.
"""

import json, re
from pathlib import Path

KS_DIR = Path('/home/z/my-project/upload/knowledge-sources')

def write_ks(filename, content):
    path = KS_DIR / filename
    path.write_text(content, encoding='utf-8')
    print(f'  ✅ {filename} ({len(content):,} chars)')

def clean_readme(text):
    """Strip badges, images, excessive whitespace from README"""
    text = re.sub(r'<!\[CDATA[\s\S]*?\]\]>', '', text)
    text = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', text)
    text = re.sub(r'<img[^>]*>', '', text)
    text = re.sub(r'\n{4,}', '\n\n', text)
    return text.strip()

repos = json.load(open('/tmp/gh-google-api-with-readmes.json'))

# ============================================================
# 1. MASTER: GitHub Google API Topic Directory
# ============================================================
print('\n🔵 1. Creating Google API topic directory...')

directory = '# GitHub Google API Topic — Top 50 Repositories\n\n'
directory += f'Source: https://github.com/topics/google-api (2,469 total repos)\n\n'
directory += 'This knowledge covers the top 50 most-starred repositories tagged with google-api on GitHub.\n\n'

# Group by category
groups = {
    'Official Client Libraries & SDKs': [],
    'Google Workspace Tools': [],
    'Google Maps & Places': [],
    'Google AI & Gemini': [],
    'Google Auth & OAuth': [],
    'Google Cloud & Services': [],
    'React/JS/Angular Components': [],
    'Scraping & Meta Search': [],
    'Automation & Integration': [],
    'Mobile & Cross-Platform': [],
}

for r in repos:
    name = r['full_name']
    stars = r['stargazers_count']
    desc = r.get('description') or 'No description'
    lang = r.get('language') or 'N/A'
    topics = r.get('topics', [])
    url = r.get('html_url', f'https://github.com/{name}')
    
    entry = f'### [{name}]({url}) ⭐{stars:,}\n- **Language**: {lang}\n- **Description**: {desc}\n- **Topics**: {', '.join(topics[:8])}\n'
    
    nl = name.lower()
    if 'googleapis/' in nl or 'google-dotnet' in nl or 'aiogoogle' in nl or 'mscraftsman/generative' in nl:
        groups['Official Client Libraries & SDKs'].append(entry)
    elif any(k in nl for k in ['gam-team', 'googleworkspace/cli', 'google admin']):
        groups['Google Workspace Tools'].append(entry)
    elif any(k in nl for k in ['maps', 'places', 'gpup', 'keyless']):
        groups['Google Maps & Places'].append(entry)
    elif any(k in nl for k in ['gemini', 'generative-ai', 'vibe-prompting', 'langchain-coder']):
        groups['Google AI & Gemini'].append(entry)
    elif any(k in nl for k in ['login', 'auth', 'oauth', 'sign-in']):
        groups['Google Auth & OAuth'].append(entry)
    elif any(k in nl for k in ['gkeepapi', 'gmail-tester', 'raccoon', 'youtube-video', 'google-contacts', 'google-meet', 'google-chat', 'gtm-mcp', 'imagedl']):
        groups['Google Cloud & Services'].append(entry)
    elif any(k in nl for k in ['react-google', 'angular-google', 'vue-gapi', 'ng-gapi']):
        groups['React/JS/Angular Components'].append(entry)
    elif any(k in nl for k in ['librex', 'araa', 'secret-regex', 'reverse-image', 'sports-results', 'figma-to-google']):
        groups['Scraping & Meta Search'].append(entry)
    elif any(k in nl for k in ['saas', 'builderbook', 'expenses', 'apps-script', 'openapi', 'resp', 'jobseeker']):
        groups['Automation & Integration'].append(entry)
    elif any(k in nl for k in ['react-native', 'whatsapp']):
        groups['Mobile & Cross-Platform'].append(entry)
    else:
        groups['Official Client Libraries & SDKs'].append(entry)

for group, entries in groups.items():
    if entries:
        directory += f'## {group} ({len(entries)} repos)\n\n'
        directory += '\n'.join(entries) + '\n\n'

write_ks('github-google-api-topic-directory.md', directory)

# ============================================================
# 2. Google API Client Libraries (reference-quality)
# ============================================================
print('\n🟢 2. Creating Google API client library references...')

client_libs = [r for r in repos if any(k in r['full_name'].lower() for k in ['googleapis/', 'aiogoogle', 'mscraftsman/generative', 'google-dotnet'])]

libs_content = '# Google API Client Libraries — Reference\n\n'
libs_content += 'Comprehensive reference for official and popular Google API client libraries.\n\n'

for r in client_libs:
    readme = clean_readme(r.get('_readme', ''))
    libs_content += f'## {r["full_name"]} ⭐{r["stargazers_count"]:,}\n\n'
    libs_content += f'**URL**: {r["html_url"]}\n\n'
    libs_content += f'**Language**: {r.get("language") or "N/A"}\n\n'
    if r.get('description'):
        libs_content += f'**Description**: {r["description"]}\n\n'
    libs_content += f'{readme[:4000]}\n\n---\n\n'

write_ks('google-api-client-libraries.md', libs_content)

# ============================================================
# 3. Google Workspace & Productivity Tools
# ============================================================
print('\n🟡 3. Creating Google Workspace tools reference...')

ws_repos = [r for r in repos if any(k in r['full_name'].lower() for k in ['googleworkspace/cli', 'gam-team', 'gkeepapi', 'gmail-tester', 'google-contacts', 'google-meet', 'google-chat', 'whatsapp', 'google-calendar', 'figma-to-google', 'gpup', 'youtube-video', 'google-places-api', 'gtm-mcp', 'apps-script'])]

ws_content = '# Google Workspace & Productivity API Tools\n\n'
ws_content += 'Tools and libraries for interacting with Google Workspace services: Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin, Photos, YouTube, Contacts, Meet, Places, and Tag Manager.\n\n'

for r in ws_repos:
    readme = clean_readme(r.get('_readme', ''))
    ws_content += f'## {r["full_name"]} ⭐{r["stargazers_count"]:,}\n\n'
    ws_content += f'**URL**: {r["html_url"]}\n\n'
    if r.get('description'):
        ws_content += f'**Description**: {r["description"]}\n\n'
    ws_content += f'{readme[:3000]}\n\n---\n\n'

write_ks('google-workspace-api-tools.md', ws_content)

# ============================================================
# 4. Google Maps, Places & Geo APIs
# ============================================================
print('\n🔴 4. Creating Google Maps/Places reference...')

geo_repos = [r for r in repos if any(k in r['full_name'].lower() for k in ['maps', 'places', 'keyless'])]

geo_content = '# Google Maps, Places & Geolocation API Tools\n\n'
geo_content += 'Libraries and components for Google Maps integration, Places Autocomplete, Geocoding, and reverse image search.\n\n'

for r in geo_repos:
    readme = clean_readme(r.get('_readme', ''))
    geo_content += f'## {r["full_name"]} ⭐{r["stargazers_count"]:,}\n\n'
    geo_content += f'**URL**: {r["html_url"]}\n\n'
    if r.get('description'):
        geo_content += f'**Description**: {r["description"]}\n\n'
    geo_content += f'{readme[:3000]}\n\n---\n\n'

write_ks('google-maps-places-api-tools.md', geo_content)

# ============================================================
# 5. Google AI, Gemini & LLM Tools
# ============================================================
print('\n🟣 5. Creating Google AI/Gemini reference...')

ai_repos = [r for r in repos if any(k in r['full_name'].lower() for k in ['gemini', 'generative-ai', 'vibe-prompting', 'langchain-coder'])]

ai_content = '# Google AI, Gemini & LLM API Tools\n\n'
ai_content += 'Tools for Google Gemini API, generative AI SDKs, and LLM-powered applications.\n\n'

for r in ai_repos:
    readme = clean_readme(r.get('_readme', ''))
    ai_content += f'## {r["full_name"]} ⭐{r["stargazers_count"]:,}\n\n'
    ai_content += f'**URL**: {r["html_url"]}\n\n'
    if r.get('description'):
        ai_content += f'**Description**: {r["description"]}\n\n'
    ai_content += f'{readme[:3000]}\n\n---\n\n'

write_ks('google-ai-gemini-api-tools.md', ai_content)

# ============================================================
# 6. Google Auth & OAuth Libraries
# ============================================================
print('\n🟠 6. Creating Google Auth/OAuth reference...')

auth_repos = [r for r in repos if any(k in r['full_name'].lower() for k in ['login', 'auth', 'oauth', 'sign-in'])]

auth_content = '# Google Authentication & OAuth Libraries\n\n'
auth_content += 'Libraries for Google Sign-In, OAuth 2.0, and authentication across React, Angular, Vue, React Native, and Elixir.\n\n'

for r in auth_repos:
    readme = clean_readme(r.get('_readme', ''))
    auth_content += f'## {r["full_name"]} ⭐{r["stargazers_count"]:,}\n\n'
    auth_content += f'**URL**: {r["html_url"]}\n\n'
    if r.get('description'):
        auth_content += f'**Description**: {r["description"]}\n\n'
    auth_content += f'{readme[:3000]}\n\n---\n\n'

write_ks('google-auth-oauth-libraries.md', auth_content)

# ============================================================
# 7. Scraping, Meta Search & Automation
# ============================================================
print('\n🔵 7. Creating scraping/automation reference...')

scrape_repos = [r for r in repos if any(k in r['full_name'].lower() for k in ['librex', 'araa', 'secret-regex', 'reverse-image', 'sports-results', 'saas', 'builderbook', 'expenses', 'openapi', 'resp', 'jobseeker', 'raccoon', 'imagedl'])]

scrape_content = '# Google-Related Scraping, Meta Search & Automation Tools\n\n'
scrape_content += 'Privacy-respecting meta search engines, API scraping tools, SaaS boilerplates, and automation frameworks that leverage Google APIs.\n\n'

for r in scrape_repos:
    readme = clean_readme(r.get('_readme', ''))
    scrape_content += f'## {r["full_name"]} ⭐{r["stargazers_count"]:,}\n\n'
    scrape_content += f'**URL**: {r["html_url"]}\n\n'
    if r.get('description'):
        scrape_content += f'**Description**: {r["description"]}\n\n'
    scrape_content += f'{readme[:2500]}\n\n---\n\n'

write_ks('google-scraping-automation-tools.md', scrape_content)

# ============================================================
# SUMMARY
# ============================================================
print('\n' + '='*60)
print('✅ GITHUB GOOGLE API TOPIC ABSORPTION COMPLETE')
print('='*60)

new_files = list(KS_DIR.glob('github-google-api-*.md')) + \
            list(KS_DIR.glob('google-api-client-*.md')) + \
            list(KS_DIR.glob('google-workspace-*.md')) + \
            list(KS_DIR.glob('google-maps-*.md')) + \
            list(KS_DIR.glob('google-ai-gemini-*.md')) + \
            list(KS_DIR.glob('google-auth-oauth-*.md')) + \
            list(KS_DIR.glob('google-scraping-automation-*.md'))

total = sum(f.stat().st_size for f in new_files)
for f in sorted(new_files):
    print(f'  {f.name:<50} {f.stat().st_size:>8,} bytes')
print(f'  {"—"*50} {"—":>8}')
print(f'  {len(new_files)} files, {total:,} bytes total')
print(f'\n  Knowledge base total: {len(list(KS_DIR.glob("*")))} files')
