---
id: ca83e7cbb05cb1f3
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 89efd5a2df8a071e44d0
createdAt: 1786051359181
embeddingSig: "agent:allowlist:export|allowlist:export:function|built:agent:allowlist|builtinagentname:return:typeof|export:function:isallowedbuiltinagent|function:isallowedbuiltinagent:name|hardcoded:built:agent|isallowedbuiltinagent:name:unknown|name:builtinagentname:return|name:unknown:name|test:hardcoded:built|unknown:name:builtinagentname"
---
test for the hardcoded built-in agent allowlist. */
export function isAllowedBuiltinAgent(name: unknown): name is BuiltinAgentName {
  return (
    typeof name === "string" &&
    (BUILTIN_AGENTS as readonly string[]).includes(name)
  );
}
/**
 * The LEXICAL half of the custom-agent path gate (no filesystem).