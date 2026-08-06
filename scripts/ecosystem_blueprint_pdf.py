#!/usr/bin/env python3
"""
VirtuaLab Digital - Complete Ecosystem System Architecture Blueprint
Systematic Approach: Baserow + n8n + GHL + AI Agent Orchestration
"""

FONT_DIR = '/usr/share/fonts'

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ========================
# FONT REGISTRATION
# ========================
pdfmetrics.registerFont(TTFont('LibSans', f'{FONT_DIR}/truetype/liberation/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LibSans-Bold', f'{FONT_DIR}/truetype/liberation/LiberationSans-Bold.ttf'))
registerFontFamily('LibSans', normal='LibSans', bold='LibSans-Bold')

# ========================
# PALETTE
# ========================
TABLE_STRIPE  = HexColor('#ecedee')
HEADER_FILL   = HexColor('#1a2e3b')
ACCENT        = HexColor('#2e7fa7')
TEXT_PRIMARY   = HexColor('#222526')
TEXT_MUTED     = HexColor('#71787b')
BORDER_COLOR  = HexColor('#bacbd3')
WHITE         = HexColor('#ffffff')
DARK_HEADER   = HexColor('#0f1c26')
MID_HEADER    = HexColor('#2a4758')
LIGHT_BG      = HexColor('#eef3f6')
TAG_BG        = HexColor('#d4e8f2')

PAGE_W, PAGE_H = A4
LEFT_M = 20*mm
RIGHT_M = 20*mm
TOP_M = 22*mm
BOT_M = 22*mm
CONTENT_W = PAGE_W - LEFT_M - RIGHT_M

styles = getSampleStyleSheet()

s_h1 = ParagraphStyle('H1', fontName='LibSans-Bold', fontSize=20, leading=26, textColor=DARK_HEADER, spaceAfter=10, spaceBefore=16)
s_h2 = ParagraphStyle('H2', fontName='LibSans-Bold', fontSize=15, leading=20, textColor=ACCENT, spaceAfter=8, spaceBefore=14)
s_h3 = ParagraphStyle('H3', fontName='LibSans-Bold', fontSize=12, leading=16, textColor=MID_HEADER, spaceAfter=6, spaceBefore=10)
s_body = ParagraphStyle('Body', fontName='LibSans', fontSize=9.5, leading=14, textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=5)
s_table_header = ParagraphStyle('TH', fontName='LibSans-Bold', fontSize=8, leading=10, textColor=WHITE, alignment=TA_CENTER)
s_table_cell = ParagraphStyle('TC', fontName='LibSans', fontSize=7.5, leading=10, textColor=TEXT_PRIMARY, alignment=TA_LEFT)
s_tag = ParagraphStyle('Tag', fontName='LibSans-Bold', fontSize=7, leading=9, textColor=ACCENT, backColor=TAG_BG, spaceBefore=2, spaceAfter=2, borderPadding=3)
s_callout = ParagraphStyle('Callout', fontName='LibSans', fontSize=9, leading=13, textColor=HEADER_FILL, backColor=LIGHT_BG, spaceBefore=6, spaceAfter=6, leftIndent=8, rightIndent=8, borderPadding=8)

# ========================
# HELPERS
# ========================
def make_table(headers, rows, col_widths=None, header_bg=None):
    if header_bg is None:
        header_bg = HEADER_FILL
    hdr = [Paragraph(h, s_table_header) for h in headers]
    data = [hdr]
    for row in rows:
        data.append([Paragraph(str(c), s_table_cell) if not isinstance(c, Paragraph) else c for c in row])
    if col_widths is None:
        col_widths = [CONTENT_W / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'LibSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('GRID', (0, 0), (-1, -1), 0.4, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_STRIPE))
    t.setStyle(TableStyle(cmds))
    return t

def hr(): return HRFlowable(width='100%', thickness=0.8, color=BORDER_COLOR, spaceAfter=6, spaceBefore=6)
def sp(pts=6): return Spacer(1, pts)

def callout(text):
    return Paragraph(text, s_callout)

def tag(text):
    return Paragraph(text, s_tag)

# ========================
# BUILD DOCUMENT
# ========================
output_path = '/home/z/my-project/download/VirtuaLab_Digital_Ecosystem_System_Architecture.pdf'

doc = SimpleDocTemplate(
    output_path, pagesize=A4,
    leftMargin=LEFT_M, rightMargin=RIGHT_M,
    topMargin=TOP_M, bottomMargin=BOT_M,
    title='VirtuaLab Digital - Complete Ecosystem System Architecture',
    author='VirtuaLab Digital',
    subject='Systematic Ecosystem Blueprint: Baserow + n8n + GHL + AI Agent Orchestration',
)

story = []

# ========================
# COVER PAGE
# ========================
story.append(Paragraph('VirtuaLab Digital', ParagraphStyle('CT', fontName='LibSans-Bold', fontSize=30, leading=36, textColor=DARK_HEADER, alignment=TA_CENTER, spaceAfter=6)))
story.append(Paragraph('Complete Ecosystem System Architecture', ParagraphStyle('CS', fontName='LibSans-Bold', fontSize=18, leading=24, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4)))
story.append(Paragraph('Systematic Blueprint: No Guessing, Just Systems', ParagraphStyle('CS2', fontName='LibSans', fontSize=13, leading=17, textColor=TEXT_MUTED, alignment=TA_CENTER, spaceAfter=16)))
story.append(hr())
story.append(Paragraph('Baserow Data Layer | n8n Automation Layer | GoHighLevel CRM Layer | AI Agent Orchestration Layer', ParagraphStyle('CD', fontName='LibSans', fontSize=9.5, leading=13, textColor=TEXT_MUTED, alignment=TA_CENTER, spaceAfter=12)))
story.append(sp(20))

meta_data = [
    ['Document Type', 'System Architecture Blueprint'],
    ['Framework', 'AISEO Framework v3.0 (75-Tab Strategic Blueprint)'],
    ['Prepared For', 'VirtuaLab Digital Operations'],
    ['Classification', 'Internal - Operational'],
    ['Date', 'August 2026'],
    ['Principle', 'Every action is data-driven, tracked, repeatable, and measurable.'],
]
meta_t = Table(meta_data, colWidths=[120, CONTENT_W - 120])
meta_t.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'LibSans-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('TEXTCOLOR', (0, 0), (0, -1), HEADER_FILL),
    ('TEXTCOLOR', (1, 0), (1, -1), TEXT_PRIMARY),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('LINEBELOW', (0, 0), (-1, -2), 0.4, BORDER_COLOR),
    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
    ('RIGHTPADDING', (0, 0), (0, -1), 12),
]))
story.append(meta_t)

story.append(PageBreak())

# ========================
# CHAPTER 1: SYSTEM PHILOSOPHY
# ========================
story.append(Paragraph('1. System Philosophy: Why Systematic, Not Guessing', s_h1))
story.append(sp(4))

story.append(Paragraph(
    'The fundamental problem with most digital marketing agencies is that their operations rely on tribal knowledge, individual heroics, and ad-hoc decision making. A senior SEO specialist "knows" what keywords to target based on experience. A content writer "feels" what topics will resonate. An account manager "remembers" to check client rankings every few weeks. This approach is fragile, unscalable, and fundamentally unmeasurable. When the specialist leaves, the knowledge leaves. When the workload doubles, quality halves. When a new client onboards, the process restarts from zero every time.', s_body))

story.append(Paragraph(
    'VirtuaLab Digital operates on a different principle: every strategic decision, every content action, every client interaction, and every measurement must flow through a systematic, data-driven infrastructure. This ecosystem blueprint defines the exact data structures (Baserow), automation workflows (n8n), client management pipelines (GoHighLevel), and AI agent orchestration protocols that transform the 75-tab AISEO Framework from a static document into a living, breathing operational machine. The goal is simple: any trained operator should be able to execute the strategy by following the system, regardless of their individual expertise level. The system captures intelligence, automates repetition, enforces consistency, and measures everything.', s_body))

