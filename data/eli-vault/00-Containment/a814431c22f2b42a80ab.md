---
id: 5ddf2ebbc59fc6c7
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: a814431c22f2b42a80ab
createdAt: 1786051359181
embeddingSig: "choice:discriminated:union|data:json:under|discriminated:union:persisted|length:null:return|null:return:skill|persisted:verbatim:data|return:skill:stored|skill:stored:choice|slice:length:null|stored:choice:discriminated|union:persisted:verbatim|verbatim:data:json"
---
l.slice(1, -1);
    }
    out[key] = val.length ? val : null;
  }
  return out;
}
/**
 * The per-skill stored choice (a discriminated union). Persisted verbatim in
 * data.json under `skillAgent[skillId]`. Absent key = Default.
 */
export type SkillAgent =
  | { kind: "default" }
  | { kind: "builtin"; name: string }