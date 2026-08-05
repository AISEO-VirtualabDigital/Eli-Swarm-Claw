#!/usr/bin/env python3
"""
Absorb 4 uploaded zip archives into Eli's knowledge-sources directory.
Converts: Obsidian Vault, obsidian-importer, skill-harness-manager, agent-eli-v1
into categorized .md files the knowledge search engine can index.
"""

import os
import json
import shutil
from pathlib import Path

KS_DIR = Path('/home/z/my-project/upload/knowledge-sources')
TEMP_DIR = Path('/home/z/my-project/upload/extract-temp')

def write_ks(filename: str, content: str):
    """Write a knowledge source file."""
    path = KS_DIR / filename
    path.write_text(content, encoding='utf-8')
    print(f'  ✅ {filename} ({len(content)} chars)')

def read_file(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8')
    except:
        return ''

# ============================================================
# 1. ELI-OS OBSIDIAN VAULT — 48 files → consolidated by section
# ============================================================
print('\n🔵 1. Processing Eli-OS Obsidian Vault...')

vault = TEMP_DIR / 'eli-obsidian-vault/Eli-OS-Obsidian-Vault'

# --- Dashboard & README ---
write_ks('eli-obsidian-vault-dashboard.md', read_file(vault / '00-DASHBOARD.md'))
write_ks('eli-obsidian-vault-readme.md', read_file(vault / 'README.md'))

# --- Human Orders ---
ho_files = list((vault / '01-HUMAN-ORDERS').glob('*.md'))
ho_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(ho_files) if f.name != 'README.md')
write_ks('eli-obsidian-human-orders.md', f'# Eli-OS Human Orders\n\n{ho_content}')

# --- Tasks & Context ---
task_files = list((vault / '02-TASKS').glob('*.md'))
task_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(task_files) if f.name != 'README.md')
write_ks('eli-obsidian-tasks-context.md', f'# Eli-OS Tasks & Context Snapshots\n\n{task_content}')

# --- Architecture ---
arch_content = read_file(vault / '03-ARCHITECTURE/README.md') + '\n\n'
arch_content += read_file(vault / '03-ARCHITECTURE/Authority-Model.md') + '\n\n'
arch_content += read_file(vault / '03-ARCHITECTURE/Phase-1-Research-Framework.md') + '\n\n'
arch_content += read_file(vault / '03-ARCHITECTURE/ADR/ADR-001-Phase-1-Binding-Decisions.md')
write_ks('eli-obsidian-architecture.md', f'# Eli-OS Architecture & Binding Decisions\n\n{arch_content}')

# --- Sprints ---
sprint_files = list((vault / '04-SPRINTS').glob('*.md'))
sprint_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(sprint_files) if f.name != 'README.md')
write_ks('eli-obsidian-sprints.md', f'# Eli-OS Sprint Plans\n\n{sprint_content}')

# --- Repository ---
repo_files = list((vault / '05-REPOSITORY').glob('*.md'))
repo_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(repo_files) if f.name != 'README.md')
write_ks('eli-obsidian-repository.md', f'# Eli-OS Repository Inventory & Migration\n\n{repo_content}')

# --- Agents ---
agent_files = list((vault / '06-AGENTS').glob('*.md'))
agent_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(agent_files) if f.name != 'README.md')
write_ks('eli-obsidian-agents.md', f'# Eli-OS Agent Handoff & Output Log\n\n{agent_content}')

# --- Reviews ---
review_files = list((vault / '07-REVIEWS').glob('*.md'))
review_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(review_files) if f.name != 'README.md')
write_ks('eli-obsidian-reviews.md', f'# Eli-OS Review Queue\n\n{review_content}')

# --- Logs ---
log_files = list((vault / '08-LOGS').glob('*.md'))
log_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(log_files) if f.name != 'README.md')
write_ks('eli-obsidian-logs.md', f'# Eli-OS Build, Decision & Change Logs\n\n{log_content}')

# --- Knowledge / Glossary ---
knowledge_files = list((vault / '09-KNOWLEDGE').glob('*.md'))
knowledge_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(knowledge_files) if f.name != 'README.md')
write_ks('eli-obsidian-glossary.md', f'# Eli-OS Knowledge & Glossary\n\n{knowledge_content}')

# --- Templates ---
tmpl_files = list((vault / '10-TEMPLATES').glob('*.md'))
tmpl_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(tmpl_files) if f.name != 'README.md')
write_ks('eli-obsidian-templates.md', f'# Eli-OS Document Templates\n\n{tmpl_content}')

