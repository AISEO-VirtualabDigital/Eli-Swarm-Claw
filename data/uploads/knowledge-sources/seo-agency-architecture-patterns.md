# SEO Agency Architecture Patterns: Building AI-Powered Marketing SaaS

This document defines the architectural patterns for building an AI-powered SEO and marketing agency platform as a SaaS product. These patterns are drawn from practical implementation experience and designed to support multi-tenant operation, agent orchestration, and real-time data processing at scale.

---

## MicroSaaS Architecture for AI Agents (Eli's Pattern)

The core architectural approach is a MicroSaaS model where the application is composed of small, independently deployable services, each responsible for a specific marketing function. This differs from both monolithic SaaS and microservices in its emphasis on AI-agent-mediated workflows.

**Principles:**
- Each service exposes both a human-facing UI and an agent-facing API (MCP or REST).
- Services communicate through a shared event bus for asynchronous operations and direct API calls for synchronous queries.
- AI agents sit between the user and the services, translating natural language requests into API calls and formatting responses.
- State is managed per-tenant with complete data isolation.
- Each service can be developed, deployed, and scaled independently.

**Service Decomposition:** Keyword Research Service, Rank Tracking Service, Site Audit Service, Content Generation Service, Backlink Analysis Service, Competitor Intelligence Service, Reporting Service, Client Management Service, Billing Service. Each service owns its data domain and exposes a clean API boundary.

---

## Multi-Agent Orchestration Patterns

### Supervisor Pattern
A central orchestrator agent receives user requests, classifies the task, delegates to specialist agents, and synthesizes results. The supervisor maintains conversation context, handles task routing, and manages agent handoffs. This is the default pattern for complex marketing strategy tasks that span multiple domains.

**Implementation:** The supervisor agent loads specialist agent prompts dynamically from a prompt registry. It calls specialist agents via function calling or MCP tool use. Each specialist returns structured output (JSON) that the supervisor formats for the user.

### Pipeline Pattern
For well-defined, sequential workflows (e.g., SEO audit pipeline), agents are arranged in a fixed sequence. The output of agent N becomes the input of agent N+1. This pattern is used for automated processes that run on a schedule.

**Implementation:** Define pipeline steps as a directed acyclic graph (DAG). Each node is an agent invocation with input/output schemas. A pipeline runner executes the DAG, handles retries and error states, and stores intermediate results for auditability.

### Debate Pattern
For high-stakes decisions (budget allocation, channel strategy), multiple agents with different perspectives analyze the same data and produce independent recommendations. A judge agent evaluates the recommendations and produces a final synthesis.

**Implementation:** Parallel agent invocations with shared context. The judge agent receives all recommendations plus the original data. Outputs include the final decision, confidence level, and dissenting opinions documented for transparency.

---

## RAG Pipeline Design for Marketing Knowledge

The Retrieval-Augmented Generation pipeline provides agents with access to the knowledge base of SEO and marketing best practices.

**Pipeline Stages:**
1. **Ingestion:** Marketing knowledge documents (strategy guides, audit checklists, tool documentation) are chunked into 500-1000 token segments with metadata tags (topic, source, date, confidence level).
2. **Embedding:** Chunks are embedded using a marketing-optimized embedding model and stored in a vector database.
3. **Indexing:** Full-text search index (BM25) is maintained alongside vector index for hybrid retrieval.
4. **Retrieval:** Agent queries trigger hybrid search (vector similarity + keyword relevance). Top-K results are reranked using a cross-encoder model.
5. **Augmentation:** Retrieved context is injected into the agent's system prompt or function response.
6. **Generation:** The agent produces its output grounded in retrieved knowledge.

**Storage:** PostgreSQL with pgvector extension provides both relational and vector storage in a single database, reducing operational complexity. For larger scale, Pinecone or Weaviate can replace the vector component.

---

## Keyword Research Data Pipeline

The keyword research pipeline moves data from raw API responses through processing to user-facing results.

**Flow:** DataForSEO API -> Ingestion Worker (validates, deduplicates, normalizes) -> Processing Queue (calculates composite scores, clusters keywords, assigns intent) -> Storage (PostgreSQL: keywords, search volumes, difficulty scores, SERP features) -> API Layer (GraphQL for flexible queries) -> UI (keyword explorer, content briefs, gap analysis).

**Key Design Decisions:**
- Cache all API responses indefinitely (historical keyword data has lasting value). Use a write-through cache with DataForSEO as the source of truth for current data.
- Keyword clustering runs asynchronously after ingestion. A background worker groups semantically similar keywords using embedding similarity (threshold: 0.85 cosine similarity).
- Intent classification uses a lightweight local classifier (not LLM) for speed: rule-based with TF-IDF features trained on intent-labeled keyword sets.
- Composite opportunity score formula: (Search Volume Normalized * 0.4) + ((100 - Keyword Difficulty) * 0.35) + (SERP Feature Opportunity * 0.15) + (Business Relevance * 0.1).

---

## SEO Audit Automation Workflow

Automated site audits run on a configurable schedule (weekly for active clients, monthly for maintenance).

