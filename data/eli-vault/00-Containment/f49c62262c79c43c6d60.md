---
id: afcadadacc990df3
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern", "capability"]
containmentHash: f49c62262c79c43c6d60
createdAt: 1786051359181
embeddingSig: "agent:display:metadata|builtin:name:builtinagentname|builtinagentname:mode:custom|custom:agent:display|custom:path:string|discovered:custom:agent|display:metadata:only|mode:builtin:name|mode:custom:path|name:builtinagentname:mode|path:string:discovered|string:discovered:custom"
---
}
  | { mode: "builtin"; name: BuiltinAgentName }
  | { mode: "custom"; path: string };
/** A discovered custom agent (display metadata + the only argv-bound field, path). */
export interface CustomAgent {
  /**
   * Absolute launch path — the ONLY field that can reach argv. Either a loose
   * YAML config FILE or a BUNDLE directory (`omnigent run <dir>`); never the
   * `config.yaml` inside a bundle.
   */
  path: string;