story.append(Paragraph('1.1 The Four-Layer Architecture', s_h2))
story.append(Paragraph(
    'The VirtuaLab Digital ecosystem is organized into four interdependent layers, each with a distinct technological foundation and operational responsibility. The Data Layer (Baserow) serves as the single source of truth for all operational data including keywords, content, competitors, clients, and performance metrics. The Automation Layer (n8n) connects all systems, automates repetitive workflows, and enforces process consistency. The CRM and Client Delivery Layer (GoHighLevel) manages the client lifecycle from lead capture through onboarding, delivery, and retention. The AI Agent Orchestration Layer coordinates the six specialized AI agents defined in the AISEO Framework, ensuring that each agent receives the correct inputs, produces standardized outputs, and feeds results back into the data layer for continuous learning.', s_body))

story.append(callout(
    '<b>Core Principle:</b> Data enters the system once, flows through automated workflows, triggers agent actions, surfaces in client reports, and feeds back into strategic decisions. No data lives in silos. No action is taken without a data trigger. No decision is made without a measurement checkpoint.'))

story.append(Paragraph('1.2 Data Flow Architecture', s_h2))
story.append(Paragraph(
    'Information flows through the ecosystem in a unidirectional pipeline with feedback loops. Raw data enters through web search APIs, SERP monitoring tools, Google Search Console, and manual research inputs. This data is normalized and stored in Baserow tables. n8n workflows poll Baserow for new records, process them through AI agents (via LLM API calls), and write outputs back to Baserow. Client-facing actions (content publishing, report generation, email notifications) are triggered by n8n and executed through GoHighLevel or direct API calls. Performance data from published content flows back through web analytics APIs into Baserow, where it is compared against baselines and triggers optimization workflows. This closed-loop system ensures that every action is informed by data and every outcome is measured against objectives.', s_body))

# Data flow table
flow_data = [
    ['1. Data Ingestion', 'External APIs, Manual Input', 'Baserow Tables', 'Keywords, competitors, SERP data, client info stored as structured records.'],
    ['2. Processing', 'Baserow (trigger)', 'n8n Workflows', 'New records trigger workflows: clustering, content briefs, competitor alerts.'],
    ['3. Agent Orchestration', 'n8n (dispatch)', 'AI Agent APIs', '6 specialized agents process tasks: research, positioning, analysis, strategy.'],
    ['4. Output Generation', 'AI Agents (return)', 'Baserow + n8n', 'Agent outputs stored: content briefs, keyword maps, optimization recommendations.'],
    ['5. Client Delivery', 'Baserow (status change)', 'GHL + n8n', 'Approved content published, reports generated, clients notified.'],
    ['6. Performance Feedback', 'Analytics APIs', 'Baserow Tables', 'Rankings, traffic, citations, leads flow back into measurement tables.'],
    ['7. Optimization Loop', 'Baserow (threshold)', 'n8n Workflows', 'Performance below threshold triggers re-optimization workflows.'],
]
t_flow = make_table(
    ['Stage', 'Trigger Source', 'Destination', 'Action'],
    flow_data,
    col_widths=[80, 75, 70, CONTENT_W - 225]
)
story.append(t_flow)

story.append(PageBreak())

# ========================
# CHAPTER 2: BASEROW DATA LAYER
# ========================
story.append(Paragraph('2. Baserow Data Layer: The Single Source of Truth', s_h1))
story.append(sp(4))

story.append(Paragraph(
    'Baserow is the operational database backbone of the VirtuaLab Digital ecosystem. Every keyword, every competitor, every content piece, every client interaction, and every performance metric lives in Baserow. The database is organized into 12 interconnected tables grouped into four functional domains. Each table has defined fields, field types, relationships to other tables, and standardized status fields that trigger n8n workflows. The following specification defines every table, every field, and every relationship with enough precision that a database administrator can implement the entire structure without ambiguity.', s_body))

story.append(Paragraph('2.1 Domain 1: Keyword Intelligence (3 Tables)', s_h2))

# Table 1: Keywords Master
story.append(Paragraph('2.1.1 Table: Keywords Master', s_h3))
story.append(Paragraph(
    'This is the central keyword repository. Every keyword discovered through research, competitor analysis, or client input is stored here. Keywords are never deleted, only deprecated. Each record carries its complete research metadata including search intent classification, demand tier, competitive difficulty, and the specific page it maps to within the site architecture. The status field drives the content pipeline: when a keyword moves from "Research" to "Approved," it becomes eligible for content brief generation by the AI SEO Strategist agent.', s_body))

kw_fields = [
    ['Keyword ID', 'Auto Number', 'Unique', 'System-generated unique identifier.'],
    ['Keyword', 'Text (Single Line)', 'Required', 'The exact search query string.'],
    ['Search Volume (Monthly)', 'Number', 'Optional', 'Monthly estimated search volume from GSC or third-party tool.'],
    ['CPC', 'Currency', 'Optional', 'Cost-per-click data for paid advertising reference.'],
    ['Keyword Difficulty', 'Rating (1-100)', 'Optional', 'Competitive difficulty score (0=easiest, 100=hardest).'],
    ['Search Intent', 'Single Select', 'Required', 'Informational / Commercial / Transactional / Navigational / Technical.'],
    ['Buyer Awareness Stage', 'Single Select', 'Required', 'Unaware / Problem-Aware / Solution-Aware / Most-Aware.'],
    ['Demand Tier', 'Single Select', 'Required', 'High / Medium / Emerging / Low / Seasonal.'],
    ['Keyword Cluster', 'Link to Table', 'Required', 'Links to Keyword Clusters table.'],
    ['Target Industry', 'Link to Table', 'Optional', 'Links to Industries table (HVAC, Roofing, etc.).'],
    ['Target Page URL', 'Text (URL)', 'Required', 'The specific page this keyword maps to on the site.'],
    ['Content Template', 'Single Select', 'Required', 'Hub Page / Service Detail / Resource Guide / Blog Post / FAQ / Industry Landing.'],
    ['Current SERP Position', 'Number', 'Optional', 'Current organic ranking position (updated by monitoring workflow).'],
    ['Current AI Citation Status', 'Single Select', 'Optional', 'Not Tracked / Not Cited / Cited (Positive) / Cited (Negative).'],
    ['Status', 'Single Select', 'Required', 'Research / Clustered / Approved / In Production / Published / Deprecated.'],
    ['Assigned To', 'Link to Table', 'Optional', 'Links to Team Members table.'],
    ['Date Discovered', 'Date', 'Auto', 'When this keyword was added to the database.'],
    ['Last Checked', 'Date', 'Auto', 'Last time SERP position was verified.'],
    ['Notes', 'Long Text', 'Optional', 'Strategic notes, observations, or instructions.'],
]
t_kw = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    kw_fields,
    col_widths=[95, 75, 55, CONTENT_W - 225]
)
story.append(t_kw)
story.append(sp(6))

# Table 2: Keyword Clusters
story.append(Paragraph('2.1.2 Table: Keyword Clusters', s_h3))
story.append(Paragraph(
    'Clusters group related keywords into topical entities. Each cluster represents a distinct theme that maps to a specific section of the website content architecture. Clusters prevent keyword cannibalization by establishing clear ownership boundaries. When the system detects that a new keyword might cannibalize an existing page, it flags the record for human review before content production begins.', s_body))

cluster_fields = [
    ['Cluster ID', 'Auto Number', 'Unique', 'System-generated unique identifier.'],
    ['Cluster Name', 'Text', 'Required', 'e.g., "Core Agency Brand", "Google Maps and GBP", "GEO and AI Search".'],
    ['Cluster Description', 'Long Text', 'Required', 'Detailed description of what this cluster covers and why it exists.'],
    ['Primary Page URL', 'Text (URL)', 'Required', 'The hub page that owns this cluster.'],
    ['Supporting Pages', 'Array of URLs', 'Optional', 'Spoke pages that support the hub.'],
    ['Keywords Count', 'Formula (Count)', 'Auto', 'Count of linked keywords from Keywords Master table.'],
    ['Avg Keyword Difficulty', 'Formula (Avg)', 'Auto', 'Average difficulty of all linked keywords.'],
    ['Total Monthly Volume', 'Formula (Sum)', 'Auto', 'Sum of search volumes across all linked keywords.'],
    ['Cannibalization Rule', 'Long Text', 'Required', 'Keywords to EXCLUDE from this cluster to prevent overlap.'],
    ['Content Status', 'Single Select', 'Auto', 'No Content / In Progress / Published / Needs Update.'],
    ['Last Updated', 'Date', 'Auto', 'Last time any keyword in this cluster was modified.'],
]
t_cl = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    cluster_fields,
    col_widths=[95, 75, 55, CONTENT_W - 225]
)
story.append(t_cl)
story.append(sp(6))

