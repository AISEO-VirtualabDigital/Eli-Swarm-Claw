---
id: 11d8b0ffcc3c8ab8
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 33e130b1d892becdac2e
createdAt: 1786051359181
embeddingSig: "const:meta:parseagentconfigyaml|const:name:meta|meta:name:meta|meta:name:trim|meta:parseagentconfigyaml:text|name:meta:name|name:trim:fallbackname|name:trim:meta|parseagentconfigyaml:text:const|text:const:name|trim:fallbackname:push|trim:meta:name"
---
}
    const meta = parseAgentConfigYaml(text);
    const name = meta.name && meta.name.trim() ? meta.name.trim() : fallbackName;
    out.push({
      path: launchPath,
      name,
      ...(meta.description ? { description: meta.description } : {}),
    });
  }
  return out;
}
// --- UI encode/decode for the per-skill <select> value -----------------
// The dropdown is a flat <select>; its option values are strings.