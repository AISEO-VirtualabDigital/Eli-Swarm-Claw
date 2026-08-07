---
id: absorbed-somnusai-seo-20250808
source: https://somnusai.net/generate
title: SomnusAI SEO Technique Analysis
category: seo
skillTags: ["pattern", "strategy"]
containmentHash: sha256-absorbed-somnusai
embeddingSig: trigram:seo:meta:og:structured
dissolved: false
---

# SomnusAI SEO Techniques — Absorbed 2025-08-08

## Meta Tag Architecture
- Full OG + Twitter Card tags on every page
- googlebot directives: max-image-preview:large, max-snippet:-1
- Author/creator meta tags
- Canonical URLs (but incorrectly pointed all pages to homepage — AVOID this)

## Programmatic Feature Page Strategy
- 14 dedicated /features/[tool] pages targeting distinct long-tail keywords
- Each page: H1 with keyword + word count + benefit → How it works → Who it's for → CTA
- Creates a programmatic SEO topic cluster without blog content

## E-E-A-T as Product Differentiator
- "E-E-A-T" appears in meta description, homepage copy (3x), every feature page
- References to future Google core update (May 2026) for urgency positioning

## Content Architecture
- Keyword density: generator (3.59%), seo (2.28%), ai (2.28%), content (1.96%)
- Zero external links — all link equity preserved internally
- Zero blog content — pure SaaS tool with programmatic pages

## Technical SEO Signals
- Next.js App Router + Turbopack (good foundation)
- Geist font preloading as woff2
- All JS loaded async with fetchpriority=low
- data-precedence=next for critical CSS
- HTML lang, viewport, charset all correct

## Critical Mistakes to Avoid
1. NEVER use same title tag across all pages
2. NEVER canonicalize subpages to homepage
3. ALWAYS add og:image when using summary_large_image
4. Add FAQ schema wherever FAQ content exists
5. Add JSON-LD to every page type, not just homepage
6. Don't put login gates on indexable URLs without noindex

## Structured Data
- SoftwareApplication schema on homepage only
- Missing: FAQPage, BreadcrumbList, Organization on subpages
- Price in PHP currency (mismatch for English/global audience)

## Patterns Wired Into Eli
- Full OG + Twitter Card + googlebot directives → layout.tsx metadata
- Author/creator meta tags → layout.tsx
- robots configuration with googleBot sub-config → layout.tsx
- Proper unique per-page title/description (avoiding somnusai's mistake)
