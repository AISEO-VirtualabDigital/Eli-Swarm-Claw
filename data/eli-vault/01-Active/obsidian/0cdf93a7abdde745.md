---
id: 0cdf93a7abdde745
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: 9c00b24ae54c31c62e02
createdAt: 1786051359181
embeddingSig: "agent:choice:keyed|choice:keyed:skill|keyed:skill:same|path:used:skillicons|record:string:string|same:stable:path|skill:agent:choice|skill:same:stable|skillicons:record:string|stable:path:used|string:skill:agent|string:string:skill"
---
*/
  skillIcons: Record<string, string>;
  /**
   * Per-skill AGENT choice, keyed by skill id (the same stable path used in
   * `skillIcons`/`pinnedSkillIds`). The value is a discriminated object
   * (`{kind:'default'}` | `{kind:'builtin',name}` | `{kind:'custom',path}`); an
   * absent key = the Default agent.