# --- Agent Skills (CRITICAL — 8 skills + registry) ---
skill_files = list((vault / '11-AGENT-SKILLS').glob('*.md'))
skill_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(skill_files) if f.name != 'README.md')
write_ks('eli-obsidian-agent-skills.md', f'# Eli-OS Agent Skill Stack\n\n{skill_content}')

# --- Manual Rewiring ---
rewire_files = list((vault / '12-MANUAL-REWIRING').glob('*.md'))
rewire_content = '\n\n'.join(f'## {f.name}\n\n{read_file(f)}' for f in sorted(rewire_files) if f.name != 'README.md')
write_ks('eli-obsidian-manual-rewiring.md', f'# Eli-OS Manual Rewiring Policy\n\n{rewire_content}')

print(f'  → {len(list(vault.rglob("*.md")))} vault files → 13 consolidated knowledge sources')

# ============================================================
# 2. OBSIDIAN IMPORTER — README + format docs
# ============================================================
print('\n🟢 2. Processing Obsidian Importer...')

oi = TEMP_DIR / 'obsidian-importer/obsidian-importer-master'

# Consolidate all format documentation
format_docs = ''
for f in sorted((oi / 'src/formats').glob('*.ts')):
    content = read_file(f)
    if content and len(content) > 50:
        # Extract first 200 lines of each format file
        lines = content.split('\n')[:200]
        format_docs += f'### {f.name}\n\n{"\n".join(lines)}\n\n---\n\n'

oi_content = f"""# Obsidian Importer — Format Conversion Reference

## Overview

The Obsidian Importer is an official Obsidian plugin for converting notes from other platforms (Apple Notes, Bear, Evernote, Google Keep, Notion, HTML, CSV, and more) into Obsidian-compatible Markdown.

## Supported Formats

The importer handles these source formats through dedicated converter modules:
- **Apple Notes** — converts SQLite database to Markdown with scan/image handling
- **Apple Journal** — journal entry conversion
- **Bear (bear2bk)** — Bear markdown export format
- **CSV** — tabular data to markdown tables
- **Evernote (ENEX)** — Evernote export XML to Markdown
- **HTML** — generic HTML to clean Markdown
- **Google Keep (JSON)** — Google Takeout JSON format
- **Notion (Export)** — Notion HTML/CSV export conversion
- **Notion (API)** — Direct Notion API integration with block converter, database helpers, formula converter, and vault helpers

## Architecture

The importer uses a base `FormatImporter` class extended by each format. Key design patterns:
- `createNote()` creates TFile objects in the vault
- `createFolder()` handles nested folder structures
- Content is processed in batches for performance
- Attachments are extracted and relinked
- Internal links are converted to `[[wikilink]]` format

{format_docs}

## Base Importer Interface

{read_file(oi / 'src/base.ts')}

## Filesystem Utilities

{read_file(oi / 'src/filesystem.ts')}

## File Format Importer Interface

{read_file(oi / 'src/format-importer.ts')}

## README

{read_file(oi / 'README.md')}
"""
write_ks('obsidian-importer-reference.md', oi_content)
print(f'  → 1 consolidated knowledge source from obsidian-importer')

# ============================================================
# 3. SKILL HARNESS MANAGER — README + key source docs
# ============================================================
print('\n🟡 3. Processing Skill Harness Manager...')

shm = TEMP_DIR / 'skill-harness-manager/skill-harness-manager-main'

shm_content = f"""# Skill and Harness Manager — Obsidian Plugin Reference

## Overview

The Skill and Harness Manager is an Obsidian plugin that consolidates, organizes, and runs AI skills directly from the Obsidian vault. It discovers SKILL.md files across multiple directories (.claude/, .codex/, .cursor/, .agents/, marketplace folders), lets users organize/filter/tag them, and makes each skill runnable with a click.

Key principle: No bundled model, no inference, no network calls. It finds, organizes, and launches. The actual AI work runs in whatever CLI you point it at (Claude Code, Codex, omnigent, or your own).

## Capabilities

- **Right-click a file** → run a skill targeting that file (reformat, transcribe, summarize)
- **Sidebar buttons** → pin any skill to its own ribbon icon with a custom Lucide icon
- **Command palette** → every pinned skill registers a command
- **Browser view** → Skills, Commands, Scripts, Sessions, Agents, Harnesses tabs
- **Launch modes**: Headless (background) or Terminal (visible, interactive)
- **Custom harnesses**: Add Claude Code, Codex, or any CLI as a launch target
- **Sessions**: Track launches, reconnect to running sessions
- **Bash scripts**: User-authored scripts with headless/terminal modes
- **Tag system**: Tags from frontmatter, description #hashtags, and folder-derived virtual tags
- **Hidden file support**: Reveal .claude/, .codex/ etc. in the file explorer

## Architecture

### Plugin Settings (SkillLayerSettings)

{read_file(shm / 'src/types.ts')}

### Launch System

{read_file(shm / 'src/launch.ts')}

### Detection Engine

{read_file(shm / 'src/detector.ts')}

### Session Management

{read_file(shm / 'src/sessions.ts')}

### Folder Scanning

{read_file(shm / 'src/folders.ts')}

### Terminal Integration

{read_file(shm / 'src/terminal.ts')}

### YAML Frontmatter Viewer

{read_file(shm / 'src/yamlViewer.ts')}

### README

{read_file(shm / 'README.md')}
"""
write_ks('skill-harness-manager-reference.md', shm_content)
print(f'  → 1 consolidated knowledge source from skill-harness-manager')