**Pipeline:** Crawl trigger -> Headless browser crawl (Playwright) -> Technical analysis (redirects, status codes, indexability) -> On-page analysis (meta tags, headings, content quality, internal links) -> Performance analysis (Core Web Vitals via Lighthouse) -> Structured data validation -> Issue aggregation and prioritization (critical/warning/info) -> Report generation -> Client notification.

**Scaling:** Each crawl runs in an isolated container with resource limits. A crawl orchestrator manages the queue, assigns crawls to available workers, and handles timeouts. For large sites (50,000+ pages), crawls are distributed across multiple workers with URL range partitioning.

---

## Content Generation Pipeline

**Flow:** Keyword/Topic Input -> RAG Context Retrieval (topical authority content, competitor analysis, brand guidelines) -> Outline Generation Agent (produces H2/H3 structure with key points) -> Human Review Gate (optional, configurable per client) -> Section-by-Section Generation (parallel agent calls for each section) -> Assembly Agent (combines sections, ensures coherence, adds transitions) -> SEO Optimization Agent (meta tags, internal links, structured data suggestions) -> Plagiarism and Fact Check -> Publishing API.

**Quality Controls:** All generated content passes through a quality scoring agent that evaluates readability (Flesch-Kincaid), keyword density, heading structure, content depth (word count and topic coverage), and brand voice adherence. Content below the quality threshold is flagged for revision rather than published.

---

## Rank Tracking Architecture

**Data Sources:** Google Search Console API (organic data, free), DataForSEO API (SERP position data, paid), and direct SERP scraping (backup).

**Pipeline:** Scheduled keyword position checks (daily for top-priority keywords, weekly for long-tail) -> Position data storage with full history -> Aggregation (average position, distribution, visibility score) -> Change detection (rank gains, losses, new entries, lost rankings) -> Alert triggers (significant position changes, new competitors) -> Dashboard API.

**Efficiency:** Rank checks are batched and throttled to respect API rate limits. Historical data is compressed after 90 days (daily granularity becomes weekly). The visibility score is calculated as: sum of (1 / position) for all tracked keywords where position <= 20, expressed as a percentage of maximum possible.

---

## Client Reporting Automation

Reports are generated from a template system that pulls data from all services.

**Architecture:** Report Template Engine (Jinja2-based with custom filters for marketing metrics) -> Data Aggregation Layer (queries all service APIs for the reporting period) -> Chart Generation (static SVG charts for PDF, interactive Chart.js for web dashboards) -> Output Formats (PDF via WeasyPrint, HTML for web, CSV for data export).

**Scheduling:** Reports are generated on client-defined schedules (weekly, monthly, quarterly). Each report generation is an async job that runs at the configured time and delivers via email and in-app notification.

---

## Integration Patterns

### Google Search Console
Use the Google Search Console API (OAuth2 service account) to pull search performance data, index coverage reports, and sitemap status. Data syncs daily. Store raw data in the analytics warehouse for trend analysis beyond GSC's 16-month retention.

### Google Analytics
GA4 Data API (v1) via OAuth2 service account. Pull user acquisition, engagement, and conversion data. Create custom reports via the API that go beyond standard GA4 interface capabilities.

### GoHighLevel (GHL)
GHL REST API for CRM data, pipeline management, and workflow triggers. Bidirectional sync: marketing performance data flows into GHL contacts, and GHL conversion data flows back into the reporting system. Use GHL webhooks for real-time event triggers.

### n8n
n8n serves as the workflow automation layer connecting services that lack native integration. Key workflows: new lead in GHL triggers keyword research task, rank change alert triggers content update review, monthly report completion triggers client email. n8n's self-hosted option keeps data within the platform.

### Baserow
Baserow (open-source Airtable alternative) serves as the operational database for non-technical team members. Keyword maps, content calendars, client onboarding checklists, and competitive analysis matrices are managed in Baserow. API access allows agents and services to read/write operational data.

---

## LLM Backend Integration

### Grok API via chenyme/grok2api
Deploy the grok2api Docker container as an OpenAI-compatible proxy. Configure it with an xAI API key. Point the agent orchestration layer's LLM configuration to this proxy endpoint using the standard OpenAI SDK. This provides access to Grok's real-time knowledge (powered by X/Twitter data) for tasks requiring current events awareness, trend analysis, and news-based content. The OpenAI compatibility means no code changes are needed in the agent layer -- just swap the base URL and API key.

### Gemini API
Use Google's Gemini API (via the google-generativeai Python/Node SDK) as a secondary or primary LLM backend. Gemini's strengths for marketing applications include: native grounding with Google Search (for fact verification), multimodal capabilities (analyzing landing page screenshots, ad creatives, and SERP screenshots), and long context window (up to 1M tokens for processing full site audits in a single prompt). Implement a model router that selects the optimal LLM per task based on cost, speed, and capability requirements.

### MCP (Model Context Protocol) for Tool Integration
MCP provides a standardized protocol for LLMs to discover and invoke tools. Implement MCP servers for each internal service (keyword research, rank tracking, site audit, content generation). The agent orchestration layer connects to MCP servers as a client, allowing any connected LLM to invoke marketing tools without custom integration code. MCP servers handle authentication, rate limiting, and input validation. This pattern enables rapid addition of new tools and supports third-party MCP servers (like OpenSEO) alongside internal ones.
