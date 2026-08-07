---
id: a63efeae8d932aa9
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 556bb36bcaf079cb4fb7
createdAt: 1786051359181
embeddingSig: "agent:default:value|choice:select:option|const:agent:default|default:encode:stored|default:value:default|encode:stored:choice|export:const:agent|option:value:export|select:option:value|stored:choice:select|value:default:encode|value:export:function"
---
).
export const AGENT_DEFAULT_VALUE = "default";

/** Encode a stored choice to its <select> option value. */
export function encodeAgentChoice(agent: SkillAgent | undefined | null): string {
  if (!agent || typeof agent !== "object") return AGENT_DEFAULT_VALUE;
  if (agent.kind === "builtin") return `builtin:${agent.name}`;
  if (agent.kind === "custom") return `custom:${agent.path}`;
  return AGENT_DEFAULT_VALUE;