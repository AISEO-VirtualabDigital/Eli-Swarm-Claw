---
id: 34933197f80b41a3
source: "SKILL-009-Memory-Stack-Retain.md"
"title: Skill 009 — Memory Stack & Retain"
category: ai-agent
skillTags: ["tool", "metric", "warning"]
containmentHash: c5de0d5a3835b23bdfad
createdAt: 1786051352589
embeddingSig: "auto:cleaned:rate|cleaned:rate:limited|content:deduplication:before|deduplication:before:absorption|files:auto:cleaned|intermediate:files:auto|json:intermediate:files|limited:responses:with|rate:limited:responses|responses:with:useful|useful:content:deduplication|with:useful:content"
---
- JSON intermediate files in /tmp (auto-cleaned)
- Rate-limited API responses with no useful content
### Deduplication

Before any absorption batch, existing knowledge is checked to avoid re-indexing the same repositories or content. The deduplication key for GitHub repos is `full_name`. For documents, it is the source URL or filename.
### Provenance Tracking