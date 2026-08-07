---
id: 572b8a71c23ec54b
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern", "capability", "tool", "code"]
containmentHash: 78d0e3fe9ffe11c9c7da
createdAt: 1786051359181
embeddingSig: "anything:else:unknown|built:name:custom|custom:path:outside|else:unknown:kind|exists:anything:else|isvalidcustomagentpath:still:exists|kind:missing:value|missing:value:built|name:custom:path|still:exists:anything|unknown:kind:missing|value:built:name"
---
ses
 * `isValidCustomAgentPath` AND still exists. Anything else — unknown kind,
 * missing value, bad built-in name, custom path outside the scan dir / wrong
 * extension / non-existent — resolves to `{ mode: 'default' }`. `exists` is
 * injected so this stays pure / unit-testable. NEVER consults a display label.
 */
export function resolveAgentLaunch(
  stored: SkillAgent | undefined | null,
  opts: {
    scanDir: string;