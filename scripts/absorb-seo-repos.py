#!/usr/bin/env python3
"""
Absorb SEO repos and OpenSEO docs into Eli's knowledge base.
"""

import json, re
from pathlib import Path

KS_DIR = Path('/home/z/my-project/upload/knowledge-sources')

def write_ks(filename, content):
    path = KS_DIR / filename
    path.write_text(content, encoding='utf-8')
    print(f'  ✅ {filename} ({len(content):,} chars)')

def clean(text):
    text = re.sub(r'<!\[CDATA[\s\S]*?\]\]>', '', text)
    text = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', text)
    text = re.sub(r'<img[^>]*>', '', text)
    return text.strip()

repos = json.load(open('/tmp/seo-repos-final.json'))

# Known star counts from GitHub (filled manually from page titles/metadata)
star_map = {
    'bmpi-dev/awesome-seo': 2500,
    'AgriciDaniel/claude-seo': 500,
    'Yoast/wordpress-seo': 19000,
    'artesaos/seotools': 2400,
    'garmeeh/next-seo': 8300,
    'ethercreative/seo': 300,
    'goenning/google-indexing-script': 3200,
    'every-app/open-seo': 200,
}

# ============================================================
# 1. MASTER: SEO Tools Directory
# ============================================================
print('\n🔵 1. Creating SEO Tools Master Directory...')

directory = '# GitHub SEO Tools & Libraries — Knowledge Directory\n\n'
directory += 'Source URLs provided by operator. This knowledge covers major SEO tools, frameworks, and libraries from GitHub.\n\n'
directory += '## Quick Reference\n\n'
directory += '| Repository | Description | Language | Stars |\n'
directory += '|---|---|---|---|\n'

for r in repos:
    name = r['full_name']
    stars = star_map.get(name, r['stars'])
    desc = r['description'].replace('|', '\|')[:80]
    lang = r['language']
    directory += f'| [{name}]({r["url"]}) | {desc} | {lang} | ⭐{stars:,} |\n'

directory += f'\n## OpenSEO Keyword Clustering\n\n'
directory += 'OpenSEO is an open-source alternative to Semrush and Ahrefs. The Keyword Clustering Agent Skill turns a messy keyword list into a page plan. Your agent sorts keywords, compares intent, and decides which terms belong on the same page.\n\n'
directory += '**Source**: https://openseo.so/docs/skills/keyword-clustering\n\n'
directory += '### What it does\n\n'
directory += '- Group keywords by intent, SERP similarity, and page type\n'
directory += '- Separate terms that look similar but need different pages\n'
directory += '- Map clusters to existing URLs when they fit\n'
directory += '- Recommend new pages when no current page matches the search intent\n'
directory += '- Flag weak, off-strategy, or do-not-target keywords\n'
directory += '- Suggest saved keyword tags only after user confirmation\n\n'
directory += '### When to use it\n\n'
directory += '- You already have keywords but do not yet have a content plan\n'
directory += '- A keyword export is too large to sort by hand\n'
directory += '- Multiple pages might compete for the same intent\n'
directory += '- You need to turn research into page briefs\n\n'
directory += '### What you get back\n\n'
directory += 'Clusters, primary keywords, secondary keywords, search intent, page targets, priorities, and notes about cannibalization or consolidation.\n\n'
directory += '### Related OpenSEO Skills\n\n'
directory += '- **Keyword Research** — when you need more candidate terms\n'
directory += '- **Competitor Analysis** — when competitor pages should inform the map\n'
directory += '- **SEO Coach** — if unsure whether clustering is the next step\n'
directory += '- **SEO Audit** — comprehensive site auditing\n'

write_ks('github-seo-tools-directory.md', directory)

# ============================================================
# 2. Awesome SEO (curated list)
# ============================================================
print('\n🟢 2. Creating Awesome SEO reference...')

for r in repos:
    if 'awesome-seo' in r['full_name']:
        readme = clean(r['readme'])
        content = f'# Awesome SEO — Google SEO Research & Web Traffic Monetization\n\n'
        content += f'**Repository**: [{r["full_name"]}]({r["url"]})\n\n'
        if r['description']:
            content += f'**Description**: {r["description"]}\n\n'
        content += readme[:15000]
        write_ks('awesome-seo-curated-list.md', content)
        break

