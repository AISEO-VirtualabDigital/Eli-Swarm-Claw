---
title: Skill Contain System
tags:
  - "skill-contain"
  - "system"
  - "permanent-memory"
type: system-doc
created: 2026-08-07
---

# Skill Contain System

> **Core Principle**: Knowledge is NEVER deleted. It is only dissolved.

## How It Works

1. **Ingestion**: Source files are dissolved into 100-600 char micro-chunks
2. **Tagging**: Each chunk receives skill tags (process, pattern, capability, tool, strategy, metric, warning, code)
3. **Semantic Signature**: Word trigrams create a lightweight embedding for matching
4. **Containment Hash**: SHA-256 proof of existence — even if chunk moves to containment
5. **Active → Dissolved**: When knowledge is updated, old chunks move to `00-Containment/`
6. **Permanent Memory**: Containment chunks are STILL searchable. Eli remembers patterns forever.

## Skill Tags

| Tag | Emoji | Count | Meaning |
|-----|-------|-------|---------|
| process | ⚙️ | 1,018 | Step-by-step workflows & procedures |
| capability | 💪 | 1,053 | What tools/systems can do |
| metric | 📊 | 2,251 | Quantitative data & KPIs |
| pattern | 🔄 | 846 | Reusable patterns & frameworks |
| tool | 🔧 | 4,466 | Specific tools, APIs, libraries |
| strategy | 🎯 | 285 | Strategic approaches & methodologies |
| code | 💻 | 1,015 | Code snippets & technical configs |
| warning | ⚠️ | 204 | Pitfalls, errors, gotchas |

## Containment Proof

Every chunk has a `containmentHash` — a truncated SHA-256 that serves as proof of existence.
Even if the source file is deleted and the chunk is dissolved, the hash remains in the index.

This means: **Eli can prove she knew something, even after it's "gone".**

## Vault Statistics

```
Total chunks:     24331
Active:           24331
Dissolved:        0
Skill types:      8
Source files:     171
Total characters: 7,249,200
Avg chunk size:   298 chars
Engine:           micro-chunk-containment-v2
Last ingestion:   2026-08-06 21:22 UTC
```

## Related

- [[Eli-System-Architecture]]
- [[Sync Setup]]
- [[Air-LLM-Pipeline]]