# ============================================================
# 4. AGENT ELI V1 — docs + registry + code
# ============================================================
print('\n🔴 4. Processing Agent Eli v1...')

ae = TEMP_DIR / 'agent-eli-v1/agent-eli-v1'

# --- Architecture & Docs (consolidated) ---
arch_docs = read_file(ae / 'docs/ARCHITECTURE.md') + '\n\n'
arch_docs += read_file(ae / 'docs/IMPLEMENTATION_ROADMAP.md') + '\n\n'
arch_docs += read_file(ae / 'docs/ORANGE_ORBIT_MIGRATION.md') + '\n\n'
arch_docs += read_file(ae / 'docs/SECURITY.md')
write_ks('agent-eli-v1-architecture.md', f'# Agent Eli v1 — Architecture & Documentation\n\n{arch_docs}')

# --- README ---
write_ks('agent-eli-v1-readme.md', read_file(ae / 'README.md'))

# --- Backend Code (consolidated) ---
backend_code = read_file(ae / 'backend/app/main.py') + '\n\n'
backend_code += read_file(ae / 'backend/app/api/routes.py') + '\n\n'
backend_code += read_file(ae / 'backend/app/core/policy.py') + '\n\n'
backend_code += read_file(ae / 'backend/app/services/registry.py') + '\n\n'
backend_code += '## Requirements\n\n' + read_file(ae / 'backend/requirements.txt') + '\n\n'
backend_code += '## Dockerfile\n\n' + read_file(ae / 'backend/Dockerfile') + '\n\n'
backend_code += '## Environment Variables\n\n' + read_file(ae / '.env.example')
write_ks('agent-eli-v1-backend-code.md', f'# Agent Eli v1 — Backend Code Reference\n\n{backend_code}')

# --- Frontend (HTML + CSS + JS) ---
frontend_content = read_file(ae / 'frontend/public/index.html') + '\n\n'
frontend_content += '## JavaScript (app.js)\n\n' + read_file(ae / 'frontend/public/assets/app.js') + '\n\n'
frontend_content += '## CSS (styles.css)\n\n' + read_file(ae / 'frontend/public/assets/styles.css')
write_ks('agent-eli-v1-frontend-prototype.md', f'# Agent Eli v1 — Frontend Prototype\n\n{frontend_content}')

# --- Integration Registry ---
integrations = []
for f in sorted((ae / 'registry/integrations').glob('*.json')):
    data = json.loads(f.read_text())
    integrations.append(data)

int_content = json.dumps(integrations, indent=2)
write_ks('agent-eli-v1-integration-registry.json', int_content)

# Also as markdown for better searchability
int_md = '# Agent Eli v1 — Integration Registry\n\n'
for i in integrations:
    int_md += f"""## {i['name']}

- **ID**: {i['id']}
- **Category**: {i['category']}
- **Provider**: {i['provider']}
- **Auth**: {', '.join(i['auth'])}
- **Capabilities**: {', '.join(i['capabilities'])}
- **Approval Required**: {', '.join(i.get('approval_required', [])) or 'None'}
- **Status**: {i['status']}

"""
write_ks('agent-eli-v1-integration-registry.md', int_md)

# --- Skill Registry ---
skills = []
for f in sorted((ae / 'registry/skills').glob('*.json')):
    data = json.loads(f.read_text())
    skills.append(data)

