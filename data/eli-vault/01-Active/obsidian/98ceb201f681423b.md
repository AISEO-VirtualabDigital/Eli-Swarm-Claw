---
id: 98ceb201f681423b
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["metric", "code"]
containmentHash: dbbc7dd2c13ccd6399c2
createdAt: 1786051359181
embeddingSig: "array:empty:strings|array:filesystem:passes|command:array:filesystem|custom:harness:command|empty:array:empty|empty:strings:whose|filesystem:passes:only|harness:command:array|only:empty:array|passes:only:empty|strings:whose:first|whose:first:element"
---
e a custom-harness command array (no filesystem). Passes ONLY if it is
 * a non-empty array of non-empty strings whose FIRST element is an ABSOLUTE path
 * and where at least one element contains the `{prompt}` placeholder. Pure /
 * unit-testable. (Filesystem existence of the binary is checked separately,
 * fail-closed, at launch.)
 */
export function isValidCustomHarnessCommand(command: unknown): command is string[] {