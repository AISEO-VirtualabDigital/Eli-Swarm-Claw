---
id: ae1db492d4d7b255
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: eece7cf7afa2a46cb67a
createdAt: 1786051359181
embeddingSig: "bundle:config:yaml|else:fsops:isdirectory|false:fsops:isfile|fsops:isdirectory:bundle|fsops:isdirectory:fsops|fsops:isfile:kindok|isdirectory:bundle:config|isdirectory:fsops:isdirectory|isfile:kindok:test|kindok:false:fsops|kindok:test:else|test:else:fsops"
---
let kindOk = false;
    if (fsOps.isFile(p)) {
      kindOk = /\.ya?ml$/i.test(p);
    } else if (fsOps.isDirectory && fsOps.isDirectory(p)) {
      // The bundle's config.yaml must be a directly-contained REGULAR file:
      // checked WITHOUT following the final symlink, so a symlinked config.yaml
      // (escaping the bundle) or a config.yaml directory is rejected.
      kindOk =