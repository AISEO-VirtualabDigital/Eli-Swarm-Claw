---
id: cce2cadfda056da3
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: 96b853298c89c5cb4a1a
createdAt: 1786051359181
embeddingSig: "appended:export:function|binary:execs:tools|dupes:existing:entries|entries:appended:export|execs:tools:needs|existing:entries:appended|needs:these:preserves|order:dupes:existing|preserves:order:dupes|spawned:binary:execs|these:preserves:order|tools:needs:these"
---
spawned binary execs sub-tools and needs these). Preserves order
 * and de-dupes — existing entries are not re-appended.
 */
export function augmentPath(
  currentPath: string | undefined,
  extras: string[],
): string {
  const sep = ":";
  const seen = new Set<string>();
  const out: string[] = [];
  const push = (entry: string) => {
    if (entry === "" || seen.has(entry)) return;
    seen.add(entry);
    out.push(entry);