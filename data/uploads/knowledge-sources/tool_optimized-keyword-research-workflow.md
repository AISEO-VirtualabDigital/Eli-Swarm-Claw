# Optimized Keyword Research Workflow
# KE + Gemini + Claude + Perplexity — Combined for Maximum Accuracy

## VirtuaLab Digital — Eli AI Scientist Keyword Intelligence Pipeline

---

## The Problem with Single-Source Keyword Research

No single tool gives you the full picture:
- **Keywords Everywhere** gives you search volume, CPC, and SERP data — but it doesn't reason about strategy
- **Gemini** has real-time Google Search grounding and can access current SERPs — but needs structured prompting
- **Claude** excels at deep analysis, clustering logic, and content strategy — but can't browse the live web natively
- **Perplexity** provides cited, real-time web research with source transparency — but lacks SEO-specific metrics

The optimized approach uses each LLM for what it's **best at**, with Keywords Everywhere as the **data backbone**.

---

## The 4-Tier Keyword Research Pipeline

### Tier 1: Data Collection — Keywords Everywhere (Ground Truth)

**What KE provides that nothing else can:**
- Real Google Keyword Planner search volumes (not estimates)
- CPC data (commercial intent signal)
- SEO difficulty / competition scores
- Related keywords + People Also Search For (PASF) from live SERPs
- Trend data, click-through-rate estimates

**Workflow:**
1. Install KE browser extension
2. Search seed keyword on Google
3. Collect: Related keywords, PASF, "Also search for"
4. Enable search volume display in extension settings
5. Export data (KE API or manual CSV export)

**Output:** Raw keyword list with volume, CPC, difficulty, trend data

---

### Tier 2: Real-Time SERP Validation — Gemini (Google-Grounded)

**Why Gemini:**
- Has native Google Search grounding (built by Google)
- Can access current SERP data, trending topics, and real-time results
- Understands Google's own ranking signals better than any other LLM
- Can validate whether KE data matches current SERP reality

**Prompt Template:**
```
You are an SEO analyst. I have keyword research data from Keywords Everywhere.

Seed keyword: [KEYWORD]
Niche: [NICHE] — US suburban local services
Target location: [CITY, STATE]

Keywords from KE (volume / CPC / difficulty):
[RAW KEYWORD DATA]

For each keyword:
1. Search Google and verify the current SERP composition
2. Check if AI Overviews appear for this query
3. Identify what content type ranks (blog, service page, directory, video)
4. Note any featured snippets or knowledge panels
5. Flag any keywords where the current SERP doesn't match KE's difficulty rating

Return a table with columns: Keyword | Verified Intent | SERP Type | AI Overview? | Content Gap | Priority (1-5)
```

**Output:** Validated keyword list with real-time SERP intelligence

---

### Tier 3: Deep Analysis & Clustering — Claude (Strategic Reasoning)

**Why Claude:**
- Superior at nuanced classification and clustering logic
- Handles complex multi-factor analysis better than Gemini or GPT
- Generates more structured, actionable strategy documents
- Better at understanding semantic relationships between keywords

**Prompt Template:**
```
You are a senior SEO strategist. I have keyword research data validated by Gemini.

Client: [CLIENT NAME]
Niche: [NICHE]
Location: [CITY, STATE]
Current domain authority: [DA]
Budget: [CONTENT BUDGET] pages/month

Validated keyword data:
[GEMINI OUTPUT TABLE]

Tasks:
1. Cluster keywords into topical silos (max 7-10 keywords per cluster)
2. For each cluster, define:
   - Primary keyword (highest volume + achievable difficulty)
   - Supporting keywords
   - Recommended content type and word count
   - Internal linking strategy
   - Estimated timeline to rank (based on DA vs required DA from KE rankability data)
3. Identify quick wins (low difficulty + high volume + commercial intent)
4. Identify content gaps (keywords with demand but no quality content ranking)
5. Create a 90-day content calendar prioritizing by expected ROI

Format: Structured markdown with tables
```

**Output:** Clustered keyword strategy with 90-day content plan

---

### Tier 4: Competitive Intelligence & Citation Research — Perplexity (Sourced Research)

**Why Perplexity:**
- Provides cited sources for every claim — you can verify
- Excels at competitive analysis and market research
- Can find competitor strategies, backlink sources, and content gaps
- Real-time web access with transparency on source quality

**Prompt Template:**
```
I'm doing competitive keyword research for a [NICHE] business in [LOCATION].

Top competitors:
[COMPETITOR 1 URL]
[COMPETITOR 2 URL]
[COMPETITOR 3 URL]

For each competitor:
1. What keywords are they ranking for in the top 3?
2. What backlink sources do they have that we could replicate?
3. What content topics do they cover that we don't?
4. What is their estimated organic traffic and top traffic pages?
5. Are they appearing in AI Overviews or ChatGPT recommendations?

Also research:
- Recent Google algorithm updates affecting this niche
- Emerging search trends in [NICHE] for 2026
- Best citation sources for E-E-A-T in this industry

Cite all sources.
```

**Output:** Competitive intelligence report with verified citations

---

## Combined Workflow Diagram

