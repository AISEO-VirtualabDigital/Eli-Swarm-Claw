# Digital Marketing Pro: Strategic Methodology Reference

This document extracts the core methodology from the indranilbanerjee/digital-marketing-pro framework. The system defines a rigorous, agent-driven approach to digital marketing strategy that enforces objectivity, traceability, and structured decision-making across all channels and disciplines.

---

## The 12-Part Strategy Flow (61 Steps)

The methodology sequences every engagement through 12 distinct phases, ensuring nothing is missed and every recommendation is grounded in data. The 61 steps within these phases are summarized below.

**Phase 1: Discovery and Scope (Steps 1-5)**
Business context gathering, stakeholder interviews, competitive landscape identification, goal articulation (revenue targets, growth rates, timeline), constraint documentation (budget, brand guidelines, compliance requirements), and formal scope agreement.

**Phase 2: Market and Audience Intelligence (Steps 6-12)**
Total addressable market sizing, buyer persona development with psychographic and behavioral dimensions, customer journey mapping across all touchpoints, audience segmentation by value and behavior, voice-of-customer research (reviews, surveys, support transcripts), competitive intelligence matrix, and market trend analysis.

**Phase 3: Current State Audit (Steps 13-18)**
Technical SEO audit, content inventory and quality assessment, backlink profile analysis, paid media account audit, social media presence review, analytics and tracking verification, conversion rate audit, and brand sentiment baseline.

**Phase 4: Channel Strategy (Steps 19-25)**
Channel evaluation across all 17 channels (see Channel Strategy section below), channel prioritization using the Decision Matrix, budget allocation modeling, channel synergy mapping, owned/earned/paid media distribution plan, and channel-specific KPI definition.

**Phase 5: Keyword and Topic Strategy (Steps 26-30)**
Seed keyword expansion, search intent classification, keyword clustering and topical mapping, content gap identification against competitors, and priority keyword shortlist with difficulty and opportunity scoring.

**Phase 6: Content Strategy (Steps 31-36)**
Content pillar definition, editorial calendar creation, content format selection per channel, content production workflow design, content governance (review, approval, publishing), and AEO content requirements (llms.txt, structured data for AI engines).

**Phase 7: Technical Implementation Plan (Steps 37-41)**
Site architecture recommendations, structured data implementation plan, page speed optimization roadmap, Core Web Vitals improvement plan, crawl budget optimization, and server/infrastructure requirements.

**Phase 8: Paid Media Strategy (Steps 42-47)**
Campaign architecture design, audience targeting strategy, bid strategy selection, creative briefs per channel, tracking and attribution setup, landing page requirements, and budget pacing plan.

**Phase 9: Growth and Experimental Initiatives (Steps 48-51)**
Growth hacking experiment pipeline, partnership and co-marketing opportunities, referral program design, and community building strategy.

**Phase 10: Measurement Framework (Steps 52-55)**
Analytics implementation verification, dashboard design, reporting cadence definition, attribution model selection, and anomaly detection setup.

**Phase 11: Forecasting and Projections (Steps 56-58)**
Three-scenario forecasting (conservative, moderate, aggressive), unit economics modeling, and break-even analysis.

**Phase 12: Governance and Compliance (Steps 59-61)**
Regulatory compliance review (16 jurisdictions), data privacy implementation, accessibility audit (WCAG), and ongoing governance framework.

---

## The Two-Views Model

A defining feature of this methodology: every strategic recommendation must be presented through two distinct analytical lenses.

**View 1: Unbiased Market Analysis**
The first view represents the objective, data-driven assessment. It uses only market data, competitive intelligence, tool outputs, and verifiable metrics. No client-provided assumptions are incorporated. This view answers: "What does the market data actually say?" It serves as a reality check against client optimism or organizational bias.

**View 2: Client-Validated Perspective**
The second view incorporates client-specific knowledge, historical performance data, proprietary insights, and business context that external tools cannot access. This view answers: "Given what we know about this specific business, what adjustments make sense?" The client validates or corrects the assumptions from View 1.

The final strategy merges both views, documenting where they align and where they diverge, with explicit reasoning for resolution.

---

## Stone vs. Opinion Confidence Tagging

Every assertion in strategy documents is tagged with a confidence level to ensure transparency about the evidence base.

**Stone (Factual):** Data-derived, tool-verified, or directly observed. Examples: "Site loads in 4.2 seconds (Lighthouse report)," "Competitor X ranks for 12,300 non-branded keywords (Ahrefs data)." Stone facts require a source citation.

**Opinion (Judgment):** Expert assessment based on experience and pattern recognition. Examples: "Given the competitive density, targeting this keyword cluster will require 6-9 months to see page-1 rankings," "The current landing page design likely contributes to the high bounce rate." Opinions must be flagged and should reference supporting evidence even if the conclusion is interpretive.

This tagging prevents the common agency problem of presenting opinions as facts and forces rigorous sourcing.

---

## Decision Matrix Pattern

The Decision Matrix is the framework used to evaluate and prioritize options at every decision point. It uses a consistent structure:

| Criterion | Weight | Option A Score | Option B Score | Option C Score |
|---|---|---|---|---|
| Expected Impact | 30% | 8 | 6 | 9 |
| Implementation Effort | 20% | 5 | 8 | 4 |
| Time to Result | 20% | 7 | 9 | 5 |
| Cost | 15% | 6 | 8 | 4 |
| Risk Level | 15% | 8 | 7 | 6 |
| **Weighted Total** | **100%** | **6.9** | **7.5** | **5.9** |

