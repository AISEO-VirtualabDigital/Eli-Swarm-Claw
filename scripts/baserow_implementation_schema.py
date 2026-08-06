#!/usr/bin/env python3
"""
VirtuaLab Digital — Baserow Implementation Schema
Field-by-field database specifications for the systematic ecosystem.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

FONT_DIR = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('LibSans', f'{FONT_DIR}/truetype/liberation/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LibSans-Bold', f'{FONT_DIR}/truetype/liberation/LiberationSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LibSans-Italic', f'{FONT_DIR}/truetype/liberation/LiberationSans-Italic.ttf'))
registerFontFamily('LibSans', normal='LibSans', bold='LibSans-Bold', italic='LibSans-Italic')

# Palette
TABLE_STRIPE = HexColor('#f0f2f4')
HEADER_FILL  = HexColor('#1a2e3b')
ACCENT       = HexColor('#2e7fa7')
TEXT_P       = HexColor('#222526')
TEXT_M       = HexColor('#71787b')
BORDER       = HexColor('#bacbd3')
WHITE        = HexColor('#ffffff')
DARK_H       = HexColor('#0f1c26')
MID_H        = HexColor('#2a4758')
LIGHT_BG     = HexColor('#eef3f6')
TAG_BG       = HexColor('#d4e8f2')

PAGE_W, PAGE_H = A4
LEFT_M = 18*mm
RIGHT_M = 18*mm
TOP_M = 20*mm
BOT_M = 20*mm
CW = PAGE_W - LEFT_M - RIGHT_M

# Styles
s_h1 = ParagraphStyle('H1', fontName='LibSans-Bold', fontSize=18, leading=24, textColor=DARK_H, spaceAfter=8, spaceBefore=14)
s_h2 = ParagraphStyle('H2', fontName='LibSans-Bold', fontSize=14, leading=19, textColor=ACCENT, spaceAfter=6, spaceBefore=12)
s_h3 = ParagraphStyle('H3', fontName='LibSans-Bold', fontSize=11, leading=15, textColor=MID_H, spaceAfter=4, spaceBefore=8)
s_body = ParagraphStyle('Body', fontName='LibSans', fontSize=9, leading=13, textColor=TEXT_P, alignment=TA_JUSTIFY, spaceAfter=4)
s_th = ParagraphStyle('TH', fontName='LibSans-Bold', fontSize=7.5, leading=10, textColor=WHITE, alignment=TA_CENTER)
s_td = ParagraphStyle('TD', fontName='LibSans', fontSize=7, leading=10, textColor=TEXT_P)
s_td_c = ParagraphStyle('TDC', parent=s_td, alignment=TA_CENTER)
s_tag = ParagraphStyle('Tag', fontName='LibSans-Bold', fontSize=6.5, leading=9, textColor=ACCENT, backColor=TAG_BG, spaceBefore=2, spaceAfter=2, borderPadding=3)
s_cap = ParagraphStyle('Cap', fontName='LibSans-Italic', fontSize=7.5, leading=10, textColor=TEXT_M)
s_callout = ParagraphStyle('Callout', fontName='LibSans', fontSize=8.5, leading=12, textColor=HEADER_FILL, backColor=LIGHT_BG, spaceBefore=4, spaceAfter=4, leftIndent=6, rightIndent=6, borderPadding=6)

def mt(headers, rows, cw=None):
    if not cw:
        cw = [CW / len(headers)] * len(headers)
    hdr = [Paragraph(h, s_th) for h in headers]
    data = [hdr]
    for row in rows:
        data.append([Paragraph(str(c), s_td) if i == 0 else Paragraph(str(c), s_td_c) if len(str(c)) < 30 else Paragraph(str(c), s_td) for i, c in enumerate(row)])
    t = Table(data, colWidths=cw, repeatRows=1)
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_FILL),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_STRIPE))
    t.setStyle(TableStyle(cmds))
    return t

def hr(): return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=8, spaceBefore=8)

def p(t): return Paragraph(t, s_body)
def h1(t): return Paragraph(t, s_h1)
def h2(t): return Paragraph(t, s_h2)
def h3(t): return Paragraph(t, s_h3)
def cap(t): return Paragraph(t, s_cap)
def sp(h=4): return Spacer(1, h)

def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('LibSans', 7)
    canvas.setFillColor(TEXT_M)
    canvas.drawRightString(PAGE_W - LEFT_M, 12*mm, f'{doc.page}')
    canvas.drawString(LEFT_M, 12*mm, 'VirtuaLab Digital | Baserow Implementation Schema')
    canvas.restoreState()

# ── Build Story ──
story = []

# ══════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════
story.append(Spacer(1, 140))
story.append(Paragraph('BASEROW IMPLEMENTATION SCHEMA', ParagraphStyle('CT', fontName='LibSans-Bold', fontSize=10, leading=13, textColor=HexColor('#5a8a9f'), letterSpacing=3)))
story.append(Spacer(1, 12))
story.append(Paragraph('VirtuaLab Digital', ParagraphStyle('T', fontName='LibSans-Bold', fontSize=36, leading=42, textColor=DARK_H)))
story.append(Spacer(1, 8))
story.append(Paragraph('Database Field Specifications for the Systematic Ecosystem', ParagraphStyle('ST', fontName='LibSans', fontSize=14, leading=20, textColor=MID_H)))
story.append(Spacer(1, 30))
story.append(HRFlowable(width="40%", thickness=2, color=ACCENT, spaceAfter=20, spaceBefore=0))
story.append(Paragraph('AISEO Framework | 40+ Tables | 7 Domains | n8n + GHL Integration Ready', ParagraphStyle('Meta', fontName='LibSans', fontSize=10, leading=14, textColor=TEXT_M)))
story.append(Spacer(1, 60))
story.append(Paragraph('Prepared by: Asymmetric SEO Strategist & Parasite SEO Strategist | August 2026 | Version 1.0', ParagraphStyle('Foot', fontName='LibSans', fontSize=8, leading=12, textColor=TEXT_M)))
story.append(Paragraph('Classification: Internal Operations | Systematic Approach Foundation', ParagraphStyle('Foot', fontName='LibSans', fontSize=8, leading=12, textColor=TEXT_M)))
story.append(PageBreak())

# ══════════════════════════════════════════════════
# TOC
# ══════════════════════════════════════════════════
story.append(h1('Table of Contents'))
story.append(sp(8))
toc = [
    ('1', 'Schema Overview & Design Principles'),
    ('2', 'Domain 1: Master Data (5 tables)'),
    ('3', 'Domain 2: Client & Campaign Management (6 tables)'),
    ('4', 'Domain 3: Content Operations (7 tables)'),
    ('5', 'Domain 4: Off-Page & Parasite SEO (6 tables)'),
    ('6', 'Domain 5: Technical SEO & Indexing (5 tables)'),
    ('7', 'Domain 6: GEO & AI Citation Tracking (5 tables)'),
    ('8', 'Domain 7: Reporting & Analytics (4 tables)'),
    ('9', 'Pre-Populated Data: Keywords, Competitors, ICPs'),
    ('10', 'n8n Workflow Trigger Specifications'),
    ('11', 'GHL Pipeline Configuration'),
]
for num, title in toc:
    story.append(Paragraph(f'<b>{num}.</b>  {title}', ParagraphStyle('TOC', fontName='LibSans', fontSize=10, leading=16, textColor=TEXT_P, leftIndent=0 if '.' in num and num.strip()[-1].isdigit() and '.' not in num.strip()[:-1] else 15)))
story.append(PageBreak())

# ══════════════════════════════════════════════════
# CHAPTER 1: SCHEMA OVERVIEW
# ══════════════════════════════════════════════════
story.append(h1('1. Schema Overview & Design Principles'))
story.append(p(
    'This document provides the complete field-level specification for every Baserow table in the VirtuaLab Digital systematic ecosystem. Each table definition includes the exact field names, Baserow field types, configuration options, default values, validation rules, and the n8n workflows that read from or write to it. The schema is designed to be directly implementable: a Baserow user can create every table by following these specifications without additional design decisions. This eliminates the primary source of operational inconsistency across client engagements, ensuring that every keyword cluster, every competitor analysis, and every content brief follows the same structured format.'
))
story.append(p(
    'The schema is organized into seven functional domains. Master Data tables store brand configuration, competitor intelligence, and reusable ICP templates that persist across all engagements. Client and Campaign Management tables track each client relationship from onboarding through monthly reporting. Content Operations tables manage the full lifecycle from keyword seed to published and reviewed content. Off-Page and Parasite SEO tables systematize platform scoring, content distribution, and backlink monitoring. Technical SEO and Indexing tables store audit results, schema deployments, and crawl issue tracking. GEO and AI Citation Tracking tables implement the citation probing, trend analysis, and recommendation system described in the strategic blueprint. Reporting and Analytics tables aggregate data from all other domains for monthly client deliverables.'
))
story.append(sp(4))
story.append(h2('1.1 Design Principles'))
story.append(p('<b>Principle 1 — Single Source of Truth:</b> Every piece of strategic data exists in exactly one Baserow table and one field. No data is duplicated across tables unless explicitly linked via Baserow Link-to-Table fields. This prevents the synchronization problems that plagued the previous document-based approach, where the same competitor name or keyword might appear in three different Google Doc tabs with slightly different spellings or metrics. When a keyword volume is updated in the keywords table, every view, filter, and report that references that keyword sees the updated value immediately.'))
story.append(p('<b>Principle 2 — Workflow-Readable Structure:</b> Every table is designed so that n8n workflows can read from and write to it using the Baserow API without complex data transformation. Field names use snake_case conventions. Select options use human-readable labels that match the exact strings used in n8n workflow conditions. Date fields use ISO 8601 format (YYYY-MM-DD). This eliminates the need for n8n Set nodes that translate between display labels and stored values, reducing workflow complexity and failure points.'))
story.append(p('<b>Principle 3 — Audit Trail via Status Fields:</b> Every operational table includes a status field with predefined options that correspond to n8n workflow stages. When a keyword research job transitions from "pending" to "in_progress" to "completed", the n8n workflow updates this single field. Any record stuck in a non-terminal status for more than a defined threshold triggers an escalation to the quality_audit_log table. This replaces the previous approach where task completion was tracked only in the operators memory or scattered across email threads and Slack messages.'))
story.append(sp(4))
story.append(h2('1.2 Baserow Field Type Reference'))
story.append(mt(
    ['Baserow Type', 'Used For', 'Example in This Schema'],
    [
        ('Text (single line)', 'Names, URLs, short identifiers', 'Competitor domain, keyword string'),
        ('Long Text', 'Descriptions, briefs, JSON payloads', 'Content brief body, SERP analysis notes'),
        ('Number (integer)', 'Counts, IDs, scores (0-100)', 'Search volume, difficulty, citation count'),
        ('Number (decimal)', 'Percentages, ratios, monetary values', 'CTR, conversion rate, budget allocation'),
        ('Select (single)', 'Status fields, category choices', 'Intent (info/nav/commercial/transactional)'),
        ('Select (multiple)', 'Multi-category tagging', 'Vertical tags, tool types used'),
        ('Date', 'Timestamps, deadlines', 'Publish date, audit date, contract end'),
        ('Created On / Last Modified', 'Auto-tracked timestamps', 'Every table includes these system fields'),
        ('Link to Table', 'Foreign key relationships', 'Client ID on every client-scoped table'),
        ('Formula', 'Computed values', 'Days since last audit, ROI calculation'),
        ('Rollup', 'Aggregated counts from linked tables', 'Total keywords per cluster, total content per client'),
        ('Lookup', 'Display linked field values', 'Client name (looked up from client ID)'),
        ('File', 'Uploaded documents', 'SERP screenshot, audit PDF export'),
        ('Boolean (Checkbox)', 'Yes/No flags', 'Is priority, index status, TOS compliant'),
    ],
    [75, 120, 265]
))
story.append(cap('Table 1.1: Baserow Field Type Mapping'))
story.append(PageBreak())

# ══════════════════════════════════════════════════
# CHAPTER 2: MASTER DATA
# ══════════════════════════════════════════════════
story.append(h1('2. Domain 1: Master Data'))
story.append(p('Master Data tables store persistent, cross-engagement configuration that does not change with individual clients. These tables are populated once during initial system setup and updated only when the VirtuaLab Digital brand, competitive landscape, or service offerings change. All other tables reference Master Data through Link-to-Table relationships, ensuring that a single update to brand_settings propagates consistently across every content brief, client report, and automated workflow.'))

story.append(h2('2.1 brand_settings'))
story.append(p('This is a singleton table (exactly one row) that stores the VirtuaLab Digital brand identity, positioning rules, and content standards that govern all output. Every content brief, every client-facing report, and every automated email template references this table for brand voice, allowed claims, and prohibited language. The n8n Content Production Pipeline reads the brand_voice_rules and claims_to_avoid fields before generating any client-facing content, ensuring that no output violates the established brand standards.'))
story.append(mt(
    ['Field Name', 'Type', 'Config / Options', 'Default', 'Notes'],
    [
        ('brand_name', 'Text', 'Max length: 100', 'VirtuaLab Digital', 'Used in all report headers and email signatures'),
        ('tagline', 'Text', 'Max length: 200', 'The SEO AI Scientist', 'Used in homepage hero and meta descriptions'),
        ('positioning_statement', 'Long Text', '-', '', 'Core brand positioning narrative (2-3 paragraphs)'),
        ('target_markets', 'Select (multiple)', 'US Suburban Local Services, US Healthcare, US Education, US Real Estate, US E-Commerce', 'US Suburban Local Services', 'Defines which ICP templates are active'),
        ('primary_verticals', 'Select (multiple)', 'HVAC, Plumbing, Roofing, Electrical, General Contractors, Landscaping, Pest Control, Moving Services', 'HVAC, Plumbing, Roofing', 'Ordered by current revenue contribution'),
        ('brand_voice_rules', 'Long Text', '-', '', 'Tone guidelines, reading level (8th-10th grade), prohibited words'),
        ('claims_allowed', 'Long Text', '-', '', 'Specific data-backed claims that may be used in content'),
        ('claims_to_avoid', 'Long Text', '-', '', 'See extraction data: no guaranteed rankings, no superlatives without evidence'),
        ('content_standards', 'Long Text', '-', '', 'BLUF format, min 3 stats/1000 words, min 2 quotes, min 3 external refs, FAQ schema for 3+ questions'),
        ('schema_types_used', 'Select (multiple)', 'LocalBusiness, Service, FAQPage, Organization, WebSite, BreadcrumbList, Person, OfferCatalog', 'All listed', 'Nested schema configuration reference'),
        ('robots_txt_ai_crawlers', 'Long Text', '-', '', 'Pre-configured GPTBot, PerplexityBot, Google-Extended rules'),
        ('free_tools_enabled', 'Select (multiple)', 'Local Marketing ROI Calculator, Local Proximity Visualizer, Lead Prioritization Matrix', 'All listed', 'Which lead-gen tools are active on the website'),
        ('updated_at', 'Last Modified', 'Auto', 'Auto', 'Track when brand settings were last changed'),
    ],
    [80, 65, 120, 60, 135]
))
story.append(cap('Table 2.1: brand_settings — Singleton brand configuration'))
story.append(sp(6))

story.append(h2('2.2 competitor_registry'))
story.append(p('This growing table stores every identified competitor with their classification, strengths, weaknesses, and strategic gaps. The data is sourced from the competitive analysis in the AISEO Framework and supplemented by ongoing monitoring. The n8n Client Onboarding Pipeline reads this table to populate the initial competitor benchmarking for new clients. The competitor_agent in Eli-OS queries this table to identify cross-client competitive patterns. Each competitor entry is tagged with its type (national full-service, niche specialist, or boutique advisory) to enable filtered views that match the current engagement scope.'))
story.append(mt(
    ['Field Name', 'Type', 'Config / Options', 'Default', 'Notes'],
    [
        ('competitor_name', 'Text', 'Max: 200', '', 'Company or brand name'),
        ('domain', 'Text (URL)', '-', '', 'Primary domain (https://)'),
        ('competitor_type', 'Select (single)', 'National Full-Service, Niche Specialist, Boutique Advisory, Platform/Proprietary, YouTube/Content Creator', 'Niche Specialist', 'Classification from AISEO Framework'),
        ('primary_verticals', 'Select (multiple)', 'HVAC, Plumbing, Roofing, Electrical, General Contractors, Pest Control, Healthcare, Legal, Real Estate, E-Commerce', '', 'Which verticals they serve'),
        ('pricing_model', 'Text', 'Max: 300', '', 'e.g. "Starting at $2,800/mo, $1M+ revenue minimum" (Hook Agency)'),
        ('key_strengths', 'Long Text', '-', '', 'From extraction: transparent pricing, live dashboards, trade specialty, high visual appeal'),
        ('key_weaknesses', 'Long Text', '-', '', 'From extraction: no GEO education, no un-gated content, enterprise-only focus'),
        ('strategic_gaps', 'Long Text', '-', '', 'Exploitable deficiencies: no AI readiness, no CRM integration, no local suburb content'),
        ('our_counter_strategy', 'Long Text', '-', '', 'How VirtuaLab should position against this competitor'),
        ('min_revenue_threshold', 'Text', 'Max: 100', '', 'If they require minimum revenue (e.g. $1M for Hook Agency)'),
        ('contract_requirements', 'Text', 'Max: 200', '', 'e.g. "12-month contract lock"'),
        ('da_score', 'Number (integer)', '0-100', '', 'Domain Authority, updated monthly'),
        ('visible_keywords_count', 'Number (integer)', '0+', '', 'Number of keywords they rank for (from SEMrush/Ahrefs)'),
        ('status', 'Select (single)', 'Active, Inactive, Acquired, Rebranded', 'Active', 'Lifecycle status'),
        ('last_analyzed', 'Date', '-', '', 'Date of most recent competitive analysis'),
    ],
    [80, 55, 115, 50, 160]
))
story.append(cap('Table 2.2: competitor_registry — Pre-populated with 7 competitors from extraction'))

story.append(h2('2.3 icp_templates'))
story.append(p('This table stores the three segmented Ideal Customer Profile archetypes (Operator, Practitioner, Institution) defined in the AISEO Framework. Each ICP template contains the complete psychographic, demographic, and behavioral profile that the n8n Content Production Pipeline uses to tailor content briefs. When a new client is onboarded, the system matches the client to the closest ICP archetype and creates a client-specific profile in client_icp_profiles that inherits all fields from the matched template. This ensures that content for a plumbing company in Dallas follows the same structural and tonal guidelines as content for an HVAC company in Atlanta, while allowing for client-specific overrides.'))
story.append(mt(
    ['Field Name', 'Type', 'Config / Options', 'Notes'],
    [
        ('icp_name', 'Text', 'Max: 100', 'e.g. "The Operator", "The Practitioner", "The Institution"'),
        ('vertical', 'Select (multiple)', 'HVAC, Plumbing, Roofing, Electrical, General Contractors, Landscaping, Dentistry, Physical Therapy, Law Firms, Real Estate, Private Schools, Sports Facilities', 'Primary verticals for this ICP'),
        ('business_size_range', 'Text', 'Max: 100', 'e.g. "1-25 employees" or "20-100+ administrative staff"'),
        ('annual_revenue_range', 'Text', 'Max: 100', 'e.g. "$500K-$5M (sweet spot: $1M-$10M)"'),
        ('service_area_type', 'Select (single)', 'Hyper-local Suburban, Multi-city Regional, Fixed Physical Clinic, District/County Regional', 'Defines content localization strategy'),
        ('digital_maturity', 'Select (single)', 'Very Low, Low, Moderate, High, Very High', 'Determines depth of technical recommendations'),
        ('ad_dependency_level', 'Select (single)', 'Very High (LSA+Ads+Aggregators), High (Google Ads+LSA), Moderate (Search+Social), Low (Community+Referral), Very Low (Organic Only)', 'Drives messaging about owned vs rented assets'),
        ('seo_maturity', 'Select (single)', 'None (Zero Visibility), Low (Thin Pages), Moderate (Fragmented), High (Optimized but Stagnant)', 'Determines starting point for strategy'),
        ('gbp_maturity', 'Select (single)', 'Unmanaged, Basic Setup, Moderate Visibility, High Prominence', 'Determines GBP audit intensity'),
        ('website_quality', 'Select (single)', 'Legacy/Unresponsive, Templated/Basic, Clean/Low Depth, Custom/High Quality', 'Determines technical audit scope'),
        ('tracking_maturity', 'Select (single)', 'None, Basic (Call Counts), Moderate (CRM Integration), Advanced (Full Attribution)', 'Determines GHL integration complexity'),
        ('primary_pain_points', 'Long Text', '-', 'From extraction: Lead Aggregator Fatigue, Ad Budget Volatility, Maps Invisibility, Reporting Confusion, Page 2 Syndrome, Leaky Lead Capture'),
        ('decision_speed', 'Select (single)', 'Very Slow (6+ months), Slow (3-6 months), Moderate (1-3 months), Fast (Under 1 month)', 'Determines nurture sequence length'),
        ('risk_tolerance', 'Select (single)', 'Very Low, Low, Moderate, High', 'Frames messaging: "long-term risk reduction" for low tolerance'),
        ('messaging_angle', 'Text', 'Max: 300', 'Primary value proposition angle for this ICP'),
        ('best_cta', 'Text', 'Max: 200', 'e.g. "Request a Local Visibility Diagnostic Audit (Delivered in 48 Hours)"'),
        ('current_ad_spend_range', 'Text', 'Max: 100', 'e.g. "$2,000-$10,000/month"'),
        ('typical_cac_range', 'Text', 'Max: 100', 'Customer acquisition cost range'),
        ('status', 'Select (single)', 'Active, Draft, Archived', 'Active', ''),
    ],
    [80, 80, 140, 160]
))
story.append(cap('Table 2.3: icp_templates — 3 pre-populated archetypes from AISEO Framework'))

story.append(h2('2.4 team_members'))
story.append(mt(
    ['Field Name', 'Type', 'Config / Options', 'Notes'],
    [
        ('name', 'Text', 'Max: 100', 'Team member name'),
        ('role', 'Select (single)', 'SEO Strategist, Content Writer, Technical SEO, Web Developer, Project Manager, Sales/Account Manager', 'Primary role'),
        ('specializations', 'Select (multiple)', 'Local SEO, Technical SEO, Content Strategy, GEO/AEO, Parasite SEO, GHL/CRM, Web Design, Video/YouTube', 'Skill areas'),
        ('agent_assignments', 'Select (multiple)', 'keyword_agent, technical_seo, on_page_seo, entity_agent, competitor_agent, local_seo, parasite_seo, geo_agent, ai_citation, indexing_agent, qa_agent, report_agent', 'Which Eli-OS agents this human oversees'),
        ('capacity_allocation', 'Select (single)', 'Full (40h/week), Three-Quarter (30h), Half (20h), Quarter (10h)', 'Available capacity for new work'),
        ('email', 'Text (Email)', '-', 'For automated notifications'),
        ('status', 'Select (single)', 'Active, On Leave, Inactive', 'Active'),
    ],
    [80, 80, 120, 170]
))
story.append(cap('Table 2.4: team_members'))

story.append(h2('2.5 tech_stack'))
story.append(mt(
    ['Field Name', 'Type', 'Config / Options', 'Notes'],
    [
        ('tool_name', 'Text', 'Max: 100', 'Display name'),
        ('category', 'Select (single)', 'SEO Tool, CMS, CRM, Automation, AI Platform, Analytics, Crawler, Schema, Communication', 'Functional category'),
        ('api_available', 'Boolean', '', 'Whether API access is configured'),
        ('api_key_reference', 'Text', 'Max: 200', 'Reference to stored key (never store actual keys in Baserow)'),
        ('integration_status', 'Select (single)', 'Not Started, In Progress, Active, Broken', 'Current connection status'),
        ('n8n_node_type', 'Text', 'Max: 100', 'e.g. "HTTP Request", "Baserow", "GoHighLevel"'),
        ('used_by_workflows', 'Select (multiple)', 'WF-01 through WF-06', 'Which workflows use this tool'),
    ],
    [80, 70, 100, 60, 150]
))
story.append(cap('Table 2.5: tech_stack'))
story.append(PageBreak())

# ══════════════════════════════════════════════════
# CHAPTER 3: CLIENT & CAMPAIGN
# ══════════════════════════════════════════════════
story.append(h1('3. Domain 2: Client & Campaign Management'))
story.append(p('Client and Campaign Management tables form the operational backbone of every engagement. These tables are created and populated by the n8n Client Onboarding Pipeline (WF-01) when a new client record is created in Baserow. Each subsequent workflow reads from and writes to these tables, creating a complete audit trail from initial contact through monthly reporting. The Link-to-Table relationships between these tables and the Content Operations, Off-Page, Technical SEO, and GEO tables ensure that every piece of data can be traced back to the specific client and campaign it serves.'))

story.append(h2('3.1 clients'))
story.append(mt(
    ['Field Name', 'Type', 'Config / Options', 'Notes'],
    [
        ('client_name', 'Text', 'Max: 200', 'Business name'),
        ('contact_name', 'Text', 'Max: 100', 'Primary contact person'),
        ('email', 'Text (Email)', '-', 'Contact email (used for GHL sync)'),
        ('phone', 'Text (Phone)', '-', 'Contact phone (used for GHL sync)'),
        ('website_url', 'Text (URL)', '-', 'Client website to audit'),
        ('industry_vertical', 'Link to Table (icp_templates)', '', 'Links to ICP archetype for inheritance'),
        ('service_area', 'Text', 'Max: 500', 'Cities, zip codes, radius descriptions'),
        ('contract_start', 'Date', '-', 'Service start date'),
        ('contract_end', 'Date', '-', 'Service end date'),
        ('ghl_contact_id', 'Text', 'Max: 50', 'GoHighLevel contact ID for API sync'),
        ('ghl_pipeline_id', 'Text', 'Max: 50', 'GHL sales pipeline ID'),
        ('assigned_team_lead', 'Link to Table (team_members)', '', 'Primary responsible team member'),
        ('onboarding_status', 'Select (single)', 'Not Started, Diagnostic Running, Strategy Formation, Active, Churned', 'Lifecycle stage'),
        ('icp_archetype', 'Select (single)', 'A: The Operator, B: The Practitioner, C: The Institution', 'Auto-matched from industry_vertical'),
        ('notes', 'Long Text', '-', 'Internal team notes'),
    ],
    [80, 70, 110, 60, 140]
))
story.append(cap('Table 3.1: clients — Created by GHL webhook or manual entry'))

story.append(h2('3.2 client_icp_profiles'))
story.append(mt(
    ['Field Name', 'Type', 'Config / Options', 'Notes'],
    [
        ('client', 'Link to Table (clients)', '', 'Foreign key to clients table'),
        ('icp_archetype', 'Link to Table (icp_templates)', '', 'Inherited template'),
        ('verified_pain_points', 'Long Text', '-', 'Client-confirmed pain points from discovery call'),
        ('digital_maturity_score', 'Number (integer)', '0-100', 'Composite score from technical audit'),
        ('ad_dependency_score', 'Number (integer)', '0-100', 'Percentage of leads from paid sources'),
        ('current_monthly_ad_spend', 'Number (decimal)', '$0.00', 'Current verified ad spend per month'),
        ('current_monthly_leads', 'Number (integer)', '0', 'Current verified inbound leads per month'),
        ('current_cac', 'Number (decimal)', '$0.00', 'Current customer acquisition cost'),
        ('target_cac', 'Number (decimal)', '$0.00', 'Target CAC after SEO implementation'),
        ('competitor_names', 'Long Text', '-', 'Top 3-5 competitors named by client'),
        ('buyer_triggers', 'Long Text', '-', 'Events that trigger buying intent (CPC spike, lost deal, etc.)'),
        ('objections', 'Long Text', '-', 'Common objections heard during sales process'),
        ('custom_messaging_notes', 'Long Text', '-', 'Client-specific messaging adjustments'),
    ],
    [80, 70, 110, 60, 140]
))
story.append(cap('Table 3.2: client_icp_profiles — Per-client ICP overrides'))

story.append(h2('3.3 campaigns, campaign_goals, gbp_profiles, service_area_targets'))
story.append(p('The campaigns table tracks each active engagement type (SEO, Local, GEO, Parasite) with its budget allocation and timeline. The campaign_goals table breaks each campaign into measurable targets (organic sessions, map pack impressions, calls tracked, leads generated, revenue attributed) with current values that the n8n Client Reporting Pipeline aggregates monthly. The gbp_profiles table stores Google Business Profile data including NAP consistency scores, review counts and ratings, and last audit dates. The service_area_targets table defines the geographic priority matrix that drives content localization decisions. Together, these four tables provide the complete engagement management layer.'))

# Compact multi-table view
for tbl_name, tbl_data in [
    ('campaigns', [
        ('campaign_name', 'Text', 'Max: 200', 'e.g. "Dallas Plumber SEO Q3 2026"'),
        ('client', 'Link to Table (clients)', '', 'FK to clients'),
        ('campaign_type', 'Select (single)', 'Organic SEO, Local SEO, GEO/AEO, Parasite SEO, Full Service', 'Primary focus'),
        ('start_date', 'Date', '-', 'Campaign start'),
        ('end_date', 'Date', '-', 'Campaign end (blank = ongoing)'),
        ('status', 'Select (single)', 'Planning, Active, Paused, Completed', 'Active'),
        ('budget_monthly', 'Number (decimal)', '$0.00', 'Monthly budget allocation'),
        ('assigned_agents', 'Select (multiple)', 'keyword_agent, technical_seo, competitor_agent, geo_agent, parasite_seo, local_seo', 'Which Eli-OS agents are assigned'),
    ]),
    ('campaign_goals', [
        ('campaign', 'Link to Table (campaigns)', '', 'FK to campaigns'),
        ('metric', 'Select (single)', 'Organic Sessions, Map Pack Impressions, Map Pack Clicks, Calls Tracked, Leads Generated, Revenue Attributed, AI Citation Rate, Keyword Rankings (Top 10), Keyword Rankings (Top 3)', 'KPI to track'),
        ('target_value', 'Number (decimal)', '0', 'Target value for period end'),
        ('current_value', 'Number (decimal)', '0', 'Latest measured value'),
        ('baseline_value', 'Number (decimal)', '0', 'Value at campaign start'),
        ('unit', 'Select (single)', 'Count, Percentage, Currency ($)', 'Unit for display in reports'),
        ('deadline', 'Date', '-', 'Target achievement date'),
        ('measurement_source', 'Text', 'Max: 200', 'e.g. "GHL CRM", "Google Search Console", "Manual AI probe"'),
    ]),
    ('gbp_profiles', [
        ('client', 'Link to Table (clients)', '', 'FK to clients'),
        ('gbp_id', 'Text', 'Max: 100', 'Google Business Profile ID'),
        ('primary_category', 'Text', 'Max: 100', 'e.g. "HVAC Contractor"'),
        ('secondary_categories', 'Select (multiple)', 'Air Conditioning, Heating, Duct Cleaning, Ventilation, Emergency Services', 'Additional GBP categories'),
        ('business_name', 'Text', 'Max: 200', 'GBP display name'),
        ('address', 'Text', 'Max: 300', 'Street address'),
        ('city', 'Text', 'Max: 100', 'City'),
        ('state', 'Text', 'Max: 50', 'State'),
        ('zip_code', 'Text', 'Max: 20', 'ZIP code'),
        ('phone', 'Text (Phone)', '-', 'GBP phone number'),
        ('website_url', 'Text (URL)', '-', 'GBP linked website'),
        ('nap_consistency_score', 'Number (integer)', '0-100', 'NAP consistency across directories (from Whitespark audit)'),
        ('review_count', 'Number (integer)', '0', 'Total Google reviews'),
        ('avg_rating', 'Number (decimal)', '0.0-5.0', 'Average Google rating'),
        ('last_audit_date', 'Date', '-', 'Most recent GBP audit'),
    ]),
    ('service_area_targets', [
        ('client', 'Link to Table (clients)', '', 'FK to clients'),
        ('city', 'Text', 'Max: 100', 'Target city'),
        ('state', 'Text', 'Max: 50', 'State'),
        ('zip_codes', 'Text', 'Max: 500', 'Comma-separated ZIP codes'),
        ('priority_tier', 'Select (single)', 'Tier 1 (Core Market), Tier 2 (Expansion), Tier 3 (Opportunistic)', 'Content investment priority'),
        ('assigned_content_cluster', 'Link to Table (keyword_clusters)', '', 'Which keyword cluster serves this area'),
        ('population_estimate', 'Number (integer)', '0', 'Approximate population for opportunity sizing'),
        ('competitor_density', 'Select (single)', 'Low, Medium, High', 'Number of competitors in local pack'),
        ('status', 'Select (single)', 'Not Started, Content Drafted, Published, Optimized', 'Content deployment status'),
    ]),
]:
    story.append(sp(4))
    story.append(h3(f'Table 3.3.{tbl_name}'))
    rows = [(r[0], r[1], r[2], r[3]) for r in tbl_data]
    story.append(mt(
        ['Field Name', 'Type', 'Config / Options', 'Notes'],
        rows,
        [80, 70, 130, 60, 150] if 'Select' not in str(tbl_data) else [80, 70, 130, 60, 150]
    ))

story.append(PageBreak())

# ══════════════════════════════════════════════════
# CHAPTERS 4-8: REMAINING DOMAINS
# ══════════════════════════════════════════════════
remaining_domains = [
    ('4. Content Operations', [
        ('keyword_research_jobs', [('client', 'Link to Table (clients)', '', 'FK to clients'), ('seed_keywords', 'Long Text', '-', 'Comma-separated seed keyword list'), ('analysis_type', 'Select (single)', 'Initial Research, Expansion, Gap Analysis, Competitor Gap', 'Type of research to perform'), ('status', 'Select (single)', 'Pending, In Progress, Completed, Failed', 'Workflow stage'), ('assigned_agent', 'Select (single)', 'keyword_agent', 'Eli-OS agent that processes this job'), ('created_date', 'Created On', 'Auto', ''), ('completed_date', 'Date', '-', ''), ('result_summary', 'Long Text', '-', 'Agent output summary'), ('keywords_found_count', 'Number (integer)', '0', 'Total keywords discovered')]),
        ('keywords', [('keyword', 'Text', 'Max: 200', 'Keyword string'), ('search_volume', 'Number (integer)', '0', 'Monthly search volume (from SEMrush/Ahrefs)'), ('difficulty', 'Number (integer)', '0-100', 'Keyword difficulty score'), ('intent', 'Select (single)', 'Informational, Navigational, Commercial, Transactional', 'Search intent classification'), ('cluster', 'Link to Table (keyword_clusters)', '', 'FK to keyword_clusters'), ('cpc', 'Number (decimal)', '$0.00', 'Cost per click'), ('serp_features', 'Select (multiple)', 'Featured Snippet, Local Pack, People Also Ask, Knowledge Panel, Image Pack, Video Pack, AI Overview', 'Which SERP features appear'), ('current_ranking_url', 'Text (URL)', '-', 'URL currently ranking (if any)'), ('current_position', 'Number (integer)', '0', 'Current organic position (0 = not ranking)'), ('target_page', 'Text (URL)', '-', 'Page that should rank for this keyword'), ('priority', 'Select (single)', 'Critical, High, Medium, Low', 'Content production priority'), ('status', 'Select (single)', 'Unassigned, In Brief, In Draft, Published, Not Targeting', 'Lifecycle status')]),
        ('keyword_clusters', [('cluster_label', 'Text', 'Max: 300', 'Descriptive cluster name'), ('client', 'Link to Table (clients)', '', 'FK to clients'), ('primary_keyword', 'Link to Table (keywords)', '', 'Primary keyword for this cluster'), ('keyword_count', 'Formula', 'count(link(keywords.cluster))', 'Auto-count of linked keywords'), ('total_volume', 'Formula', 'sum(keywords.search_volume)', 'Auto-sum of search volumes'), ('target_page_url', 'Text (URL)', '-', 'Page that should rank for this cluster'), ('content_status', 'Select (single)', 'No Content, Brief Created, Draft Written, In Review, Published', 'Content production stage'), ('priority', 'Select (single)', 'Critical, High, Medium, Low', 'Cluster priority based on total volume and business potential'), ('word_count_target', 'Number (integer)', '0', 'Recommended content length from SERP analysis'), ('assigned_writer', 'Link to Table (team_members)', '', 'Content writer assigned'), ('h_tag_structure', 'Long Text', '-', 'Recommended H2/H3 structure from SEO brief'), ('schema_requirements', 'Select (multiple)', 'FAQPage, LocalBusiness, Service, HowTo, Organization', 'Required schema types for the target page'), ('bluf_answer', 'Long Text', '-', '40-60 word BLUF answer capsule for this topic')]),
        ('content_briefs', [('cluster', 'Link to Table (keyword_clusters)', '', 'FK to keyword_clusters'), ('target_keyword', 'Link to Table (keywords)', '', 'Primary target keyword'), ('secondary_keywords', 'Long Text', '-', 'Secondary keywords to include'), ('word_count_target', 'Number (integer)', '0', 'Target word count from SERP analysis'), ('h_tag_structure', 'Long Text', '-', 'Full H-tag blueprint from SEO brief architect'), ('schema_requirements', 'Long Text', '-', 'Schema types and field specifications'), ('internal_link_targets', 'Long Text', '-', 'Pages to link to from this content'), ('bluf_answer', 'Long Text', '-', '40-60 word answer capsule'), ('assigned_writer', 'Link to Table (team_members)', '', ''), ('status', 'Select (single)', 'Generated, In Review, Approved, Assigned, Completed', ''), ('created_date', 'Created On', 'Auto', ''), ('completed_date', 'Date', '-', '')]),
        ('content_pieces', [('brief', 'Link to Table (content_briefs)', '', 'FK to content_briefs'), ('title', 'Text', 'Max: 300', 'Content title'), ('url', 'Text (URL)', '-', 'Published URL'), ('word_count', 'Number (integer)', '0', 'Actual word count of published content'), ('publish_date', 'Date', '-', ''), ('status', 'Select (single)', 'Draft, In AI Review, Revised, Final Review, Published, Archived', ''), ('ai_review_score', 'Number (decimal)', '0.0-10.0', 'Average score from 7-platform AI review'), ('bluf_present', 'Boolean', '', 'Whether BLUF answer capsule is present'), ('schema_deployed', 'Boolean', '', 'Whether JSON-LD schema is deployed'), ('indexed', 'Boolean', '', 'Whether page is indexed in Google'), ('assigned_to_parasite', 'Boolean', '', 'Whether marked for parasite SEO distribution')]),
        ('ai_review_log', [('content_piece', 'Link to Table (content_pieces)', '', 'FK'), ('platform', 'Select (single)', 'Gemini, ChatGPT, Perplexity, Google AI Overview, Bing/Copilot, Claude', 'AI platform used for review'), ('review_date', 'Date', '-', ''), ('score', 'Number (decimal)', '0.0-10.0', 'Quality score assigned by AI'), ('recommendations', 'Long Text', '-', 'Specific recommendations from AI review'), ('applied', 'Boolean', '', 'Whether recommendations were incorporated')]),
        ('page_templates', [('template_name', 'Text', 'Max: 200', 'e.g. "Visibility Hub Page", "Service Area Page", "Conversion Page"'), ('template_type', 'Select (single)', 'Visibility Hub, Service Area, Conversion, Industry Page, Service Page', ''), ('h_tag_blueprint', 'Long Text', '-', 'H-tag structure template'), ('schema_template', 'Long Text', '-', 'JSON-LD schema template'), ('word_count_range', 'Text', 'Max: 50', 'e.g. "2500-4000"'), ('bluf_required', 'Boolean', '', 'Whether BLUF capsule is mandatory'), ('used_count', 'Formula', 'count(link(content_briefs))', 'Number of briefs using this template')]),
    ]),
    ('5. Off-Page & Parasite SEO', [
        ('parasite_platforms', [('platform_name', 'Text', 'Max: 100', ''), ('da_score', 'Number (integer)', '0-100', 'Domain Authority'), ('tos_risk_level', 'Select (single)', 'Low, Medium, High, Unacceptable', ''), ('topical_relevance', 'Number (decimal)', '0.0-1.0', 'NLP similarity score to client vertical'), ('indexing_speed', 'Text', 'Max: 100', 'e.g. "2-5 days"'), ('editorial_barrier', 'Select (single)', 'None, Low, Medium, High', ''), ('composite_score', 'Formula', '(DA*0.3 + Relevance*100*0.25 + (4-TOS)*25*0.2 + Speed*0.15 + (4-Barrier)*25*0.1)', 'Weighted platform score'), ('status', 'Select (single)', 'Active, Under Review, Suspended, Removed', ''), ('last_tos_check', 'Date', '-', ''), ('content_guidelines', 'Long Text', '-', 'Platform-specific content rules')]),
        ('parasite_campaigns', [('client', 'Link to Table (clients)', '', 'FK'), ('platform', 'Link to Table (parasite_platforms)', '', 'FK'), ('content_title', 'Text', 'Max: 300', ''), ('source_content', 'Link to Table (content_pieces)', '', 'FK to content being distributed'), ('publish_url', 'Text (URL)', '-', ''), ('publish_date', 'Date', '-', ''), ('backlink_obtained', 'Boolean', '', ''), ('anchor_text', 'Text', 'Max: 200', ''), ('anchor_type', 'Select (single)', 'Exact Match, Partial Match, Branded, Naked URL, Generic', ''), ('index_status', 'Select (single)', 'Not Checked, Not Indexed, Indexed', ''), ('status', 'Select (single)', 'Draft, Submitted, Published, Rejected', '')]),
        ('backlink_profile', [('client', 'Link to Table (clients)', '', 'FK'), ('source_url', 'Text (URL)', '-', ''), ('da', 'Number (integer)', '0-100', ''), ('anchor_text', 'Text', 'Max: 200', ''), ('anchor_type', 'Select (single)', 'Exact Match, Partial Match, Branded, Naked URL, Generic', ''), ('follow_status', 'Select (single)', 'Follow, Nofollow, UGC, Sponsored', ''), ('acquired_date', 'Date', '-', ''), ('loss_date', 'Date', '-', 'Blank = still active'), ('link_value_score', 'Number (decimal)', '0-10', '')]),
        ('anchor_text_log', [('client', 'Link to Table (clients)', '', 'FK'), ('anchor_text', 'Text', 'Max: 200', ''), ('type', 'Select (single)', 'Exact Match, Partial Match, Branded, Naked URL, Generic', ''), ('occurrence_count', 'Number (integer)', '0', ''), ('risk_flag', 'Boolean', '', 'True if exact match exceeds 30% threshold'), ('last_checked', 'Date', '-', '')]),
        ('youtube_videos', [('client', 'Link to Table (clients)', '', 'FK'), ('title', 'Text', 'Max: 300', ''), ('url', 'Text (URL)', '-', ''), ('publish_date', 'Date', '-', ''), ('views', 'Number (integer)', '0', ''), ('transcript_status', 'Select (single)', 'Not Generated, Generated, Embedded', ''), ('embedded_on_site', 'Boolean', '', ''), ('schema_markup', 'Boolean', '', 'VideoObject schema deployed'), ('target_keyword', 'Link to Table (keywords)', '', '')]),
        ('social_media_assets', [('platform', 'Select (single)', 'YouTube, Instagram, Facebook, LinkedIn, TikTok, Twitter/X, Google Business Profile', ''), ('profile_url', 'Text (URL)', '-', ''), ('client', 'Link to Table (clients)', '', 'FK'), ('follower_count', 'Number (integer)', '0', ''), ('posting_frequency', 'Select (single)', 'Daily, 3x/Week, Weekly, Bi-Weekly, Monthly, As Needed', ''), ('content_type_mix', 'Text', 'Max: 300', 'e.g. "60% educational, 30% case study, 10% promotional"'), ('status', 'Select (single)', 'Active, Paused, Under Review', '')]),
    ]),
    ('6. Technical SEO & Indexing', [
        ('tech_seo_audits', [('client', 'Link to Table (clients)', '', 'FK'), ('url', 'Text (URL)', '-', 'Audited URL'), ('audit_date', 'Date', '-', ''), ('http_status', 'Text', 'Max: 50', 'e.g. "200 OK"'), ('lcp', 'Number (decimal)', '0s', 'Largest Contentful Paint'), ('fid', 'Number (decimal)', '0ms', 'First Input Delay'), ('cls', 'Number (decimal)', '0.0-1.0', 'Cumulative Layout Shift'), ('robots_issues', 'Long Text', '-', ''), ('canonical_issues', 'Long Text', '-', ''), ('schema_errors', 'Long Text', '-', ''), ('ssr_verified', 'Boolean', '', 'Server-side rendering confirmed'), ('overall_score', 'Number (integer)', '0-100', 'Composite technical health score')]),
        ('schema_deployments', [('client', 'Link to Table (clients)', '', 'FK'), ('url', 'Text (URL)', '-', ''), ('schema_type', 'Select (single)', 'FAQPage, HowTo, LocalBusiness, Service, Organization, WebSite, BreadcrumbList, Person, OfferCatalog, VideoObject', ''), ('deployment_date', 'Date', '-', ''), ('validation_status', 'Select (single)', 'Not Validated, Valid, Warnings, Errors', ''), ('validation_errors', 'Long Text', '-', ''), ('is_nested', 'Boolean', '', 'Whether multi-schema nesting is used')]),
        ('indexing_log', [('client', 'Link to Table (clients)', '', 'FK'), ('url', 'Text (URL)', '-', ''), ('submission_method', 'Select (single)', 'IndexNow, GSC, Sitemap, Manual', ''), ('submission_date', 'Date', '-', ''), ('indexed_date', 'Date', '-', 'Blank if not indexed'), ('status', 'Select (single)', 'Submitted, Pending, Indexed, Failed', '')]),
        ('crawl_issues', [('client', 'Link to Table (clients)', '', 'FK'), ('url', 'Text (URL)', '-', ''), ('issue_type', 'Select (single)', 'Noindex, Redirect, Soft 404, Canonical Conflict, Orphan Page, Crawl Budget Waste', ''), ('discovered_date', 'Date', '-', ''), ('resolved_date', 'Date', '-', 'Blank = unresolved'), ('severity', 'Select (single)', 'Critical, High, Medium, Low', ''), ('resolution_notes', 'Long Text', '-', '')]),
        ('internal_link_map', [('client', 'Link to Table (clients)', '', 'FK'), ('source_url', 'Text (URL)', '-', ''), ('target_url', 'Text (URL)', '-', ''), ('anchor_text', 'Text', 'Max: 200', ''), ('link_type', 'Select (single)', 'Navigational, Contextual, Breadcrumbs, Footer, Related Posts', ''), ('created_date', 'Created On', 'Auto', '')]),
    ]),
    ('7. GEO & AI Citation Tracking', [
        ('geo_citation_probes', [('client', 'Link to Table (clients)', '', 'FK'), ('query', 'Text', 'Max: 300', 'Test query sent to AI platform'), ('platform', 'Select (single)', 'ChatGPT, Claude, Perplexity, Bing Copilot, Google AI Overview', ''), ('probe_date', 'Date', '-', ''), ('brand_cited', 'Boolean', '', 'Whether VirtuaLab Digital was mentioned'), ('client_cited', 'Boolean', '', 'Whether client was mentioned'), ('competitor_cited', 'Text', 'Max: 200', 'Which competitors were mentioned instead'), ('response_excerpt', 'Long Text', '-', 'First 500 chars of AI response'), ('sentiment', 'Select (single)', 'Positive, Neutral, Negative, Mixed', '')]),
        ('geo_citation_logs', [('probe', 'Link to Table (geo_citation_probes)', '', 'FK'), ('citation_url', 'Text (URL)', '-', 'URL cited by AI as source'), ('citation_text_excerpt', 'Long Text', '-', 'Excerpt of text that was cited'), ('competitor_cited', 'Text', 'Max: 200', 'Competitor mentioned alongside or instead'), ('salience_score', 'Number (decimal)', '0.0-1.0', 'Entity salience score from geo_agent'), ('citation_position', 'Select (single)', 'Primary Source, Supporting Source, Mentioned', '')]),
        ('geo_citation_trends', [('client', 'Link to Table (clients)', '', 'FK'), ('platform', 'Select (single)', 'ChatGPT, Claude, Perplexity, Bing Copilot, Google AI Overview', ''), ('month', 'Date', '-', 'Month start date'), ('citation_rate', 'Number (decimal)', '0.0-100.0', 'Percentage of queries where brand was cited'), ('trend_direction', 'Select (single)', 'Improving, Stable, Declining, New', ''), ('competitor_benchmark_rate', 'Number (decimal)', '0.0-100.0', 'Average competitor citation rate for comparison'), ('query_count', 'Number (integer)', '0', 'Number of test queries this month')]),
        ('geo_recommendations', [('client', 'Link to Table (clients)', '', 'FK'), ('priority', 'Select (single)', 'Critical, High, Medium, Low', ''), ('action', 'Long Text', '-', 'Specific recommendation text'), ('rationale', 'Long Text', '-', 'Why this action is recommended'), ('target_queries', 'Long Text', '-', 'Queries this recommendation would improve'), ('status', 'Select (single)', 'Open, In Progress, Resolved, Deferred', '')]),
        ('llms_txt_config', [('client', 'Link to Table (clients)', '', 'FK'), ('version', 'Text', 'Max: 20', 'e.g. "v1.0"'), ('content', 'Long Text', '-', 'Full llms.txt file content'), ('deployment_url', 'Text (URL)', '-', 'e.g. "https://clientdomain.com/llms.txt"'), ('last_updated', 'Last Modified', 'Auto', ''), ('is_live', 'Boolean', '', 'Whether deployed and accessible')]),
    ]),
]

for chap_title, tables_data in remaining_domains:
    story.append(h1(chap_title))
    story.append(p(f'The tables in this domain are accessed by the n8n workflows defined in the ecosystem blueprint. Each table includes a Link-to-Table field pointing back to the clients table, ensuring that all data is scoped to the correct engagement. The status fields in each table use the exact option strings shown here, which match the condition checks in the corresponding n8n workflow branches. This eliminates the need for data transformation between Baserow storage and workflow logic, a common source of bugs in automation systems.'))
    for tbl_rows in tables_data:
        tbl_name = tbl_rows[0][0]
        story.append(h2(tbl_name))
        rows = [(r[0], r[1], r[2], r[3]) for r in tbl_rows]
        story.append(mt(['Field Name', 'Type', 'Config / Options', 'Notes'], rows, [80, 70, 130, 180]))
    story.append(PageBreak())

# ══════════════════════════════════════════════════
# CHAPTER 9: PRE-POPULATED DATA
# ══════════════════════════════════════════════════
story.append(h1('9. Pre-Populated Data Specifications'))
story.append(p(
    'The following data should be imported into Baserow during initial system setup. This data is derived directly from the extracted AISEO Framework documents and keyword research files, ensuring that the system begins with real strategic intelligence rather than empty tables. Each data set below specifies the target Baserow table, the source of the data, and the exact records to create. After import, every record should be verified to ensure that field values match the Select option definitions in the corresponding table schema from the previous chapters.'
))

story.append(h2('9.1 Competitors to Pre-Load'))
story.append(mt(
    ['Competitor', 'Domain', 'Type', 'Key Weakness to Exploit'],
    [
        ('Hook Agency', 'hookagency.com', 'National Full-Service', 'No GEO/AEO education; $1M+ revenue minimum excludes growing suburban trades'),
        ('Rival Digital', 'rivaldigital.com', 'Agency', 'High pricing; no plain-English technical guides; multi-service scope overwhelms'),
        ('PlumberSEO.net', 'plumberseo.net', 'Speciality', 'Sales-heavy; no un-gated technical algorithm breakdowns'),
        ('Sequoia GEO', 'sequoiageo.com', 'Boutique Advisory', 'Boutique scale limits delivery; few standardized templates'),
        ('RYNO Strategic', 'rynoss.com', 'Enterprise', 'Complex packages; enterprise-only; heavy paid focus'),
        ('Blue Corona', 'bluecorona.com', 'Agency', 'High entry pricing; heavy paid allocation; sales-heavy content'),
        ('Scorpion', '(unverified)', 'Platform', 'Proprietary tech limits portability; franchise-only focus'),
    ],
    [75, 80, 80, 225]
))
story.append(cap('Table 9.1: competitor_registry — Pre-load from AISEO Framework Tab 3'))

story.append(h2('9.2 ICP Templates to Pre-Load'))
story.append(mt(
    ['ICP Name', 'Vertical', 'Revenue Range', 'Ad Dependency', 'Key Pain Point'],
    [
        ('The Operator', 'HVAC, Plumbing, Roofing, Electrical', '$500K-$5M (sweet spot $1M-$10M)', 'Very High', 'Ad Budget Volatility, Lead Aggregator Fatigue'),
        ('The Practitioner', 'Dentistry, Physical Therapy, Law, Real Estate', '$800K-$2M per location', 'Moderate', 'Fragmented Local Listings, Weak Backlink Profiles'),
        ('The Institution', 'Private Schools, Sports Facilities, Foundations', '$2M-$15M budgets', 'Low', 'Low Digital Focus, Outdated Legacy Platforms'),
    ],
    [60, 80, 75, 60, 185]
))
story.append(cap('Table 9.2: icp_templates — Pre-load from AISEO Framework Tab 1'))

story.append(h2('9.3 Keyword Data Integration'))
story.append(p(
    'The 16 keyword research JSON files (160 total keyword entries) should be imported into the keywords table. Each file represents a different research dimension: asymmetric SEO, cloud stacking, clustering, competitors detail, contractor SEO, entity SEO, GBP, GEO, home services, LLM citation, parasite SEO, pest SEO, pest control, programmatic SEO, trades SEO, and YouTube SEO. During import, the intent field should be classified using the keyword_agent intent classifier, and keywords should be clustered using embedding-based similarity. The search volume and difficulty values from the research files should be preserved as the initial values, with the understanding that verified SEMrush/Ahrefs data will replace them during the first automated Keyword Research Pipeline execution.'
))
story.append(sp(6))
story.append(h2('9.4 Site Architecture URLs to Pre-Load'))
story.append(p(
    'The 48-URL sitemap inventory from the AISEO Framework should be imported into a url_registry table (not shown in previous chapters but recommended as an addition). Each URL record should include: the URL path, the page type (Core, Service, Industry, Utility), the pillar it belongs to (Get Found, Get Noticed, Convert More, Operate Smarter), the target keyword cluster, and the current content status. This creates the baseline that the Content Production Pipeline uses to identify gaps between the planned site architecture and the actually published content. Any URL in the planned architecture that has no corresponding content_piece record represents a content gap that should be prioritized in the next production cycle.'
))
story.append(PageBreak())

# ══════════════════════════════════════════════════
# CHAPTER 10: N8N WORKFLOW TRIGGERS
# ══════════════════════════════════════════════════
story.append(h1('10. n8n Workflow Trigger Specifications'))
story.append(p(
    'Each n8n workflow has a defined trigger mechanism, execution schedule, and Baserow read/write operations. The following table summarizes the six core workflows. The Baserow API endpoint for each trigger is the table webhook URL, which can be generated in the Baserow table settings. When a trigger fires, the n8n workflow reads the relevant record(s), executes its defined steps, and writes results back to the appropriate tables. Failed executions are logged with full context for debugging, and executions that exceed timeout thresholds trigger alerts to the assigned team member.'
))
story.append(mt(
    ['Workflow', 'Trigger', 'Schedule', 'Reads From', 'Writes To', 'Timeout'],
    [
        ('WF-01: Client Onboarding', 'Baserow webhook (clients table create)', 'On-demand', 'clients, competitor_registry, icp_templates, gbp_profiles', 'client_icp_profiles, keyword_research_jobs, geo_citation_probes, campaign_goals, ghl_contacts', '30 min'),
        ('WF-02: Keyword Research', 'Manual + Weekly cron', 'Weekly (active campaigns)', 'keyword_research_jobs, keywords, competitor_registry', 'keywords, keyword_clusters, keyword_gap_results', '15 min/job'),
        ('WF-03: Content Production', 'Manual + Baserow webhook (cluster status change)', 'On-demand', 'keyword_clusters, content_briefs, brand_settings', 'content_briefs, content_pieces, ai_review_log', '20 min/brief'),
        ('WF-04: Parasite Distribution', 'Manual + Baserow webhook (content_pieces.assigned_to_parasite = true)', 'On-demand', 'content_pieces, parasite_platforms, anchor_text_log', 'parasite_campaigns, backlink_profile', '10 min/piece'),
        ('WF-05: GEO Citation Monitor', 'Cron schedule', 'High-priority: every 6h; Standard: every 24h', 'keyword_clusters, geo_citation_probes', 'geo_citation_probes, geo_citation_logs, geo_citation_trends, geo_recommendations', '5 min/batch'),
        ('WF-06: Client Reporting', 'Monthly cron (1st of month) + Manual', 'Monthly', 'campaign_goals, keyword_clusters, geo_citation_trends, backlink_profile, tech_seo_audits, kpi_snapshots', 'report_registry', '10 min/report'),
    ],
    [55, 60, 55, 75, 75, 40]
))
story.append(cap('Table 10.1: n8n Workflow Trigger & Data Flow Matrix'))
story.append(PageBreak())

# ══════════════════════════════════════════════════
# CHAPTER 11: GHL CONFIGURATION
# ══════════════════════════════════════════════════
story.append(h1('11. GHL Pipeline Configuration'))
story.append(p(
    'The GoHighLevel CRM integration completes the data loop between SEO operations and business outcomes. The following configuration specifies the GHL pipeline stages, webhook endpoints, and field mappings that enable end-to-end lead attribution from search query to booked job. The n8n Client Onboarding Pipeline creates the initial GHL contact and pipeline entry. Subsequent n8n workflows update pipeline stages as leads progress through the buyer journey. The monthly Client Reporting Pipeline reads GHL pipeline data to include business outcome metrics alongside SEO metrics in client reports.'
))
story.append(h2('11.1 Pipeline Stage Mapping'))
story.append(mt(
    ['GHL Stage', 'Buyer Journey Phase', 'Trigger Condition', 'Data Written to Baserow'],
    [
        ('New Lead', 'Problem Awareness', 'Form submission or phone call with UTM data', 'clients (GHL contact ID), campaign_goals (first touch attribution)'),
        ('Qualified', 'Agency Comparison', 'Email opened + website visited + 2+ pages viewed', 'client_icp_profiles (verified pain points updated)'),
        ('Consultation Booked', 'Solution Evaluation', 'Calendar appointment confirmed', 'campaign_goals (stage transition date, estimated deal value)'),
        ('Proposal Sent', 'Trust Validation', 'Proposal document sent via GHL', 'campaigns (budget allocation updated if proposal accepted)'),
        ('Client Onboarded', 'Commitment', 'Contract signed, first payment received', 'clients (onboarding_status = Active), all sub-tables created'),
        ('Review (Monthly)', 'Retention', 'Monthly report delivered, satisfaction check', 'report_registry (new report record), campaign_goals (current_value updated)'),
    ],
    [70, 75, 120, 195]
))
story.append(cap('Table 11.1: GHL Pipeline Stage to Buyer Journey Mapping'))

story.append(h2('11.2 UTM Parameter Schema'))
story.append(p(
    'All internal links from content pieces to conversion pages must include UTM parameters that identify the source keyword cluster, content piece, and campaign. The n8n Content Production Pipeline automatically appends these parameters to internal links when generating published content. GHL webhooks capture UTM data as custom fields on the contact record, enabling the Reporting Pipeline to attribute leads and revenue to specific SEO activities.'))
story.append(mt(
    ['UTM Parameter', 'Source', 'Example Value', 'Used By'],
    [
        ('utm_source', 'Fixed per channel', 'google, bing, chatgpt, perplexity, claude', 'Lead source identification in GHL'),
        ('utm_medium', 'Fixed per channel', 'organic, ai-citation, referral, social', 'Medium categorization in reports'),
        ('utm_campaign', 'Keyword cluster label', 'dallas-plumber-seo, hvac-map-pack-optimization', 'Campaign attribution in Baserow'),
        ('utm_content', 'Content piece title', 'how-to-choose-plumber-dallas-tx', 'Content performance tracking'),
        ('utm_term', 'Target keyword', 'best plumber in dallas texas', 'Keyword-level ROI tracking'),
    ],
    [60, 60, 130, 180]
))
story.append(cap('Table 11.2: UTM Parameter Schema for Lead Attribution'))

# ── Build PDF ──
OUTPUT = '/home/z/my-project/download/VirtuaLab_Digital_Baserow_Implementation_Schema.pdf'

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=LEFT_M, rightMargin=RIGHT_M,
    topMargin=TOP_M, bottomMargin=BOT_M,
    title='VirtuaLab Digital Baserow Implementation Schema',
    author='VirtuaLab Digital',
    subject='AISEO Framework Systematic Approach - Database Specifications',
)

doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
print(f'PDF generated: {OUTPUT}')

import subprocess, os
result = subprocess.run(['python3', '-c', f'import fitz, os\ndoc = fitz.open("{OUTPUT}")\nprint(f"Pages: {{doc.page_count}}")\nprint(f"Size: {{os.path.getsize("{OUTPUT}") / 1024:.1f}} KB")\ndoc.close()'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(f'Warning: {{result.stderr}}')
