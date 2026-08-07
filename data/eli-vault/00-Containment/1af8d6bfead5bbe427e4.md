---
id: 455667ff8d4a1cb1
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: 1af8d6bfead5bbe427e4
createdAt: 1786051359181
embeddingSig: "able:terminal:other|bash:body:return|body:return:platform|both:share:same|other:unix:uses|platform:darwin:command|return:platform:darwin|same:bash:body|share:same:bash|terminal:other:unix|unix:uses:both|uses:both:share"
---
n`-able in Terminal); other
  // Unix uses `.sh`. Both share the same bash body.
  return {
    ext: platform === "darwin" ? ".command" : ".sh",
    content: buildBashScript(argv, cwd, failHint, keepOpen),
  };
}
/**
 * A terminal script that `cd`s into `cwd` and runs a RAW user-authored script
 * `body` (the Bash Scripts tab).