# Table 3: SERP & LLM Citation Tracking
story.append(Paragraph('2.1.3 Table: SERP and LLM Citation Tracking', s_h3))
story.append(Paragraph(
    'This table stores the results of systematic SERP monitoring and AI citation tracking. Every week, the n8n SERP Monitoring workflow queries the top 50 target keywords across Google, ChatGPT, Perplexity, and Google AI Overviews. The results are stored here with structured fields for position, citation context, and citation source. This data feeds the monthly Citation Dominance Score calculation and triggers optimization workflows when performance drops below defined thresholds.', s_body))

serp_fields = [
    ['Record ID', 'Auto Number', 'Unique', 'System-generated unique identifier.'],
    ['Keyword', 'Link to Keywords Master', 'Required', 'Which keyword is being tracked.'],
    ['Platform', 'Single Select', 'Required', 'Google Organic / Google Maps / ChatGPT / Perplexity / Gemini / AI Overviews.'],
    ['VirtuaLab Mentioned', 'Checkbox', 'Required', 'Whether VirtuaLab Digital was mentioned in results.'],
    ['Mention Context', 'Single Select', 'Required', 'Not Mentioned / Positive Citation / Neutral Mention / Negative / Competitor Only.'],
    ['Citation Source URL', 'Text (URL)', 'Optional', 'The URL of the source that AI cited about VirtuaLab.'],
    ['SERP Position', 'Number', 'Optional', 'Organic ranking position (1-100, or 0 if not found).'],
    ['Featured Snippet', 'Checkbox', 'Optional', 'Whether a featured snippet appeared for this query.'],
    ['AI Overview Present', 'Checkbox', 'Optional', 'Whether Google AI Overviews appeared.'],
    ['Top Competitor Cited', 'Link to Competitors', 'Optional', 'Which competitor was cited instead of VirtuaLab.'],
    ['Check Date', 'Date', 'Required', 'Date this check was performed.'],
    ['Triggered Action', 'Single Select', 'Auto', 'None / Content Gap Alert / Optimization Workflow / Parasite Content Needed.'],
]
t_serp = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    serp_fields,
    col_widths=[95, 80, 50, CONTENT_W - 225]
)
story.append(t_serp)

story.append(PageBreak())

# ========================
# 2.2 Domain 2: Content Operations
# ========================
story.append(Paragraph('2.2 Domain 2: Content Operations (3 Tables)', s_h2))

story.append(Paragraph('2.2.1 Table: Content Calendar', s_h3))
story.append(Paragraph(
    'Every piece of content, whether for the primary domain or a parasite platform, is tracked in the Content Calendar. This table is the operational backbone of the content pipeline. When a keyword moves to "Approved" status in Keywords Master, an n8n workflow automatically creates a draft Content Calendar record with a pre-filled content brief generated by the AI SEO Strategist agent. The content brief includes the target keyword, search intent, buyer awareness stage, recommended word count, internal linking targets, and GEO optimization requirements. Human editors review and approve briefs before content production begins.', s_body))

content_fields = [
    ['Content ID', 'Auto Number', 'Unique', 'System-generated unique identifier.'],
    ['Title', 'Text', 'Required', 'Working title of the content piece.'],
    ['Content Type', 'Single Select', 'Required', 'Blog Post / Service Page / Industry Page / Resource Guide / FAQ / Parasite Article / YouTube Script / Social Post / GBP Post.'],
    ['Target Platform', 'Single Select', 'Required', 'Primary Domain / LinkedIn / Medium / YouTube / Reddit / Quora / GBP.'],
    ['Target Keyword', 'Link to Keywords Master', 'Required', 'Primary keyword this content targets.'],
    ['Secondary Keywords', 'Array (Link)', 'Optional', 'Additional keywords to naturally incorporate.'],
    ['Keyword Cluster', 'Link to Keyword Clusters', 'Required', 'Which cluster this content belongs to.'],
    ['Target Industry', 'Link to Industries', 'Optional', 'Industry vertical if applicable.'],
    ['Content Brief', 'Long Text', 'Required', 'Auto-generated by AI SEO Strategist. Includes outline, word count, GEO factors, internal links.'],
    ['GEO Requirements', 'Long Text', 'Optional', 'Specific GEO factors to implement: statistics, citations, BLUF, entities.'],
    ['Assigned Writer', 'Link to Team Members', 'Optional', 'Who is writing this content.'],
    ['Assigned Client', 'Link to Clients', 'Optional', 'If this is client-specific content.'],
    ['Word Count Target', 'Number', 'Required', 'Target word count for quality control.'],
    ['Status', 'Single Select', 'Required', 'Brief Generated / Brief Approved / In Writing / In Review / Approved / Published / Archived.'],
    ['Publish Date', 'Date', 'Required', 'Scheduled publication date.'],
    ['Actual Publish Date', 'Date', 'Optional', 'Actual date content went live.'],
    ['URL (Published)', 'Text (URL)', 'Optional', 'URL where content was published.'],
    ['Internal Links Added', 'Checkbox', 'Auto', 'Whether internal links were verified after publication.'],
    ['Schema Markup Added', 'Checkbox', 'Auto', 'Whether schema was added after publication.'],
    ['Performance Check Date', 'Date', 'Auto', 'Date when 30-day performance review is scheduled.'],
]
t_content = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    content_fields,
    col_widths=[90, 72, 48, CONTENT_W - 210]
)
story.append(t_content)
story.append(sp(6))

story.append(Paragraph('2.2.2 Table: Competitor Intelligence', s_h3))
story.append(Paragraph(
    'Every competitor identified in the strategy is tracked systematically. The Competitor Analysis Sentinel agent is responsible for maintaining this table with current data on competitor keywords, backlink profiles, content gaps, and pricing structures. When a competitor publishes new content or changes their pricing, the monitoring workflow updates this table and triggers an alert. This ensures that VirtuaLab always has current competitive intelligence without manual research efforts.', s_body))

comp_fields = [
    ['Competitor ID', 'Auto Number', 'Unique', 'System identifier.'],
    ['Company Name', 'Text', 'Required', 'Competitor name.'],
    ['Website URL', 'Text (URL)', 'Required', 'Primary domain.'],
    ['Competitor Type', 'Single Select', 'Required', 'Direct Agency / Niche Specialist / Platform / Freelancer Network.'],
    ['Target Verticals', 'Array (Link)', 'Optional', 'Which industries they target.'],
    ['Pricing Model', 'Long Text', 'Optional', 'Known pricing tiers, minimums, contract terms.'],
    ['Key Strengths', 'Long Text', 'Required', 'Documented strengths from analysis.'],
    ['Key Weaknesses', 'Long Text', 'Required', 'Documented weaknesses and gaps.'],
    ['Content Gap Opportunities', 'Long Text', 'Required', 'Specific content/topics they lack that VirtuaLab can exploit.'],
    ['VirtuaLab Positioning', 'Long Text', 'Required', 'How VirtuaLab differentiates against this competitor.'],
    ['Est. Domain Authority', 'Number', 'Optional', 'Estimated or measured domain authority.'],
    ['Organic Keywords Tracked', 'Array (Link)', 'Optional', 'Keywords where this competitor ranks.'],
    ['LLM Citation Frequency', 'Number', 'Optional', 'How often they appear in AI-generated responses.'],
    ['Last Analyzed', 'Date', 'Auto', 'Last date of systematic competitive analysis.'],
    ['Alert Active', 'Checkbox', 'Auto', 'Whether monitoring alerts are active for this competitor.'],
]
t_comp = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    comp_fields,
    col_widths=[95, 72, 48, CONTENT_W - 215]
)
story.append(t_comp)

story.append(PageBreak())

# ========================
# 2.3 Domain 3: Client Operations
# ========================
story.append(Paragraph('2.3 Domain 3: Client Operations (3 Tables)', s_h2))

