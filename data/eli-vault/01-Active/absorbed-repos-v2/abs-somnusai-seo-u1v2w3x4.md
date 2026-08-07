---
absorbedFrom: https://somnusai.net
absorbedAt: 2026-08-08
chunkType: seo-technique-audit
tags: [somnusai, seo, meta-tags, schema-markup, nextjs-ssr, tailwind, og-tags, semrush, e-e-a-t, sitemap, structured-data]
---

# SomnusAI — SEO Technique Audit & Patterns to Absorb

## Site Overview
AI-powered SEO content generator SaaS. Next.js 15 + Turbopack + Tailwind CSS + Geist fonts. Server-side rendered. 14 tools across content generation, SEO analysis, and utilities.

## Pattern 1: Comprehensive Meta Tag Stack
Complete inventory of meta tags covering every platform:
- `<title>` with brand + descriptor
- `<meta name="description">` keyword-rich (E-E-A-T, May 2026 Core Update)
- `<meta name="keywords">` comma-separated
- `<meta name="robots">` index, follow
- `<meta name="googlebot">` with max-image-preview and max-snippet
- `<link rel="canonical">` absolute URL
- Full OG set: og:title, og:description, og:url, og:type, og:site_name, og:locale
- Full Twitter set: twitter:card (summary_large_image), twitter:title, twitter:description
- `<meta name="author">` + `<link rel="author">`

**Absorb into Eli**: Add this full meta stack to Eli's layout.tsx. Currently Eli likely has minimal meta tags.

## Pattern 2: Schema Markup (SoftwareApplication)
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "SomnusAI",
  "url": "https://somnusai.net",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": { "@type": "Offer", "price": "700", "priceCurrency": "PHP" },
  "provider": { "@type": "Organization", "name": "SomnusAI" }
}
```

**Absorb into Eli**: Add Organization + WebSite + SoftwareApplication schema to Eli's layout. Eli is a SaaS AI agent — SoftwareApplication is the right type.

## Pattern 3: Clean Heading Hierarchy
Single H1 → multiple H2 → multiple H3. No skipped levels. No H4-H6. Each section has a clear heading.

**Absorb into Eli**: Audit Eli's dashboard pages for heading hierarchy.

## Pattern 4: Strong Internal Linking to Feature Pages
14 dedicated feature pages (`/features/blog-generator`, etc.) all linked from homepage. Each feature page is a potential ranking page.

**Absorb into Eli**: Eli's dashboard views (Chat, Knowledge, Keywords, Skills) should be linkable public pages for SEO. Create lightweight public-facing pages for each major feature.

## Pattern 5: Alternating Section Backgrounds (Dark/Light)
Dark hero → light stats → white features → slate how-it-works → white pricing → dark CTA. Creates visual rhythm.

**Absorb into Eli**: Apply to Eli's landing/intro page.

## Pattern 6: Social Proof Stats Bar
4 KPIs in a horizontal bar: "14+ tools | 2000+ words | <30s generation | 2026-ready". Immediate credibility signal.

**Absorb into Eli**: Add a stats bar below Eli's hero: "24K+ knowledge chunks | 18 categories | 8 skill types | 6 AI agents".

## Pattern 7: 3-Step How-It-Works
Reduces complexity: Step 1 (Input) → Step 2 (AI Processing) → Step 3 (Published). Simple mental model.

**Absorb into Eli**: "Ask Eli a question" → "Eli searches 24K chunks" → "Get expert SEO advice".

## Pattern 8: Pricing Table with "Most Popular" Badge
3 tiers (Free/Pro/Agency). Pro highlighted as "Most Popular". "No credit card required" reassurance.

## Pattern 9: 5 Conversion CTAs Across Page
"Get Started Free" / "Sign up" repeated strategically. Final dark CTA banner.

## Pattern 10: Font Preloading with fetchpriority
```html
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
<link href="...Geist..." rel="stylesheet" fetchpriority="high">
```

## Critical Issues to AVOID (learned from their mistakes)
1. **Missing og:image** — social shares show NO preview. ALWAYS include og:image.
2. **Zero analytics** — no GA4/GTM. Always install tracking.
3. **Schema price mismatch** — says 75 credits but pricing shows 100. Keep schema in sync.
4. **PHP currency for global SaaS** — use USD or multi-currency.
5. **Zero outbound links** — no authority signaling. Add relevant outbound links.
6. **No rel attributes** — add rel="noopener" to external links.
7. **Gated page with homepage metadata** — `/generate` serves login but has homepage meta. Use noindex for gated pages.
8. **No sitemap.xml reference** — add sitemap link in head.
9. **No blog** — zero organic content engine. Create a blog for content marketing.
10. **No FAQ section** — ironic for an SEO tool. Add FAQ with FAQPage schema.