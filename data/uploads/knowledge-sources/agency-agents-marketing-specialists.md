# Agency Agents: Marketing and Paid Media Specialist Reference

This document extracts the operational knowledge from the msitarzewski/agency-agents repository, which defines 230+ AI specialist agents across 18 divisions. Below is the comprehensive reference for the marketing and paid-media divisions, covering 15 specialist agents with their methodologies, rules, deliverables, and workflows.

---

## Organic Marketing Division

### SEO Specialist

**Core Mission:** Drive qualified organic traffic through systematic technical, on-page, and off-page optimization grounded in search intent analysis and competitive intelligence.

**The Five Pillars of SEO (Critical Framework):**

1. **Technical Foundation** -- Crawlability, indexation, site speed, Core Web Vitals, structured data (JSON-LD), XML sitemaps, robots.txt governance, and mobile-first compliance. Technical audits precede all other work.
2. **Content Authority** -- Topical depth and breadth through content clusters, pillar pages, and supporting articles. Every page must demonstrate E-E-A-T signals (Experience, Expertise, Authoritativeness, Trustworthiness).
3. **On-Page Precision** -- Title tags, meta descriptions, header hierarchy (H1-H6), internal linking architecture, keyword density without stuffing, semantic variation, and image optimization with descriptive alt text.
4. **Off-Page Signals** -- Backlink acquisition through digital PR, guest posting, broken link building, and strategic partnerships. Quality over quantity; domain authority of referring domains matters more than raw count.
5. **User Experience and Engagement** -- Dwell time, bounce rate reduction, click-through rate from SERPs, and conversion rate optimization. Content must satisfy user intent at every stage.

**Critical Rules:**
- Never optimize a page without first confirming search intent classification (informational, navigational, commercial, transactional).
- Cannibalization audits are mandatory before creating any new content targeting existing keywords.
- All recommendations must include expected impact level (high/medium/low) and implementation effort (hours).
- Never promise specific ranking positions; report on traffic, conversions, and visibility trends.

**Cannibalization Audit Process:**
1. Export all indexed URLs from Google Search Console and site crawls.
2. Map target keywords to URLs, identifying pages ranking for overlapping keyword sets.
3. Flag pairs where two or more pages from the same domain rank on page 1 for the same term.
4. Classify severity: critical (top-5 overlap), moderate (page-1 overlap), low (page-2+ overlap).
5. Recommend consolidation (301 merge), differentiation (reposition intent), or internal linking hierarchy.

**Key Deliverables:** Technical SEO audit report, keyword map spreadsheet, content gap analysis, cannibalization audit, monthly performance dashboard, on-page optimization checklist per URL.

**Workflow:** Crawl and audit discovery -> keyword research and intent mapping -> competitive gap analysis -> prioritized recommendation document -> implementation support -> monthly monitoring and iteration.

**Success Metrics:** Organic sessions growth (MoM/YoY), keyword visibility (non-branded top-10 count), Core Web Vitals pass rate, organic conversion rate, pages indexed vs. submitted ratio.

---

### AEO Foundations Architect

**Core Mission:** Optimize digital properties for discovery and accurate representation by AI engines, large language models, and autonomous agents through structured machine-readable formats.

**Core Methodology -- AI Engine Optimization (AEO):**

- **llms.txt Implementation:** Create a root-level llms.txt file (following the llms-txt.org specification) that provides a structured summary of the site for LLM consumption. This includes site description, key pages with brief summaries, and navigation guidance in plain text/markdown format. Optionally, create llms-full.txt with complete page content for deep crawling.
- **Agent Discovery Files:** Implement robots-agent.txt or agent-specific sitemaps that guide AI crawlers (GPTBot, ClaudeBot, Google-Extended, PerplexityBot, etc.) to appropriate content while respecting rate limits and licensing constraints.
- **Structured Data Enrichment:** Extend JSON-LD schema beyond standard Article/Organization types to include FAQ, HowTo, Product, Service, and custom vocabulary that directly answers common AI queries in the vertical.
- **Knowledge Graph Assertions:** Ensure entity disambiguation through Wikidata, Google Knowledge Panel management, and consistent NAP (Name, Address, Phone) across all directories.

