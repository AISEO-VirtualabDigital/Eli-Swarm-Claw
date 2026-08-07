---
id: 31319ca810af0b38
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: aba1ab9a978d16adeeb9
createdAt: 1786051359181
embeddingSig: "connect:runs:this|continues:existing:session|existing:session:when|harness:overriding:built|prompt:resume:continues|resume:continues:existing|runs:this:harness|session:when:what|sessions:connect:runs|this:harness:overriding|what:sessions:connect|when:what:sessions"
---
{prompt}` (resume continues an existing session). When set, it is what the
   * Sessions-tab "Connect" runs for this harness — overriding the built-in
   * defaults (claude/codex/isaac) and the generic best-effort guess. Absent =
   * best-effort (`<binary> --continue`) with a terminal hint to configure this.
   */
  resumeCommand?: string[];
}
/** Strip ASCII control chars (incl. NUL / CR / LF) from an interpolated value.