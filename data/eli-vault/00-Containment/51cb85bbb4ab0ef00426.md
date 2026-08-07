---
id: 7e5c1c8cecdaec3d
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: 51cb85bbb4ab0ef00426
createdAt: 1786051359181
embeddingSig: "agent:string:stripcontrolchars|agent:trim:first|agent:typeof:opts|first:resolve:optional|onst:agent:typeof|opts:agent:string|opts:agent:trim|resolve:optional:agent|string:stripcontrolchars:opts|stripcontrolchars:opts:agent|trim:first:resolve|typeof:opts:agent"
---
onst agent =
    typeof opts.agent === "string" ? stripControlChars(opts.agent).trim() : "";
// First resolve the OPTIONAL {agent} token(s). With an agent selected,
  // substitute it within the token (like {prompt}); with none, drop the token
  // AND — if the token was the standalone value of a preceding flag (e.g.
  // `--agent {agent}`) — drop that flag too, so nothing dangles.