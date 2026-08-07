---
id: 7943e65e0ac87e97
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool", "warning"]
containmentHash: a5f194fdca2dad8154ef
createdAt: 1786051359181
embeddingSig: "adapter:private:reconcile|claude:obsidian:file|explorer:when:plugin|file:explorer:when|obsidian:file:explorer|patches:vault:adapter|path:surface:dotfiles|plugin:patches:vault|private:reconcile:path|reconcile:path:surface|vault:adapter:private|when:plugin:patches"
---
claude/`) in Obsidian's file explorer
   * (M15). When on, the plugin patches the vault adapter's private reconcile
   * path to surface dotfiles and suppresses the "bad dotfile" warning; when off
   * (default), the explorer behaves normally. Cleanly reverted on toggle-off and
   * on unload.