---
id: b7be29ecaa00aa6a
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 8a581b1a850f13204ea1
createdAt: 1786051359181
embeddingSig: "decodeharnesschoice:value:string|default:export:function|export:function:decodeharnesschoice|function:decodeharnesschoice:value|harness:name:null|name:null:default|null:default:export|null:return:isallowedharness|omnigentharness:null:return|string:omnigentharness:null|value:harness:name|value:string:omnigentharness"
---
ion value to a harness name, or null for Default. */
export function decodeHarnessChoice(value: string): OmnigentHarness | null {
  return isAllowedHarness(value) ? value : null;
}
// =====================================================================
// CUSTOM (user-defined) harnesses (M15.3) — the escape hatch for a command the
// built-in omnigent `--harness` set does not cover (e.g.