---
id: 722c9ff973217741
source: "eli-obsidian-architecture.md"
"title: Eli-OS Architecture & Binding Decisions"
category: obsidian
skillTags: ["tool"]
containmentHash: de9d3bfebfa7d469eb21
createdAt: 1786051353889
embeddingSig: "auto:publish:minimum|based:degradation:policy|below:fallback:drift|confidence:human:review|degradation:policy:auto|drift:maximum:hard|fallback:drift:maximum|human:review:below|minimum:confidence:human|policy:auto:publish|publish:minimum:confidence|review:below:fallback"
---
g

- URL-based
- `/api/v1`
## Degradation Policy

- Auto-publish minimum confidence: 0.90
- Human review below: 0.80
- Fallback drift maximum: 0.10
- Hard validator failure: block
- Sensitive actions: human approval
## Human Review

- PostgreSQL: source of truth
- Redis: realtime coordination
- Approved with edits: revalidate affected nodes
## OpenAPI