---
id: 8eecd5ce04db914c
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: d7cc46324150c831791d
createdAt: 1786051359181
embeddingSig: "adapter:this:vault|const:adapter:this|null:const:adapter|null:when:unavailable|path:vault:root|root:null:when|string:null:const|this:vault:adapter|unavailable:vaultbasepath:string|vault:root:null|vaultbasepath:string:null|when:unavailable:vaultbasepath"
---
path to the vault root, or null when unavailable. */
  vaultBasePath(): string | null {
    const adapter = this.app.vault.adapter;
    if (adapter instanceof FileSystemAdapter) return adapter.getBasePath();
    return null;
  }
/** Run all enabled roots, dedupe by absolute path. */
  async scan(): Promise<Skill[]> {
    const settings = this.getSettings();