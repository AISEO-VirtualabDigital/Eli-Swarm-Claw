---
id: 0c1a3ef9d4a901f5
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["capability", "code"]
containmentHash: bdad9e8baffcba7037b1
createdAt: 1786051359181
embeddingSig: "bundle:config:name|config:yaml:directory|directory:rejected:kindok|fsops:isregularfilenofollow:fsops|fsops:isregularfilenofollow:nodepath|isregularfilenofollow:fsops:isregularfilenofollow|isregularfilenofollow:nodepath:join|join:bundle:config|kindok:fsops:isregularfilenofollow|nodepath:join:bundle|rejected:kindok:fsops|yaml:directory:rejected"
---
config.yaml directory is rejected.
      kindOk =
        !!fsOps.isRegularFileNoFollow &&
        fsOps.isRegularFileNoFollow(nodePath.join(p, BUNDLE_CONFIG_NAME));
    }
    if (!kindOk) return null;
    const real = fsOps.realpath(p);
    const realDir = fsOps.realpath(scanDir);
    // Real, direct child of the real scan dir — closes the symlink gap that the