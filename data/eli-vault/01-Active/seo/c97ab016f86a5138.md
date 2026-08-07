---
id: c97ab016f86a5138
source: "seo-writing-skill-README.md"
"title: Awesome SEO Writing Skill"
category: seo
skillTags: ["process", "code"]
containmentHash: 5d6e52eddfedae0ac1f8
createdAt: 1786051359123
embeddingSig: "bash:node:writer|file:then:bash|file:writer:output|fill:ignored:local|ignored:local:file|local:file:then|node:writer:scripts|scripts:upload:file|then:bash:node|upload:file:writer|writer:output:article|writer:scripts:upload"
---
on
```
Fill in the ignored local file, then run:

```bash
node writer/scripts/upload-r2.mjs \
  --file writer/output/<article-slug>/hero-16x9.png \
  --article writer/output/<article-slug>/article.md \
  --manifest writer/output/<article-slug>/image-urls.json \
  --seoName "AI music detector hero" \
  --keyword "AI music detector" \
  --alt "AI music detector workflow hero image"