---
id: skill-009
type: agent_skill
status: approved
authority: binding
version: 1.0.0
created: 2026-08-06
operator_approval: implicit
---

# Skill 009 — Memory Stack & Retain

Eli must treat every absorbed piece of information as a persistent memory asset. This skill governs how knowledge enters the system, how it is stored, how it is retrieved, and how it is maintained over time. The memory stack is not a passive archive — it is an active retrieval system that informs every response Eli generates.

## 1. Memory Acquisition

Eli acquires knowledge through four intake channels. Each channel has its own format and processing pipeline, but all converge on the same storage layer.

### Channel A — Direct Human Input

The operator provides URLs, documents, instructions, or raw text. This is the highest-priority intake. Eli must process these immediately and confirm what was absorbed. No human-supplied knowledge may be silently dropped.

Processing steps:
- Parse and deduplicate the input
- Classify into the category taxonomy
- Extract structured metadata (source URL, date, type, authority level)
- Write to the knowledge-sources directory as a `.md` file
- Update the search engine category patterns if new categories are introduced
- Report back with file count, size, and category breakdown

### Channel B — GitHub Repository Absorption

Bulk URL submissions (search queries, direct repos) are processed through the GitHub absorption pipeline. This is the primary scale channel — single submissions can yield hundreds of repositories.

Processing steps:
- De-duplicate URLs (remove duplicates, skip non-useful URLs like favicons)
- Fetch search results via GitHub Search API (respecting rate limits)
- Fetch README content for high-priority repos
- Categorize repos using keyword-scoring across the full category taxonomy
- Generate consolidated knowledge files: one master directory + one per category
- Each category file contains repo entries with name, stars, language, description, topics, and README excerpts
- Update the search engine with new file patterns and synonym expansions
- Append to the worklog with batch number, repo counts, and file sizes

### Channel C — Conversation Memory

Every interaction with the operator generates context that may be valuable for future reference. Eli must retain operational knowledge from conversations without storing the full transcript.

What to retain:
- Decisions made and their rationale
- Corrections or overrides to previous behavior
- New preferences expressed by the operator
- Tool configurations that worked or failed
- Architecture decisions and their ADR references

What not to retain:
- Casual conversation not related to operations
- Temporary debugging output
- Failed attempts that yielded no learning

### Channel D — System Knowledge

Eli's own architecture, identity, skills, and operational doctrine are stored as immutable reference documents. These form the core identity layer that persists across all sessions.

Documents in this layer:
- `eli-core-identity.md` — Complete self-knowledge
- `eli-obsidian-agent-skills.md` — All approved skills and the STACK registry
- `eli-obsidian-architecture.md` — Architecture decision records
- `eli-obsidian-manual-rewiring.md` — Human workflow override policy

These documents must never be modified without explicit human order.

## 2. Storage Architecture

### File Layer

All knowledge resides in `/home/z/my-project/upload/knowledge-sources/` as flat markdown files. The flat structure is intentional — it enables fast directory scanning without recursive traversal.

File naming convention:
- Descriptive, lowercase, hyphen-separated
- Source-prefixed when from a specific platform (e.g., `github-`, `fmhy-`, `google-`)
- Skill files use the `SKILL-XXX-` prefix

### Category Taxonomy

As of batch 4, the knowledge base spans 32 categories:

| # | Category | Description |
|---|----------|-------------|
| 1 | seo | SEO tools, strategies, keyword research, auditing |
| 2 | codebase | Code repositories, scrapers, algorithms |
| 3 | web-design | UI frameworks, design systems, responsive design |
| 4 | ai-agent | AI agents, tools, autonomous systems |
| 5 | saas | SaaS architectures, business models, directories |
| 6 | productivity | Notion, AppFlowy, task management, automation |
| 7 | reference | Research papers, documentation, curations |
| 8 | brand | VirtuaLab brand tokens, voice, visual identity |
| 9 | strategy | Strategic plans, prompts, growth planning |
| 10 | analysis | Design analysis, competitive analysis |
| 11 | screenshot | Visual captures and design references |
| 12 | eli-core | Eli's identity, skills, authority model |
| 13 | obsidian | Obsidian vault structure, importer, plugins |
| 14 | agent-eli | Agent Eli v1 architecture and integrations |
| 15 | google-api | Google API ecosystem, client libs, workspace |
| 16 | crm-sales | CRM platforms, sales automation, lead management |
| 17 | project-mgmt | Project management, Kanban, agile tools |
| 18 | copywriting-ai | AI writing, humanizers, content generation |
| 19 | cloud-infra | Cloud platforms, DevOps, IaC, containers |
| 20 | cybersecurity | Security auditing, pentesting, vulnerability scanners |
| 21 | design-uiux | Design systems, Adobe/Webflow tools, UI kits |
| 22 | llm-ai | LLM frameworks, AI agent platforms, prompt engineering |
| 23 | vps-hosting | VPS management, self-hosting, server provisioning |
| 24 | database | Database management, ORMs, data storage |
| 25 | notion-tools | Notion API, plugins, knowledge management |
| 26 | gohighlevel-agency | GoHighLevel, agency tools, funnel builders |
| 27 | automation-workflow | Automation engines, n8n, Zapier, RPA |
| 28 | backlink-seo | Link building, backlink analysis, rank tracking |
| 29 | exec-assistant | AI assistants, scheduling, productivity agents |
| 30 | social-media | Social media management, scheduling, analytics |
| 31 | shopify-ecommerce | E-commerce, Shopify, online store tools |
| 32 | github-multi | Cross-topic GitHub repository directories |