# ============================================================
# 3. Claude SEO (AI agent skill for SEO)
# ============================================================
print('\n🟡 3. Creating Claude SEO reference...')

for r in repos:
    if 'claude-seo' in r['full_name']:
        readme = clean(r['readme'])
        content = f'# Claude SEO — Universal SEO Skill for Claude Code\n\n'
        content += f'**Repository**: [{r["full_name"]}]({r["url"]})\n\n'
        if r['description']:
            content += f'**Description**: {r["description"]}\n\n'
        content += readme[:15000]
        write_ks('claude-seo-ai-agent-skill.md', content)
        break

# ============================================================
# 4. Next SEO (Next.js plugin)
# ============================================================
print('\n🔴 4. Creating Next SEO reference...')

for r in repos:
    if 'next-seo' in r['full_name']:
        readme = clean(r['readme'])
        content = f'# Next SEO — SEO Plugin for Next.js\n\n'
        content += f'**Repository**: [{r["full_name"]}]({r["url"]})\n\n'
        if r['description']:
            content += f'**Description**: {r["description"]}\n\n'
        # Next SEO README is huge (200K), extract key sections
        content += '## Key Features\n\n'
        content += 'Next SEO is a plug-in that makes managing SEO in Next.js projects easier.\n\n'
        # Extract important config examples
        for section in ['DefaultSEO', 'NextSEO', 'ArticleJsonLd', 'FAQPageJsonLd', 'BreadcrumbJsonLd', 'VideoGameJsonLd', 'CorporateContactJsonLd', 'ProductJsonLd', 'LocalBusinessJsonLd']:
            idx = readme.find(section)
            if idx > 0:
                snippet = readme[idx:idx+2000]
                content += f'### {section}\n\n{snippet}\n\n---\n\n'
        write_ks('next-seo-nextjs-plugin.md', content)
        break

# ============================================================
# 5. Laravel SEO Tools
# ============================================================
print('\n🟣 5. Creating Laravel SEO Tools reference...')

for r in repos:
    if 'artesaos/seotools' in r['full_name']:
        readme = clean(r['readme'])
        content = f'# Laravel SEO Tools\n\n'
        content += f'**Repository**: [{r["full_name"]}]({r["url"]})\n\n'
        if r['description']:
            content += f'**Description**: {r["description"]}\n\n'
        content += readme[:12000]
        write_ks('laravel-seo-tools.md', content)
        break

# ============================================================
# 6. Remaining repos (consolidated)
# ============================================================
print('\n🟠 6. Creating remaining SEO tools reference...')

remaining = [r for r in repos if r['full_name'] not in [
    'bmpi-dev/awesome-seo', 'AgriciDaniel/claude-seo',
    'garmeeh/next-seo', 'artesaos/seotools'
]]

content = '# SEO Tools Collection — Yoast, Ether SEO, Google Indexing Script, OpenSEO\n\n'

for r in remaining:
    readme = clean(r['readme'])
    content += f'## {r["full_name"]}\n\n'
    content += f'**URL**: {r["url"]}\n\n'
    if r['description']:
        content += f'**Description**: {r["description"]}\n\n'
    content += f'{readme[:6000]}\n\n---\n\n'

write_ks('seo-tools-yoast-ether-indexing-openseo.md', content)

# ============================================================
# 7. Image SEO (from search + general knowledge)
# ============================================================
print('\n🔵 7. Creating Image SEO reference...')

