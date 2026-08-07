#!/usr/bin/env python3
"""
Generate a clean Obsidian vault from Eli's chunk engine data.

Creates a human-readable, Obsidian-native vault structure at /home/z/my-project/download/Eli-Vault/
with: system maps, skill contain records, category dashboards, and a sync API bridge.
"""

import json
import os
import shutil
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ────────────────────────────────────────────────────────

ELI_VAULT = "/home/z/my-project/data/eli-vault"
ACTIVE_DIR = os.path.join(ELI_VAULT, "01-Active")
CONTAINMENT_DIR = os.path.join(ELI_VAULT, "00-Containment")
SKILLS_DIR = os.path.join(ELI_VAULT, "02-Skills")
INDEX_DIR = os.path.join(ELI_VAULT, "03-Index")
KNOWLEDGE_SOURCES = "/home/z/my-project/data/uploads/knowledge-sources"
OUTPUT_DIR = "/home/z/my-project/download/Eli-Vault"

# Category emoji mapping
CATEGORY_EMOJI = {
    "seo": "🔍", "web-design": "🎨", "google-api": "☁️",
    "scraping": "🕷️", "social": "📱", "ai-agent": "🤖",
    "obsidian": "📝", "saas": "💼", "automation": "⚡",
    "eli-core": "🧠", "content": "✍️", "infra": "🖥️",
    "ecommerce": "🛒", "crm": "👥", "security": "🔒",
    "database": "🗄️", "knowledge": "📚", "project-mgmt": "📋",
}

SKILL_EMOJI = {
    "process": "⚙️", "pattern": "🔄", "capability": "💪",
    "tool": "🔧", "strategy": "🎯", "metric": "📊",
    "warning": "⚠️", "code": "💻",
}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_frontmatter(content):
    """Parse Obsidian frontmatter from chunk file."""
    if not content.startswith("---"):
        return {}, content
    
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    
    fm_raw = content[3:end].strip()
    body = content[end+3:].strip()
    
    meta = {}
    for line in fm_raw.split("\n"):
        line = line.strip().lstrip('"')
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip().strip('"')
            val = val.strip().strip('"')
            # Handle arrays like ["process", "tool"]
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"') for v in val[1:-1].split(",") if v.strip()]
            meta[key] = val
    
    return meta, body


def write_markdown(filepath, frontmatter, body):
    """Write a proper Obsidian markdown file with frontmatter."""
    fm_lines = ["---"]
    for k, v in frontmatter.items():
        if isinstance(v, list):
            fm_lines.append(f"{k}:")
            for item in v:
                fm_lines.append(f"  - \"{item}\"")
        elif isinstance(v, str) and any(c in v for c in [':', '#', '[', ']', '{', '}']):
            fm_lines.append(f'{k}: "{v}"')
        else:
            fm_lines.append(f"{k}: {v}")
    fm_lines.append("---")
    fm_lines.append("")
    
    content = "\n".join(fm_lines) + body
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_system_map():
    """Generate the Eli System Architecture map."""
    fm = {
        "title": "Eli System Architecture",
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "tags": ["system", "architecture", "map"],
        "type": "dashboard",
    }
    
    body = """
# Eli System Architecture

> Complete system map of Eli MicroSaaS — VirtuaLab Digital's AI Growth Intelligence

## Backend Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| Runtime | Bun + Next.js 16.1.1 | ✅ Active |
| Frontend | React 19 + Tailwind CSS 4 + shadcn/ui | ✅ Active |
| Knowledge Engine | Micro-Chunk Containment v2 | ✅ 24,331 chunks |
| LLM Backend | Google Gemini 2.0 Flash (Air LLM) | ⚠️ Needs API Key |
| Database | SQLite (Prisma) | ⚠️ Unused scaffold |
| Reverse Proxy | Caddy (auto-HTTPS) | ✅ Production |
| Vault Storage | Obsidian-flavored markdown | ✅ 208 MB |

## API Routes

| Route | Method | Purpose | Status |
|-------|--------|---------|--------|
| `/api/eli-chat` | POST/GET | Core chat with vault retrieval | ✅ Fixed |
| `/api/health` | GET | System health + vault stats | ✅ Fixed |
| `/api/knowledge-stats` | GET | Knowledge base statistics | ✅ Fixed |
| `/api/eli-intro` | GET | Introduction config | ✅ Working |
| `/api/keywords` | GET | Keyword research datasets | ✅ Working |
| `/api/skills` | GET | Skill templates | ✅ Working |

## Knowledge Architecture

```
eli-vault/
├── 00-Containment/    ← Deletion-proof memory (Skill Contain)
├── 01-Active/         ← 24,331 active micro-chunks
│   ├── seo/           ← 2,841 chunks
│   ├── web-design/    ← 7,724 chunks
│   ├── google-api/    ← 3,211 chunks
│   ├── knowledge/     ← 3,640 chunks
│   ├── scraping/      ← 2,749 chunks
│   ├── social/        ← 1,205 chunks
│   ├── ai-agent/      ← 808 chunks
│   ├── obsidian/      ← 681 chunks
│   ├── saas/          ← 644 chunks
│   └── ... (9 more categories)
├── 02-Skills/         ← Extracted patterns & processes
└── 03-Index/          ← Fast term→file lookup indexes
```

## Skill Contain System

> **Every chunk is permanent.** When knowledge is updated or removed from active vault, it moves to `00-Containment/` — Eli retains the patterns forever.

- **Total chunks**: 24,331
- **Active**: 24,331 | **Dissolved**: 0
- **Skill tags**: process (1,018) · capability (1,053) · metric (2,251) · pattern (846) · tool (4,466) · strategy (285) · code (1,015) · warning (204)
- **Sources ingested**: 171 files (7.2M chars)
- **Avg chunk size**: 298 chars (100-600 range)

## Air LLM Pipeline

```
User Query
    ↓
searchVault() → pre-built index lookup (O(1) term→file)
    ↓
parseChunkFile() → read top 10-12 chunks
    ↓
buildVaultKnowledgeMap() → category awareness
    ↓
Gemini 2.0 Flash → generate response with sources
    ↓
Response + source tracking + containment hits
```

## Obsidian Sync

This vault connects to Eli's live system via the sync API.
See [[Sync Setup]] for configuration.
"""
    
    write_markdown(os.path.join(OUTPUT_DIR, "00-System", "Eli-System-Architecture.md"), fm, body)


