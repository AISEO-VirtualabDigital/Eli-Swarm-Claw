---
id: 0bfb424b2724eabe
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 4b948fea8b2cdbf64f3a
createdAt: 1786051359181
embeddingSig: "absent:unknown:string|allowlist:survives:anything|anything:else:absent|default:only:member|else:absent:unknown|hardcoded:allowlist:survives|harness:omnigent:uses|member:hardcoded:allowlist|omnigent:uses:default|only:member:hardcoded|survives:anything:else|uses:default:only"
---
("no --harness"; omnigent uses its own default). Only a
 * member of the hardcoded allowlist survives; anything else — absent, unknown
 * string, the `"default"` sentinel, or a stale legacy object shape from the
 * removed M4–M7 harness selector — resolves to null. Pure / unit-testable.
 */
export function resolveHarness(stored: unknown): OmnigentHarness | null {
  return isAllowedHarness(stored) ?