story.append(Paragraph('2.3.1 Table: Clients', s_h3))
client_fields = [
    ['Client ID', 'Auto Number', 'Unique', 'System identifier.'],
    ['Company Name', 'Text', 'Required', 'Client business name.'],
    ['Industry Vertical', 'Link to Industries', 'Required', 'Primary industry.'],
    ['Website URL', 'Text (URL)', 'Required', 'Client website domain.'],
    ['GBP URL', 'Text (URL)', 'Optional', 'Google Business Profile URL.'],
    ['Archetype', 'Single Select', 'Required', 'The Operator / The Practitioner / The Institution.'],
    ['Annual Revenue Range', 'Single Select', 'Required', 'Under $500K / $500K-$1M / $1M-$5M / $5M-$10M / $10M-$15M / Over $15M.'],
    ['Employee Count', 'Number', 'Optional', 'Approximate number of employees.'],
    ['Monthly Ad Spend', 'Currency', 'Optional', 'Current monthly paid advertising budget.'],
    ['Primary Pain Point', 'Single Select', 'Required', 'Paid Ad Fatigue / Maps Invisibility / Page 2 Syndrome / Leaky Leads / No SEO.'],
    ['Service Package', 'Link to Service Packages', 'Required', 'Which VirtuaLab service package they purchased.'],
    ['Contract Start Date', 'Date', 'Required', 'When the engagement began.'],
    ['Contract End Date', 'Date', 'Required', 'When the engagement ends.'],
    ['GHL Contact ID', 'Text', 'Optional', 'Linked GoHighLevel contact record.'],
    ['Onboarding Status', 'Single Select', 'Required', 'Lead / Qualified / Proposal Sent / Contract Signed / Onboarding / Active / Churned.'],
    ['Baseline Organic Traffic', 'Number', 'Optional', 'Monthly organic sessions at engagement start.'],
    ['Baseline Map Pack Rate', 'Number', 'Optional', 'Percentage of target keywords in Map Pack at start.'],
    ['Current Organic Traffic', 'Number', 'Auto', 'Latest monthly organic sessions (from GSC integration).'],
    ['Current Map Pack Rate', 'Number', 'Auto', 'Latest Map Pack appearance percentage.'],
    ['Lead Cost Baseline', 'Currency', 'Optional', 'Cost per lead at engagement start.'],
    ['Current Lead Cost', 'Currency', 'Auto', 'Latest calculated cost per lead.'],
]
t_client = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    client_fields,
    col_widths=[95, 72, 48, CONTENT_W - 215]
)
story.append(t_client)
story.append(sp(6))

story.append(Paragraph('2.3.2 Table: Service Packages', s_h3))
pkg_fields = [
    ['Package ID', 'Auto Number', 'Unique', 'System identifier.'],
    ['Package Name', 'Text', 'Required', 'e.g., "Local Visibility Starter", "Full AEO-Ready Website", "Multi-Location Dominance".'],
    ['Description', 'Long Text', 'Required', 'What the package includes.'],
    ['Price Range (Min)', 'Currency', 'Required', 'Minimum monthly or one-time fee.'],
    ['Price Range (Max)', 'Currency', 'Required', 'Maximum monthly or one-time fee.'],
    ['Billing Model', 'Single Select', 'Required', 'Monthly Retainer / One-Time Project / Hybrid.'],
    ['Included Services', 'Array (Link)', 'Required', 'Links to Services table.'],
    ['Deliverables', 'Long Text', 'Required', 'Specific deliverables per month/phase.'],
    ['Contract Duration', 'Single Select', 'Required', 'Month-to-Month / 3 Months / 6 Months / 12 Months.'],
    ['Active', 'Checkbox', 'Required', 'Whether this package is currently offered.'],
]
t_pkg = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    pkg_fields,
    col_widths=[95, 80, 50, CONTENT_W - 225]
)
story.append(t_pkg)

story.append(Paragraph('2.3.3 Table: Industries', s_h3))
ind_fields = [
    ['Industry ID', 'Auto Number', 'Unique', 'System identifier.'],
    ['Industry Name', 'Text', 'Required', 'e.g., HVAC, Plumbing, Roofing, Pest Control, Electrical, Dentistry, Landscaping.'],
    ['Slug', 'Text', 'Required', 'URL slug: /industries/hvac.'],
    ['Target Keywords Count', 'Formula', 'Auto', 'Count of keywords targeting this industry.'],
    ['Active Clients Count', 'Formula', 'Auto', 'Count of active clients in this vertical.'],
    ['Content Published Count', 'Formula', 'Auto', 'Count of published content pieces.'],
    ['Average Client Revenue', 'Formula (Avg)', 'Auto', 'Average revenue of active clients in this vertical.'],
    ['Seasonal Patterns', 'Long Text', 'Optional', 'Known seasonal demand patterns (e.g., HVAC peaks in summer).'],
    ['Specific Search Challenges', 'Long Text', 'Optional', 'Vertical-specific search behavior notes.'],
    ['Priority Level', 'Single Select', 'Required', 'Primary (active focus) / Secondary (established) / Emerging (new vertical).'],
]
t_ind = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    ind_fields,
    col_widths=[95, 72, 55, CONTENT_W - 222]
)
story.append(t_ind)

story.append(PageBreak())

# ========================
# 2.4 Domain 4: Performance & Reporting
# ========================
story.append(Paragraph('2.4 Domain 4: Performance and Reporting (3 Tables)', s_h2))

story.append(Paragraph('2.4.1 Table: KPI Dashboard', s_h3))
kpi_fields = [
    ['KPI ID', 'Auto Number', 'Unique', 'System identifier.'],
    ['Client', 'Link to Clients', 'Required', 'Which client this measures.'],
    ['Metric Name', 'Single Select', 'Required', 'Organic Traffic / Map Pack Rate / Citation Score / Cost Per Lead / Review Velocity / Keyword Rankings.'],
    ['Baseline Value', 'Number', 'Required', 'Value at contract start.'],
    ['Current Value', 'Number', 'Auto', 'Latest measured value.'],
    ['Target Value', 'Number', 'Required', 'Goal value for contract period.'],
    ['Progress Percentage', 'Formula', 'Auto', '(Current - Baseline) / (Target - Baseline) x 100.'],
    ['Measurement Date', 'Date', 'Auto', 'When this value was last measured.'],
    ['Data Source', 'Single Select', 'Required', 'Google Search Console / BrightLocal / Manual AI Query / GHL CRM / Ahrefs.'],
    ['Status', 'Formula', 'Auto', 'On Track (green) / At Risk (yellow) / Behind (red) - based on progress vs timeline.'],
]
t_kpi = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    kpi_fields,
    col_widths=[90, 72, 48, CONTENT_W - 210]
)
story.append(t_kpi)
story.append(sp(6))

story.append(Paragraph('2.4.2 Table: Parasite Platform Assets', s_h3))
para_fields = [
    ['Asset ID', 'Auto Number', 'Unique', 'System identifier.'],
    ['Platform', 'Single Select', 'Required', 'LinkedIn / Medium / YouTube / Reddit / Quora / Google Sites / Cloud Property.'],
    ['Profile URL', 'Text (URL)', 'Required', 'URL of the profile or property.'],
    ['Platform Authority (DA)', 'Number', 'Optional', 'Domain authority of the platform.'],
    ['Content Published Count', 'Formula', 'Auto', 'Count of content pieces published on this platform.'],
    ['Total Impressions', 'Number', 'Auto', 'Aggregate impressions across all content on this platform.'],
    ['Total Clicks', 'Number', 'Auto', 'Aggregate clicks to primary domain from this platform.'],
    ['Last Published Date', 'Date', 'Auto', 'Most recent content publication date.'],
    ['Publishing Cadence', 'Single Select', 'Required', 'Weekly / Bi-Weekly / Monthly / As Needed.'],
    ['Status', 'Single Select', 'Required', 'Active / Paused / Needs Setup.'],
]
t_para = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    para_fields,
    col_widths=[95, 72, 48, CONTENT_W - 215]
)
story.append(t_para)

