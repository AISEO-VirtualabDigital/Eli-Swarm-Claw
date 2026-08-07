---
id: 2e78d2c6bdf9cd05
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern", "capability", "tool"]
containmentHash: d5afb613fab397f1feb9
createdAt: 1786051359181
embeddingSig: "absolute:path:never|dash:safe:construction|evil:yaml:refused|flag:leading:dash|leading:dash:safe|never:read:flag|onfigs:evil:yaml|outright:absolute:path|path:never:read|read:flag:leading|refused:outright:absolute|yaml:refused:outright"
---
onfigs/evil.yaml`, is refused outright); it is an
 * ABSOLUTE path (so it can never be read as a flag — leading-dash safe by
 * construction); it carries either a `.yaml`/`.yml` extension (a loose file) OR
 * NO file extension at all (a candidate BUNDLE directory `<name>/config.yaml`,
 * whose directory path has no extension) — any OTHER extension (e.g. `.txt`) is
 * rejected here; and it is a direct child of `scanDir`.