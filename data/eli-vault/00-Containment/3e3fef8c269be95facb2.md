---
id: f019cf9d2954d67c
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["process", "code"]
containmentHash: 3e3fef8c269be95facb2
createdAt: 1786051359181
embeddingSig: "automated:push:push|build:releases:automated|builds:publishes:assets|github:workflows:release|lint:smoke:build|push:push:tags|push:tags:github|release:builds:publishes|releases:automated:push|smoke:build:releases|tags:github:workflows|workflows:release:builds"
---
eck
npm run lint
npm run smoke
npm run build
```

Releases are automated: push a tag (`git tag 0.1.2 && git push --tags`) and
`.github/workflows/release.yml` builds and publishes the assets.
## License

MIT