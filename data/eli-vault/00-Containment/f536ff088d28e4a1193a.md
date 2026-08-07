---
id: c5bce6ba13cc8aa8
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern", "code"]
containmentHash: f536ff088d28e4a1193a
createdAt: 1786051359181
embeddingSig: "agents:invocation:string|argv:export:const|clipboard:text:only|copyable:agents:invocation|export:const:agent|invocation:string:this|never:reaches:argv|only:never:reaches|reaches:argv:export|string:this:clipboard|text:only:never|this:clipboard:text"
---
e copyable Agents-tab invocation string
 * (M10). This is clipboard text only — it never reaches argv.
 */
export const AGENT_INVOCATION_PLACEHOLDER = "<your prompt here>";
/**
 * The exact CLI to start a session with a custom agent, for the Agents-tab
 * "Copy invocation" action (M10): `omnigent run '<agentPath>' -p "<placeholder>"`.
 * `agentPath` MUST be the validated absolute real path (a loose `.yaml`/`.yml`