---
id: b1ffa9e450c5bbf1
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: ea1bca06520dee5b80a6
createdAt: 1786051359181
embeddingSig: "binary:supported:tool|command:binary:supported|custom:harness:command|export:function:sessiontoolfromcommand|function:sessiontoolfromcommand:binary|harness:command:binary|null:export:function|return:startedat:session|session:custom:harness|startedat:session:custom|supported:tool:null|tool:null:export"
---
return now - s.startedAt >= SESSION_MAX_AGE_MS;
}
/** Map a custom-harness command's binary to a supported tool, or null. */
export function sessionToolFromCommand(binary: string): SessionTool | null {
  const base = (binary.split("/").pop() ?? binary).toLowerCase();
  if (base === "claude") return "claude";
  if (base === "codex") return "codex";
  if (base === "isaac") return "isaac";
  return null;