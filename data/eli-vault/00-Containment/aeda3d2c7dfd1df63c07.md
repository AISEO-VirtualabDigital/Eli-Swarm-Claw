---
id: 3f02131b22773bd3
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: aeda3d2c7dfd1df63c07
createdAt: 1786051359181
embeddingSig: "bypath:string:skill|const:bypath:string|const:root:settings|const:settings:this|getsettings:const:bypath|root:settings:scanroots|scanroots:root:enabled|settings:scanroots:root|settings:this:getsettings|skill:const:root|string:skill:const|this:getsettings:const"
---
ill[]> {
    const settings = this.getSettings();
    const byPath = new Map<string, Skill>();
for (const root of settings.scanRoots) {
      if (!root.enabled) continue;
      let found: Skill[] = [];
      try {
        if (root.kind === "vault") {
          found = await this.scanVaultRoot(root);
        } else if (root.kind === "adapter") {
          found = await this.scanAdapterRoot(root);