story.append(Paragraph('2.4.3 Table: Team Members', s_h3))
team_fields = [
    ['Member ID', 'Auto Number', 'Unique', 'System identifier.'],
    ['Name', 'Text', 'Required', 'Team member name.'],
    ['Role', 'Single Select', 'Required', 'SEO Strategist / Content Writer / Technical SEO / Account Manager / Web Developer.'],
    ['Email', 'Email', 'Required', 'Contact email.'],
    ['GHL User ID', 'Text', 'Optional', 'Linked GoHighLevel user.'],
    ['Active Clients', 'Array (Link)', 'Auto', 'Clients assigned to this team member.'],
    ['Capacity Status', 'Single Select', 'Required', 'Available / At Capacity / Overloaded.'],
]
t_team = make_table(
    ['Field Name', 'Field Type', 'Constraint', 'Description'],
    team_fields,
    col_widths=[90, 72, 55, CONTENT_W - 217]
)
story.append(t_team)

story.append(callout(
    '<b>Baserow Implementation Note:</b> All tables use Baserow Link to Table fields for relationships. Formula fields are calculated automatically. Single Select fields use predefined options (no free-text for status/intent fields). Auto fields are system-generated. The n8n integration uses Baserow API webhooks for real-time triggering on record creation and status changes.'))

story.append(PageBreak())

# ========================
# CHAPTER 3: n8n AUTOMATION LAYER
# ========================
story.append(Paragraph('3. n8n Automation Layer: The Nervous System', s_h1))
story.append(sp(4))

story.append(Paragraph(
    'n8n is the automation engine that connects every component of the ecosystem. Without n8n, Baserow is a static database, GHL is a standalone CRM, and AI agents are isolated tools. With n8n, the entire ecosystem becomes a living system where data flows automatically between components, triggers actions based on business rules, and enforces process consistency. Every workflow defined below has a specific trigger, a defined process, and a measurable output. No workflow runs without a data trigger. No action is taken without a record being created or updated in Baserow.', s_body))

story.append(Paragraph('3.1 Workflow 1: Keyword Research and Clustering Pipeline', s_h2))
story.append(Paragraph(
    'This workflow automates the discovery, classification, and clustering of new keywords. It runs on a weekly schedule and also triggers on-demand when a new client onboards. The workflow pulls search data from the web search API, classifies each keyword by intent and awareness stage using an LLM call, checks for cannibalization against existing clusters in Baserow, and creates new records in the Keywords Master table with all fields pre-filled. The AI SEO Strategist agent processes the clustering logic.', s_body))

wf1_data = [
    ['Trigger', 'Weekly Schedule (Monday 6AM) OR Manual Webhook', 'Starts the pipeline on schedule or on demand.'],
    ['Step 1', 'Fetch Seed Keywords from Baserow', 'Pulls all keywords with Status = "Research" from Keywords Master.'],
    ['Step 2', 'Expand Keywords via Search API', 'For each seed keyword, query search API for related terms, PAA questions, and variations.'],
    ['Step 3', 'Classify Intent (LLM Call)', 'Send each keyword to AI SEO Strategist agent for intent/stage classification.'],
    ['Step 4', 'Check Cannibalization', 'Compare new keywords against existing Keyword Clusters to detect overlap.'],
    ['Step 5', 'Assign to Cluster', 'Based on intent + industry + cannibalization check, assign to appropriate cluster.'],
    ['Step 6', 'Calculate Difficulty', 'Pull SERP data for top 10 results, estimate difficulty score.'],
    ['Step 7', 'Write to Baserow', 'Create new records in Keywords Master with all fields populated.'],
    ['Step 8', 'Update Cluster Counts', 'Recalculate keyword counts and avg difficulty for affected clusters.'],
    ['Step 9', 'Alert if High-Value', 'If any keyword has High demand + Low difficulty + No content, send Slack/email alert.'],
]
t_wf1 = make_table(
    ['Step', 'Action', 'Description'],
    wf1_data,
    col_widths=[60, 160, CONTENT_W - 220]
)
story.append(t_wf1)
story.append(sp(6))

story.append(Paragraph('3.2 Workflow 2: Content Brief Generation Pipeline', s_h2))
story.append(Paragraph(
    'When a keyword moves to "Approved" status in Baserow, this workflow automatically generates a comprehensive content brief. The brief is created by the AI SEO Strategist agent and includes the target keyword, secondary keywords, recommended word count, H2/H3 outline, GEO optimization requirements, internal linking targets, and the specific buyer awareness stage messaging angle. The brief is written to the Content Calendar table as a new record with Status = "Brief Generated." A notification is sent to the assigned writer for review and approval before content production begins.', s_body))

wf2_data = [
    ['Trigger', 'Baserow Webhook: Keywords Master.Status changes to Approved', 'Reactive trigger on keyword approval.'],
    ['Step 1', 'Read Keyword Record', 'Fetch full keyword record including cluster, industry, intent, stage.'],
    ['Step 2', 'Fetch Cluster Context', 'Pull all keywords in the same cluster to understand topical boundaries.'],
    ['Step 3', 'Check Existing Content', 'Search Content Calendar for any existing content targeting this keyword.'],
    ['Step 4', 'Generate Brief (LLM Call)', 'AI SEO Strategist agent generates full content brief with outline.'],
    ['Step 5', 'Add GEO Requirements', 'Based on content type, add specific GEO factors to implement.'],
    ['Step 6', 'Create Content Calendar Record', 'Write brief to Content Calendar with Status = "Brief Generated".'],
    ['Step 7', 'Notify Writer', 'Send notification via GHL task or email to assigned writer.'],
]
t_wf2 = make_table(
    ['Step', 'Action', 'Description'],
    wf2_data,
    col_widths=[60, 160, CONTENT_W - 220]
)
story.append(t_wf2)

story.append(Paragraph('3.3 Workflow 3: SERP and AI Citation Monitoring', s_h2))
story.append(Paragraph(
    'This workflow runs weekly and systematically checks the top 50 target keywords across six platforms: Google Organic, Google Maps, ChatGPT, Perplexity, Google Gemini, and Google AI Overviews. For each keyword-platform combination, the workflow records whether VirtuaLab was mentioned, the context of the mention, the ranking position, and which competitor was cited if VirtuaLab was not. This data flows into the SERP and LLM Citation Tracking table and feeds the monthly Citation Dominance Score report. When a tracked keyword drops more than 5 positions or loses an AI citation, the workflow triggers an optimization alert.', s_body))

wf3_data = [
    ['Trigger', 'Weekly Schedule (Wednesday 6AM)', 'Systematic weekly check across all platforms.'],
    ['Step 1', 'Fetch Target Keywords', 'Pull all keywords with Status = "Published" or "Approved" from Baserow.'],
    ['Step 2', 'Query Google SERP', 'For each keyword, scrape top 10 organic results, record position.'],
    ['Step 3', 'Query Google Maps', 'Check Map Pack for local intent keywords, record appearance.'],
    ['Step 4', 'Query AI Platforms', 'Send target queries to ChatGPT, Perplexity, Gemini via API.'],
    ['Step 5', 'Parse AI Responses', 'Extract mentions, context, and cited sources from AI responses.'],
    ['Step 6', 'Write to Tracking Table', 'Create records in SERP and LLM Citation Tracking table.'],
    ['Step 7', 'Calculate Citation Score', 'Compute monthly Citation Dominance Score percentage.'],
    ['Step 8', 'Threshold Alert', 'If position drop > 5 or citation lost, create alert record.'],
    ['Step 9', 'Trigger Optimization', 'For alerts, create optimization task in Content Calendar.'],
]
t_wf3 = make_table(
    ['Step', 'Action', 'Description'],
    wf3_data,
    col_widths=[60, 150, CONTENT_W - 210]
)
story.append(t_wf3)

story.append(Paragraph('3.4 Workflow 4: Competitor Monitoring Alert', s_h2))
story.append(Paragraph(
    'This workflow monitors the top 7 identified competitors (Hook Agency, Rival Digital, Blue Corona, Scorpion, RYNO Strategic, PlumberSEO.net, Sequoia GEO) for new content publications, pricing changes, and keyword movements. When a competitor publishes new content that targets keywords in VirtuaLab clusters, the workflow creates an alert in Baserow and optionally generates a response content brief. This ensures VirtuaLab can react quickly to competitive threats rather than discovering them months later during manual reviews.', s_body))

