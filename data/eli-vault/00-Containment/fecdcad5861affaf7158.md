---
id: aa125d87b9b1858d
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: fecdcad5861affaf7158
createdAt: 1786051359181
embeddingSig: "building:manual:release|download:main:manifest|enable:node:building|harness:manager:install|install:enable:node|main:manifest:json|manager:install:enable|manifest:json:styles|manual:release:download|node:building:manual|release:download:main|skill:harness:manager"
---
"Skill and Harness Manager"** → Install → Enable. No Node, no building.
**Manual / pre-release:** download `main.js`, `manifest.json`, and `styles.css`
from the [latest release](https://github.com/joeutke-dev/skill-harness-manager/releases)
into `<vault>/.obsidian/plugins/skill-harness-manager/`, then enable it.
## Development

```bash
npm install
npm run typecheck
npm run lint
npm run smoke
npm run build
```