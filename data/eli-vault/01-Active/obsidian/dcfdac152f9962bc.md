---
id: dcfdac152f9962bc
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern", "tool"]
containmentHash: 9729d9a2b9170352e483
createdAt: 1786051359181
embeddingSig: "bundle:path:string|display:label:level|else:filename:stem|filename:stem:never|inside:bundle:path|label:level:name|level:name:else|name:else:filename|nfig:yaml:inside|path:string:display|string:display:label|yaml:inside:bundle"
---
nfig.yaml` inside a bundle.
   */
  path: string;
  /** Display label (top-level `name:`, else the filename stem). Never argv. */
  name: string;
  /** Optional tooltip (top-level `description:`). Never argv. */
  description?: string;
}
/** Membership test for the hardcoded built-in agent allowlist.