wf4_data = [
    ['Trigger', 'Weekly Schedule (Friday 6AM)', 'Weekly competitor scan.'],
    ['Step 1', 'Fetch Active Competitors', 'Pull all competitors with Alert Active = true from Competitor Intelligence.'],
    ['Step 2', 'Scrape Competitor Blogs', 'Check for new blog posts or content pages published since last check.'],
    ['Step 3', 'Extract Target Keywords', 'Parse competitor content for target keyword usage.'],
    ['Step 4', 'Check for Overlap', 'Cross-reference competitor keywords with VirtuaLab keyword clusters.'],
    ['Step 5', 'Monitor Pricing Pages', 'Scrape pricing pages for changes in tiers or minimums.'],
    ['Step 6', 'Generate Alert', 'If overlap or pricing change detected, create alert in Baserow.'],
    ['Step 7', 'Optional: Generate Response Brief', 'If high-priority overlap, auto-generate response content brief.'],
    ['Step 8', 'Update Competitor Record', 'Update Last Analyzed date and citation frequency.'],
]
t_wf4 = make_table(
    ['Step', 'Action', 'Description'],
    wf4_data,
    col_widths=[60, 150, CONTENT_W - 210]
)
story.append(t_wf4)

story.append(PageBreak())

story.append(Paragraph('3.5 Workflow 5: Client Reporting Pipeline', s_h2))
story.append(Paragraph(
    'This workflow automates the generation of monthly client performance reports. On the first business day of each month, the workflow pulls KPI data from Google Search Console, BrightLocal (for local rankings), the SERP/LLM Citation Tracking table, and the GHL CRM (for lead data). It calculates month-over-month changes, computes progress toward targets, and generates a structured report that is uploaded to GHL as a PDF and sent to the client via email. The report includes organic traffic trends, Map Pack appearance rates, keyword ranking changes, AI citation progress, and cost-per-lead calculations. This eliminates the manual report-writing process and ensures every client receives a consistent, data-rich monthly report.', s_body))

wf5_data = [
    ['Trigger', 'Monthly Schedule (1st of month, 7AM)', 'Automated monthly reporting.'],
    ['Step 1', 'Fetch Active Clients', 'Pull all clients with Onboarding Status = "Active" from Baserow.'],
    ['Step 2', 'Pull GSC Data', 'For each client, query Google Search Console API for last 30 days.'],
    ['Step 3', 'Pull Local Data', 'Query BrightLocal API for Map Pack and local ranking data.'],
    ['Step 4', 'Pull Citation Data', 'Aggregate SERP/LLM Citation Tracking data for the month.'],
    ['Step 5', 'Pull Lead Data', 'Query GHL CRM for leads generated, conversion rate, cost per lead.'],
    ['Step 6', 'Calculate KPIs', 'Compute all KPI values and update KPI Dashboard table in Baserow.'],
    ['Step 7', 'Generate Report (LLM)', 'AI agent generates narrative analysis of the data.'],
    ['Step 8', 'Create PDF Report', 'Render report as PDF using template system.'],
    ['Step 9', 'Upload to GHL', 'Attach PDF to client contact record in GoHighLevel.'],
    ['Step 10', 'Send Email', 'Send report email to client with PDF attachment.'],
]
t_wf5 = make_table(
    ['Step', 'Action', 'Description'],
    wf5_data,
    col_widths=[60, 140, CONTENT_W - 200]
)
story.append(t_wf5)

story.append(Paragraph('3.6 Workflow 6: Content Publishing and Verification', s_h2))
story.append(Paragraph(
    'When content moves to "Approved" status in the Content Calendar, this workflow manages the publication process. For primary domain content, it triggers a notification for the web developer to publish. For parasite platform content, it generates platform-specific formatting and posts via API where possible (LinkedIn, Medium). After publication, the workflow verifies that the content is live, checks that internal links are functional, confirms schema markup is present, and updates the content record with the published URL and date. It also schedules a 30-day performance review by creating a future-dated task in the system.', s_body))

story.append(Paragraph('3.7 n8n Workflow Summary', s_h2))
wf_summary = [
    ['WF-01: Keyword Research and Clustering', 'Weekly + On-Demand', 'Baserow Webhook', 'Keywords Master', 'Auto-discover, classify, and cluster keywords.'],
    ['WF-02: Content Brief Generation', 'Reactive (on keyword approval)', 'Baserow Webhook', 'Content Calendar', 'Generate AI content briefs for approved keywords.'],
    ['WF-03: SERP and AI Citation Monitoring', 'Weekly', 'Schedule', 'SERP/LLM Tracking', 'Track rankings and AI citations across 6 platforms.'],
    ['WF-04: Competitor Monitoring', 'Weekly', 'Schedule', 'Competitor Intelligence', 'Monitor competitors for new content and pricing changes.'],
    ['WF-05: Client Reporting', 'Monthly', 'Schedule', 'KPI Dashboard + GHL', 'Generate and deliver monthly performance reports.'],
    ['WF-06: Content Publishing', 'Reactive (on content approval)', 'Baserow Webhook', 'Content Calendar', 'Manage publication and post-publish verification.'],
    ['WF-07: Review Generation Nudge', 'Bi-Weekly', 'Schedule', 'GHL Tasks', 'Nudge clients to request Google reviews from customers.'],
    ['WF-08: GBP Post Scheduling', 'Bi-Weekly', 'Schedule', 'Content Calendar', 'Schedule and track Google Business Profile posts.'],
]
t_wf_sum = make_table(
    ['Workflow', 'Frequency', 'Trigger', 'Writes To', 'Purpose'],
    wf_summary,
    col_widths=[105, 55, 55, 72, CONTENT_W - 287]
)
story.append(t_wf_sum)

story.append(PageBreak())

# ========================
# CHAPTER 4: GHL CRM LAYER
# ========================
story.append(Paragraph('4. GoHighLevel CRM Layer: Client Delivery Pipeline', s_h1))
story.append(sp(4))

story.append(Paragraph(
    'GoHighLevel (GHL) serves as the client-facing operational layer of the ecosystem. While Baserow is the internal data backbone and n8n is the automation engine, GHL is where client interactions happen: lead capture, proposal delivery, contract signing, onboarding checklists, task management, communication, and reporting. The GHL pipeline is designed to mirror the buyer journey defined in the strategy document, with pipeline stages that correspond to each step from initial awareness through active delivery and renewal.', s_body))

story.append(Paragraph('4.1 Pipeline Stages', s_h2))
ghl_stages = [
    ['Stage 1: New Lead', 'Contact created via website form, diagnostic audit request, or referral. No qualification yet.', 'Auto-respond with diagnostic audit delivery (if applicable). Add to nurture sequence.'],
    ['Stage 2: Qualified', 'Lead has engaged with content, requested audit, or met qualification criteria ($1M+ revenue, local service, paid ad dependency).', 'Trigger n8n to create Client record in Baserow. Assign account manager.'],
    ['Stage 3: Proposal Sent', 'Custom proposal generated based on industry vertical, pain points, and service needs. Sent via GHL email/document system.', 'Proposal includes specific deliverables, timeline, pricing, and case study references. Track open rate.'],
    ['Stage 4: Contract Signed', 'Client has signed the engagement contract and paid initial invoice.', 'Trigger n8n onboarding workflow: create Baserow records, set up GSC access, schedule kick-off call.'],
    ['Stage 5: Onboarding (Week 1-2)', 'Technical audit completed. Access established. Baseline metrics recorded in Baserow. KPI Dashboard initialized.', 'Complete onboarding checklist: GSC, GBP access, CRM integration, baseline report.'],
    ['Stage 6: Active Delivery', 'Ongoing SEO, content, and optimization work. Monthly reports delivered. Weekly tasks assigned and tracked.', 'n8n workflows drive content pipeline, reporting, and monitoring automatically.'],
    ['Stage 7: Renewal (60 days before end)', 'Renewal conversation initiated. Performance data compiled. ROI presentation prepared.', 'Generate ROI summary from Baserow KPI Dashboard. Prepare renewal proposal.'],
    ['Stage 8: Churned / Lost', 'Client did not renew or terminated early. Reason recorded for analysis.', 'Log churn reason in Baserow. Trigger post-mortem analysis workflow.'],
]
t_ghl = make_table(
    ['Pipeline Stage', 'Definition', 'Automated Actions'],
    ghl_stages,
    col_widths=[80, 175, CONTENT_W - 255]
)
story.append(t_ghl)

