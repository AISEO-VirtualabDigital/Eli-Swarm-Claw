---
id: e03cf49a79232b9c
source: "browseros-README.md"
"title: Browseros README"
category: knowledge
skillTags: ["code"]
containmentHash: efb0dca6b9af80feae44
createdAt: 1786051353089
embeddingSig: "architecture:both:products|both:products:ship|browseros:architecture:both|docs:browseros:architecture|from:this:monorepo|https:docs:browseros|main:subsystems:browser|monorepo:main:subsystems|products:ship:from|ship:from:this|subsystems:browser:chromium|this:monorepo:main"
---
ocs](https://docs.browseros.com)
## Architecture

Both products ship from this monorepo. Two main subsystems: the **browser** (Chromium fork) and the **agent platform** (TypeScript/Go).
```
BrowserOS/
├── packages/browseros/              # Chromium fork + build system (Python)
│   ├── chromium_patches/            # Patches applied to Chromium source
│   ├── build/                       # Build CLI and modules