---
id: 2ae0ba7f21eab4ff
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 0ff8ffc65d0ad8a95414
createdAt: 1786051359181
embeddingSig: "custom:string:parse|harness:value:into|kind:custom:string|kind:omnigent:name|name:omnigentharness:kind|omnigent:name:omnigentharness|omnigentharness:kind:custom|parse:stored:selected|selected:skill:harness|skill:harness:value|stored:selected:skill|string:parse:stored"
---
}
  | { kind: "omnigent"; name: OmnigentHarness }
  | { kind: "custom"; id: string };
/**
 * Parse a stored/selected per-skill harness value into a choice: a hardcoded
 * omnigent-harness name, a `custom:<id>` reference, or none (Default / anything
 * unrecognized). Pure / unit-testable.
 */
export function parseHarnessValue(value: unknown): HarnessChoice {