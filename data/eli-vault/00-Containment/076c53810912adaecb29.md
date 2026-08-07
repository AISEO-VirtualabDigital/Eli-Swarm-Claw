---
id: 948c4cbabea6fb08
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 076c53810912adaecb29
createdAt: 1786051359181
embeddingSig: "adapter:this:vault|const:adapter:this|const:skills:skill|const:start:normalizepath|normalizepath:root:path|path:const:skills|root:path:const|skill:const:adapter|skills:skill:const|start:normalizepath:root|this:vault:adapter|vault:adapter:const"
---
[]> {
    const start = normalizePath(root.path);
    const skills: Skill[] = [];
    const adapter = this.app.vault.adapter;
const files: string[] = [];
    await this.walkAdapter(start, 0, files);

    for (const rel of files) {
      if (!isMarkdown(rel)) continue;
      let content: string;
      try {
        content = await adapter.read(rel);
      } catch (err) {