```
SEED KEYWORD
     │
     ▼
┌─────────────────────────┐
│  Tier 1: Keywords       │
│  Everywhere             │
│  ─────────────────────  │
│  • Search volume        │
│  • CPC & difficulty     │
│  • Related + PASF       │
│  • SEO Reports (6 types)│
└───────────┬─────────────┘
            │
            │ Raw keyword data
            ▼
┌─────────────────────────┐
│  Tier 2: Gemini         │
│  (Google-Grounded)      │
│  ─────────────────────  │
│  • SERP validation      │
│  • AI Overview check    │
│  • Content type verify  │
│  • Intent confirmation  │
└───────────┬─────────────┘
            │
            │ Validated data
            ▼
┌─────────────────────────┐
│  Tier 3: Claude         │
│  (Strategic Analysis)   │
│  ─────────────────────  │
│  • Keyword clustering   │
│  • Silo architecture    │
│  • 90-day content plan  │
│  • Priority scoring     │
└───────────┬─────────────┘
            │
            │ Strategy + gaps
            ▼
┌─────────────────────────┐
│  Tier 4: Perplexity     │
│  (Competitive Intel)    │
│  ─────────────────────  │
│  • Competitor keywords  │
│  • Backlink sources     │
│  • Trend research       │
│  • E-E-A-T citations    │
└───────────┬─────────────┘
            │
            │ Competitive data
            ▼
   FINAL KEYWORD STRATEGY
   ─────────────────────
   • Clustered keyword map
   • Content calendar
   • Competitive benchmark
   • Priority queue
```

---

## KE SEO Reports — When to Use Which LLM Button

KE offers ChatGPT, Claude, and Gemini buttons for each report. Here's when to use each:

| Report | Best LLM | Why |
|--------|----------|-----|
| Get User Search Intent | **Claude** | Better at nuanced intent classification beyond standard 4 categories |
| Analyze Content Types | **Gemini** | Google-grounded understanding of what content types Google favors |
| Cluster All Keywords | **Claude** | Superior semantic clustering logic |
| Analyze Titles for SERP | **ChatGPT** | Good at pattern recognition across titles |
| Check Rankability | **Gemini** | Access to current Google ranking factors |
| Suggest Anchor Texts | **Claude** | Better at natural language variation for anchors |

---

## Automation: n8n Workflow Integration

### Keywords Everywhere API in n8n

```
n8n Workflow: Automated Keyword Intelligence

Trigger: Webhook (new client/keyword from GHL)
  │
  ├─→ HTTP Request: KE API → Get keyword data (volume, CPC, difficulty)
  │
  ├─→ HTTP Request: Gemini API → Validate SERP, check AI Overviews
  │
  ├─→ HTTP Request: Claude API → Cluster keywords, generate strategy
  │
  ├─→ HTTP Request: Perplexity API → Competitive research
  │
  ├─→ Merge all results
  │
  └─→ Output: Structured keyword strategy → Baserow table + GHL note
```

### KE MCP Server — Direct LLM Integration

Keywords Everywhere offers an MCP (Model Context Protocol) server. This means:
- Eli agents can query KE data **natively** without API wrapper code
- Claude Desktop / Claude Code can use KE tools directly
- Reduces latency vs HTTP API calls
- More natural LLM-tool interaction

---

## Accuracy Optimization Rules

### 1. Triple-Validate Volume Data
- KE provides Google Keyword Planner data (most accurate)
- Cross-check with Gemini's Google grounding for trending terms
- If KE shows "?" for volume, the keyword has <10 searches/month — deprioritize

### 2. Intent Verification
- KE's SEO Reports give LLM-analyzed intent — use Claude's button
- Cross-check with Gemini's real-time SERP analysis
- Perplexity can find user intent studies and surveys for the niche

### 3. Difficulty Reality Check
- KE's rankability report specifies min DA, referring domains, backlinks
- Compare against client's actual metrics before targeting
- Gemini can verify if low-difficulty keywords are truly achievable

### 4. AI Overview Tracking
- Gemini can check if AI Overviews appear for target keywords
- KE's AI Overview Metrics track AI Overview presence
- Keywords with AI Overviews need different strategy (concise, authoritative answers)

### 5. ChatGPT/Claude Recommendation Tracking
- Use KE's AI Brand Tracker to monitor if client appears in AI answers
- If not appearing, optimize for cited sources (Perplexity research)
- Post-May-2026: ChatGPT shows clickable links — this is real traffic

---

## Quick-Reference: Which Tool for Which Question

| Question | Tool | Action |
|----------|------|--------|
| What's the search volume? | KE | Extension or API |
| Is this keyword worth targeting? | KE + Claude | KE rankability report via Claude |
| What's currently ranking? | Gemini | Google-grounded SERP analysis |
| Is there an AI Overview? | Gemini | Search and check |
| How should I cluster these keywords? | Claude | KE cluster report via Claude |
| What are my competitors targeting? | Perplexity | Competitive research with citations |
| What content type should I create? | KE + Gemini | KE content type report via Gemini |
| What anchor text should I use? | Claude | KE anchor text report via Claude |
| Are we visible in ChatGPT? | KE AI Brand Tracker | Check aibrandtracker.keywordseverywhere.com |
| What's the search intent? | KE + Claude | KE intent report via Claude |
| What citations should I include? | Perplexity + KE Citation | Perplexity for sources, KE for formatting |
| How do I embed a free tool on a client site? | KE Embed | Copy iframe snippet from keywordseverywhere.com/tools/embed/ |