story.append(Paragraph('4.2 GHL Automation Rules', s_h2))
story.append(Paragraph(
    'GHL workflows complement n8n automations by handling the client communication and task management layer. When a new lead enters Stage 1, GHL automatically sends a welcome email with the diagnostic audit results (if applicable) and adds the contact to a 5-email nurture sequence. The nurture sequence is paced over 14 days and includes educational content about local SEO, paid ad dependency, and GEO. Each email includes a tracking pixel that updates the lead score in GHL based on opens and clicks. When a lead score reaches a defined threshold, GHL automatically moves the contact to Stage 2 (Qualified) and assigns an account manager through a round-robin distribution rule.', s_body))

story.append(Paragraph(
    'During Active Delivery (Stage 6), GHL task management ensures that every weekly deliverable is tracked. n8n creates GHL tasks for content publication, review requests, and reporting deadlines. Each task has a due date, an assignee, and a checklist of completion criteria. When a task is marked complete, GHL triggers a webhook to n8n, which updates the corresponding Baserow record and proceeds to the next step in the workflow. This bidirectional integration between GHL and Baserow (mediated by n8n) ensures that client-facing task management and internal data management stay perfectly synchronized.', s_body))

story.append(Paragraph('4.3 GHL Dashboard Configuration', s_h2))
story.append(Paragraph(
    'The GHL dashboard is configured to show account managers a real-time view of their client portfolio. The primary dashboard displays each active client with key metrics: organic traffic trend (sparkline), Map Pack appearance rate, citation score, leads this month, and cost per lead. Color coding (green/yellow/red) reflects KPI status from the Baserow KPI Dashboard table. A secondary dashboard shows the content pipeline: how many briefs are pending, in writing, in review, and published this month. A third dashboard shows parasite platform performance: impressions, clicks, and citation contributions from each external platform. All dashboard data is pulled from Baserow via n8n API calls, ensuring a single source of truth.', s_body))

story.append(PageBreak())

# ========================
# CHAPTER 5: AI AGENT ORCHESTRATION
# ========================
story.append(Paragraph('5. AI Agent Orchestration Layer', s_h1))
story.append(sp(4))

story.append(Paragraph(
    'The AISEO Framework defines six specialized AI agents that operate within the ecosystem. Each agent has a distinct role, a defined input/output specification, and a clear integration point with the Baserow/n8n infrastructure. Agents are not autonomous decision-makers; they are specialized processors that receive structured inputs from Baserow (via n8n), apply their expertise, and return structured outputs that are written back to Baserow. Human operators review agent outputs before they trigger client-facing actions. This ensures quality control while leveraging AI speed and consistency for data-heavy tasks.', s_body))

story.append(Paragraph('5.1 Agent Specifications', s_h2))

agent_data = [
    ['1. Deep Marketing Strategist', 'Market analysis, buyer psychology, demand modeling, competitive positioning', 'Baserow: Clients table, Industries table, Competitor Intelligence table', 'Baserow: Updates client ICP notes, industry demand patterns, positioning recommendations', 'n8n WF-01 (keyword expansion), WF-04 (competitor analysis)', 'LLM system prompt includes full ICP data and psychographic profiles from strategy doc. Outputs must include data citations.'],
    ['2. Positioning Strategist', 'Brand messaging, differentiation analysis, value proposition development, content angle creation', 'Baserow: Competitor Intelligence, Keywords Master (commercial intent), Content Calendar', 'Baserow: Content briefs with messaging angles, competitor differentiation notes', 'n8n WF-02 (content brief generation)', 'Inputs include competitor strengths/weaknesses. Outputs must specify unique angles vs each competitor.'],
    ['3. Competitor Analysis Sentinel', 'SERP analysis, competitor content monitoring, backlink profiling, gap identification', 'Baserow: Competitor Intelligence, SERP/LLM Citation Tracking, Keywords Master', 'Baserow: Competitor records, gap opportunities, alert triggers', 'n8n WF-03 (SERP monitoring), WF-04 (competitor alerts)', 'Must track all 7 primary competitors. Output must include specific URL-level gaps.'],
    ['4. AI SEO Strategist', 'Keyword clustering, content brief generation, GEO optimization, topic mapping', 'Baserow: Keywords Master, Keyword Clusters, Content Calendar', 'Baserow: Keyword clusters, content briefs, GEO requirements', 'n8n WF-01 (clustering), WF-02 (briefs)', 'Core agent for content pipeline. Must implement all 9 GEO factors in briefs.'],
    ['5. Parasite SEO Strategist', 'Platform selection, content formatting per platform, publishing cadence, citation tracking', 'Baserow: Parasite Platform Assets, Content Calendar (parasite type), SERP/LLM Tracking', 'Baserow: Platform-specific content guidelines, publication calendar, performance tracking', 'n8n WF-06 (publishing), WF-03 (citation tracking)', 'Must know platform-specific DA, audience, and content format rules.'],
    ['6. Sentinel (Quality Gate)', 'Output validation, quality scoring, cannibalization checking, brand voice compliance', 'Baserow: All tables (read-only audit)', 'Baserow: Quality scores, validation flags, required revision notes', 'All workflows (post-processing step)', 'Final gate before any content reaches human review or publication. Rejects content that violates brand rules.'],
]

agent_t = make_table(
    ['Agent', 'Responsibilities', 'Input Sources (Baserow)', 'Output Destinations', 'n8n Integration', 'Operating Rules'],
    agent_data,
    col_widths=[60, 72, 65, 65, 58, CONTENT_W - 320]
)
story.append(agent_t)

story.append(Paragraph('5.2 Agent Communication Protocol', s_h2))
story.append(Paragraph(
    'Agents communicate through Baserow, not directly with each other. When the AI SEO Strategist generates a content brief, it writes the brief to the Content Calendar table. The Sentinel agent then reads the brief from Baserow, validates it against quality rules, and writes a quality score and any revision notes back to the same record. This indirect communication pattern ensures that every agent interaction is logged, auditable, and recoverable. If an agent produces an error, the record in Baserow shows exactly what went wrong and which agent was responsible.', s_body))

story.append(Paragraph(
    'The n8n workflow acts as the orchestrator that sequences agent calls. For example, in the content brief generation workflow (WF-02), n8n first calls the AI SEO Strategist to generate the brief, then calls the Sentinel to validate it. If the Sentinel approves, the record status moves to "Brief Generated" and a notification is sent. If the Sentinel rejects, the record stays in draft and a revision task is created. This sequential, quality-gated approach ensures that no substandard output reaches human reviewers or clients.', s_body))

story.append(Paragraph('5.3 Agent Input/Output Schema', s_h2))
story.append(Paragraph(
    'Every agent interaction follows a standardized JSON schema that is stored in Baserow Long Text fields. This ensures consistency and enables the Sentinel agent to validate outputs programmatically. The schema includes: agent_id (which agent produced this), input_data (the structured inputs received), output_data (the structured response), quality_score (0-100, assigned by Sentinel), validation_flags (array of issues found), timestamp, and processing_time_ms. This structured logging enables performance tracking across agents, identification of which agents produce the highest-quality outputs, and continuous improvement of agent prompts based on quality data.', s_body))

story.append(PageBreak())

# ========================
# CHAPTER 6: MEASUREMENT PROTOCOL
# ========================
story.append(Paragraph('6. Measurement and Feedback Protocol', s_h1))
story.append(sp(4))

story.append(Paragraph(
    'The measurement protocol defines exactly what is measured, how often, by which tool, and what actions are triggered by the results. This is the layer that closes the feedback loop and transforms the ecosystem from a static system into a self-improving machine. Every metric has a defined data source, collection frequency, storage location (Baserow table), threshold for action, and automated response workflow. There is no metric that is tracked without a corresponding action trigger. If a metric is worth measuring, it is worth acting on when it crosses a threshold.', s_body))

