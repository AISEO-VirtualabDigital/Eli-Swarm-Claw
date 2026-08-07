---
id: 05d03b8752fb0b58
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: befd4ff7ebbbcca74a3c
createdAt: 1786051359181
embeddingSig: "array:from:bypath|bypath:skill:bypath|bypath:skill:skill|const:skill:found|found:bypath:skill|from:bypath:values|priority:const:skill|return:array:from|skill:bypath:skill|skill:found:bypath|skill:return:array|skill:skill:return"
---
the priority).
      for (const skill of found) {
        if (!byPath.has(skill.id)) byPath.set(skill.id, skill);
      }
    }
return Array.from(byPath.values()).sort((a, b) =>
      a.name.localeCompare(b.name),
    );
  }

  // --- Path 1: Vault API + metadataCache (non-dot folders) ---------------
  private async scanVaultRoot(root: ScanRoot): Promise<Skill[]> {
    const base = this.vaultBasePath();