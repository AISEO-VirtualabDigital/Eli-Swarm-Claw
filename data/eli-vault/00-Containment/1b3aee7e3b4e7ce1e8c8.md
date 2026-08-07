---
id: 225e7b63894a6d04
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 1b3aee7e3b4e7ce1e8c8
createdAt: 1786051359181
embeddingSig: "default:export:function|export:function:safecustomagentrealpath|from:resolves:null|injected:this:stays|null:injected:this|real:default:export|resolves:null:injected|stays:unit:testable|testable:real:default|this:stays:unit|throw:from:resolves|unit:testable:real"
---
ENT / any throw from the fs ops resolves to null. fs
 * ops are injected so this stays unit-testable; the real `fs` is the default.
 */
export function safeCustomAgentRealPath(
  rawPath: unknown,
  scanDir: string,
  fsOps: {
    exists?: (p: string) => boolean;
    realpath: (p: string) => string;
    isFile: (p: string) => boolean;
    isDirectory?: (p: string) => boolean;