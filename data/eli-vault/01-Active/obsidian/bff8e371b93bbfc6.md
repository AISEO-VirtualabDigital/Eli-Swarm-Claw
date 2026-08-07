---
id: bff8e371b93bbfc6
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern", "code"]
containmentHash: 80eea3e3f7f30758a2dc
createdAt: 1786051359181
embeddingSig: "argv:pure:unit|display:strings:which|export:function:parseagentconfigyaml|function:parseagentconfigyaml:text|never:reach:argv|parseagentconfigyaml:text:string|pure:unit:testable|reach:argv:pure|strings:which:never|testable:export:function|unit:testable:export|which:never:reach"
---
lds two display strings (which never reach argv). Pure / unit-testable.
 */
export function parseAgentConfigYaml(text: string): {
  name: string | null;
  description: string | null;
} {
  const out: { name: string | null; description: string | null } = {
    name: null,
    description: null,
  };
  if (typeof text !== "string") return out;
  for (const line of text.split(/\r?\n/)) {