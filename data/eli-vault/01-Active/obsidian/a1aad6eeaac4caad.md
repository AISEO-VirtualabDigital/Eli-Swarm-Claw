---
id: a1aad6eeaac4caad
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["process", "pattern"]
containmentHash: 72f1a735692f64355f29
createdAt: 1786051359181
embeddingSig: "append:entry:describing|array:create:missing|create:missing:append|describing:interactively:with|entry:describing:interactively|evel:harnesses:array|harnesses:array:create|interactively:with:single|missing:append:entry|prompt:short:kebab|single:prompt:short|with:single:prompt"
---
evel "harnesses" array (create it if missing).
3. Append ONE entry describing how to run YOU non-interactively with a single prompt:
     {
       "id": "<short-kebab-id>",
       "label": "<your product name>",
       "command": ["<absolute path to your CLI>", "<non-interactive flags>", "{prompt}"]
     }
   Rules: command[0] must be an absolute path; exactly one element must contain the