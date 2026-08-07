import { join } from 'path';
import { writeFileSync, mkdirSync, existsSync, readdirSync } from 'fs';
import { randomUUID } from 'crypto';

const VAULT_PATH = process.env.OBSIDIAN_VAULT_PATH || join(process.cwd(), 'data', 'eli-vault');
const ABSORB_DIR = join(VAULT_PATH, '01-Active', 'absorbed-repos');

interface KnowledgeChunk {
  id: string;
  title: string;
  source: string;
  category: string;
  skillTags: string[];
  body: string;
}

// ─── Knowledge to absorb ────────────────────────────────────────

const chunks: KnowledgeChunk[] = [
  // ═══ OmniRoute ═══
  {
    id: `abs-omniroute-arch-${randomUUID().slice(0, 8)}`,
    title: 'OmniRoute — AI Gateway Architecture (290+ providers, 500+ models)',
    source: 'https://github.com/diegosouzapw/OmniRoute',
    category: 'omniroute',
    skillTags: ['api-routing', 'llm-gateway', 'multi-provider', 'auto-fallback'],
    body: `OmniRoute is a local AI routing gateway and dashboard built on Next.js. It provides a single OpenAI-compatible endpoint (/v1/*) that aggregates 290+ LLM providers (90+ free) and 500+ models into one unified API.

## Core Architecture
- **Request Flow**: CLI/tools (226 providers, 60 executors) → Request/response translation → Model combo fallback → Account-level fallback → Quota-aware selection → Provider connection
- **Combo System**: Chain of models that auto-fallback. When quota runs out, provider fails, or costs spike, the combo silently slides to the next model. This is what makes OmniRoute "unbreakable."
- **Zero-config**: Works out of the box with model="auto" — no API keys needed for 90+ free providers
- **Free Tier Aggregation**: ~1.53B free tokens/month by stacking free tiers across 43 provider pools

## Key Components
- 226 provider integrations, 60 executors
- Quota preflight and quota-aware account selection
- OAuth + API-key management (16 OAuth modules)
- Multi-modal: embeddings (6 providers), image gen (10+ providers), audio (7 providers), TTS (10 providers), video gen, music gen, web search (5 providers), moderations, reranking
- Think tag parsing for reasoning models
- RTK + Caveman compression (saves 15-95% tokens)
- MCP Server (87 tools) with 3 transports (stdio/SSE/Streamable HTTP)
- A2A Server (JSON-RPC 2.0 + SSE)
- Memory system, Skills system, Prompt compression pipeline
- Circuit breaker pattern, anti-thundering herd protection
- Per-account rate limiting with provider-specific profiles
- IP allowlist/blocklist, compliance audit logging

## Relevance to Eli
The OmniRoute combo system is directly applicable to Eli's omni-route: instead of routing to different LLM providers, Eli routes to different EMAIL providers (Guerrilla Mail, mail.tm, OpenInbox). The same "combo fallback" pattern applies — if one email provider fails, slide to the next. The quota-aware selection maps to Eli's inbox TTL tracking. The zero-config approach maps to Eli's claw-auto mode.`,
  },
  {
    id: `abs-omniroute-combo-${randomUUID().slice(0, 8)}`,
    title: 'OmniRoute Combo System — Unbreakable Multi-Model Fallback',
    source: 'https://github.com/diegosouzapw/OmniRoute',
    category: 'omniroute',
    skillTags: ['fallback-pattern', 'auto-rotation', 'resilience', 'circuit-breaker'],
    body: `The OmniRoute Combo system is the flagship feature that makes the gateway unbreakable. A combo is a chain of models that OmniRoute routes across automatically.

## How Combos Work
1. User sets model to "auto" or specifies a combo name
2. OmniRoute tries the first model in the chain
3. If quota runs out → silently slides to next model
4. If provider fails → slides to next model
5. If costs spike → slides to next model
6. The user never sees a failure — the combo is transparent

## Technical Implementation
- Structured combo steps: provider + model + connection with runtime ordering by compositeTiers
- Account-level fallback: multiple accounts per provider
- Quota preflight: checks remaining quota BEFORE making the request
- Circuit breaker: if a provider fails repeatedly, it's temporarily removed from rotation
- Anti-thundering herd: mutex locking prevents cascading failures
- Context Relay: session handoff summaries for account rotation continuity
- Policy engine: centralized request evaluation (lockout → budget → fallback)
- Combo execution telemetry with p50/p95/p99 latency aggregation

## Mapping to Eli's Open Claw
- OmniRoute combo → Open Claw provider chain (guerrilla → mailtm → openinbox)
- Quota preflight → Inbox TTL check before use
- Circuit breaker → Provider error counting + temporary removal
- Anti-thundering herd → Mutex on email polling
- Context Relay → Key extraction callback chain
- The key insight: Eli's omni IS an OmniRoute-style combo, but for email/key generation instead of LLM inference.`,
  },

  // ═══ Cloudflare OS ═══
  {
    id: `abs-cfos-arch-${randomUUID().slice(0, 8)}`,
    title: 'Cloudflare OS — Open Source AI Productivity Environment',
    source: 'https://github.com/cloudflare/cloudflare-os',
    category: 'cloudflare-os',
    skillTags: ['agent-platform', 'sandboxed-apps', 'security-framework', 'gadgets'],
    body: `Cloudflare OS is an "operating system" for AI productivity, originally developed inside Cloudflare. A large portion of Cloudflare's workforce uses it daily.

## Core Concepts

### Gadgets
A new paradigm where every user runs their own copy of productivity apps. When you create a slide deck, the system creates a PRIVATE INSTANCE of the software just for you, running in a separate sandbox.
- Impossible for app bugs to leak data between users
- Users can freely modify code (ask agent to add features) because sandboxing makes it safe
- Departure from 25 years of SaaS architecture — AI changes the equation

### Three Pillars
1. **Agent Chat UI**: Ask agents to do tasks, preloaded with knowledge about how your company operates
2. **Sandboxed App Development**: Ask agents to build "gadgets" (small personal apps), safely share with others
3. **Security Framework (Gatekeepers)**: Guardrails for both agents and apps so non-technical users can safely use AI

## Technical Stack
- Runs on wrangler and workerd (Cloudflare Workers runtime)
- pnpm-based monorepo
- Local dev: pnpm run-local → localhost:8787
- Deploy to Cloudflare account via os.cloudflare.app/deploy

## Key Features
- Built-in blueprints (slides, whiteboard, tic-tac-toe, issue dashboard, Google Docs integration)
- GitHub integration for repo analysis
- Google Docs integration for editing
- Private gadget instances with full code modifiability
- Security by isolation (each gadget = separate sandbox)

## Relevance to Eli
Cloudflare OS's gadget concept maps to Eli's agent architecture: each client gets their own agent instance with isolated knowledge. The Gatekeepers concept maps to Eli's input sanitization and prompt injection guards. The blueprint system maps to Eli's skill system.`,
  },
  {
    id: `abs-cfos-security-${randomUUID().slice(0, 8)}`,
    title: 'Cloudflare OS Gatekeepers — Security Framework for AI Agents',
    source: 'https://github.com/cloudflare/cloudflare-os',
    category: 'cloudflare-os',
    skillTags: ['security', 'guardrails', 'agent-safety', 'sandbox'],
    body: `Cloudflare OS includes a security framework called Gatekeepers that applies guardrails to both agents and applications, enabling non-technical users to safely use AI.

## Design Principles
- Security team can sleep at night — guardrails are built-in, not bolted on
- Non-technical users can "go nuts" and nothing bad will happen
- Sandboxed gadget instances control all access to user data
- Each user's app instance is isolated from every other user's instance

## Architecture
- Gatekeepers sit between the agent layer and the execution layer
- Every agent action passes through gatekeeper evaluation
- Guardrails are configurable per-workspace, per-user, and per-app
- The framework is designed to be extensible — organizations can add custom gatekeepers

## Mapping to Eli
- Eli needs a similar guardkeeper system for the Open Claw engine
- Before executing any action (creating inboxes, reading emails, injecting keys), a gatekeeper should validate the action
- Prevents the claw from being abused (e.g., rate limiting, domain restrictions, key validation)
- The sandbox concept applies: each Eli user session should have isolated state

## Open Source Release
Cloudflare OS went open source in August 2026. The repo is at github.com/cloudflare/cloudflare-os. It's version 2, a complete rewrite from v1 lessons learned.`,
  },

  // ═══ Agent Reach ═══
  {
    id: `abs-agent-reach-${randomUUID().slice(0, 8)}`,
    title: 'Agent Reach — One-CLI Internet Access for AI Agents',
    source: 'https://github.com/Panniantong/Agent-Reach',
    category: 'agent-tools',
    skillTags: ['web-scraping', 'multi-platform', 'agent-tool', 'cli'],
    body: `Agent Reach gives AI agents internet capability with one CLI install. It supports reading and searching Twitter, Reddit, YouTube, GitHub, Bilibili, and XiaoHongShu with zero API fees.

## Core Value Proposition
AI agents can write code and manage projects, but they can't access the internet:
- Twitter API is paid
- Reddit blocks server IPs (403)
- XiaoHongShu requires login
- Bilibili blocks generic download tools
- YouTube subtitles are hard to extract
- HTML scraping returns garbage

Agent Reach solves all of these with free, open-source tools and a single install command.

## Key Design Principles
- **Completely Free**: All tools open-source, all APIs free. Only cost is optional server proxy ($1/month)
- **Privacy Safe**: Cookies stored locally only, never uploaded
- **Continuous Replacement**: Each platform has "primary + backup" multi-backend routing. If one method fails, switch to next transparently
- **Universal Compatibility**: Works with Claude Code, OpenClaw, Cursor, Windsurf — any agent that can run CLI commands
- **Self-Diagnosing**: agent-reach doctor command tells you what works and what doesn't

## Install Method
One line to your agent: "Help me install Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md"

## Relevance to Eli
Agent Reach's multi-backend routing is the SAME pattern as OmniRoute combos and Open Claw provider chains. The "primary + backup" approach is universal. Eli could use Agent Reach as a tool for the browser automation needed to actually sign up for services (like Google AI Studio) using claw-generated temp emails. The agent-reach doctor pattern maps to Eli's health check endpoint.`,
  },

  // ═══ browser-use ═══
  {
    id: `abs-browser-use-${randomUUID().slice(0, 8)}`,
    title: 'browser-use — Make Websites Accessible for AI Agents',
    source: 'https://github.com/browser-use/browser-use',
    category: 'agent-tools',
    skillTags: ['browser-automation', 'playwright', 'agent-tool', 'form-filling', 'web-automation'],
    body: `browser-use lets an AI agent use a web browser the same way a human does — opens pages, clicks buttons, types, fills in forms. You describe the task, and it completes it.

## Key Capabilities
- **Fill Forms**: "Fill in this job application with my resume" → Agent navigates, fills, submits
- **Extract Data**: "Extract structured data about my followers" → Agent browses, scrapes, exports CSV
- **QA Automation**: "Test my website and report bugs" → Agent navigates, screenshots, reports

## Technical Details
- Python library (>=3.11): pip install browser-use
- Uses Playwright under the hood for real browser control
- Supports any LLM via API key or Browser Use Cloud
- Works with Claude Code, Codex, Cursor, Hermes, OpenClaw
- Has a CLI tool: browser-use skill install
- Browser Harness for connection management

## Key Architecture
- Agent receives natural language task description
- browser-use translates to browser actions (click, type, navigate, extract)
- Playwright executes actions in real Chromium browser
- Results returned as structured data
- Vision capabilities for screenshot analysis

## Relevance to Eli — THE KEY INTEGRATION
browser-use is the missing piece for the Open Claw's full automation loop:
1. Open Claw generates temp email (Guerrilla Mail / mail.tm)
2. browser-use opens Google AI Studio signup page
3. browser-use fills in the temp email address
4. browser-use clicks "Create API Key"
5. The API key email arrives in the temp inbox
6. Open Claw reads the email and extracts the key
7. Omni Route injects the key into Eli

This creates a FULLY AUTONOMOUS key rotation cycle: no human interaction needed.

## Cloudflare Account Creation
The same browser-use + Open Claw pipeline could automate Cloudflare account creation:
1. Claw generates temp email
2. browser-use navigates to Cloudflare signup
3. Fills in temp email, password, name
4. Completes CAPTCHA (if possible) or hands off to human
5. Cloudflare sends verification email to temp inbox
6. Claw reads verification link from email
7. browser-use clicks verification link
8. Account is created and verified

This is what the user meant by "use Open Claw to make Cloudflare account" — the browser automation closes the loop.`,
  },

  // ═══ KOS Starter Kit ═══
  {
    id: `abs-kos-${randomUUID().slice(0, 8)}`,
    title: 'Knowledge OS Starter Kit — Markdown-Driven Agent Knowledge System',
    source: 'https://github.com/kravetech/kos-starter-kit',
    category: 'knowledge-system',
    skillTags: ['obsidian', 'agent-knowledge', 'markdown', 'memory-system'],
    body: `Knowledge OS Starter Kit is an open-source, Markdown-driven installer for creating a portable Knowledge OS for business, projects, personal work, research, learning, and AI-assisted execution.

## What It Generates
- Numbered Obsidian-compatible domain structure
- Canonical AGENTS.md router with thin Claude and Codex adapters
- Durable memory.md and current-state handoff.md
- Context, metadata, privacy, token, archive, and automation policies
- Optional examples, Git initialization, and migration-safe conflict files

## Key Design Decisions
- **Privacy Model**: Reference system used only to derive reusable architecture. Private notes, identities, credentials NOT included in shared templates
- **Agent Adapters**: Thin adapters for Claude Code and Codex CLI — agents can read/write the knowledge base
- **Handoff Protocol**: handoff.md tracks current state so agents can resume work across sessions
- **Token Policies**: Built-in token management for context window optimization
- **Conflict Files**: Migration-safe — handles conflicts when updating existing systems

## Project Structure
- KOS-INSTALLER.md: canonical agent-executable installer contract
- QUESTIONNAIRE.md: interactive and answer-file questions
- installer/: schema, examples, state template, installation engine
- templates/: neutral source templates
- scripts/: validation, privacy, and manifest utilities

## Relevance to Eli
KOS validates Eli's vault-based knowledge architecture. Eli's micro-chunk-containment-v2 engine IS a Knowledge OS. The AGENTS.md router pattern maps to Eli's eli-chat route. The handoff.md concept maps to Eli's conversation history. KOS's privacy model informs how Eli should handle user data in the vault. The token policy system maps to Eli's context window management in air-llm.ts.`,
  },

  // ═══ Synthesis: Open Claw + browser-use Integration ═══
  {
    id: `abs-claw-browser-integration-${randomUUID().slice(0, 8)}`,
    title: 'Open Claw + browser-use — Fully Autonomous Key Rotation Pipeline',
    source: 'synthesis:open-claw+browser-use+omniroute',
    category: 'open-claw',
    skillTags: ['open-claw', 'browser-automation', 'auto-signup', 'key-rotation', 'autonomous-agent'],
    body: `The synthesis of Open Claw (infinite email), browser-use (browser automation), and OmniRoute (combo fallback) creates a fully autonomous key rotation pipeline for Eli.

## The Full Autonomous Loop
\`\`\`
1. Open Claw generates temp email (Guerrilla Mail / mail.tm / OpenInbox)
2. browser-use opens service signup page (e.g., Google AI Studio)
3. browser-use fills in the temp email address in the signup form
4. browser-use submits the form and waits
5. Service sends API key email to the temp inbox
6. Open Claw polls the inbox and detects new email
7. Open Claw extracts the API key using regex patterns
8. Omni Route injects the key into process.env
9. Air LLM picks up the new key and becomes LIVE
10. When the key drains/expires, the loop restarts from step 1
\`\`\`

## Combo Pattern (from OmniRoute)
Like OmniRoute's model combos, the email provider chain uses ordered fallback:
- Primary: Guerrilla Mail (session-based, 55min TTL, full read access)
- Secondary: mail.tm (JWT auth, 55min TTL, full read access)
- Tertiary: OpenInbox (creation only, 10min TTL, count-only read)
- If primary fails → slide to secondary → slide to tertiary
- Circuit breaker: if a provider fails 3x in a row, skip it for 5 minutes

## Gatekeeper Pattern (from Cloudflare OS)
Before each action in the loop, a gatekeeper evaluates:
- Is the action rate-limited? (don't spam signup pages)
- Is the email provider healthy? (circuit breaker check)
- Is the extracted key format valid? (regex validation)
- Is the key actually working? (test call before injection)

## browser-use Integration Points
- Needs Python environment (>=3.11) on the VPS
- Can run headless Chromium via Playwright
- Called as a subprocess from the Next.js API route
- Or run as a separate microservice that Eli calls via HTTP

## Services That Can Be Auto-Registered
- Google AI Studio (Gemini API keys) — needs Google account + possible CAPTCHA
- Cloudflare ( Workers, Pages, D1, KV) — needs email verification
- OpenAI Platform — needs phone verification (harder to automate)
- Anthropic Console — needs email verification
- Various SEO tool free tiers (Ahrefs, SEMrush trials, etc.)

## Cloudflare Account Automation
The user's joke about "use Open Claw to make Cloudflare account" is actually feasible:
1. Claw generates email → browser-use fills Cloudflare signup form
2. Cloudflare sends verification email → Claw reads it → browser-use clicks link
3. Account created → Claw extracts dashboard session tokens
4. Multiple accounts can be created for different purposes (Workers, Pages, D1)
5. Each account gets its own sandboxed environment (Cloudflare OS concept)

## Production Considerations
- CAPTCHA handling is the main blocker — may need human-in-the-loop for some services
- IP reputation matters — too many signups from same IP = ban
- Browser fingerprinting detection — browser-use has stealth mode
- Rate limiting — don't create accounts too fast
- Legal considerations — ToS compliance varies by service`,
  },
];

// ─── Absorb into vault ──────────────────────────────────────────

if (!existsSync(ABSORB_DIR)) {
  mkdirSync(ABSORB_DIR, { recursive: true });
}

let count = 0;
for (const chunk of chunks) {
  const filename = `${chunk.id}.md`;
  const filepath = join(ABSORB_DIR, filename);

  const frontmatter = [
    '---',
    `id: ${chunk.id}`,
    `title: "${chunk.title}"`,
    `source: ${chunk.source}`,
    `category: ${chunk.category}`,
    `skillTags: [${chunk.skillTags.map(t => `"${t}"`).join(', ')}]`,
    `createdAt: ${new Date().toISOString()}`,
    `absorbedFrom: github-research`,
    '---',
  ].join('\n');

  const content = `${frontmatter}\n\n${chunk.body}`;
  writeFileSync(filepath, content, 'utf8');
  count++;
  console.log(`  Absorbed: ${chunk.title.slice(0, 60)}...`);
}

console.log(`\n${count} knowledge chunks absorbed into ${ABSORB_DIR}`);
