# Keywords Everywhere — Complete Tool Reference for VirtuaLab Digital

**Source URLs absorbed:**
- https://keywordseverywhere.com/seo-reports.html
- https://keywordseverywhere.com/ctl/chatgpt-prompts
- https://keywordseverywhere.com/tools/backlink-gap-analyzer/
- https://keywordseverywhere.com/tools/embed/
- https://keywordseverywhere.com/tools/citation-generator/
- https://keywordseverywhere.com/tools/seo-analyzer/
- https://aibrandtracker.keywordseverywhere.com/methodology

---

## FILTERED: What We CAN Use vs What We CAN'T

### USABLE — Direct SEO/Keyword Value

| Tool | What It Does | How We Use It |
|------|-------------|---------------|
| **SEO Reports** (6 report types) | AI-powered SERP analysis via ChatGPT/Claude/Gemini buttons | Core keyword research pipeline — intent, clustering, rankability checks |
| **AI Brand Tracker** | Estimates ChatGPT recommendation traffic per domain, anchored to Google demand | Track VirtuaLab client visibility in AI answers vs competitors |
| **ChatGPT Prompts Library** (132 prompts) | Pre-built SEO/marketing prompts for content generation | Prompt templates for Eli's content generation agents |
| **Embed Tools** (41 free SEO tools) | Copy-paste iframe embeds for client sites | Lead-warming widgets on GHL landing pages for VirtuaLab clients |
| **Citation Generator** | APA/MLA/Chicago/Harvard/IEEE/Vancouver from URL auto-fill | Content citation for parasite SEO articles — adds E-E-A-T trust signals |
| **API** | REST API for keyword data, search volume, CPC | Programmatic keyword research in n8n workflows |
| **MCP Server** | Model Context Protocol server for KE data | Direct LLM integration — Eli agents query KE data natively |

### NOT USABLE — Skipped

| URL | Why Skipped |
|-----|------------|
| SurferSEO Brand Assets (Notion) | Design files only — no SEO/tool value |
| 6x Website Templates (GitHub) | Generic HTML/Bootstrap templates — not relevant to SEO tooling |
| github.com/search?q=claude | Search result page, not a tool |
| vscode-extension-packs | Dev convenience pack — no SEO application |

---

## 1. SEO Reports — The Core Keyword Research Engine

Keywords Everywhere's SEO Reports are the centerpiece for our workflow. They appear as a widget on every Google SERP and offer 6 report types, each runnable via **ChatGPT, Claude, or Gemini**.

### Report Types

**a) Get User Search Intent**
- Analyzes every ranking page for a query
- Identifies specific intent beyond standard 4 categories (Nav/Info/Comm/Trans)
- Returns the exact keywords your article needs to satisfy that intent
- *Best for:* Understanding what content to create for a target keyword

**b) Analyze Content Types**
- Classifies each ranking page (how-to, tutorial, list post, comparison, etc.)
- Shows which content types are most common in SERPs
- *Best for:* Deciding content format before writing

**c) Cluster All Keywords**
- Groups all keywords from Related + PASF widgets into page-level clusters
- Suggests which page should target which keyword group
- Includes Google search volume per keyword (if volume enabled in settings)
- *Best for:* Content planning and silo architecture

**d) Analyze Titles for SERP**
- Reads all ranking page titles, finds common patterns
- Suggests an optimized title to compete
- *Best for:* On-page title optimization

**e) Check Rankability for SERP**
- Analyzes difficulty data + ranking pages
- Suggests approach, title, meta description, and URL
- Specifies minimum DA, referring domains, and backlinks needed for page 1
- *Best for:* Go/no-go decision on a keyword target

**f) Suggest Anchor Texts**
- Analyzes all keywords for a query
- Suggests internal link anchor text
- *Best for:* Internal linking strategy

### How to Use
1. Install KE extension (Chrome/Firefox/Edge)
2. Search Google normally
3. "Run SEO Reports" widget appears top-right
4. Click ChatGPT, Claude, or Gemini button for preferred LLM
5. Report opens in a new tab with full analysis

### Cost
- Uses KE credits for search volume data (same as normal extension usage)
- The AI report itself runs in YOUR OWN ChatGPT/Claude/Gemini account — no extra cost

---

## 2. AI Brand Tracker — ChatGPT Recommendation Visibility

**URL:** https://aibrandtracker.keywordseverywhere.com/

