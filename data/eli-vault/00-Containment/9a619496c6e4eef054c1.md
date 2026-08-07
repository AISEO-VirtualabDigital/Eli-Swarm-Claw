---
id: 507ecb0dfcd4c1b3
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 9a619496c6e4eef054c1
createdAt: 1786051359181
embeddingSig: "agent:placeholder:agent|agent:skill:select|command:need:contain|const:harness:agent|contain:export:const|export:const:harness|harness:agent:placeholder|need:contain:export|optional:command:need|placeholder:agent:skill|select:value:prefix|skill:select:value"
---
t is optional: a command need not contain it.
 */
export const HARNESS_AGENT_PLACEHOLDER = "{agent}";
/** The per-skill <select> value prefix identifying a custom-harness choice. */
export const CUSTOM_HARNESS_VALUE_PREFIX = "custom:";
/**
 * A user-defined harness. `command` is an argv template: `command[0]` is the
 * absolute binary, the rest are inert args, and at least one token contains
 * `{prompt}`.