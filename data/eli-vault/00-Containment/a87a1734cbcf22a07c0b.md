---
id: 2f99e1f9b27efddd
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: a87a1734cbcf22a07c0b
createdAt: 1786051359181
embeddingSig: "const:isfileok:opts|file:const:isfileok|isfile:probe:opts|isfile:true:isfileok|isfileok:launchpath:readpath|isfileok:opts:isfile|launchpath:readpath:fallbackname|opts:isfile:probe|opts:isfile:true|probe:opts:isfile|readpath:fallbackname:entry|true:isfileok:launchpath"
---
t is a file.
      const isFileOk = opts.isFile ? probe(abs, opts.isFile) : true;
      if (isFileOk) {
        launchPath = abs;
        readPath = abs;
        fallbackName = entry.replace(/\.ya?ml$/i, "");
      }
    }
    if (launchPath === null && probe(abs, opts.isDirectory)) {
      // BUNDLE DIR: must directly contain a regular `config.yaml`.
      const config = nodePath.join(abs, BUNDLE_CONFIG_NAME);