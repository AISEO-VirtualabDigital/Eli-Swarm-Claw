---
id: 7fd5b8ef6636999f
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code", "warning"]
containmentHash: a7bc5acc5e1d8c37e6af
createdAt: 1786051359181
embeddingSig: "async:walkfs:string|external:tags:relfortag|null:root:path|path:external:tags|private:async:walkfs|relfortag:return:skills|return:skills:private|root:path:external|skills:private:async|string:rootreal:string|tags:relfortag:return|walkfs:string:rootreal"
---
lds, abs, null, root.path, "external", fm.tags ?? [], relForTag),
      );
    }
    return skills;
  }
private async walkFs(
    dir: string,
    rootReal: string,
    depth: number,
    out: string[],
    seen: Set<string>,
  ): Promise<void> {
    if (depth > MAX_DEPTH) return;
    // Resolve symlinks and skip already-visited real directories to avoid
    // cycles (e.g.