def generate_category_dashboards(index_data):
    """Generate a dashboard for each knowledge category."""
    categories = index_data.get("categories", {})
    skill_tags = index_data.get("skillTags", {})
    
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        emoji = CATEGORY_EMOJI.get(cat, "📁")
        cat_dir = os.path.join(ACTIVE_DIR, cat)
        
        # Get sample chunks for this category
        sample_chunks = []
        if os.path.isdir(cat_dir):
            files = sorted(os.listdir(cat_dir))[:5]
            for f in files:
                path = os.path.join(cat_dir, f)
                try:
                    with open(path, 'r', encoding='utf-8') as fh:
                        meta, body = parse_frontmatter(fh.read())
                        if body:
                            sample_chunks.append({
                                "title": meta.get("title", "Untitled"),
                                "source": meta.get("source", "unknown"),
                                "skills": meta.get("skillTags", []),
                                "preview": body[:150].replace("\n", " "),
                            })
                except:
                    pass
        
        fm = {
            "title": f"{emoji} {cat.upper()}",
            "category": cat,
            "chunk_count": count,
            "tags": [cat, "dashboard", "category"],
            "type": "category-dashboard",
            "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        
        chunks_table = ""
        for i, c in enumerate(sample_chunks, 1):
            skills_str = ", ".join(c["skills"]) if isinstance(c["skills"], list) else str(c["skills"])
            chunks_table += f"{i}. **{c['title']}** `[{skills_str}]`\n   > {c['preview']}...\n   > *Source: {c['source']}*\n\n"
        
        body = f"""
# {emoji} {cat.upper()} — {count} chunks

> Part of Eli's micro-chunk knowledge vault

## Overview

| Metric | Value |
|--------|-------|
| Total Chunks | {count} |
| Vault Engine | micro-chunk-containment-v2 |
| Avg Chunk Size | ~298 chars |

## Skill Breakdown

"""
        
        # Add skill tag counts for this category (approximate from global)
        for tag, tag_count in sorted(skill_tags.items(), key=lambda x: -x[1]):
            tag_emoji = SKILL_EMOJI.get(tag, "📌")
            body += f"- {tag_emoji} {tag}: ~{tag_count} chunks\n"
        
        body += f"""

## Sample Chunks

"""
        body += chunks_table
        
        body += f"""
---
*Last synced from Eli's vault on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*\n*Category path: `01-Active/{cat}/`*\n"""
        
        write_markdown(os.path.join(OUTPUT_DIR, "01-Categories", f"{cat}.md"), fm, body)


def generate_skill_contain_records(index_data):
    """Generate Skill Contain system documentation."""
    skills_dir = os.path.join(ELI_VAULT, "02-Skills")
    
    fm = {
        "title": "Skill Contain System",
        "tags": ["skill-contain", "system", "permanent-memory"],
        "type": "system-doc",
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    
    body = """
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
Total chunks:     {total_chunks}
Active:           {active}
Dissolved:        {dissolved}
Skill types:      {skills}
Source files:     {sources}
Total characters: {chars:,}
Avg chunk size:   {avg} chars
Engine:           micro-chunk-containment-v2
Last ingestion:   {timestamp}
```

## Related

- [[Eli-System-Architecture]]
- [[Sync Setup]]
- [[Air-LLM-Pipeline]]
""".format(
        total_chunks=index_data.get("totalChunks", 0),
        active=index_data.get("activeChunks", 0),
        dissolved=index_data.get("dissolvedChunks", 0),
        skills=index_data.get("skills", 0),
        sources=index_data.get("totalFiles", 0),
        chars=index_data.get("totalSourceChars", 0),
        avg=index_data.get("avgChunkSize", 0),
        timestamp=datetime.fromtimestamp(index_data.get("lastIngestion", 0)/1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if index_data.get("lastIngestion") else "N/A",
    )
    
    write_markdown(os.path.join(OUTPUT_DIR, "02-Skill-Contain", "Skill-Contain-System.md"), fm, body)
    
    # Generate individual skill type pages
    skill_tags = index_data.get("skillTags", {})
    for skill, count in sorted(skill_tags.items(), key=lambda x: -x[1]):
        emoji = SKILL_EMOJI.get(skill, "📌")
        
        # Collect sample chunks for this skill type
        samples = []
        for cat in os.listdir(ACTIVE_DIR):
            cat_path = os.path.join(ACTIVE_DIR, cat)
            if not os.path.isdir(cat_path):
                continue
            for fname in sorted(os.listdir(cat_path))[:3]:
                fpath = os.path.join(cat_path, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        meta, body = parse_frontmatter(f.read())
                        tags = meta.get("skillTags", [])
                        if isinstance(tags, list) and skill in tags:
                            samples.append({
                                "title": meta.get("title", ""),
                                "category": cat,
                                "preview": (body or "")[:120],
                            })
                except:
                    pass
            if len(samples) >= 10:
                break
        
        sfm = {
            "title": f"{emoji} {skill.capitalize()}",
            "skill_type": skill,
            "count": count,
            "tags": ["skill-contain", skill],
            "type": "skill-record",
        }
        
        sbody = f"""
# {emoji} {skill.capitalize()} — {count} chunks

> Skill type in Eli's containment system

## Definition

Chunks tagged with `{skill}` represent: _{get_skill_description(skill)}_

## Sample Chunks

"""
        for i, s in enumerate(samples[:8], 1):
            sbody += f"{i}. **{s['title']}** [{s['category']}]\n   > {s['preview']}...\n\n"
        
        if not samples:
            sbody += "_No samples collected. The skill tags are distributed across all categories._\n"
        
        sbody += f"""
---
*Part of the [[Skill-Contain-System]]*\n"""
        
        write_markdown(os.path.join(OUTPUT_DIR, "02-Skill-Contain", f"{skill}.md"), sfm, sbody)


def get_skill_description(skill):
    descriptions = {
        "process": "Step-by-step workflows, procedures, and multi-step operations",
        "pattern": "Reusable patterns, frameworks, and recurring structures",
        "capability": "What tools, systems, and platforms can do",
        "tool": "Specific tools, APIs, libraries, SDKs, and CLIs",
        "strategy": "Strategic approaches, methodologies, and playbooks",
        "metric": "Quantitative data, KPIs, scores, and measurable values",
        "warning": "Pitfalls, errors, gotchas, and things to avoid",
        "code": "Code snippets, configurations, and technical implementations",
    }
    return descriptions.get(skill, "Knowledge chunks with this classification")


def generate_source_inventory():
    """Generate an inventory of all 171 knowledge source files."""
    sources = []
    if os.path.isdir(KNOWLEDGE_SOURCES):
        for fname in sorted(os.listdir(KNOWLEDGE_SOURCES)):
            fpath = os.path.join(KNOWLEDGE_SOURCES, fname)
            if os.path.isfile(fpath):
                size = os.path.getsize(fpath)
                sources.append({"name": fname, "size": size})
    
    fm = {
        "title": "Knowledge Source Inventory",
        "total_sources": len(sources),
        "total_size": sum(s["size"] for s in sources),
        "tags": ["inventory", "sources", "knowledge"],
        "type": "inventory",
    }
    
    body = "# Knowledge Source Inventory\n\n"
    body += f"> {len(sources)} source files ingested into Eli's vault\n\n"
    body += "| # | Source File | Size |\n|---|-------------|------|\n"
    
    for i, s in enumerate(sources, 1):
        size_kb = s["size"] / 1024
        body += f"| {i} | `{s['name']}` | {size_kb:.1f} KB |\n"
    
    body += f"\n---\n*Total: {sum(s['size'] for s in sources) / 1024 / 1024:.1f} MB across {len(sources)} files*\n"
    
    write_markdown(os.path.join(OUTPUT_DIR, "03-Sources", "Source-Inventory.md"), fm, body)


def generate_sync_setup():
    """Generate sync bridge documentation."""
    fm = {
        "title": "Sync Setup",
        "tags": ["sync", "setup", "api", "bridge"],
        "type": "setup-guide",
    }
    
    body = """
# Obsidian ↔ Eli Sync Setup

> Connect your local Obsidian vault to Eli's live system

## Overview

This vault syncs with Eli's knowledge engine on `eli.virtualabdigital.com`.
The sync is **one-way pull** — Eli's server is the source of truth.

## Sync API Endpoints

### Pull Vault Stats
```
GET https://eli.virtualabdigital.com/api/health
```
Returns vault statistics, chunk counts, category breakdown.

### Pull Knowledge Stats
```
GET https://eli.virtualabdigital.com/api/knowledge-stats
```
Returns detailed knowledge base statistics.

### Chat with Eli
```
POST https://eli.virtualabdigital.com/api/eli-chat
Body: { "message": "your question", "history": [] }
```
Returns Eli's response with vault sources and containment hits.

### Pull Skill Templates
```
GET https://eli.virtualabdigital.com/api/skills
```
Returns all available SEO agent skill templates.

### Pull Keyword Data
```
GET https://eli.virtualabdigital.com/api/keywords
```
Returns keyword research datasets.

## Obsidian Sync Plugin

For automated sync, use the **Obsidian Git** plugin or **Periodic Notes**:

1. Install "Obsidian Git" community plugin
2. Point the git repo to Eli's vault on your VPS
3. Set auto-pull interval (e.g., every 5 minutes)

Alternatively, use the `/api/health` endpoint with a simple cron/scheduled task
to periodically export fresh vault data.

## Vault Structure

```
Eli-Vault/                    ← This vault
├── 00-System/                ← System architecture & maps
├── 01-Categories/            ← One dashboard per knowledge category
├── 02-Skill-Contain/         ← Skill Contain system & records
├── 03-Sources/               ← Source file inventory
├── 04-Sync/                  ← Sync configuration & logs
└── .obsidian/                ← Obsidian app settings
```

## Related

- [[Eli-System-Architecture]]
- [[Skill-Contain-System]]
"""
    
    write_markdown(os.path.join(OUTPUT_DIR, "04-Sync", "Sync-Setup.md"), fm, body)


def generate_air_llm_doc():
    """Generate Air LLM pipeline documentation."""
    fm = {
        "title": "Air LLM Pipeline",
        "tags": ["air-llm", "pipeline", "gemini", "architecture"],
        "type": "system-doc",
    }
    
    body = """
# Air LLM Pipeline

> Lightweight Gemini-powered retrieval + generation

## Concept

"Air" = no heavy infrastructure. Air LLM is a thin layer that:
1. Retrieves relevant micro-chunks from the vault
2. Builds a compact, chunk-aware prompt
3. Calls Google Gemini for generation
4. Returns response with full source tracking

## Pipeline

```mermaid
graph TD
    A[User Query] --> B[searchVault - index lookup]
    B --> C[parseChunkFile - read 10-12 chunks]
    C --> D[buildVaultKnowledgeMap]
    D --> E[Merge context + containment]
    E --> F[Gemini 2.0 Flash]
    F --> G[Response + Sources]
    
    B -.->|fallback| H[Chunk list only]
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key |
| `OBSIDIAN_VAULT_PATH` | No | Falls back to `data/eli-vault` |

## Fallback Behavior

When Gemini is unavailable:
- Returns chunk source list instead of generated response
- Includes containment hits from dissolved knowledge
- Preserves all source tracking

## Containment Integration

Air LLM checks the containment layer (dissolved chunks) for additional context.
These are marked as `[CONTAINMENT]` in the prompt so Gemini knows they're
pattern memories from previously deleted/updated knowledge.

## Related

- [[Eli-System-Architecture]]
- [[Skill-Contain-System]]
- [[Sync-Setup]]
"""
    
    write_markdown(os.path.join(OUTPUT_DIR, "00-System", "Air-LLM-Pipeline.md"), fm, body)


def generate_moc():
    """Generate the main Map of Content for the vault."""
    fm = {
        "title": "Eli Vault — Map of Content",
        "tags": ["moc", "dashboard", "home"],
        "type": "moc",
    }
    
    body = """
# 🧠 Eli Vault

> VirtuaLab Digital — AI Growth Intelligence Knowledge Base

---

## 📋 System

- [[Eli-System-Architecture]] — Complete backend architecture map
- [[Air-LLM-Pipeline]] — How Eli retrieves and generates knowledge

## 📂 Knowledge Categories

| Category | Chunks | Dashboard |
|----------|--------|-----------|
| 🎨 Web Design | 7,724 | [[web-design]] |
| 📚 Knowledge | 3,640 | [[knowledge]] |
| ☁️ Google API | 3,211 | [[google-api]] |
| 🔍 SEO | 2,841 | [[seo]] |
| 🕷️ Scraping | 2,749 | [[scraping]] |
| 📱 Social | 1,205 | [[social]] |
| 🤖 AI Agent | 808 | [[ai-agent]] |
| 📝 Obsidian | 681 | [[obsidian]] |
| 💼 SaaS | 644 | [[saas]] |
| ⚡ Automation | 374 | [[automation]] |
| 🧠 Eli Core | 117 | [[eli-core]] |
| 🛒 eCommerce | 106 | [[ecommerce]] |
| 🔒 Security | 30 | [[security]] |
| 🗄️ Database | 28 | [[database]] |
| 📋 Project Mgmt | 18 | [[project-mgmt]] |
| 👥 CRM | 16 | [[crm]] |
| ✍️ Content | 84 | [[content]] |
| 🖥️ Infra | 55 | [[infra]] |

## 🔄 Skill Contain

- [[Skill-Contain-System]] — How permanent memory works
- [[process]] — Workflows & procedures (1,018)
- [[tool]] — Tools, APIs, libraries (4,466)
- [[metric]] — Data & KPIs (2,251)
- [[code]] — Code snippets (1,015)
- [[capability]] — System capabilities (1,053)
- [[pattern]] — Reusable patterns (846)
- [[strategy]] — Strategic approaches (285)
- [[warning]] — Pitfalls & gotchas (204)

## 📦 Sources

- [[Source-Inventory]] — All 171 ingested source files

## ⚡ Sync

- [[Sync-Setup]] — Connect to Eli's live system

---

*Vault generated on {timestamp}*
*Engine: micro-chunk-containment-v2*
*Total: 24,331 chunks from 171 sources*
""".format(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    )
    
    write_markdown(os.path.join(OUTPUT_DIR, "Eli-Vault-MOC.md"), fm, body)


def main():
    print("[1/7] Loading vault index...")
    index_path = os.path.join(INDEX_DIR, "vault-index.json")
    index_data = load_json(index_path)
    
    print("[2/7] Cleaning output directory...")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    # Create Obsidian config
    os.makedirs(os.path.join(OUTPUT_DIR, ".obsidian"), exist_ok=True)
    obsidian_config = {
        "vaultName": "Eli Vault",
        "theme": "obsidian",
    }
    with open(os.path.join(OUTPUT_DIR, ".obsidian", "app.json"), 'w') as f:
        json.dump(obsidian_config, f, indent=2)
    
    print("[3/7] Generating system maps...")
    generate_system_map()
    generate_air_llm_doc()
    
    print("[4/7] Generating category dashboards...")
    generate_category_dashboards(index_data)
    
    print("[5/7] Generating Skill Contain records...")
    generate_skill_contain_records(index_data)
    
    print("[6/7] Generating source inventory...")
    generate_source_inventory()
    
    print("[7/7] Generating sync setup + MOC...")
    generate_sync_setup()
    generate_moc()
    
    # Count output
    total_files = 0
    for root, dirs, files in os.walk(OUTPUT_DIR):
        total_files += len(files)
    
    print(f"\n✅ Obsidian vault generated: {OUTPUT_DIR}")
    print(f"   {total_files} files across {len(os.listdir(OUTPUT_DIR))} top-level directories")
    
    # Create zip
    zip_path = OUTPUT_DIR + ".zip"
    shutil.make_archive(OUTPUT_DIR, 'zip', OUTPUT_DIR)
    zip_size = os.path.getsize(zip_path) / 1024
    print(f"   Zipped: {zip_path} ({zip_size:.0f} KB)")


if __name__ == "__main__":
    main()
