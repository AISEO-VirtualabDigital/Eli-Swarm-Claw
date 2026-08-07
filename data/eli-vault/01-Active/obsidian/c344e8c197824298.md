---
id: c344e8c197824298
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 88ba9d8acc82ba19eac2
createdAt: 1786051359181
embeddingSig: "behavior:return:resolved|each:surviving:token|harness:prompt:placeholder|placeholder:join:safeprompt|prompt:placeholder:join|resolved:split:harness|return:resolved:split|split:harness:prompt|surviving:token:unchanged|token:unchanged:behavior|unchanged:behavior:return|within:each:surviving"
---
within each surviving token (unchanged behavior).
  return resolved.map((t) => t.split(HARNESS_PROMPT_PLACEHOLDER).join(safePrompt));
}
/** The per-skill stored value for a custom-harness selection. */
export function encodeCustomHarnessChoice(id: string): string {
  return `${CUSTOM_HARNESS_VALUE_PREFIX}${id}`;
}
/**
 * The print/headless flags used by the supported CLIs.