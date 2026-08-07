# AI Marketing Tools Ecosystem: Curated Reference

This document catalogs the most significant open-source AI marketing tools and repositories identified through research. Each entry includes what the tool does, its technical stack, integration potential with AI marketing agents, and API availability.

---

## OpenSEO (every-app/open-seo)

**What it does:** A full-featured open-source SEO platform that provides keyword research, rank tracking, site auditing, backlink analysis, and competitor monitoring. It also includes an MCP (Model Context Protocol) server, making it directly callable by AI agents as a tool. This is one of the most comprehensive open-source SEO toolkits available.

**Tech Stack:** Python backend, React frontend, PostgreSQL for data storage, Redis for caching. The MCP server component uses the standard Model Context Protocol specification.

**AI Agent Integration:** The built-in MCP server is the primary integration point. Any MCP-compatible AI agent (Claude, desktop agents, custom orchestrators) can call OpenSEO functions directly: keyword research, rank checks, site audit triggers, and report generation. For non-MCP agents, it exposes a REST API.

**API Availability:** REST API documented in the repository. MCP server included. Self-hosted only (no managed SaaS offering).

---

## Kai Marketing OS (cgallic/kai-cmo-harness)

**What it does:** An AI-powered marketing audit and strategy framework that evaluates marketing efforts using the "Four U's" scoring rubric. The Four U's measure: **Usefulness** (does it solve a real problem?), **Urgency** (does it create time-sensitivity?), **Uniqueness** (does it stand apart from alternatives?), and **Ultra-specificity** (is it precise enough to drive action?). The system runs structured audits against these dimensions and generates prioritized improvement recommendations.

**Tech Stack:** Python-based, designed as a prompt engineering framework for LLM-based marketing analysis. Can operate as a standalone CLI tool or be embedded as a module.

**AI Agent Integration:** Kai Marketing OS is itself an agent orchestration harness. It can be invoked by a parent agent as a specialist sub-agent for marketing audit tasks. Input a website URL or marketing asset description and it returns a structured audit with Four U's scores and recommendations.

**API Availability:** No traditional REST API. Functions as a Python library with callable functions. Can be wrapped in a FastAPI layer or MCP server for remote access.

---

## Adaptico OS (adaptico/adaptico-os)

**What it does:** A go-to-market audit and scoring platform that evaluates businesses across seven dimensions: Market Fit, Channel Strategy, Content Quality, Technical Foundation, Competitive Positioning, Growth Readiness, and Operational Scalability. Each dimension is scored 0-100 with specific sub-metrics. The output is a GTM readiness score with a prioritized action plan.

**Tech Stack:** TypeScript/Node.js backend, React dashboard UI. Uses a modular plugin architecture where each audit dimension is a separate module that can be updated independently.

**AI Agent Integration:** The 7-dimension audit can be triggered programmatically. An AI marketing agent can send business data (URL, analytics data, competitive set) and receive a structured audit report. Useful as a discovery and diagnostic tool at the start of client engagements.

**API Availability:** REST API endpoints for triggering audits and retrieving results. OpenAPI specification available in the repository.

---

## SEOToolSuite (nitishkgupta/seotoolsuite)

**What it does:** An open-source keyword research and SEO analysis UI that provides a visual interface for keyword exploration, SERP analysis, and content optimization suggestions. It integrates with the DataForSEO API as its data backend, giving access to real keyword volume, difficulty, and SERP data without building a custom data pipeline.

**Tech Stack:** Next.js frontend, Python/FastAPI backend, DataForSEO API for data. Uses PostgreSQL for caching results and user data.

**AI Agent Integration:** The FastAPI backend exposes endpoints that an AI agent can call for keyword data, SERP analysis, and content scoring. The agent sends a keyword or URL and receives structured data in return. Particularly useful for agents that need real keyword metrics but cannot directly access paid APIs.

**API Availability:** REST API. Requires a DataForSEO API key (paid, pay-per-request). The tool itself is free and open-source.

---

## SEO Tools API (oguzhan18/seo-tools-api)

**What it does:** A NestJS-based REST API that aggregates multiple SEO data sources into a unified API. It provides endpoints for keyword research, backlink analysis, site auditing, rank tracking, and SERP monitoring. Designed as a backend service for SEO tools and dashboards.

