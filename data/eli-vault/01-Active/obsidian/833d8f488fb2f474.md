---
id: 833d8f488fb2f474
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 98cfedaad121be3a5e33
createdAt: 1786051359181
embeddingSig: "choice:isvalidcustomharnesscommand:command|command:return:kind|const:customharnesses:find|custom:const:customharnesses|custom:harness:return|customharnesses:find:choice|find:choice:isvalidcustomharnesscommand|harness:return:kind|isvalidcustomharnesscommand:command:return|kind:custom:harness|return:kind:custom|return:kind:none"
---
=== "custom") {
    const h = (customHarnesses ?? []).find((c) => c && c.id === choice.id);
    if (h && isValidCustomHarnessCommand(h.command)) {
      return { kind: "custom", harness: h };
    }
  }
  return { kind: "none" };
}
/**
 * The copyable CLI string for a custom harness (clipboard only).