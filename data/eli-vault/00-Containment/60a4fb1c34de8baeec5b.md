---
id: aea3d7f548cf15ea
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 60a4fb1c34de8baeec5b
createdAt: 1786051359181
embeddingSig: "async:walkadapter:string|depth:number:string|descend:folders:ourselves|folders:ourselves:private|number:string:promise|ourselves:private:async|private:async:walkadapter|promise:void:depth|recursive:descend:folders|string:depth:number|string:promise:void|walkadapter:string:depth"
---
` is non-recursive — descend `folders` ourselves. */
  private async walkAdapter(
    dir: string,
    depth: number,
    out: string[],
  ): Promise<void> {
    if (depth > MAX_DEPTH) return;
    const adapter = this.app.vault.adapter;
    let listed;
    try {
      listed = await adapter.list(dir);
    } catch {
      return; // missing/unreadable folder — skip quietly
    }
    for (const f of listed.files) out.push(f);