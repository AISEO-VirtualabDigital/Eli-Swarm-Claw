---
id: ddc4f14c49b2afdf
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: 65bc3e3b7752aa33be88
createdAt: 1786051359181
embeddingSig: "filter:length:harness|harness:omnigent:configured|length:harness:omnigent|line:string:return|line:trim:split|omnigent:configured:parsed|return:line:trim|return:return:line|split:filter:length|string:return:return|trim:split:filter|typeof:line:string"
---
ng[] {
  if (typeof line !== "string") return [];
  return line.trim().split(/\s+/).filter((t) => t.length > 0);
}
/** A harness omnigent has configured (parsed from `omnigent config list`). */
export interface ConfiguredHarness {
  /** Display name exactly as omnigent groups it, e.g. "Claude", "Codex". */
  name: string;
  /** True when at least one credential is configured (not "(none configured)").