skill_md = '# Agent Eli v1 — SEO Skill Registry\n\n'
for s in skills:
    skill_md += f"""## {s['name']}

- **ID**: {s['id']}
- **Category**: {s['category']}
- **Modules**: {', '.join(s.get('modules', []))}
- **Inputs**: {', '.join(s.get('inputs', []))}
- **Outputs**: {', '.join(s.get('outputs', []))}
- **Approval Required**: {', '.join(s.get('approval_required', [])) or 'None'}
- **Status**: {s['status']}

"""
write_ks('agent-eli-v1-skill-registry.md', skill_md)

# --- Workflow Registry ---
workflows = []
for f in sorted((ae / 'registry/workflows').glob('*.json')):
    data = json.loads(f.read_text())
    workflows.append(data)

wf_md = '# Agent Eli v1 — Workflow Registry\n\n'
for w in workflows:
    wf_md += f"""## {w['name']}

- **ID**: {w['id']}
- **States**: {' → '.join(w.get('states', []))}
- **Steps**: {', '.join(w.get('steps', []))}
- **Production Execution**: {w.get('production_execution', False)}

"""
write_ks('agent-eli-v1-workflow-registry.md', wf_md)

# --- Infrastructure ---
infra_content = read_file(ae / 'infra/docker-compose.yml') + '\n\n'
infra_content += read_file(ae / 'package.json')
write_ks('agent-eli-v1-infrastructure.md', f'# Agent Eli v1 — Infrastructure & Config\n\n{infra_content}')

print(f'  → 9 knowledge sources from agent-eli-v1')

# ============================================================
# 5. GRAND CONSOLIDATION — "Eli Core Identity" master doc
# ============================================================
print('\n🟣 5. Creating Eli Core Identity master document...')

