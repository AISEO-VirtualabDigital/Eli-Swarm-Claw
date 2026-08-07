---
id: eca3fc80930563bd
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 4fbecb0e30b5dc9ce0fb
createdAt: 1786051359181
embeddingSig: "dirent:entries:await|entries:await:promises|entries:dirent:entries|nodepath:return:seen|real:entries:dirent|real:return:seen|real:startswith:rootreal|return:seen:real|rootreal:nodepath:return|seen:real:entries|seen:real:return|startswith:rootreal:nodepath"
---
real.startsWith(rootReal + nodePath.sep)) return;
    if (seen.has(real)) return;
    seen.add(real);
let entries: fs.Dirent[];
    try {
      entries = await fs.promises.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = nodePath.join(dir, entry.name);
      if (entry.isDirectory() || entry.isSymbolicLink()) {