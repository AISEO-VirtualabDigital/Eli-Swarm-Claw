---
id: 878bd1fbc9692698
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["process"]
containmentHash: da7f65b98dce9bcc6dbc
createdAt: 1786051359181
embeddingSig: "child:ending:yaml|children:kinds:loose|direct:children:kinds|ending:yaml:launch|file:child:ending|file:display:name|kinds:loose:file|launch:path:file|loose:file:child|only:direct:children|path:file:display|yaml:launch:path"
---
ing ONLY direct children of
 * two kinds:
 *   1. LOOSE FILE  — a child ending `.yaml`/`.yml`; the launch path is the FILE,
 *      its display name is read from that file's top-level `name:` (else the
 *      filename stem).
 *   2. BUNDLE DIR  — a child directory that directly contains a regular
 *      `config.yaml`; the launch path is the DIRECTORY (`omnigent run <dir>` is