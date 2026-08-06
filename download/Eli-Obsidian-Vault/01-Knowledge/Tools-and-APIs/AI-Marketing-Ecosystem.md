# AI Marketing Tools Ecosystem

A living map of the AI-powered marketing tools and platforms that Eli references in recommendations and can integrate with operationally.

## OpenSEO

- **Type:** MCP (Model Context Protocol) server for SEO operations
- **Repository:** Open-source, 10.7K+ GitHub stars
- **Backend:** DataForSEO API for keyword data and SERP analysis
- **Function:** Exposes SEO tooling as standardized MCP tools that any MCP-compatible agent or LLM can invoke
- **Relevance:** Provides the tool standardization layer described in [[SEO-Architecture-Patterns]]

## Kai Marketing OS

- **Type:** Strategic marketing intelligence platform
- **Key Feature:** "Four U's" scoring framework — measures marketing effectiveness across **Usefulness**, **Urgency**, **Uniqueness**, and **Ultra-specificity**
- **Function:** Evaluates content, campaigns, and messaging against a structured scoring rubric rather than gut feel
- **Relevance:** Complements the Stone vs. Opinion tagging in [[Digital-Marketing-Pro-Methodology]] by adding a quantitative content quality layer

## Adaptico OS

- **Type:** Go-to-market audit platform
- **Key Feature:** 7-dimension GTM audit covering positioning, messaging, channel fit, sales alignment, content operations, technology stack, and measurement
- **Function:** Produces a structured diagnostic of a company's go-to-market readiness
- **Relevance:** Maps directly to the Discovery and Technical Assessment phases of the methodology

## SEOToolSuite

- **Type:** Open-source keyword research UI
- **Stack:** Next.js frontend
- **Function:** Wraps the DataForSEO API with a user-friendly interface for keyword volume, CPC, and competition data
- **Relevance:** Reference implementation for building keyword data tools; see also [[Keyword-Research-APIs]]

## DataForSEO API

- **Type:** Pay-per-request SEO data API
- **Data:** Keyword volume, CPC, competition scores, SERP features, backlink profiles, site audit metrics
- **Pricing:** Pay-per-request — no subscription, costs scale with actual usage
- **Relevance:** Industry-standard data source that powers OpenSEO, SEOToolSuite, and the keyword pipeline in [[SEO-Architecture-Patterns]]

## chenyme/grok2api

- **Type:** OpenAI-compatible API gateway for Grok models
- **Stack:** Go backend + React admin UI, deployable via Docker
- **Models:** grok-4.5, grok-4.3, grok-chat
- **Relevance:** Planned LLM backend for Eli; see [[Grok-Integration-Path]] and [[LLM-Backend]]

## AutoClaw

- **Type:** AI agent benchmarking platform
- **Scope:** 50+ skills across coding, research, writing, analysis, and tool use
- **Function:** Measures and compares agent capabilities across standardized tasks
- **Relevance:** Used to benchmark Eli's capabilities against other agent systems and identify skill gaps

## Ecosystem Relationships

```
DataForSEO API
    ├─→ OpenSEO (MCP server)
    ├─→ SEOToolSuite (Next.js UI)
    └─→ Keyword Research Pipeline

Grok Models → chenyme/grok2api → Eli LLM Backend

Kai Marketing OS ──→ Content Quality Scoring
Adaptico OS ────→ GTM Audit
AutoClaw ────────→ Agent Benchmarking
```