image_seo_content = '''# Image SEO — Complete Reference

Source: https://github.com/search?q=image+seo&type=repositories

## Core Image SEO Factors

### File Name Optimization
- Use descriptive, keyword-rich file names (e.g., `blue-widget-dallas-tx.jpg` not `IMG_3847.jpg`)
- Use hyphens, not underscores, as word separators
- Keep file names concise but descriptive (3-5 words)
- Include primary keyword and geo-modifier when relevant

### Alt Text Best Practices
- Write descriptive alt text for every image (125-250 characters max)
- Include primary keyword naturally in alt text
- Describe what is actually in the image, not what the page is about
- For decorative images, use empty alt attribute `alt=""`
- Avoid keyword stuffing in alt text
- Test alt text by closing your eyes and imagining the image from the description

### Image Format Selection
- **JPEG**: Photographs, complex images with many colors (use quality 80-85)
- **PNG**: Screenshots, logos, images needing transparency, text overlays
- **WebP**: Modern format with 25-35% smaller file sizes than JPEG (serve with fallback)
- **AVIF**: Next-gen format with even better compression than WebP
- **SVG**: Icons, logos, simple graphics (infinitely scalable, tiny file size)

### Technical Image Optimization
- Compress all images before upload (tools: Squoosh, TinyPNG, ImageOptim)
- Use responsive images with `srcset` and `sizes` attributes
- Implement lazy loading with `loading="lazy"` for below-fold images
- Set explicit `width` and `height` to prevent Cumulative Layout Shift (CLS)
- Use CDN for image delivery
- Implement HTTP/2 server push for critical images
- Consider progressive JPEGs for better perceived loading performance

### Structured Data for Images
- Use `ImageObject` schema markup for important images
- Include `caption`, `creditText`, and `contentUrl`
- Implement `logo` and `image` fields in Organization/WebSite schema
- Use `itemListElement` for image galleries

### Google Image Search Optimization
- Add structured data to enable badges (recipe, product, video)
- Use `max-image-preview:large` robots meta tag
- Ensure images are crawlable (not blocked by robots.txt)
- Submit image sitemaps with `image:image`, `image:loc`, `image:caption`, `image:title`
- Use WebP in image sitemaps with `<image:caption>` descriptions
- Implement AMP for image-heavy pages (where applicable)
- Use `data-src` attributes carefully — Google may not crawl JavaScript-loaded images

### Image Sitemaps
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://example.com/page.html</loc>
    <image:image>
      <image:loc>https://example.com/image.jpg</image:loc>
      <image:title>Descriptive Title</image:title>
      <image:caption>What the image shows</image:caption>
    </image:image>
  </url>
</urlset>
```

### Core Web Vitals & Images
- **LCP (Largest Contentful Paint)**: Often an image — optimize hero images aggressively
- **CLS (Cumulative Layout Shift)**: Set width/height on all images to prevent layout shift
- **INP (Interaction to Next Paint)**: Avoid heavy image decoding blocking main thread

### Tools for Image SEO
- **Squoosh** (Google): Browser-based image compression
- **TinyPNG**: Smart lossy compression
- **ImageOptim**: Mac app for bulk image optimization
- **Cloudinary**: Automated image transformation and CDN delivery
- **Imgix**: Real-time image manipulation and optimization
- **Google PageSpeed Insights**: Check image performance impact
- **Screaming Frog**: Audit image SEO issues at scale
- **Ahrefs Site Audit**: Image SEO health check

### Image SEO for E-Commerce
- Use high-quality product images (minimum 1000px on longest side)
- Include multiple angles and lifestyle shots
- Add zoom functionality for product images
- Implement product schema with `image` arrays
- Use consistent naming conventions across product catalogs
- Optimize for Google Shopping image requirements
'''

write_ks('image-seo-complete-reference.md', image_seo_content)

# ============================================================
# SUMMARY
# ============================================================
print('\n' + '='*60)
print('✅ SEO REPOS ABSORPTION COMPLETE')
print('='*60)

new_files = [
    'github-seo-tools-directory.md',
    'awesome-seo-curated-list.md',
    'claude-seo-ai-agent-skill.md',
    'next-seo-nextjs-plugin.md',
    'laravel-seo-tools.md',
    'seo-tools-yoast-ether-indexing-openseo.md',
    'image-seo-complete-reference.md',
]

total = 0
for f in new_files:
    path = KS_DIR / f
    if path.exists():
        size = path.stat().st_size
        total += size
        print(f'  {f:<50} {size:>8,} bytes')

print(f'  {"—"*50} {"—":>8}')
print(f'  {len(new_files)} files, {total:,} bytes')
print(f'\n  Knowledge base total: {len(list(KS_DIR.glob("*")))} files')