story.append(Paragraph('6.1 Measurement Cadence', s_h2))
cadence_data = [
    ['Organic Traffic', 'Google Search Console API', 'Daily (auto-pull)', 'KPI Dashboard', '30-day trend drops > 15%', 'n8n WF-05 + Content Calendar alert'],
    ['Keyword Rankings (Top 50)', 'Ahrefs / SEMrush API', 'Bi-Weekly', 'Keywords Master.SERP Position', 'Position drop > 5 positions', 'n8n WF-03 + optimization task'],
    ['Map Pack Appearance', 'BrightLocal API', 'Weekly', 'KPI Dashboard', 'Drop below 30% for target suburbs', 'n8n WF-05 + GBP optimization task'],
    ['AI Citation Score', 'Manual AI Query (via n8n LLM calls)', 'Monthly', 'SERP/LLM Tracking', 'Score drops below 15%', 'n8n WF-03 + parasite content task'],
    ['Cost Per Lead', 'GHL CRM (leads / ad spend)', 'Monthly', 'KPI Dashboard', 'Increase > 20% from baseline', 'Account manager alert in GHL'],
    ['Review Velocity', 'Google Business Profile API', 'Bi-Weekly', 'KPI Dashboard', 'Below 3 reviews/month', 'n8n WF-07 (review nudge workflow)'],
    ['Competitor Keywords', 'Ahrefs API', 'Monthly', 'Competitor Intelligence', 'New competitor keyword in our cluster', 'n8n WF-04 + content response brief'],
    ['Content Performance', 'GSC + Baserow', 'Monthly (30-day post-publish)', 'Content Calendar', '0 organic impressions after 30 days', 'Content revision task'],
    ['Parasite Impressions', 'Platform Analytics APIs', 'Monthly', 'Parasite Platform Assets', 'Below 1K monthly impressions', 'Platform content refresh task'],
    ['Client Satisfaction', 'GHL (manual or survey)', 'Quarterly', 'Clients table (notes field)', 'NPS score below 7', 'Account manager escalation'],
]
t_cadence = make_table(
    ['Metric', 'Data Source', 'Frequency', 'Stored In', 'Action Threshold', 'Triggered Response'],
    cadence_data,
    col_widths=[65, 72, 55, 60, 72, CONTENT_W - 324]
)
story.append(t_cadence)

story.append(Paragraph('6.2 Weekly Review Protocol', s_h2))
story.append(Paragraph(
    'Every Monday, the system generates an automated Weekly Operations Digest that is sent to all team members via GHL. The digest includes: total keywords in pipeline (by status), content published this week, content due next week, SERP position changes for tracked keywords, new competitor content detected, AI citation mentions gained/lost, and any alerts requiring human attention. This digest is generated by n8n pulling data from Baserow and formatting it through an LLM call that adds narrative context. The review ensures that every team member starts the week with complete operational awareness without manually checking multiple systems.', s_body))

story.append(Paragraph('6.3 Monthly Strategic Review', s_h2))
story.append(Paragraph(
    'On the first Wednesday of every month, a strategic review is conducted that goes beyond operational metrics. This review examines: keyword cluster performance trends (which clusters are gaining/losing authority), content ROI analysis (which content types generate the most business impact), competitor landscape shifts (new entrants, positioning changes), AI citation trajectory (month-over-month growth rate), and client health scores (aggregated NPS and retention indicators). The review is documented in Baserow as a Strategic Review record and drives adjustments to the keyword strategy, content calendar, and resource allocation for the following month. This is the mechanism by which the system adapts and improves over time based on measured outcomes rather than assumptions.', s_body))

story.append(PageBreak())

# ========================
# CHAPTER 7: IMPLEMENTATION SEQUENCE
# ========================
story.append(Paragraph('7. Implementation Sequence', s_h1))
story.append(sp(4))

story.append(Paragraph(
    'The ecosystem must be built in a specific sequence to ensure that each layer functions correctly before the next layer depends on it. Building the n8n workflows before Baserow tables exist would fail. Building the GHL pipeline before the Baserow data model is defined would create orphaned client records. The implementation sequence below ensures that each step creates the prerequisite for the next, minimizing rework and ensuring that the system is functional at every stage.', s_body))

impl_data = [
    ['Phase 1: Foundation', 'Week 1-2', 'Create all 12 Baserow tables with exact field specifications from Chapter 2. Configure all Link to Table relationships. Set up Single Select options for all status/intent/type fields. Create formula fields for auto-calculations. Test with 10 sample keyword records.', 'Baserow is operational with complete schema.'],
    ['Phase 2: Core Workflows', 'Week 3-4', 'Build n8n WF-01 (Keyword Research) and WF-02 (Content Brief Generation) end-to-end. Test with 5 real keywords from the strategy. Verify Baserow records are created correctly. Verify LLM agent calls return valid outputs. Verify Sentinel quality gate works.', 'Keywords can be researched and content briefs generated automatically.'],
    ['Phase 3: Monitoring', 'Week 5-6', 'Build n8n WF-03 (SERP/AI Monitoring) and WF-04 (Competitor Monitoring). Configure weekly schedules. Run first full monitoring cycle across 50 keywords and 7 competitors. Verify tracking data flows into Baserow correctly.', 'System can track rankings, citations, and competitors automatically.'],
    ['Phase 4: Client Delivery', 'Week 7-8', 'Configure GHL pipeline stages (8 stages). Build n8n WF-05 (Client Reporting) and WF-06 (Content Publishing). Set up GHL automation rules (nurture sequences, task creation, round-robin assignment). Test with 1 internal client (VirtuaLab itself).', 'Full client lifecycle from lead to reporting is automated.'],
    ['Phase 5: Integration', 'Week 9-10', 'Build remaining workflows (WF-07 Review Nudge, WF-08 GBP Posts). Connect all bidirectional integrations (Baserow <-> n8n <-> GHL). Run full system test with 5 simulated client scenarios. Fix integration issues.', 'All 8 workflows operational. All 4 layers communicating.'],
    ['Phase 6: Data Population', 'Week 11-12', 'Import all keywords from the strategy document into Baserow. Enter all 7 competitors. Create parasite platform asset records. Set up team member records. Initialize KPI baselines for first client.', 'System is fully populated with real data and ready for production use.'],
    ['Phase 7: Go-Live', 'Week 13+', 'Begin operating the system for real client delivery. Monitor for 4 weeks. Collect feedback from team. Iterate on workflows, agent prompts, and dashboard configurations based on actual usage patterns.', 'System is production-ready and self-improving.'],
]
t_impl = make_table(
    ['Phase', 'Timeline', 'Actions', 'Success Criteria'],
    impl_data,
    col_widths=[65, 50, CONTENT_W - 170, 55]
)
story.append(t_impl)

story.append(Paragraph('7.1 System Dependencies Map', s_h2))
dep_data = [
    ['Baserow Tables', 'None', 'Everything else depends on data structures being defined first.'],
    ['n8n Workflows', 'Baserow Tables', 'Workflows read from and write to Baserow. Cannot function without tables.'],
    ['AI Agent Prompts', 'Baserow schema + Strategy Doc', 'Agent prompts reference exact field names and table structures.'],
    ['GHL Pipeline', 'Baserow Clients table', 'GHL pipeline creates records that sync back to Baserow.'],
    ['GHL Automations', 'GHL Pipeline stages', 'Automation rules trigger based on pipeline stage changes.'],
    ['n8n-GHL Integration', 'Both n8n and GHL configured', 'Bidirectional sync requires both systems operational.'],
    ['Client Reporting', 'All above', 'Reports pull from Baserow, format via n8n, deliver via GHL.'],
    ['Measurement Protocol', 'Baserow KPI Dashboard + n8n', 'Threshold alerts require Baserow data and n8n trigger logic.'],
]
t_dep = make_table(
    ['Component', 'Depends On', 'Rationale'],
    dep_data,
    col_widths=[90, 110, CONTENT_W - 200]
)
story.append(t_dep)

# ========================
# BUILD
# ========================
doc.build(story)
print(f'PDF generated successfully: {output_path}')
print(f'Pages: {doc.page}')
