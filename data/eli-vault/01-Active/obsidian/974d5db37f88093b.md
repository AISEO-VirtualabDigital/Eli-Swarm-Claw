---
id: 974d5db37f88093b
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: eaada6d8ce2cf9dc07b5
createdAt: 1786051359181
embeddingSig: "bundle:layout:omnigent|canonical:bundle:layout|config:yaml:canonical|config:yaml:must|contains:regular:file|directly:contains:regular|file:config:yaml|layout:omnigent:config|omnigent:config:yaml|regular:file:config|yaml:canonical:bundle|yaml:must:directly"
---
at DIRECTLY CONTAINS a regular file `config.yaml`
 *              (the canonical bundle layout — `omnigent run <dir>`). The
 *              `config.yaml` must be a directly-contained REGULAR file — checked
 *              with a NON-symlink-following stat (`isRegularFileNoFollow`), so a
 *              symlinked `config.yaml` (which would let the bundle consume a