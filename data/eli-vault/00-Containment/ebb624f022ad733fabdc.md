---
id: 878274ff722c5035
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: ebb624f022ad733fabdc
createdAt: 1786051359181
embeddingSig: "const:name:description|continue:const:name|continue:first:occurrence|continue:null:continue|description:continue:null|first:occurrence:wins|length:length:length|name:description:continue|null:continue:first|occurrence:wins:trim|trim:length:length|wins:trim:length"
---
ine);
    if (!m) continue;
    const key = m[1];
    if (key !== "name" && key !== "description") continue;
    if (out[key] !== null) continue; // first occurrence wins
    let val = m[2].trim();
    if (
      val.length >= 2 &&
      ((val[0] === '"' && val[val.length - 1] === '"') ||
        (val[0] === "'" && val[val.length - 1] === "'"))
    ) {
      val = val.slice(1, -1);
    }
    out[key] = val.length ?