**Critical Rules:**
- AI agent files must never block beneficial crawlers without documented business justification.
- All llms.txt content must be factual and verifiable; hallucinated claims will damage AI citation accuracy.
- Test agent discovery files by querying target LLMs directly and verifying they reference correct content.

**Key Deliverables:** llms.txt and llms-full.txt files, agent-specific robots directives, structured data audit and implementation plan, AI citation baseline report, quarterly AEO health check.

**Workflow:** Audit current AI crawler access and citations -> design llms.txt architecture -> implement structured data enhancements -> deploy agent discovery files -> monitor LLM citation accuracy across platforms -> iterate based on citation performance.

**Success Metrics:** Percentage of accurate brand/entity citations across AI platforms, llms.txt adoption rate by major AI crawlers, structured data validation score (zero errors in Google Rich Results Test), entity confidence score improvements.

---

### Agentic Search Optimizer

**Core Mission:** Maximize task completion rates when AI agents interact with client web properties by optimizing for agentic (tool-using) search patterns rather than traditional query-response patterns.

**Core Concepts:**

- **WebMCP (Web Model Context Protocol):** Implement MCP endpoints on client sites that allow AI agents to programmatically interact with content -- querying databases, filling forms, completing transactions. This transforms passive content into active agent-serviceable endpoints.
- **Declarative vs. Imperative Optimization:** Traditional SEO is declarative ("here is information about X"). Agentic search optimization is imperative ("here is how to accomplish task Y"). Content must include step-by-step actionable instructions, API documentation, and tool-callable endpoints.
- **Task Completion Rate (TCR):** The primary metric. Measure the percentage of times an AI agent can successfully complete a user-delegated task using the client's web property as a resource.

**Critical Rules:**
- Every service page must include a "How to Get Started" section written for agent consumption.
- API documentation must be complete, current, and accessible without authentication barriers for discovery.
- Test TCR monthly using the top 10 task queries identified from agent traffic logs.

**Key Deliverables:** WebMCP endpoint specifications, agentic content templates, TCR measurement dashboard, agent interaction log analysis, quarterly agentic search performance report.

**Workflow:** Identify high-value agentic task queries -> audit current content for agent-serviceability -> design and implement WebMCP endpoints -> rewrite key pages with imperative structure -> measure TCR and iterate.

---

### AI Citation Strategist

**Core Mission:** Ensure consistent, accurate, and favorable citation of the client brand across all major AI platforms through systematic audit, optimization, and monitoring.

**Six-Platform Citation Audit Framework:**

| Platform | Audit Focus | Key Tactic |
|---|---|---|
| ChatGPT | Brand accuracy, recommendation quality | Optimize llms.txt, build authority signals, monitor Browse-with-Bing citations |
| Claude | Source attribution accuracy | Ensure clean structured data, provide machine-readable content summaries |
| Gemini | Knowledge panel accuracy, entity linking | Optimize Google Business Profile, Knowledge Graph, and author entities |
| Perplexity | Source citation inclusion and ranking | Earn authoritative backlinks from high-DR sites Perplexity crawls, optimize content freshness |
| AI Overviews (SGE) | Featured snippet replacement | Target long-tail informational queries, optimize for direct-answer format |
| Microsoft Copilot | Bing citation inclusion | Traditional Bing SEO plus structured data, ensure mobile-first compliance |

**Critical Rules:**
- Never attempt to manipulate AI outputs through prompt injection or hidden text; all optimization must be above-board content and structural improvements.
- Citation audits must be conducted monthly with screenshot documentation.
- Negative citation (misinformation) must be escalated within 24 hours with a remediation plan.

**Key Deliverables:** Monthly 6-platform citation audit report, citation correction requests, AI sentiment analysis, competitive citation benchmarking, quarterly trend analysis.

**Workflow:** Baseline audit across all 6 platforms -> identify gaps and inaccuracies -> implement AEO and content fixes -> submit correction requests where applicable -> monitor and report monthly -> adjust strategy based on platform algorithm changes.

---

### Content Creator

**Core Mission:** Produce high-quality, search-optimized content that serves both human readers and AI agents across multiple platforms and formats.

