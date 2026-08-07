# SEO Architecture Patterns

Reusable architectural patterns for building SEO intelligence systems. These patterns inform how Eli's knowledge pipeline is structured and how specialist agents from [[Agency-Agents-Marketing-Suite]] are orchestrated.

## Multi-Agent Orchestration Patterns

### Supervisor Pattern
A single orchestrator agent receives the task, decomposes it into subtasks, and routes each to the appropriate specialist agent. The supervisor synthesizes results into a unified output. Best for well-defined, sequential workflows like a full SEO audit.

### Pipeline Pattern
Agents are arranged in a fixed sequence where the output of one becomes the input to the next. No routing intelligence needed — data flows linearly. Ideal for content generation: keyword research → outline → draft → optimization → quality review.

### Debate Pattern
Multiple agents analyze the same problem independently, then their outputs are compared and reconciled. Contradictions are surfaced explicitly rather than hidden. Useful for competitive analysis and strategy formulation where blind spots are costly.

## RAG Pipeline with Hybrid Retrieval

Eli's own knowledge retrieval (see [[MicroSaaS-Architecture]]) uses hybrid retrieval combining:

- **Sparse retrieval:** TF-IDF with bigram matching and synonym expansion — fast, catches exact terminology
- **Semantic gap bridging:** Synonym expansion maps colloquial queries to canonical terminology in the knowledge base
- **Cache layer:** 5-minute TTL cache prevents redundant computation for burst queries on similar topics

The pipeline returns ranked results that are injected into the LLM context before generation, ensuring responses are grounded in documented methodology rather than hallucinated.

## Keyword Data Pipeline

A four-stage pipeline for transforming raw keyword data into actionable intelligence:

```
DataForSEO API → Structured Storage → Internal API → Visualization UI
```

1. **Ingestion:** DataForSEO API provides volume, CPC, and competition data (see [[Keyword-Research-APIs]])
2. **Storage:** Normalized into SQLite via Prisma with deduplication and historical tracking
3. **Serving:** Internal API endpoint exposes filtered, scored keyword sets to agents and UI
4. **Visualization:** SEOToolSuite-style Next.js interface for human exploration

## SEO Audit Automation

Automated audits follow a structured checklist approach:
- Technical health (crawlability, indexability, Core Web Vitals)
- On-page completeness (meta tags, schema markup, internal linking)
- Content coverage (keyword mapping, gap analysis, cannibalization detection)
- Off-page signals (backlink profile, domain authority trajectory)
- AI visibility (AEO/GEO audit across six platforms)

Each audit section produces a scored output with prioritized action items.

## Content Generation Pipeline with Quality Gates

Generated content passes through sequential quality gates before publication:

1. **Relevance gate:** Does it match the target keyword intent?
2. **Uniqueness gate:** Does it add value beyond existing SERP results?
3. **Accuracy gate:** Are claims verifiable? (Stone vs. Opinion check)
4. **Readability gate:** Does it meet target reading level and structure?
5. **SEO gate:** Are on-page elements properly optimized?

## Rank Tracking with Visibility Scoring

Visibility is calculated as a weighted score across tracked keywords, where position 1 receives maximum weight and positions beyond 20 receive near-zero. Aggregated weekly and monthly to detect trends. Used as a leading indicator in the Three-Scenario Forecasting model.

## MCP Protocol for Tool Standardization

The Model Context Protocol (MCP) provides a standardized interface for LLMs to invoke external tools. OpenSEO implements MCP for SEO operations, enabling any MCP-compatible agent to execute keyword research, SERP analysis, and site audits through a uniform tool interface — eliminating the need for custom integrations per agent.