The matrix is applied to channel selection, keyword prioritization, campaign type decisions, budget allocation, and vendor/tool selection. Every matrix must define its criteria, weights, and scoring rubric before evaluation.

---

## 24 Specialist Agent Roles

The methodology assigns specific responsibilities to 24 specialist agents, organized into functional groups:

**Research and Intelligence (4):** Market Research Analyst, Competitive Intelligence Analyst, Audience Researcher, Trend Forecaster.

**Strategy and Planning (4):** Digital Strategist, Channel Planner, Content Strategist, Budget Analyst.

**Organic Acquisition (4):** SEO Specialist, Technical SEO Engineer, Content Creator, Link Building Specialist.

**Paid Acquisition (4):** PPC Strategist, Paid Social Specialist, Programmatic Buyer, Retargeting Specialist.

**Experience and Conversion (3):** CRO Specialist, UX Analyst, Landing Page Optimizer.

**Data and Operations (3):** Analytics Engineer, Reporting Specialist, Marketing Operations Manager.

**Emerging Channels (2):** AEO/GEO Specialist, Agentic Search Optimizer.

Each agent has a defined input (what they receive), process (what they do), and output (what they deliver). Agents coordinate through the 12-part flow, with handoff points documented at each phase transition.

---

## Channel Strategy: 17 Channels Across 7 Families

| Family | Channels |
|---|---|
| Search | Google Organic (SEO), Google Ads (PPC), Bing Organic, Bing Ads |
| Social | Meta (Facebook/Instagram), LinkedIn, X (Twitter), TikTok, Pinterest, YouTube |
| Content | Blog/Articles, Email Marketing, Podcast |
| Display | Programmatic Display, Retargeting/Remarketing |
| Local | Google Business Profile, Local Directories |
| Partnership | Affiliate Marketing, Influencer/Creator |
| Emerging | AI/LLM Discovery (AEO/GEO), Agentic Search (WebMCP) |

Each channel is evaluated through the Decision Matrix before inclusion in the strategy. Not all channels are recommended for every client; the framework explicitly requires justification for each selected channel and documented reasons for exclusion of others.

---

## AEO/GEO Audit Methodology (6-Platform)

The framework mandates a quarterly audit of brand presence across six AI/answer engine platforms:

1. **ChatGPT** (with Browse): Test brand queries, service queries, and comparison queries. Document citation sources and accuracy.
2. **Claude**: Same query set. Note source attribution behavior and accuracy differences.
3. **Gemini**: Include entity query tests. Cross-reference with Google Knowledge Panel data.
4. **Perplexity**: Analyze source inclusion, citation ranking, and answer freshness.
5. **Google AI Overviews (SGE)**: Track which queries trigger AI overviews, what sources are cited, and answer format.
6. **Microsoft Copilot**: Test via Bing. Compare with traditional Bing organic rankings.

The audit produces a citation accuracy score per platform, a visibility score (percentage of brand-relevant queries where the client appears), and a sentiment classification (positive/neutral/negative/mixed).

---

## Key Strategic Frameworks

### Five Digital Markets
The methodology segments the digital landscape into five market types, each requiring distinct strategies: (1) Local Service Businesses, (2) E-commerce/DTC, (3) B2B SaaS, (4) Enterprise/Corporate, (5) Media and Publishing. Strategy templates and KPI benchmarks exist for each.

### Channel Families
Channels are grouped into families (see table above) to identify synergies. Budget allocation is done at the family level first, then distributed to individual channels. This prevents over-investment in a single channel at the expense of a complementary family.

### Unit Economics
Every channel recommendation must include unit economics: customer acquisition cost (CAC), lifetime value (LTV), LTV:CAC ratio target (minimum 3:1 for B2B, 1.5:1 for e-commerce), payback period, and margin contribution. This grounds marketing strategy in business outcomes rather than vanity metrics.

### B2B DMU (Decision-Making Unit) Mapping
For B2B clients, the methodology requires mapping the Decision-Making Unit: identifying all stakeholders (initiator, influencer, decider, buyer, user, gatekeeper), their information sources, content needs at each stage, and the typical timeline from awareness to closed-won. Content strategy is then aligned to DMU needs.

### Three-Scenario Forecasting
All projections are presented in three scenarios:
- **Conservative:** Based on lower-bound assumptions (industry 25th percentile performance).
- **Moderate:** Based on median industry benchmarks, adjusted for client-specific factors.
- **Aggressive:** Based on upper-bound assumptions (industry 75th percentile), requiring optimal execution.

Each scenario includes revenue projections, traffic estimates, budget requirements, and key assumptions documented explicitly.

---

## Compliance Framework: 16 Jurisdictions

The methodology includes a compliance checklist covering data privacy, advertising regulations, and accessibility requirements across 16 jurisdictions. The core set includes: United States (CAN-SPAM, CCPA/CPRA, FTC guidelines), European Union (GDPR, ePrivacy Directive, Digital Services Act), United Kingdom (UK GDPR, ASA rules), Canada (CASL, PIPEDA), Australia (Privacy Act, ACMA Spam Act), and additional coverage for Brazil (LGPD), India (DPDPA), Japan (APPI), South Korea (PIPA), Singapore (PDPA), and others.

For each jurisdiction, the framework specifies: data collection consent requirements, cookie/trackers disclosure obligations, email marketing rules, advertising disclosure requirements, data retention limits, and right-to-erasure procedures. The compliance check is integrated into Phase 12 and must be revisited whenever targeting a new market.
