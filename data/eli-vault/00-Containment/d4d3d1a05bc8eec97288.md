---
id: ae71b1eec4eb57db
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern", "tool"]
containmentHash: d4d3d1a05bc8eec97288
createdAt: 1786051359181
embeddingSig: "chosen:terminal:emulator|decides:which:terminal|detached:this:module|emulator:instead:detached|instead:detached:this|module:decides:which|opens:that:script|terminal:emulator:instead|terminal:opens:that|that:script:never|this:module:decides|which:terminal:opens"
---
chosen
// terminal emulator instead of detached. This module decides WHICH terminal opens
// that script; it never constructs the harness command itself.
//
// Pure / injectable (no Obsidian imports; fs + platform injected) so it stays
// unit-testable, matching launch.ts. macOS is the primary target (this is a
// desktop-only, macOS-centric plugin); Windows/Linux always fall back to the