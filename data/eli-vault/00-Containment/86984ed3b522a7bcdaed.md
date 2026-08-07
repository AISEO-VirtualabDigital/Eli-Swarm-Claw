---
id: b4323a8ded1acdc0
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 86984ed3b522a7bcdaed
createdAt: 1786051359181
embeddingSig: "absolute:path:single|emitted:path:real|inert:positional:after|injectable:tests:emitted|path:real:resolved|path:single:inert|positional:after:const|real:resolved:absolute|resolved:absolute:path|runtime:injectable:tests|single:inert:positional|tests:emitted:path"
---
at runtime) and are
    // injectable for tests. The emitted path is the real (resolved) absolute
    // path — the single inert positional after `run`.
    const real = safeCustomAgentRealPath(stored.path, opts.scanDir, {
      exists: opts.exists,
      realpath: opts.realpath ?? ((p) => fs.realpathSync(p)),
      isFile: opts.isFile ?? ((p) => fs.statSync(p).isFile()),
      isDirectory: opts.isDirectory ??