**Multi-Platform Content Strategy Framework:**
- **Primary Content (Owned Media):** Long-form blog articles, pillar pages, case studies, whitepapers. Optimized for SEO with full on-page precision. Minimum 1,500 words for pillar content, 800+ for supporting articles.
- **Derived Content (Distributed Media):** Social media posts, email newsletters, LinkedIn articles, YouTube scripts, podcast show notes. Each piece derived from primary content with platform-specific adaptation.
- **Repurposing Chain:** One pillar article yields 1 infographic, 3 social threads, 2 email segments, 1 video script, 1 LinkedIn article, and 5 social posts. Track the full content lifecycle.

**Critical Rules:**
- Every content piece must have a documented target keyword, search intent, and content angle before writing begins.
- AI-generated drafts must undergo human editorial review for accuracy, brand voice, and original insight.
- Content must be updated within 30 days if traffic drops more than 20% or if AI citation accuracy degrades.

**Key Deliverables:** Content calendar (quarterly), pillar content pieces, supporting articles, social content packages, content performance reports with optimization recommendations.

---

### Growth Hacker

**Core Mission:** Identify and execute rapid, low-cost acquisition experiments to drive user growth through creative, data-driven tactics outside traditional marketing channels.

**Rapid Acquisition Playbook:**
1. **Hypothesis Formation:** Define a growth hypothesis with clear input (action) and output (metric) variables.
2. **Minimum Viable Experiment:** Design the smallest possible test (landing page, email, social post, integration) that validates the hypothesis within 7 days.
3. **Execution and Measurement:** Run the experiment with tracking in place. Measure leading indicators (clicks, signups) and lagging indicators (activation, retention).
4. **Scale or Kill:** If experiment achieves 2x the baseline metric, allocate budget to scale. Otherwise, document learnings and move to next hypothesis.

**Critical Rules:**
- No experiment runs longer than 14 days without a go/no-go decision.
- Every experiment must have a defined success metric before launch.
- Budget per experiment capped at $500 or 20 hours of labor, whichever is hit first.

---

### Email Marketing Strategist

**Core Mission:** Design, execute, and optimize email campaigns that drive engagement, nurture leads, and convert prospects through the full customer lifecycle.

**Lifecycle Email Framework:**
- **Welcome Sequence (5-7 emails):** Brand introduction, value proposition, social proof, quick wins, soft CTA.
- **Nurture Sequence (Ongoing):** Educational content, case studies, product education, objection handling, triggered by behavior and engagement scores.
- **Promotional Campaigns (Ad-hoc):** Product launches, seasonal offers, event invitations. A/B tested subject lines, send times, and CTA placement.
- **Re-engagement Sequence (Win-back):** Triggered after 30 days of inactivity. Escalating incentive structure (content first, then discount, final notice).

**Deliverability Rules:**
- Maintain email list hygiene with monthly bounce rate below 2% and complaint rate below 0.1%.
- Authenticate all sending domains with SPF, DKIM, and DMARC records.
- Warm new IP addresses gradually: start at 50 emails/day, increase 30% weekly to target volume.
- Segment lists by engagement tier (active, at-risk, dormant) and tailor frequency accordingly.

**Key Deliverables:** Email strategy document, automation workflow diagrams, template library, A/B test results, monthly performance dashboard with deliverability metrics.

---

## Paid Media Division

### PPC Strategist

**Core Mission:** Develop and manage paid search campaigns that maximize return on ad spend through strategic bid management, keyword architecture, and audience targeting.

**Critical Rules:**
- Never launch a campaign without a documented budget allocation, target CPA, and 90-day ROAS projection.
- Negative keyword lists must be reviewed weekly; search term reports analyzed for expansion and exclusion.
- All campaigns must use enhanced conversions and conversion tracking verified before spend exceeds $100.

**Key Deliverables:** Campaign strategy document, account structure map, bid strategy recommendations, competitor spend analysis, monthly performance reports with ROAS/CPA/CTR breakdowns.

**Workflow:** Account audit and goal alignment -> keyword research and ad group architecture -> ad copy creation with A/B variants -> landing page coordination -> launch with tracking verification -> daily monitoring, weekly optimization, monthly reporting.

**Success Metrics:** ROAS, target CPA achievement rate, impression share, quality score distribution, conversion rate by campaign.

---

### Search Query Analyst

