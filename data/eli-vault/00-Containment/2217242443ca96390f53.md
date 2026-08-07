---
id: 6a82b448ff0fcdfb
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 2217242443ca96390f53
createdAt: 1786051359181
embeddingSig: "choice:parseharnessvalue:stored|const:choice:parseharnessvalue|customharness:undefined:null|customharnesses:customharness:undefined|function:resolveskillharness:stored|null:resolvedskillharness:const|parseharnessvalue:stored:choice|resolvedskillharness:const:choice|resolveskillharness:stored:unknown|stored:unknown:customharnesses|undefined:null:resolvedskillharness|unknown:customharnesses:customharness"
---
function resolveSkillHarness(
  stored: unknown,
  customHarnesses: CustomHarness[] | undefined | null,
): ResolvedSkillHarness {
  const choice = parseHarnessValue(stored);
  if (choice.kind === "omnigent") return { kind: "omnigent", name: choice.name };
  if (choice.kind === "custom") {
    const h = (customHarnesses ??