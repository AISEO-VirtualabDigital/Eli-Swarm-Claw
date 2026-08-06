# Keyword Research APIs

The data layer that powers keyword intelligence across Eli's recommendations and the specialist agents in [[Agency-Agents-Marketing-Suite]].

## DataForSEO API

- **Type:** Industry-standard pay-per-request SEO data provider
- **Data coverage:** Keyword volume, CPC, competition score, SERP features, related keywords, search trends
- **Pricing model:** Pay per request — no monthly minimums or subscriptions. Costs scale directly with usage.
- **Strengths:** Most comprehensive keyword dataset available via API. Reliable, well-documented, used by major SEO platforms as their backend.
- **Weaknesses:** Costs can accumulate at scale without usage caps. Rate limits apply.
- **Integration points:** Powers OpenSEO MCP server, SEOToolSuite UI, and the keyword data pipeline described in [[SEO-Architecture-Patterns]]
- **Typical use case:** Bulk keyword research, SERP analysis, competitive keyword gap identification

## Microsoft Bing Web Search API

- **Type:** Web search API with autosuggest capability
- **Free tier:** 1,000 transactions per month at no cost
- **Data coverage:** Search suggestions, web results, related searches
- **Strengths:** Free tier is genuinely useful for light research. Autosuggest endpoint provides real query data directly from Bing's suggestion engine.
- **Weaknesses:** Smaller dataset than DataForSEO. No direct keyword volume or CPC data — suggestions only.
- **Typical use case:** Supplementing DataForSEO with free autosuggest data, validating search intent, discovering long-tail queries that don't appear in keyword tools
- **Strategic value:** The free tier makes it a no-brainer addition to any keyword research stack. Use it to seed initial research before committing DataForSEO credits.

## SEOToolSuite

- **Type:** Open-source Next.js application
- **Function:** Provides a visual UI wrapper around the DataForSEO API
- **Features:** Keyword research interface, search volume display, CPC data, competition metrics
- **Repository:** Open-source, self-hostable
- **Relevance:** Reference implementation showing how to build a keyword research UI. The architecture (Next.js frontend calling DataForSEO backend) mirrors the pattern in Eli's own [[MicroSaaS-Architecture]].
- **Limitation:** UI-only — does not add analytical intelligence beyond what DataForSEO provides

## SEO Tools API

- **Type:** NestJS-based SEO API platform
- **Capabilities:** Backlink analysis, rank tracking, site audit, sitemap generation and analysis
- **Stack:** NestJS (Node.js framework), modular architecture
- **Relevance:** Complements keyword research APIs with broader SEO data — backlinks and rank data that DataForSEO also provides but through a different interface and packaging
- **Use when:** A self-hosted, full-spectrum SEO API is preferred over pay-per-request

## Recommended Stack for Eli

```
Primary:   DataForSEO API (keyword volume, CPC, competition)
Secondary: Bing Web Search API (autosuggest, 1K free/month)
UI Layer:  SEOToolSuite pattern (Next.js + DataForSEO)
Pipeline:  See [[SEO-Architecture-Patterns]] for the full data flow
```