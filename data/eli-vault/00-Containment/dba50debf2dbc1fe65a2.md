---
id: 88d68d45d2e04f44
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern", "code"]
containmentHash: dba50debf2dbc1fe65a2
createdAt: 1786051359181
embeddingSig: "always:present:pure|auto:entry:always|else:auto:entry|entry:always:present|export:function:resolvepreferredterminal|function:resolvepreferredterminal:preferredid|lable:else:auto|present:pure:unit|pure:unit:testable|resolvepreferredterminal:preferredid:string|testable:export:function|unit:testable:export"
---
lable, else the `auto` entry
 * (always present). Pure / unit-testable.
 */
export function resolvePreferredTerminal(
  preferredId: string | undefined | null,
  detected: DetectedTerminal[],
): DetectedTerminal {
  if (typeof preferredId === "string" && preferredId) {
    const match = detected.find((d) => d.def.id === preferredId);
    if (match) return match;
  }
  const auto = detected.find((d) => d.def.id === "auto");