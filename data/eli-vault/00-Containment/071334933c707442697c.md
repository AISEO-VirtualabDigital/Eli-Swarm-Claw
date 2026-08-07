---
id: 8ecc06c59eae9b0c
source: "llm-scraper-README.md"
"title: z.string(),"
category: ai-agent
skillTags: ["capability"]
containmentHash: 071334933c707442697c
createdAt: 1786051357033
embeddingSig: "code:generation:supports|formatting:modes:html|generation:supports:formatting|html:html:loading|html:loading:html|html:loading:processed|html:processing:markdown|loading:html:processing|loading:processed:html|modes:html:loading|processed:html:html|supports:formatting:modes"
---
(#code-generation)
- Supports 6 formatting modes:
  - `html` for loading pre-processed HTML
  - `raw_html` for loading raw HTML (no processing)
  - `markdown` for loading markdown
  - `text` for loading extracted text (using [Readability.js](https://github.com/mozilla/readability))
  - `image` for loading a screenshot (multi-modal only)