**Tech Stack:** NestJS (Node.js framework with TypeScript), PostgreSQL, Redis, Bull queues for async processing. Follows clean architecture patterns with modular organization.

**AI Agent Integration:** Any AI agent with HTTP capability can call this API to retrieve SEO data. The unified endpoint structure makes it straightforward for an agent to request keyword data, backlink profiles, or audit results without managing multiple data source integrations.

**API Availability:** REST API with Swagger documentation. Self-hosted. Data sources require their own API keys (DataForSEO, Moz, etc.).

---

## DataForSEO API

**What it does:** A raw data API providing keyword research data (search volume, CPC, keyword difficulty), SERP data (organic rankings, paid results, featured snippets, AI overviews), backlink data, on-page data, and business directory data. Pay-per-request pricing model with no subscription required.

**Tech Stack:** RESTful API with JSON responses. Live and batch processing endpoints. Webhook support for async jobs.

**AI Agent Integration:** This is the data layer. An AI marketing agent calls DataForSEO endpoints directly or through a wrapper (like SEOToolSuite or SEO Tools API) to get real search data for strategy decisions. Essential for any agent that performs keyword research, competitive analysis, or rank tracking.

**API Availability:** REST API with comprehensive documentation. Paid (pay-per-request). Free trial credits available. No MCP server, but trivial to wrap.

---

## chenyme/grok2api

**What it does:** An OpenAI-compatible API gateway for xAI's Grok models. It translates OpenAI API format requests into Grok API calls and returns responses in OpenAI-compatible format. This allows any tool or agent built for the OpenAI API to use Grok as a drop-in replacement.

**Tech Stack:** Go backend for the API proxy, React admin dashboard for configuration. Deployable via Docker with a single command. Supports streaming (SSE) and function calling.

**AI Agent Integration:** Configure an AI marketing agent's LLM backend to point at the grok2api endpoint instead of OpenAI. The agent then uses Grok for all text generation, analysis, and reasoning tasks. Particularly useful when Grok's real-time knowledge access (via X data) provides competitive advantage for trending topics and news-based content.

**API Availability:** OpenAI-compatible REST API. Self-hosted. Requires an xAI API key. Supports `/v1/chat/completions`, `/v1/models`, and streaming endpoints.

---

## AutoClaw (autoclaw.z.ai)

**What it does:** A desktop AI agent platform with 50+ built-in skills spanning web browsing, file management, code generation, data analysis, image creation, and marketing tasks. It serves as both a benchmark for agent capabilities and a practical tool for marketing workflows.

**Tech Stack:** Desktop application (Electron-based), modular skill architecture, local LLM support with cloud LLM fallback. Skills are defined as structured prompt templates with tool access.

**AI Agent Integration:** AutoClaw's skill library provides tested prompt engineering patterns that can be extracted and adapted for custom AI marketing agents. The 50+ skills demonstrate proven approaches for common marketing tasks (content writing, data analysis, web research, image generation) that can be replicated in other agent frameworks.

**API Availability:** Desktop application only. No programmatic API for external agents. Value is in the skill patterns and benchmarking data, not direct integration.

---

## Agency Agents (msitarzewski/agency-agents)

**What it does:** The most comprehensive collection of AI marketing specialist agent definitions available. Contains 230+ specialist agents organized across 18 divisions including SEO, paid media, content, social media, email, analytics, CRO, branding, PR, local marketing, e-commerce, B2B, and more. Each agent is defined with a system prompt, critical rules, deliverables, workflow, and success metrics.

**Tech Stack:** Markdown-based agent definitions designed for use with any LLM platform. Agents are prompt-engineering blueprints, not running code. They can be loaded into Claude, GPT, or custom orchestration systems as system prompts.

**AI Agent Integration:** This is the agent definition library. Use individual agent prompts as system prompts for specialized sub-agents in a multi-agent marketing system. An orchestrator agent can load the relevant specialist prompt based on the current task, creating a dynamic team of AI marketing specialists.

**API Availability:** No API. Repository of markdown prompt files. Fully open-source. Agents can be loaded programmatically from the repository or embedded directly into agent configuration files.