---
id: ff5c43aebabb7e0e
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool"]
containmentHash: 9ce1bdfd957b7b529996
createdAt: 1786051359181
embeddingSig: "agent:format:frontmatter|agents:files:claude|claude:code:agent|code:agent:format|description:tools:model|files:claude:code|format:frontmatter:name|frontmatter:name:description|laude:agents:files|model:system:prompt|name:description:tools|tools:model:system"
---
laude/agents/*.md` files (Claude Code's own agent
// format: frontmatter name/description/tools/model + a system-prompt body).
// These are ORTHOGONAL to omnigent YAML agents: they apply only when the harness
// is a claude-based CUSTOM harness, and are passed via the `{agent}` placeholder
// (see HARNESS_AGENT_PLACEHOLDER).