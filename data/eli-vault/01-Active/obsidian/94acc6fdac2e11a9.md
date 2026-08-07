---
id: 94acc6fdac2e11a9
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: 1a3cddc97ecf04ff7a8b
createdAt: 1786051359181
embeddingSig: "canonical:tool:folder|const:math:floor|floor:return:const|floor:return:folder|folder:mapping:adapted|folder:scanning:canonical|mapping:adapted:from|math:floor:return|return:const:math|return:folder:scanning|scanning:canonical:tool|tool:folder:mapping"
---
.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ${m % 60}m ago`;
}
### Folder Scanning

// Canonical per-tool folder mapping (M18), adapted from the Agentfiles plugin's
// "Supported Tools" table (https://community.obsidian.md/plugins/agentfiles).
// Each coding assistant keeps its skills / commands / agents in a conventional
// dot-folder.