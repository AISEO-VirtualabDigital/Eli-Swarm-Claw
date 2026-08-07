---
id: bf54c60a2e6adfb2
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["capability", "tool"]
containmentHash: 938539cee0161e96ff43
createdAt: 1786051359181
embeddingSig: "arbitrary:external:commands|commands:skill:harness|dropdown:select:instead|each:label:command|external:commands:skill|harness:dropdown:select|harness:each:label|instead:omnigent:harness|omnigent:harness:each|rnesses:arbitrary:external|select:instead:omnigent|skill:harness:dropdown"
---
rnesses (M15.3) — arbitrary external commands the
   * per-skill Harness dropdown can select instead of an omnigent `--harness`.
   * Each is `{id, label, command[]}` where `command[0]` is an absolute binary
   * and one token holds `{prompt}`. This is the plugin's only non-omnigent spawn
   * target; every launch re-validates fail-closed (`resolveSkillHarness` +