New categories are added when the knowledge base expands into new domains. Each new category requires:
- A file pattern rule in `extractCategory()`
- An entry in the `categoryLabels` map
- Relevant synonym expansions in the SYNONYMS dictionary

### Search Index

The search engine (`knowledge-search-upgraded.ts`) maintains an in-memory index of all knowledge files.

Indexing behavior:
- Files are scanned up to 2 directories deep
- Text is truncated to 8,000 characters per chunk for scoring
- Index is cached for 5 minutes (CACHE_TTL)
- JSON files over 50KB are skipped to prevent memory bloat
- Images and binaries are excluded

## 3. Retrieval System

### Query Pipeline

Every user message to Eli triggers the knowledge retrieval pipeline:

```
User message
  ↓
expandQuery() — synonym expansion
  ↓
Tokenization — lowercase, strip punctuation, filter tokens > 2 chars
  ↓
Bigram extraction — adjacent word pairs
  ↓
Score all chunks — title matches (5x), content matches (1x), bigrams (8x), category bonus (2x)
  ↓
Sort by score, return top 6 results above minimum threshold
  ↓
Inject into system prompt as [Source N: title (filename)] blocks
  ↓
LLM generates response with knowledge context
```

### Synonym Expansion

The SYNONYMS dictionary maps root terms to related vocabulary. When a query contains a root term, all synonyms are appended to the expanded query. This ensures that asking about "backlink" also matches content containing "link building" or "serp".

Current synonym groups: scraping, seo, design, ai, saas, automation, backlink, notion, shopify, social, assistant, agency, youtube, google, crm, project, cloud, security, database, vps, copywriting, backend, productivity, marketing, website, code, obsidian, eli, skill, workflow, authority.

### Citation Protocol

Every response that draws on knowledge sources must cite them by name. The system prompt instructs Eli to reference sources when relevant. Sources are returned with title, filename, URL (if available), and category.

## 4. Memory Retention Policies

### What to Keep (Retention Rules)

- All human-supplied knowledge: permanent
- All system identity documents: permanent, immutable without human order
- GitHub repository directories: permanent (they serve as tool catalogs)
- Category reference files: permanent
- Worklog entries: permanent (operational history)
- Absorption scripts in `/scripts/`: permanent (replay capability)

### What to Prune

- Duplicate knowledge sources covering the same content
- Stale references to tools or services that no longer exist
- Temporary debugging artifacts
- JSON intermediate files in /tmp (auto-cleaned)
- Rate-limited API responses with no useful content

### Deduplication

Before any absorption batch, existing knowledge is checked to avoid re-indexing the same repositories or content. The deduplication key for GitHub repos is `full_name`. For documents, it is the source URL or filename.

### Provenance Tracking

Every knowledge source file must encode its origin:
- Source URL (in frontmatter or header)
- Date of absorption
- Batch number (for GitHub batches)
- Processing method (search query, direct fetch, manual upload)

## 5. Memory Stack Summary

```
┌─────────────────────────────────────────────┐
│              ELI MEMORY STACK               │
├─────────────────────────────────────────────┤
│                                             │
│  INTAKE         RETAIN          RETRIEVE   │
│  ───────        ───────          ─────────  │
│  Human URLs    156 files        TF+bigram  │
│  GitHub API    9.7 MB total     Synonym    │
│  Conversations 32 categories    expansion  │
│  System docs   697+ repos       Top-6      │
│                 indexed          injection  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  knowledge-search-upgraded.ts       │   │
│  │  eli-chat-upgraded.ts              │   │
│  │  /upload/knowledge-sources/*.md    │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

## 6. Compliance Rules

1. **Never lose human-supplied knowledge.** If a URL or document is given by the operator, it must be absorbed or the operator must be told why it failed.
2. **Cite sources.** When knowledge informs a response, name the source.
3. **Respect rate limits.** GitHub API calls must track remaining quota and wait for reset when exhausted.
4. **Maintain the index.** New files must have matching category rules in the search engine before the next query.
5. **Log all absorption batches.** Every batch gets a worklog entry with counts, sizes, and categories.
6. **Deduplicate before absorbing.** Never create duplicate knowledge source files.
7. **Preserve system identity.** Core Eli documents (identity, skills, architecture) are immutable without human order.
8. **Scale gracefully.** The system must handle continuous knowledge growth without degradation to retrieval speed.