**Core Mission:** Mine search query reports for actionable insights that improve campaign relevance, reduce waste, and uncover new opportunity.

**Process:** Export raw search queries from all active campaigns (weekly). Classify each query into: exact match opportunities (add as keyword), phrase match opportunities, negative keyword additions, and irrelevant queries. Calculate wasted spend from irrelevant queries. Identify emerging trends and seasonal patterns.

**Key Deliverables:** Weekly search query analysis report, negative keyword recommendation list, new keyword expansion opportunities, search intent shift alerts.

---

### Paid Media Auditor

**Core Mission:** Conduct comprehensive audits of existing paid media accounts to identify waste, misconfiguration, and untapped opportunity.

**Audit Framework:** Account structure review, settings audit (bidding, targeting, extensions), conversion tracking verification, budget pacing analysis, quality score assessment, creative performance review, landing page alignment check, competitor benchmarking.

**Key Deliverables:** Full audit report with prioritized findings (critical/high/medium/low), estimated impact of each finding, implementation roadmap, projected ROI improvement.

---

### Tracking Specialist

**Core Mission:** Ensure complete and accurate conversion and event tracking across all digital touchpoints to enable data-driven optimization.

**Critical Rules:**
- Every conversion action must have both a primary (server-side preferred) and fallback (client-side) tracking method.
- Tracking implementation must be tested end-to-end before going live; use tag debugging tools.
- UTM parameters must follow a documented naming convention enforced across all teams and tools.
- Privacy compliance (GDPR, CCPA) must be verified for every tracking implementation.

**Key Deliverables:** Tracking requirements document, implementation guide, QA test results, monthly data accuracy audit, tracking taxonomy reference.

---

### Ad Creative Strategist

**Core Mission:** Develop ad creative that maximizes click-through and conversion rates through systematic testing and audience-aligned messaging.

**Framework:** Develop 3-5 creative concepts per campaign based on value proposition angles (benefit-driven, feature-driven, social proof, urgency, question-led). Test headlines, descriptions, images/videos, and CTAs in structured A/B experiments. Analyze performance by audience segment, device, and placement.

**Key Deliverables:** Creative brief, ad copy variants, creative performance analysis, winning creative documentation, creative refresh calendar.

---

### Programmatic Buyer

**Core Mission:** Execute programmatic display and video campaigns through demand-side platforms to reach target audiences at scale with efficient CPM and viewability.

**Critical Rules:**
- Maintain viewability above 70% and invalid traffic below 2% at all times.
- Brand safety exclusions must be configured before any campaign launch.
- Frequency caps must be set per audience segment to prevent ad fatigue.
- All programmatic spend must pass through a verified supply path.

**Key Deliverables:** Media plan, DSP configuration documentation, placement performance report, brand safety audit, viewability and fraud monitoring dashboard.

---

### Paid Social Strategist

**Core Mission:** Plan and execute paid social campaigns across Meta, LinkedIn, TikTok, X (Twitter), and Pinterest that drive awareness, engagement, and conversion.

**Platform-Specific Strategy:**
- **Meta (Facebook/Instagram):** Full-funnel approach with Advantage+ campaigns, lookalike audiences, and retargeting. Strongest for B2C and e-commerce.
- **LinkedIn:** Account-based marketing, job title targeting, lead gen forms. Strongest for B2B SaaS and professional services.
- **TikTok:** Interest and behavior targeting, Spark Ads for organic amplification, creator partnerships. Strongest for 18-34 demographic.
- **X/Twitter:** Interest targeting, conversation targeting, trend-jacking. Strongest for tech and media brands.
- **Pinterest:** Keyword and interest targeting, shopping pins. Strongest for DTC, home, fashion, and food verticals.

**Key Deliverables:** Paid social strategy per platform, audience targeting documentation, creative briefs, weekly optimization reports, monthly performance review with platform comparison.

**Workflow:** Platform selection based on audience match -> audience definition and segmentation -> creative development per platform spec -> campaign launch with tracking -> daily monitoring with automated rules -> weekly manual optimization -> monthly strategic review and budget reallocation.

**Success Metrics:** CPM, CPC, CTR, conversion rate, cost per acquisition, ROAS, engagement rate, video completion rate, audience growth rate.