### What It Measures
- Which websites ChatGPT recommends for commercial "best X" queries
- Estimated monthly traffic + dollar value of that ChatGPT visibility
- Tracks 354,516 websites across 996,948 prompt categories

### Methodology (Key Points)
1. Starts with real Google search volume for "best X" queries (measured by KE)
2. Divides by 8 to estimate ChatGPT demand (based on Ahrefs finding that ChatGPT handles ~12% of Google volume)
3. Asks ChatGPT 5 times per category, records recommendations
4. Splits demand across recommended sites using click-through-rate-by-rank curve
5. Multiplies visits by CPC to estimate monthly dollar value

### Why This Matters for VirtuaLab
- Track whether VirtuaLab client sites appear in ChatGPT recommendations
- Monitor competitor visibility in AI answers
- Quantify the dollar value of AI search visibility
- Since May 2026, ChatGPT shows clickable links — this traffic is REAL and growing

### Caveats
- 8x ratio is a midpoint (range: 5x to 18-26x depending on definition)
- Click-through rates are estimated, not measured
- Absolute numbers are order-of-magnitude; **rankings are the strong signal**
- Post-May-2026 estimates likely understate current traffic (clickable links doubled referrals)

---

## 3. ChatGPT Prompts Library — 132 Pre-Built Prompts

**URL:** https://keywordseverywhere.com/ctl/chatgpt-prompts

### Categories Relevant to VirtuaLab SEO Operations

**SEO Prompts (Direct Use):**
- Keyword Strategy — create keyword strategy from seed keyword
- Get Search Intent for Keywords — batch intent analysis
- Related Keyword Generator — related keywords with intent from seed
- Long-Tail Keyword Generator — long-tail variations with intent
- Meta Title & Description Generator — bulk meta tags for keyword lists
- Create Silo Structure — SILO architecture from single keyword
- Insert Keywords into Content — natural keyword placement

**Content Generation (Eli Agent Prompts):**
- Generate Blog Post Titles / Descriptions / Outline / Complete Post
- Content Brief Generator, Content Rewriter, Article to Listicle
- FAQ Generator, Monthly Content Calendar

**GMB / Local SEO:**
- Optimize Google Business Profile
- Generate GMB Attributes, Posts, Q&A

**Social Media (Content Distribution):**
- Facebook/Instagram/LinkedIn/TikTok/Twitter/Pinterest/YouTube post generators
- Content calendars for all platforms

---

## 4. Embed Tools — 41 Free SEO Widgets for Client Sites

**URL:** https://keywordseverywhere.com/tools/embed/

### Key Tools for VirtuaLab Client Lead-Warming
- **Domain Authority Checker** — prospects check their DA on your site
- **SEO Analyzer** — full on-page SEO audit widget
- **Keyword Volume Checker** — search volume lookup
- **Backlink Checker / Backlink Gap Analyzer** — link analysis
- **Website Traffic Checker** — traffic estimates
- **Website Worth Calculator** — site valuation

### How to Embed
```html
<!-- One script tag covers all embeds on a page -->
<script src="https://keywordseverywhere.com/embed.js"></script>
<iframe data-ke-tool="domain-authority-checker" width="100%" style="border:none;min-height:400px;"></iframe>
```

### Why Embed on Client/GHL Landing Pages
- Keeps visitors on page (tools get used, content gets skimmed)
- Zero build/hosting cost — KE maintains everything
- Attracts backlinks (useful tool pages earn links naturally)
- Warms leads — prospect runs a free check, results open the sales conversation
- Mobile-friendly, auto-sizing, lazy-loaded iframes

---

## 5. Citation Generator — E-E-A-T Trust Signals

**URL:** https://keywordseverywhere.com/tools/citation-generator/

### Supported Styles
APA (7th), MLA (9th), Chicago (Author-Date), Harvard, IEEE, Vancouver

### SEO Value
- Auto-fill from URL reads page metadata (title, author, date, DOI)
- Builds reference list entries + in-text citations
- **Use for:** Parasite SEO articles to add authoritative citations
- Adds E-E-A-T credibility signals to content

---

## 6. API & MCP Server

### API
- REST API for programmatic access to keyword data
- Search volume, CPC, competition metrics
- **Use in:** n8n workflows for automated keyword research

### MCP Server
- Model Context Protocol server for direct LLM integration
- Eli agents can query KE data natively through MCP
- Eliminates the need for API wrapper code in some workflows
