---
id: a2a7bea859b82ac9
source: "SKILL-009-Memory-Stack-Retain.md"
"title: Skill 009 — Memory Stack & Retain"
category: ai-agent
skillTags: ["process"]
containmentHash: ff954ac55a2ccef6eaad
createdAt: 1786051352589
embeddingSig: "cached:minutes:cache|characters:chunk:scoring|chunk:scoring:index|deep:text:truncated|directories:deep:text|files:scanned:directories|index:cached:minutes|minutes:cache:json|scanned:directories:deep|scoring:index:cached|text:truncated:characters|truncated:characters:chunk"
---
ior:
- Files are scanned up to 2 directories deep
- Text is truncated to 8,000 characters per chunk for scoring
- Index is cached for 5 minutes (CACHE_TTL)
- JSON files over 50KB are skipped to prevent memory bloat
- Images and binaries are excluded
## 3. Retrieval System
### Query Pipeline

Every user message to Eli triggers the knowledge retrieval pipeline: