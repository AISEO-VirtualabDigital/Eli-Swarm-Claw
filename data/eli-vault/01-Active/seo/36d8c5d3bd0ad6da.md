---
id: 36d8c5d3bd0ad6da
source: "seo-writing-skill-README.md"
"title: Awesome SEO Writing Skill"
category: seo
skillTags: ["process", "code"]
containmentHash: 9a0c2cb93e156124464b
createdAt: 1786051359123
embeddingSig: "audit:changed:sections|changed:sections:deliver|configuration:exists:audit|deliver:exact:file|exact:file:paths|exists:audit:changed|file:paths:optional|local:configuration:exists|only:valid:local|paths:optional:cloudflare|sections:deliver:exact|valid:local:configuration"
---
only if valid local R2 configuration exists.
11. Re-audit changed sections and deliver exact file paths.
## Optional Cloudflare R2 Configuration

No cloud configuration is required. To enable R2 uploads:

```bash
cp writer/config/r2.config.example.json writer/config/r2.config.json
```
Fill in the ignored local file, then run: