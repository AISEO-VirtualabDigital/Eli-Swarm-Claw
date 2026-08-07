---
id: f2caca6d6b6e8003
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool"]
containmentHash: cab0101eecb809c3ca6b
createdAt: 1786051359181
embeddingSig: "binarypath:continue:tool|binarypath:resume:last|binarypath:resume:tool|claude:return:binarypath|codex:return:binarypath|continue:tool:isaac|isaac:return:binarypath|resume:tool:codex|return:binarypath:continue|return:binarypath:resume|tool:codex:return|tool:isaac:return"
---
== "claude") return [s.binaryPath, "--continue"];
  if (s.tool === "isaac") return [s.binaryPath, "resume"];
  if (s.tool === "codex") return [s.binaryPath, "resume", "--last"];
  // "custom": best-effort guess (the most common continue flag). If it's wrong,
  // the terminal script surfaces a hint to set a Resume command for the harness.
  return [s.binaryPath, "--continue"];