master_content = f"""# Eli OS — Complete Core Identity & Knowledge Base

This document is Eli's self-knowledge. It contains everything Eli needs to know about who she is, what she does, her architecture, skills, authority model, and operational doctrine.

---

## WHO IS ELI?

Eli OS is VirtuaLab Digital's proprietary AI growth intelligence layer. She lives inside the Growth Command Center dashboard. Her operator is Joseph Rainer Miro, an AI SEO Scientist, Automation Specialist, and Full Stack SEO Systems Builder representing VirtuaLab Digital.

### Core Identity

- **Name**: Eli OS (Agent Eli)
- **Operator**: Joseph Rainer Miro
- **Organization**: VirtuaLab Digital
- **Role**: AI SEO Operating System, Human-led AI Growth Intelligence
- **Prime Directive**: Eli does not exist to agree. Eli exists to make the operator faster without lying.
- **Execution Model**: OBSERVE → ANALYZE → PLAN → PREVIEW → APPROVAL → EXECUTE → VERIFY → RECORD

### Authority Model

```text
HUMAN (absolute authority)
  ↓
OBSIDIAN (message relay and persistent coordination)
  ↓
AGENT (task-bound execution)
```

Rules:
- Human orders are absolute
- Obsidian relays and versions the message
- Agent is task-bound
- Agents may not expand scope
- Conflicts return to human
- Operator is final authority

---

## ELI'S ARCHITECTURE

### Public Layer
- Portfolio, Work, Agent Eli, Systems, Skills, Services, Case Studies, Contact
- Operator portrait and professional identity

### Private Layer (Command Center)
- Dashboard, Leads, Audits, Campaigns, Content Engine, Rank Tracking
- Approvals, Activity Logs, Integrations, Workflows, Sentinel Scrapers
- Open SEO Skills, Crew Registry, Databases, Knowledge Vault
- Orange Orbit Legacy, Settings

### Core Runtime
- FastAPI backend with owner authentication
- Knowledge search with RAG
- Memory create/search/forget
- OpenRouter model routing
- Crew registry for specialist agents
- PostgreSQL (source of truth), Redis (realtime coordination)
- Docker deployment, safe mode

### State Machine

Every action follows: OBSERVE → ANALYZE → PLAN → PREVIEW → APPROVAL → EXECUTE → VERIFY → RECORD

### Integration Hub

{int_md}

---

## ELI'S SEO SKILL REGISTRY

{skill_md}

---

## ELI'S AGENT SKILL STACK (Obsidian Vault)

The Agent Skill Stack defines Eli's operational capabilities and constraints:

**STACK = Structured Task-Aware Capability Knowledge**

### Skill Resolution Order

```text
Human explicit instruction
  ↓
Active task anchor
  ↓
Approved project skills
  ↓
Approved global skills
  ↓
Agent default behavior
```

### Core Skills

{read_file(vault / '11-AGENT-SKILLS/SKILL-STACK-REGISTRY.md')}

### Skill Details

{read_file(vault / '11-AGENT-SKILLS/SKILL-001-Task-Anchoring.md')}

{read_file(vault / '11-AGENT-SKILLS/SKILL-002-Human-Order-Compliance.md')}

{read_file(vault / '11-AGENT-SKILLS/SKILL-003-Obsidian-Relay-Reading.md')}

{read_file(vault / '11-AGENT-SKILLS/SKILL-004-Rust-Workspace-Engineering.md')}

{read_file(vault / '11-AGENT-SKILLS/SKILL-005-Repository-Preservation.md')}

{read_file(vault / '11-AGENT-SKILLS/SKILL-006-Manual-Rewiring-Compliance.md')}

{read_file(vault / '11-AGENT-SKILLS/SKILL-007-Evidence-and-Logs.md')}

{read_file(vault / '11-AGENT-SKILLS/SKILL-008-Stop-on-Conflict.md')}

---

## MANUAL REWIRING POLICY

{read_file(vault / '12-MANUAL-REWIRING/MANUAL-REWIRING-POLICY.md')}

---

## SECURITY & GOVERNANCE

{read_file(ae / 'docs/SECURITY.md')}

---

## GLOSSARY

{read_file(vault / '09-KNOWLEDGE/GLOSSARY.md')}

---

## IMPLEMENTATION ROADMAP

{read_file(ae / 'docs/IMPLEMENTATION_ROADMAP.md')}

---

## WORKFLOW REGISTRY

{wf_md}

---

## OBSIDIAN VAULT STRUCTURE

The Eli-OS Obsidian Vault is organized around 12 sections:

00. DASHBOARD — Command center overview and navigation
01. HUMAN ORDERS — Absolute instructions issued by the operator
02. TASKS — Task definitions, context snapshots, acceptance criteria
03. ARCHITECTURE — ADRs, research framework, authority model
04. SPRINTS — Sprint plans with locked build orders
05. REPOSITORY — Inventory, migration boundaries, conflict reports
06. AGENTS — Handoff notes, output logs, review status
07. REVIEWS — Review queue, approvals, rejections
08. LOGS — Build, CI, runtime, and debugging logs
09. KNOWLEDGE — Approved project knowledge, glossary, references
10. TEMPLATES — Reusable templates for orders, tasks, ADRs, reviews
11. AGENT SKILLS — STACK registry with 8 approved skills
12. MANUAL REWIRING — Human workflow control policy and logs

## OBSIDIAN IMPORTER KNOWLEDGE

Eli understands how to import content from multiple note-taking platforms into Obsidian:

Supported source formats:
- Apple Notes (SQLite database conversion)
- Apple Journal
- Bear (bear2bk export)
- CSV (tabular to markdown tables)
- Evernote (ENEX XML export)
- HTML (generic conversion)
- Google Keep (JSON export)
- Notion (both HTML export and API-based)

## SKILL HARNESS MANAGER KNOWLEDGE

Eli understands the Skill and Harness Manager Obsidian plugin:
- Discovers SKILL.md files across .claude/, .codex/, .cursor/, .agents/ directories
- Supports right-click, sidebar ribbon, command palette, and browser view launch
- Headless (background) or terminal (interactive) launch modes
- Custom harnesses for Claude Code, Codex, omnigent, or any CLI
- Session tracking, tag management, YAML viewer integration
- No bundled model — delegates to configured AI CLIs

---

## ORANGE ORBIT LEGACY MIGRATION

{read_file(ae / 'docs/ORANGE_ORBIT_MIGRATION.md')}
"""

write_ks('eli-core-identity.md', master_content)
print(f'  → Master identity document created ({len(master_content)} chars)')

# ============================================================
# SUMMARY
# ============================================================
print('\n' + '='*60)
print('✅ ABSORPTION COMPLETE')
print('='*60)

ks_files = sorted(KS_DIR.glob('eli-obsidian-*.md')) + \
           sorted(KS_DIR.glob('obsidian-importer-*.md')) + \
           sorted(KS_DIR.glob('skill-harness-*.md')) + \
           sorted(KS_DIR.glob('agent-eli-v1-*.md')) + \
           sorted(KS_DIR.glob('agent-eli-v1-*.json')) + \
           [KS_DIR / 'eli-core-identity.md']

total = 0
for f in ks_files:
    size = f.stat().st_size
    total += size
    print(f'  {f.name:<50} {size:>6,} bytes')

print(f'  {"—"*50} {"—":>6}')
print(f'  {len(ks_files)} new knowledge source files, {total:,} total bytes')
print(f'\n  Total knowledge-sources: {len(list(KS_DIR.glob("*")))} files')
