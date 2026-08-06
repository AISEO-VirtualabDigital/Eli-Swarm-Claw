#!/usr/bin/env python3
"""
VirtuaLab Digital - Asymmetrical SEO & Parasite SEO Master Strategy PDF
Comprehensive strategy document with keyword mapping, topic clustering, and implementation plan.
"""

import os
import sys

# PDF Skill Directory
PDF_SKILL_DIR = '/home/z/my-project/skills/pdf'
FONT_DIR = '/usr/share/fonts'

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem,
    Image
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.colors import Color

# ========================
# FONT REGISTRATION
# ========================
pdfmetrics.registerFont(TTFont('Inter', f'{FONT_DIR}/truetype/liberation/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Inter-Bold', f'{FONT_DIR}/truetype/liberation/LiberationSans-Bold.ttf'))
registerFontFamily('Inter', normal='Inter', bold='Inter-Bold')

# ========================
# PALETTE (from cascade)
# ========================
PAGE_BG       = HexColor('#f5f6f6')
SECTION_BG    = HexColor('#f1f2f2')
CARD_BG       = HexColor('#eeeff0')
TABLE_STRIPE  = HexColor('#ecedee')
HEADER_FILL   = HexColor('#36505d')
COVER_BLOCK   = HexColor('#3c5461')
BORDER_COLOR  = HexColor('#bacbd3')
ICON_COLOR    = HexColor('#376a84')
ACCENT        = HexColor('#2e7fa7')
ACCENT2       = HexColor('#cb7458')
TEXT_PRIMARY   = HexColor('#222526')
TEXT_MUTED     = HexColor('#71787b')
SUCCESS       = HexColor('#488b5e')
WARNING       = HexColor('#b08d47')
ERROR         = HexColor('#8a4d48')
INFO          = HexColor('#527291')
WHITE         = HexColor('#ffffff')
BLACK         = HexColor('#000000')

# ========================
# PAGE DIMENSIONS
# ========================
PAGE_W, PAGE_H = A4
LEFT_M = 22*mm
RIGHT_M = 22*mm
TOP_M = 25*mm
BOT_M = 25*mm
CONTENT_W = PAGE_W - LEFT_M - RIGHT_M

# ========================
# STYLES
# ========================
styles = getSampleStyleSheet()

s_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Inter-Bold', fontSize=22, leading=28, textColor=HEADER_FILL, spaceAfter=12, spaceBefore=20)
s_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Inter-Bold', fontSize=16, leading=22, textColor=ACCENT, spaceAfter=8, spaceBefore=16)
s_h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontName='Inter-Bold', fontSize=13, leading=18, textColor=HEADER_FILL, spaceAfter=6, spaceBefore=12)
s_body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Inter', fontSize=10, leading=15, textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=6)
s_body_sm = ParagraphStyle('BodySm', parent=s_body, fontSize=9, leading=13, textColor=TEXT_MUTED)
s_bullet = ParagraphStyle('Bullet', parent=s_body, leftIndent=18, bulletIndent=6, spaceBefore=2, spaceAfter=2)
s_table_header = ParagraphStyle('TH', fontName='Inter-Bold', fontSize=8.5, leading=11, textColor=WHITE, alignment=TA_CENTER)
s_table_cell = ParagraphStyle('TC', fontName='Inter', fontSize=8, leading=11, textColor=TEXT_PRIMARY, alignment=TA_LEFT)
s_table_cell_c = ParagraphStyle('TCC', parent=s_table_cell, alignment=TA_CENTER)
s_caption = ParagraphStyle('Caption', parent=s_body_sm, alignment=TA_CENTER, textColor=TEXT_MUTED, fontName='Inter', fontSize=8.5, leading=12)
s_quote = ParagraphStyle('Quote', parent=s_body, leftIndent=20, rightIndent=20, textColor=ICON_COLOR, fontSize=9.5, leading=14, borderColor=ACCENT, borderWidth=0, borderPadding=0)

# ========================
# HELPER FUNCTIONS
# ========================
def make_table(headers, rows, col_widths=None):
    """Create a styled table with header and data rows."""
    header_row = [Paragraph(h, s_table_header) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(c), s_table_cell) if not isinstance(c, Paragraph) else c for c in row])
    
    if col_widths is None:
        col_widths = [CONTENT_W / len(headers)] * len(headers)
    
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_FILL),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Inter-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_STRIPE))
    t.setStyle(TableStyle(style_cmds))
    return t

def hr():
    return HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=8, spaceBefore=8)

def sp(pts=8):
    return Spacer(1, pts)

# ========================
# BUILD DOCUMENT
# ========================
output_path = '/home/z/my-project/download/VirtuaLab_Digital_Asymmetrical_SEO_Parasite_SEO_Strategy.pdf'

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=LEFT_M, rightMargin=RIGHT_M,
    topMargin=TOP_M, bottomMargin=BOT_M,
    title='VirtuaLab Digital - Asymmetrical SEO & Parasite SEO Master Strategy',
    author='VirtuaLab Digital',
    subject='Asymmetrical SEO, Parasite SEO, Keyword Mapping, Topic Clustering Strategy',
)

story = []

# ========================
# CHAPTER 1: EXECUTIVE OVERVIEW
# ========================
story.append(Paragraph('VirtuaLab Digital', ParagraphStyle('CoverTitle', fontName='Inter-Bold', fontSize=32, leading=38, textColor=HEADER_FILL, alignment=TA_CENTER, spaceAfter=8)))
story.append(Paragraph('Asymmetrical SEO & Parasite SEO', ParagraphStyle('CoverSub', fontName='Inter-Bold', fontSize=20, leading=26, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4)))
story.append(Paragraph('Master Strategy Document', ParagraphStyle('CoverSub2', fontName='Inter', fontSize=14, leading=18, textColor=TEXT_MUTED, alignment=TA_CENTER, spaceAfter=20)))
story.append(hr())
story.append(Paragraph('Keyword Mapping | Topic Clustering | SERP & LLM Citation Dominance | Parasite SEO Playbook | Implementation Roadmap', ParagraphStyle('CoverDesc', fontName='Inter', fontSize=10, leading=14, textColor=TEXT_MUTED, alignment=TA_CENTER, spaceAfter=12)))
story.append(sp(30))

# Metadata table
meta_data = [
    ['Prepared For', 'VirtuaLab Digital Leadership'],
    ['Classification', 'Strategic - Confidential'],
    ['Framework Version', 'AISEO Framework v3.0'],
    ['Date', 'August 2026'],
    ['Scope', 'Suburban Local Service Markets - USA'],
]
meta_t = Table(meta_data, colWidths=[140, CONTENT_W - 140])
meta_t.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Inter-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('TEXTCOLOR', (0, 0), (0, -1), HEADER_FILL),
    ('TEXTCOLOR', (1, 0), (1, -1), TEXT_PRIMARY),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_COLOR),
    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
    ('RIGHTPADDING', (0, 0), (0, -1), 12),
]))
story.append(meta_t)

story.append(PageBreak())

# ========================
# CHAPTER 1: STRATEGIC INTELLIGENCE OVERVIEW
# ========================
story.append(Paragraph('1. Strategic Intelligence Overview', s_h1))
story.append(sp(6))

story.append(Paragraph('1.1 The Multi-Surface Search Paradigm', s_h2))
story.append(Paragraph(
    'The search landscape has fundamentally shifted from a deterministic framework of keyword occurrences and backlink arrays into a multi-surface paradigm where high-intent B2B buyers deploy complex, conversational queries across Google AI Overviews, Google Gemini, OpenAI ChatGPT, and Perplexity AI. Traditional organic SEO was built to claim positions in ranked blue-link indexes. Modern search demands dominance across both traditional SERP positions and synthetic citation graphs of major large language models (LLMs). This dual-front reality creates both an unprecedented challenge and a massive asymmetrical opportunity for agencies like VirtuaLab Digital that can execute across both surfaces simultaneously.', s_body))

story.append(Paragraph(
    'When analyzing high-intent research queries such as "who are the top rated pest control SEO agency in USA," a highly concentrated group of specialized agencies systematically dominates both traditional search rankings and LLM citation graphs. Entities such as Pesty Marketing, Loopex Digital, Thrive Internet Marketing Agency, and Pest Control SEO (Dan Leibrandt) demonstrate the precise technical, structural, and off-site signals required to win modern multi-surface visibility. The key insight is that these organizations do not simply optimize for Google; they architect their digital presence to be machine-readable, entity-dense, and citation-ready across every AI retrieval pipeline.', s_body))

story.append(Paragraph(
    'For VirtuaLab Digital, this means the strategy must operate on three concurrent layers: (1) traditional organic dominance for suburban local service keywords, (2) LLM citation readiness through Generative Engine Optimization (GEO), and (3) parasitic placement on high-authority platforms to capture immediate visibility while building domain authority. These three layers form the core of the Asymmetrical SEO framework that follows.', s_body))

story.append(Paragraph('1.2 The Suburban Service Market Opportunity', s_h2))
story.append(Paragraph(
    'Suburban local service markets operate under distinct geographic and psychological constraints that separate them from dense urban centers. In suburban markets, search results are hyper-sensitive to the user\'s immediate location. A homeowner searching for "water heater repair" in a residential suburb receives a completely different Map Pack than one searching from an adjacent township. This phenomenon makes static distance less critical than localized relevance and prominence, which must be reinforced via structured suburban content. Furthermore, suburban searches for trade services are frequently driven by sudden, high-stress emergencies such as flooded basements or broken air conditioning in peak summer, shifting the psychological profile from research-oriented to high-urgency action.', s_body))

story.append(Paragraph(
    'The target market consists of three primary business profiles: Archetype A (The Operator) includes HVAC, plumbing, roofing, electrical, and general contracting businesses with 1 to 25 employees and annual revenues between $500K and $5M. Archetype B (The Practitioner) covers dentistry, physical therapy, local law firms, and real estate teams with 1 to 3 physical locations. Archetype C (The Institution) represents private schools, regional sports facilities, and local foundations with 20 to 100+ staff members. All three archetypes share a common dependency on volatile paid ad channels and a critical lack of organic search maturity.', s_body))

story.append(Paragraph('1.3 Core Strategic Positioning', s_h2))
story.append(Paragraph(
    'VirtuaLab Digital is positioned as a technical search partner offering custom, AI-ready setups with radical transparency, clear pricing ranges, and un-gated educational resources. Unlike competitors such as Hook Agency (which imposes a $1M+ revenue minimum), Rival Digital (with high pricing points excluding growing suburban trades), or Scorpion (whose proprietary technology limits client asset portability), VirtuaLab targets the underserved mid-market sweet spot of $1M to $10M annual revenue operators who need modular, scalable search frameworks. The core brand message is: "Transition from renting traffic to building long-term organic search assets." This positioning directly addresses the primary emotional frustration of suburban operators: feeling trapped in an escalating pay-to-play model while losing visibility to competitors.', s_body))

story.append(PageBreak())

# ========================
# CHAPTER 2: DEEP KEYWORD UNIVERSE
# ========================
story.append(Paragraph('2. Deep Keyword Universe & Expansion', s_h1))
story.append(sp(6))

story.append(Paragraph('2.1 Primary Keyword Clusters', s_h2))
story.append(Paragraph(
    'The keyword universe for VirtuaLab Digital is organized into eight strategic clusters, each targeting a distinct dimension of the suburban local service search ecosystem. These clusters were developed by cross-referencing the AISEO Framework document, web research on current SERP dynamics, competitor keyword gaps, and emerging search behavior patterns including AI-driven queries. Each cluster contains head terms, long-tail variants, and question-based queries that map to specific content templates and page types within the site architecture.', s_body))

# CLUSTER TABLES
cluster_data = [
    ['Cluster 1: Core Agency Brand', 'local seo for contractors', 'Commercial', 'High', 'Medium', 'Homepage Hub', 'Primary semantic anchor for the homepage and all service messaging.'],
    ['Cluster 1: Core Agency Brand', 'suburban local seo agency', 'Local/Commercial', 'Medium', 'Low', 'Hero Section', 'Targets the core geographic positioning of the agency.'],
    ['Cluster 1: Core Agency Brand', 'contractor local seo strategy', 'Commercial', 'Medium', 'Medium', 'Service Page', 'Captures active operators researching customized solutions.'],
    ['Cluster 1: Core Agency Brand', 'local service business seo agency', 'Commercial', 'Medium', 'High', 'Homepage Hub', 'Broader agency search capturing trade niches.'],
    ['Cluster 2: Google Maps & GBP', 'how to rank on google maps', 'Informational', 'High', 'Medium', 'Resource Guide', 'Core user question about Map Pack rankings.'],
    ['Cluster 2: Google Maps & GBP', 'google business profile optimization services', 'Transactional', 'High', 'Medium', 'Service Page', 'High-intent commercial search for professional optimization.'],
    ['Cluster 2: Google Maps & GBP', 'why is my business not showing in maps', 'Informational', 'High', 'Low', 'FAQ/Resource', 'Troubleshoot Map Pack visibility drops.'],
    ['Cluster 2: Google Maps & GBP', 'google maps 3-pack ranking factors', 'Informational', 'Medium', 'Low', 'Blog Post', 'Technical deep-dive on proximity, relevance, prominence.'],
    ['Cluster 3: Paid Ad Dependency', 'reduce dependency on google ads', 'Informational', 'Emerging', 'Low', 'Homepage Section', 'Core educational theme addressing primary pain point.'],
    ['Cluster 3: Paid Ad Dependency', 'local service ads vs google ppc', 'Informational', 'Medium', 'Low', 'Comparison Article', 'Breaks down LSA vs PPC with concrete statistics.'],
    ['Cluster 3: Paid Ad Dependency', 'shared lead vs organic lead cost', 'Informational', 'Emerging', 'Low', 'Whitepaper', 'Compares aggregators like Angi vs owned visibility.'],
    ['Cluster 3: Paid Ad Dependency', 'cost per lead plumbing hvac 2025', 'Informational', 'Medium', 'Medium', 'Data Report', 'Industry-specific cost benchmarks for trades.'],
    ['Cluster 4: GEO & AI Search', 'generative engine optimization for local business', 'Informational', 'Emerging', 'Low', 'Service Page', 'Establishes early topical authority on AI search trends.'],
    ['Cluster 4: GEO & AI Search', 'how to get cited by perplexity ai', 'Informational', 'Emerging', 'Low', 'GEO Guide', 'Details formatting rules for AI answer engines.'],
    ['Cluster 4: GEO & AI Search', 'AI search optimization for contractors', 'Informational', 'Emerging', 'Low', 'Blog/Service', 'Trade-specific AI optimization methodology.'],
    ['Cluster 4: GEO & AI Search', 'llms.txt file implementation guide', 'Technical', 'Emerging', 'Low', 'Technical Guide', 'Emerging AI web standard for crawler guidance.'],
]

story.append(Paragraph('2.1.1 Cluster 1-4: Foundation Keywords', s_h3))
t1 = make_table(
    ['Cluster / Keyword', 'Search Term', 'Intent', 'Demand', 'Difficulty', 'Page Target', 'Strategic Notes'],
    cluster_data,
    col_widths=[85, 105, 55, 42, 42, 60, CONTENT_W - 389]
)
story.append(t1)
story.append(sp(8))

cluster_data_2 = [
    ['Cluster 5: Industry Verticals', 'hvac digital marketing agency', 'Commercial', 'Medium', 'High', '/industries/hvac', 'Targets established HVAC firms.'],
    ['Cluster 5: Industry Verticals', 'roofing contractor seo services', 'Commercial', 'Medium', 'High', '/industries/roofing', 'Targets roofing firms seeking organic leads.'],
    ['Cluster 5: Industry Verticals', 'plumbing contractor digital marketing', 'Commercial', 'High', 'High', '/industries/plumbing', 'Highly competitive trade search term.'],
    ['Cluster 5: Industry Verticals', 'pest control seo agency', 'Commercial', 'High', 'Medium', '/industries/pest-control', 'Demonstrated LLM citation opportunity.'],
    ['Cluster 5: Industry Verticals', 'electrical contractor website design', 'Commercial', 'Medium', 'Medium', '/industries/electrical', 'Technical integration with dispatch software.'],
    ['Cluster 5: Industry Verticals', 'landscaping company seo techniques', 'Informational', 'Medium', 'Medium', '/industries/landscaping', 'Captures seasonal local search demand.'],
    ['Cluster 5: Industry Verticals', 'dentist local seo services', 'Commercial', 'Medium', 'High', '/industries/dentistry', 'Practitioner archetype targeting.'],
    ['Cluster 6: Technical & CRM', 'servicetitan marketing integrations', 'Technical', 'Low', 'Low', '/services/crm', 'Highlights dispatch software expertise.'],
    ['Cluster 6: Technical & CRM', 'best schema markup for plumbers', 'Technical', 'Low', 'Low', '/resources/schema', 'Copy-paste schema markup examples.'],
    ['Cluster 6: Technical & CRM', 'technical seo for contractors', 'Informational', 'Medium', 'Medium', '/services/technical-seo', 'Core Web Vitals and crawl optimization.'],
    ['Cluster 6: Technical & CRM', 'multi location home service seo', 'Commercial', 'Low', 'Medium', '/services/multi-location', 'Franchise and multi-territory strategies.'],
    ['Cluster 7: Parasite SEO', 'parasite SEO strategy 2025 2026', 'Informational', 'Emerging', 'Low', 'Whitepaper', 'Educational authority on parasite methods.'],
    ['Cluster 7: Parasite SEO', 'linkedin article ranking for seo agency', 'Informational', 'Emerging', 'Low', 'Playbook', 'Platform-specific parasite playbook.'],
    ['Cluster 7: Parasite SEO', 'medium publication seo for contractors', 'Informational', 'Emerging', 'Low', 'Playbook', 'Content syndication strategy.'],
    ['Cluster 7: Parasite SEO', 'youtube video ranking for local services', 'Informational', 'Medium', 'Medium', 'Video Strategy', 'YouTube SEO for trade businesses.'],
    ['Cluster 8: Suburban Strategy', 'suburban local search strategy', 'Informational', 'Emerging', 'Low', '/resources/local-strategy', 'Multi-suburb organic capture framework.'],
    ['Cluster 8: Suburban Strategy', 'programmatic seo hub and spoke trades', 'Informational', 'Emerging', 'Low', '/services/programmatic', 'Scalable content architecture.'],
    ['Cluster 8: Suburban Strategy', 'service area page optimization', 'Informational', 'Medium', 'Medium', '/resources/sap-guide', 'Location-specific content templates.'],
]

story.append(Paragraph('2.1.2 Cluster 5-8: Vertical, Technical, Parasite & Suburban Keywords', s_h3))
t2 = make_table(
    ['Cluster / Keyword', 'Search Term', 'Intent', 'Demand', 'Difficulty', 'Page Target', 'Strategic Notes'],
    cluster_data_2,
    col_widths=[85, 105, 55, 42, 42, 60, CONTENT_W - 389]
)
story.append(t2)

story.append(PageBreak())

# ========================
# CHAPTER 3: TOPIC MAPPING & CONTENT ARCHITECTURE
# ========================
story.append(Paragraph('3. Topic Mapping & Content Architecture', s_h1))
story.append(sp(6))

story.append(Paragraph('3.1 Hub-and-Spoke Topic Model', s_h2))
story.append(Paragraph(
    'The content architecture is built on a hub-and-spoke model where the homepage functions as the master knowledge hub, and individual service pages, industry pages, and resource guides serve as specialized spokes. This architecture ensures that every piece of content reinforces topical authority for the parent cluster while capturing specific long-tail queries. The model prevents keyword cannibalization by establishing clear boundaries between the homepage (brand + education), service pages (commercial intent), and resource pages (informational intent). Each spoke page links back to the hub through contextual internal links, and the hub links outward to all spokes, creating a tightly interlinked topical mesh that search engines recognize as comprehensive authority.', s_body))

story.append(Paragraph(
    'The 14-section homepage architecture is designed to function as a Semantic Knowledge Hub. Section 01 (Hero) frames search visibility as an owned asset. Section 02 introduces three core pillars: Visibility Attracts, Trust Converts, Systems Scale. Sections 03-05 deliver deep educational modules on paid ad fatigue, Maps Pack mechanics, and technical SEO. Sections 06-07 provide taxonomic directories for services and industries. Sections 08-10 cover advanced search modules including AI Search/GEO, content authority, and CRM synchronization. Sections 11-13 offer resource and verification modules including case studies, a master FAQ, and a glossary. Section 14 is the dynamic site footer with local entity links and structured schema.', s_body))

# Topic Mapping Table
topic_data = [
    ['1. Agency Brand Hub', 'Homepage', 'local seo for contractors, suburban local seo agency', '/about, /contact', 'Brand search terms, agency positioning queries'],
    ['2. Google Maps & GBP', '/services/local-seo', 'google business profile optimization services', '/resources/gbp-guide, /resources/maps-troubleshooting', 'Step-by-step guides, ranking factors, FAQ answers'],
    ['3. Paid Ad Dependency', '/resources/ad-roi', 'reduce dependency on google ads, lsa vs ppc', '/seo-services, /resources/lsa-vs-ppc', 'Comparison data, cost benchmarks, strategic whitepaper'],
    ['4. AI Search / GEO', '/services/geo', 'generative engine optimization strategies', '/resources/perplexity-seo, /resources/llms-txt', 'Citation optimization, BLUF formatting, entity authority'],
    ['5. HVAC Vertical', '/industries/hvac', 'hvac digital marketing agency', '/blog/hvac-marketing-plan, /resources/hvac-keywords', 'Seasonal campaigns, dispatch integration, map strategy'],
    ['6. Roofing Vertical', '/industries/roofing', 'roofing contractor seo services', '/blog/roofing-lead-generation, /resources/lead-costs', 'Storm damage SEO, lead cost analysis, review strategy'],
    ['7. Plumbing Vertical', '/industries/plumbing', 'plumbing contractor digital marketing', '/services/web-design, /resources/schema-guide', 'Website templates, schema markup, emergency search'],
    ['8. Pest Control Vertical', '/industries/pest-control', 'pest control seo agency', '/blog/pest-control-seasonal, /resources/pest-keywords', 'Seasonal demand capture, LLM citation dominance'],
    ['9. Technical SEO', '/services/technical-seo', 'technical seo for contractors', '/resources/schema-guide, /resources/page-2-syndrome', 'Core Web Vitals, schema, crawl optimization'],
    ['10. CRM & Automation', '/services/crm-automation', 'servicetitan marketing integrations', '/resources/servicetitan-guide, /resources/lead-tracking', 'Dispatch integration, lead attribution, booking automation'],
    ['11. Parasite SEO Assets', 'External Platforms', 'parasite seo strategy, linkedin seo articles', '/resources/parasite-playbook, /resources/white-label', 'Platform playbooks, content syndication, video SEO'],
    ['12. Suburban Strategy', '/resources/local-strategy', 'suburban local search strategy', '/resources/sap-guide, /resources/multi-suburb', 'Multi-suburb capture, programmatic hubs, centroid optimization'],
]

story.append(Paragraph('3.2 Content Cluster Taxonomy', s_h3))
t3 = make_table(
    ['Topic Cluster', 'Primary Page', 'Anchor Keywords', 'Supporting Pages', 'Content Types'],
    topic_data,
    col_widths=[75, 65, 95, 105, CONTENT_W - 340]
)
story.append(t3)

story.append(Paragraph('3.3 Cannibalization Prevention Matrix', s_h2))
story.append(Paragraph(
    'Keyword cannibalization occurs when multiple pages on the same domain compete for identical or overlapping search queries, diluting each page\'s relevance signals and confusing search engine crawlers about which page should rank for a given query. This matrix establishes strict keyword ownership boundaries across the site. The homepage retains all brand navigational queries and broad commercial terms like "local seo for contractors." Service-specific commercial terms such as "google business profile optimization services" are restricted to the /services/local-seo page. Informational queries and how-to guides are directed to /resources/ subpages. Industry-specific terms are confined to their respective /industries/ pages. Technical integration queries are routed to /services/crm-automation. This clear separation ensures each page builds concentrated topical authority rather than competing with itself.', s_body))

cannibal_data = [
    ['Agency Brand', 'Homepage', '/about, /contact', 'VirtuaLab Digital, suburban contractor seo agency', 'individual trade seo templates, diy map rankings'],
    ['Google Maps', '/services/local-seo', '/resources/gbp-guide', 'google business profile services, maps optimization', 'general website audit code, how-to design plumbing sites'],
    ['AI Search / GEO', '/services/geo', '/resources/perplexity-seo', 'generative engine optimization, ai answer readiness', 'suburban local search statistics, direct google ads costs'],
    ['HVAC Marketing', '/industries/hvac', '/blog/hvac-marketing-plan', 'hvac digital marketing agency, ac repair seo', 'roofing storm setups, general concrete services'],
    ['Roofing Marketing', '/industries/roofing', '/blog/roofing-lead-gen', 'roofing contractor marketing services, storm damage seo', 'plumbing emergency search, electrical panel upgrades'],
    ['Pest Control', '/industries/pest-control', '/blog/pest-control-seo', 'pest control seo agency, exterminator marketing', 'general lawn care, tree removal services'],
]

t4 = make_table(
    ['Content Cluster', 'Primary Landing', 'Supporting Pages', 'Keywords to Include', 'Keywords to Exclude'],
    cannibal_data,
    col_widths=[70, 70, 80, 115, CONTENT_W - 335]
)
story.append(t4)

story.append(PageBreak())

# ========================
# CHAPTER 4: KEYWORD CLUSTERING
# ========================
story.append(Paragraph('4. Keyword Clustering Methodology', s_h1))
story.append(sp(6))

story.append(Paragraph('4.1 Intent-Based Clustering Framework', s_h2))
story.append(Paragraph(
    'Keywords are clustered using a four-dimensional framework that goes beyond traditional search volume metrics. Each keyword is scored across Search Intent (informational, commercial, transactional, navigational), Buyer Awareness Stage (unaware, problem-aware, solution-aware, most-aware), Content Template Fit (hub page, service detail, resource guide, blog post, FAQ), and Competitive Difficulty (based on current SERP composition). This multi-dimensional approach ensures that every keyword is mapped not just to a page, but to a specific role within the buyer journey. The clustering methodology draws on the same academic rigor that drives Generative Engine Optimization research, recognizing that modern search engines evaluate content at the semantic entity level rather than simple keyword matching.', s_body))

story.append(Paragraph('4.2 Cluster Detail: Problem-Aware Keywords', s_h3))
problem_data = [
    ['why is my business not showing in maps', 'Informational', 'Problem-Aware', 'Section 12 FAQ + /resources/maps-troubleshooting', 'High', 'Direct answer in FAQ with link to troubleshooting guide.'],
    ['how to stop paying for shared leads', 'Informational', 'Problem-Aware', 'Homepage Paid Ad Trap section', 'Medium', 'Core hook for paid ad dependency educational content.'],
    ['why is my business buried on google page 2', 'Informational', 'Problem-Aware', '/resources/page-2-syndrome', 'Low', 'Technical audit guide diagnosing root causes.'],
    ['hvac local search visibility problems', 'Informational', 'Problem-Aware', 'Homepage Problem Section', 'High', 'HVAC operators with weak map presence.'],
    ['what is generative engine optimization', 'Informational', 'Unaware', '/services/ai-search-optimization', 'Medium', 'Builds technical authority above standard agencies.'],
    ['how to reduce cost per lead hvac', 'Informational', 'Problem-Aware', '/resources/ad-roi + /industries/hvac', 'High', 'Industry-specific cost reduction framework.'],
    ['google maps ranking dropped suddenly', 'Informational', 'Problem-Aware', '/resources/maps-troubleshooting', 'Medium', 'Emergency troubleshooting for ranking drops.'],
    ['competitor ranking higher on google maps', 'Informational', 'Problem-Aware', '/resources/competitive-maps', 'Medium', 'Competitive analysis for local map visibility.'],
]

t5 = make_table(
    ['Keyword', 'Intent', 'Stage', 'Target Location', 'Business Potential', 'Strategic Notes'],
    problem_data,
    col_widths=[100, 52, 55, 80, 42, CONTENT_W - 329]
)
story.append(t5)
story.append(sp(8))

story.append(Paragraph('4.3 Cluster Detail: Solution-Aware & Transactional Keywords', s_h3))
solution_data = [
    ['google business profile optimization services', 'Transactional', 'Solution-Aware', '/services/local-seo', 'High', 'High-intent commercial search directly linked from homepage.'],
    ['local seo for contractors', 'Commercial', 'Solution-Aware', 'Homepage Hub', 'High', 'Primary semantic anchor for the entire site.'],
    ['hvac digital marketing agency', 'Commercial', 'Solution-Aware', '/industries/hvac', 'High', 'Targets established HVAC firms with commercial intent.'],
    ['roofing contractor seo services', 'Commercial', 'Solution-Aware', '/industries/roofing', 'High', 'Captures roofing firms seeking organic lead generation.'],
    ['plumbing website design templates', 'Commercial', 'Solution-Aware', '/services/web-design', 'Medium', 'Showcases specialized layouts for home service firms.'],
    ['pest control seo company', 'Commercial', 'Solution-Aware', '/industries/pest-control', 'High', 'Demonstrated LLM citation opportunity from Search Intelligence Report.'],
    ['multi location home service seo', 'Commercial', 'Solution-Aware', '/services/multi-location', 'Medium', 'Targets larger brands and franchise networks.'],
    ['best schema markup for local business', 'Technical', 'Solution-Aware', '/resources/schema-guide', 'Medium', 'Provides copy-and-paste schema markup examples.'],
]

t6 = make_table(
    ['Keyword', 'Intent', 'Stage', 'Target Location', 'Business Potential', 'Strategic Notes'],
    solution_data,
    col_widths=[100, 52, 55, 80, 42, CONTENT_W - 329]
)
story.append(t6)

story.append(PageBreak())

# ========================
# CHAPTER 5: PARASITE SEO PLAYBOOK
# ========================
story.append(Paragraph('5. Parasite SEO Playbook', s_h1))
story.append(sp(6))

story.append(Paragraph('5.1 Parasite SEO Defined for VirtuaLab Digital', s_h2))
story.append(Paragraph(
    'Parasite SEO is the practice of creating and optimizing content on high-authority, third-party platforms to rank for target keywords and drive traffic back to the primary domain. In the context of VirtuaLab Digital, this is executed as a white-label, brand-building strategy (distinct from black-hat approaches that use manipulative tactics on low-value content). The objective is threefold: first, to capture immediate search visibility on platforms that already possess massive domain authority such as LinkedIn, Medium, YouTube, and Reddit; second, to build brand entity recognition across the web so that AI engines like ChatGPT and Perplexity encounter consistent, authoritative mentions of VirtuaLab Digital when retrieving information about SEO agencies for local service businesses; and third, to generate high-quality backlinks and entity co-occurrences that strengthen the primary domain\'s topical authority signals.', s_body))

story.append(Paragraph(
    'The key distinction in VirtuaLab\'s approach is that all parasite content is value-driven and educational, not purely promotional. Each piece of parasite content serves as a genuine resource that answers specific questions about local SEO, GEO, or trade-specific marketing. This ensures longevity, avoids platform penalties, and builds authentic trust with readers who may eventually convert into clients. The strategy leverages the fact that 45% of consumers now use AI-powered search engines for local business recommendations, and these AI systems heavily weight third-party earned media when generating their responses.', s_body))

story.append(Paragraph('5.2 Platform-Specific Strategies', s_h2))

platform_data = [
    ['LinkedIn Articles', 'DA 98+', 'Asymmetrical SEO for Suburban Trades: A 2026 Framework; Why Local Service Businesses Need GEO, Not Just SEO', 'Long-form thought leadership (1,500-2,500 words) with data citations, infographics, and clear CTAs. Publish 2x/month.', 'Immediate visibility for commercial queries; professional B2B audience; strong LLM citation signal.'],
    ['Medium Publications', 'DA 95+', 'The Complete Guide to Reducing Paid Ad Dependency for HVAC Companies; How Google Maps Actually Selects Local Businesses', 'Technical deep-dives (2,000-3,500 words) with step-by-step instructions. Submit to SEO, marketing, and SaaS publications.', 'Evergreen content ranking potential; builds topical authority; feeds LLM training data.'],
    ['YouTube', 'DA 100', 'Local SEO Audit Walkthrough for a Plumbing Company; 5 Google Maps Optimization Steps That Actually Work in 2026', 'Video tutorials (8-15 min) with screen recordings, before/after maps, and verbal expertise demonstration. 2x/month.', 'Video SEO captures informational queries; YouTube videos appear in Google SERP; builds personal brand authority.'],
    ['Reddit (r/localseo, r/SEO)', 'DA 91+', 'Answering questions about GEO, Maps ranking, and trade-specific SEO with genuine expertise and data backing.', 'Value-first participation in discussions. No self-promotion. Build reputation through consistent, high-quality answers. Weekly.', 'Reddit answers are heavily cited by Perplexity AI; builds community trust and referral traffic.'],
    ['Google Business Profile', 'N/A (Local)', 'Weekly GBP posts with local SEO tips, seasonal alerts, and service area highlights.', 'Short-form content (150-300 words) with images. Posts must include relevant keywords naturally. 2x/week.', 'Direct local search visibility; reinforces Maps prominence; generates GBP post insights.'],
    ['Quora', 'DA 93+', 'Detailed answers to questions like "What is the best SEO strategy for a pest control company?"', 'Comprehensive answers (500-1,000 words) citing specific statistics and case studies. 3-4x/month.', 'Quora answers rank in Google for long-tail queries; builds topical authority.'],
]

t7 = make_table(
    ['Platform', 'Authority', 'Content Examples', 'Production Guidelines', 'Strategic Rationale'],
    platform_data,
    col_widths=[60, 38, 105, 115, CONTENT_W - 318]
)
story.append(t7)

story.append(Paragraph('5.3 Parasite Content Calendar (90-Day Sprint)', s_h2))
story.append(Paragraph(
    'The 90-day parasite SEO sprint is designed to establish immediate multi-platform visibility while the primary domain builds organic authority. During the first 30 days, the focus is on foundational presence: claiming and optimizing all platform profiles, publishing the initial batch of cornerstone content on LinkedIn and Medium, and launching the YouTube channel with two high-impact audit walkthroughs. During days 31-60, the strategy shifts to consistency and engagement: maintaining a regular publishing cadence, actively participating in Reddit and Quora discussions, and creating platform-specific content that addresses emerging search trends such as GEO implementation for local businesses. During days 61-90, the emphasis moves to optimization and amplification: analyzing which parasite pages are generating the most impressions and clicks, refining content based on performance data, and cross-linking parasite assets to create a unified content ecosystem that reinforces VirtuaLab Digital\'s brand entity across the web.', s_body))

calendar_data = [
    ['Week 1-2', 'Foundation', 'Set up LinkedIn, Medium, YouTube, Reddit, Quora, GBP profiles. Publish 2 LinkedIn articles, 1 Medium article, 1 YouTube video.'],
    ['Week 3-4', 'Launch', 'Publish 2 LinkedIn articles, 1 Medium article, 1 YouTube video. Begin Reddit participation in r/localseo. Launch GBP posting.'],
    ['Week 5-8', 'Consistency', '2 LinkedIn articles/month, 2 Medium articles/month, 2 YouTube videos/month. Weekly Reddit and Quora participation. Bi-weekly GBP posts.'],
    ['Week 9-12', 'Optimization', 'Analyze parasite page performance. Refine underperforming content. Cross-link between platforms. Amplify top performers.'],
    ['Ongoing (90+)', 'Scale', 'Maintain cadence. Add new platforms (e.g., Substack, Beehiiv). Expand into industry-specific communities. Measure LLM citation growth.'],
]

t8 = make_table(
    ['Timeline', 'Phase', 'Actions'],
    calendar_data,
    col_widths=[60, 60, CONTENT_W - 120]
)
story.append(t8)

story.append(PageBreak())

# ========================
# CHAPTER 6: ASYMMETRICAL SEO STRATEGY
# ========================
story.append(Paragraph('6. Asymmetrical SEO Strategy', s_h1))
story.append(sp(6))

story.append(Paragraph('6.1 Asymmetrical Advantage Framework', s_h2))
story.append(Paragraph(
    'Asymmetrical SEO is the practice of exploiting structural gaps, technical inefficiencies, and content deficiencies in competitor strategies to achieve disproportionate visibility gains with fewer resources. Rather than attempting to outspend established agencies like Hook Agency, Rival Digital, or Scorpion on their own terms, VirtuaLab Digital leverages technical sophistication, emerging trend adoption, and platform diversity to create advantages that larger, slower-moving competitors cannot easily replicate. The core asymmetries are organized into five pillars: Technical Architecture Superiority, Generative Engine Optimization (GEO) First-Mover Advantage, Parasite Platform Multi-Surface Presence, Modular Transparent Pricing (versus opaque competitor models), and Suburban Market Specialization (versus generalist agency positioning).', s_body))

story.append(Paragraph('6.2 Competitive Gap Analysis', s_h2))
comp_data = [
    ['Hook Agency', 'hookagency.com', 'High visual appeal; roofing/HVAC specialization', 'Revenue threshold ($1M+); no CRM integration; 12-month contract locks', 'No GEO/AEO education; no transparent pricing; no AI search readiness'],
    ['Rival Digital', 'rivaldigital.com', 'Nexstar partnerships; founder books', 'High pricing; multi-service scope overwhelming', 'No plain-English local SEO guides; no technical mechanic breakdowns'],
    ['Blue Corona', 'bluecorona.com', 'Data-driven tracking; deep consulting', 'High entry pricing; paid ad focus', 'No structured GEO optimization; sales-heavy content'],
    ['Scorpion', 'scorpion.com', 'Regional franchise dominance', 'Proprietary platform limits portability', 'Brand promotion over education; no client ownership guarantee'],
    ['RYNO Strategic', 'rynoss.com', 'Scalable multi-channel; call tracking', 'Enterprise-focused; complex packages', 'Paid media focus; no clear local SEO guides for mid-market'],
    ['PlumberSEO.net', 'plumberseo.net', '7.1M leads generated; 3x Inc. 5000', 'Sales-heavy hero; traditional video testimonials', 'No un-gated technical breakdowns; no GEO/AI optimization'],
    ['Sequoia GEO', 'sequoiageo.com', 'HVAC to $17M; 4x Inc. 5000', 'Boutique scale limits capacity', 'No diagnostic tools; no standardized trade templates'],
]

t9 = make_table(
    ['Competitor', 'Domain', 'Core Strengths', 'Key Weaknesses', 'VirtuaLab Advantage'],
    comp_data,
    col_widths=[60, 62, 90, 90, CONTENT_W - 302]
)
story.append(t9)

story.append(Paragraph('6.3 Five Pillars of Asymmetrical Advantage', s_h2))
story.append(Paragraph(
    '<b>Pillar 1 - Technical Architecture Superiority:</b> Every VirtuaLab client site is built with clean code, proper schema markup (LocalBusiness, ProfessionalService, FAQPage), optimized Core Web Vitals, and an llms.txt file at the root directory. This technical foundation exceeds what most competitors offer at any price point, creating a structural advantage that compounds over time as search engines increasingly reward technically sound sites. The site architecture follows the hub-and-spoke model with programmatic internal linking, ensuring that topical authority flows efficiently from the homepage through every service, industry, and resource page.', s_body))

story.append(Paragraph(
    '<b>Pillar 2 - GEO First-Mover Advantage:</b> Academic research from Princeton and Georgia Tech (KDD 2024) demonstrates that targeted optimization including specific facts, structured lists, and cited sources can increase AI search visibility by up to 40%. VirtuaLab implements all nine GEO ranking factors: Statistics Addition, Source Citation, Quotation Addition, BLUF Formatting, Structured Extractability, Entity Authority, Bing Indexing, Content Freshness, and llms.txt implementation. While competitors are still optimizing for traditional blue-link SEO, VirtuaLab is positioning clients for the AI-driven search landscape that 45% of consumers already use for local recommendations.', s_body))

story.append(Paragraph(
    '<b>Pillar 3 - Parasite Multi-Surface Presence:</b> As detailed in Chapter 5, VirtuaLab maintains active content presences on LinkedIn, Medium, YouTube, Reddit, and Quora. This multi-surface strategy ensures brand visibility across every major platform that both users and AI engines consult. When Perplexity or ChatGPT retrieves information about "SEO for pest control companies" or "local SEO for HVAC," they encounter VirtuaLab\'s expertise across multiple independent sources, dramatically increasing citation probability and brand authority.', s_body))

story.append(Paragraph(
    '<b>Pillar 4 - Modular Transparent Pricing:</b> Unlike competitors who hide behind "contact us for pricing" or impose $1M+ revenue minimums, VirtuaLab offers transparent, modular pricing tiers. Standard website templates start at accessible price points while custom AI-ready designs are available for established operators. This transparency directly addresses the deep-seated skepticism that suburban operators feel toward digital marketing agencies, removing a major conversion barrier before the first conversation.', s_body))

story.append(Paragraph(
    '<b>Pillar 5 - Suburban Market Specialization:</b> VirtuaLab focuses exclusively on suburban local service markets, a segment that national agencies treat as an afterthought. This specialization enables deeper understanding of suburban search dynamics including centroid-based Map Pack behavior, emergency service search psychology, multi-suburb service area optimization, and the unique paid-ad-to-organic transition challenges that suburban operators face. Every piece of content, every technical recommendation, and every strategic playbook is purpose-built for the suburban context.', s_body))

story.append(PageBreak())

# ========================
# CHAPTER 7: SERP & LLM CITATION DOMINANCE
# ========================
story.append(Paragraph('7. SERP & LLM Citation Dominance Strategy', s_h1))
story.append(sp(6))

story.append(Paragraph('7.1 The LLM Citation Opportunity', s_h2))
story.append(Paragraph(
    'The Search Intelligence Report reveals that when high-intent B2B queries are executed across AI platforms, a small number of specialized agencies consistently dominate the citation graphs. The research identifies specific technical and structural signals that determine which sources LLMs choose to cite. Academic studies (Sadasivan et al. 2025) demonstrate that AI search retrieval systems exhibit a measurable bias toward third-party earned media and structured, fact-dense content. This means that a brand mentioned across multiple independent high-authority platforms (LinkedIn, Medium, industry publications, YouTube) with consistent entity references will be cited more frequently than a brand that exists only on its own website, regardless of the latter\'s domain authority.', s_body))

story.append(Paragraph(
    'The practical implication for VirtuaLab Digital is that the parasite SEO strategy described in Chapter 5 is not merely a traffic-generation tactic; it is the foundational infrastructure for LLM citation dominance. Every LinkedIn article, Medium publication, YouTube video, and Reddit answer that mentions VirtuaLab Digital in connection with relevant SEO expertise creates a new data point in the training and retrieval graphs that AI systems use to generate responses. Over time, this creates a compounding citation advantage where VirtuaLab becomes the default referenced entity for queries like "best SEO agency for pest control" or "how to optimize Google Maps for local service businesses."', s_body))

story.append(Paragraph('7.2 GEO Implementation Checklist', s_h2))
geo_data = [
    ['Statistics Addition', 'Critical', 'Include specific numbers (percentages, dollar amounts, review counts) in key content sections.', 'Paid Ad Trap & Maps Prominence sections', 'Princeton KDD 2024 paper'],
    ['Source Citation', 'High', 'Add inline citations linking to reputable studies (BrightLocal, Google research, Whitespark).', 'Throughout local search modules', 'Perplexity citation rules'],
    ['BLUF Formatting', 'Critical', 'State direct answers to common questions within the first 100 words of each section.', 'FAQ and Service-Area sections', 'Perplexity Sonar guidelines'],
    ['Structured Extractability', 'High', 'Use clear H2/H3 headers, bulleted lists, and HTML tables to group information.', 'Competitor and Glossary sections', 'AI crawler parsing rules'],
    ['Entity Authority', 'High', 'Focus on clear entity definitions linking services to specific trade niches.', 'Service and Industry Directories', 'RAG pipeline retrieval rules'],
    ['Bing Indexing', 'Critical', 'Verify site with Bing Webmaster Tools so ChatGPT/Copilot can crawl.', 'Global site indexing', 'ChatGPT retrieval mechanics'],
    ['Content Freshness', 'Medium', 'Regularly update data, reviews, and statistics to keep information current.', 'Global update schedule', 'Perplexity 30-day decay rule'],
    ['llms.txt File', 'High', 'Add llms.txt file to root directory to guide AI crawlers to best content.', 'Root directory (/llms.txt)', 'Emerging AI web standards'],
    ['Quotation Addition', 'Medium', 'Include expert quotes from recognized local SEO and trade business authorities.', 'Hero and Content Authority sections', 'GEO Best Practices'],
]

t10 = make_table(
    ['GEO Factor', 'Priority', 'Implementation', 'Target Location', 'Source'],
    geo_data,
    col_widths=[75, 42, 115, 75, CONTENT_W - 307]
)
story.append(t10)

story.append(Paragraph('7.3 Citation Tracking & Measurement', s_h2))
story.append(Paragraph(
    'Measuring LLM citation performance requires a fundamentally different approach than traditional SEO analytics. Instead of tracking keyword rankings and organic click-through rates, the focus shifts to citation frequency, citation context (positive, neutral, or negative), citation source diversity (how many different AI platforms reference the brand), and citation query alignment (which target queries trigger brand mentions in AI responses). The recommended tracking protocol involves weekly manual queries across ChatGPT, Perplexity, Google Gemini, and Google AI Overviews for a defined set of 50 target queries. Each query is logged with whether VirtuaLab Digital was mentioned, the context of the mention, and which source the AI cited to support its response. This data is compiled into a monthly Citation Dominance Score that tracks progress over time and identifies which content assets and parasite platforms are generating the most AI traction.', s_body))

story.append(PageBreak())

# ========================
# CHAPTER 8: IMPLEMENTATION ROADMAP
# ========================
story.append(Paragraph('8. Implementation Roadmap', s_h1))
story.append(sp(6))

story.append(Paragraph('8.1 The 7-30-90 Day Execution Plan', s_h2))

impl_data = [
    ['Day 1-7', 'Critical', 'Fix homepage spelling error ("DIRVEN" to "Driven"). Rewrite hero H1 to address structural search visibility. Implement multi-level navigation dropdowns. Add FAQPage schema markup.', 'Homepage'],
    ['Day 8-14', 'Critical', 'Rewrite all 6 service blocks with unique, fact-dense copy. Populate reusable blocks with dynamic case study statistics. Add industry-specific paragraphs for each trade in the Industries section.', 'Homepage + Services'],
    ['Day 15-21', 'High', 'Convert FAQ from hidden accordion to flat, fully readable layout. Implement llms.txt file at root directory. Verify Bing Webmaster Tools indexing. Add nested LocalBusiness schema to footer.', 'Technical'],
    ['Day 22-30', 'High', 'Publish first LinkedIn article and Medium publication. Launch YouTube channel with audit walkthrough video. Begin Reddit participation. Set up citation tracking protocol.', 'Parasite SEO'],
    ['Day 31-60', 'High', 'Build out /services/local-seo, /services/geo, and /services/technical-seo service pages with full keyword mapping. Create resource guides for GBP optimization, ad dependency, and page-2 syndrome.', 'Content + SEO'],
    ['Day 61-75', 'High', 'Launch industry landing pages for HVAC, roofing, plumbing, and pest control. Implement hub-and-spoke internal linking structure. Create keyword mapping template for each vertical.', 'Industry Pages'],
    ['Day 76-90', 'Medium', 'Analyze first-month citation data. Refine underperforming parasite content. Expand to 2 additional platforms. Compile first monthly Citation Dominance Report.', 'Analysis + Scale'],
    ['Ongoing', 'High', 'Maintain publishing cadence: 2 LinkedIn articles, 2 Medium articles, 2 YouTube videos, 4-6 Reddit/Quora answers per month. Update content freshness monthly. Quarterly competitor re-benchmarking.', 'Sustained Execution'],
]

t11 = make_table(
    ['Timeline', 'Priority', 'Actions', 'Focus Area'],
    impl_data,
    col_widths=[50, 42, CONTENT_W - 132, 40]
)
story.append(t11)

story.append(Paragraph('8.2 KPIs and Success Metrics', s_h2))
story.append(Paragraph(
    'The strategy is measured across four KPI categories that reflect the multi-surface search reality. Traditional Organic KPIs include organic traffic growth (target: 40% increase within 6 months), keyword ranking improvements for target cluster terms, and organic click-through rate from search results. Local Search KPIs include Google Maps Map Pack appearance rate, Google Business Profile engagement metrics (calls, direction requests, website clicks), and review velocity and average rating. AI Citation KPIs include Citation Dominance Score (tracked monthly across 50 target queries), citation source diversity (number of independent platforms referencing the brand), and AI-driven referral traffic to the primary domain. Business Impact KPIs include cost-per-lead reduction over baseline, organic lead-to-booked-job conversion rate, and client retention rate. Each KPI is tracked in a centralized dashboard that connects search performance data to actual business outcomes through CRM integration with platforms like ServiceTitan and Housecall Pro.', s_body))

kpi_data = [
    ['Organic Traffic Growth', '40% increase in 6 months', 'Google Search Console', 'Monthly'],
    ['Target Keyword Rankings', 'Top 10 for 15+ cluster head terms', 'Ahrefs / SEMrush', 'Bi-weekly'],
    ['Map Pack Appearance Rate', 'Appear in Map Pack for 10+ target suburbs', 'Local Falcon / BrightLocal', 'Weekly'],
    ['Citation Dominance Score', 'Mentioned in 20%+ of target AI queries', 'Manual AI Query Tracking', 'Monthly'],
    ['Citation Source Diversity', 'Brand present on 5+ independent platforms', 'Cross-platform audit', 'Monthly'],
    ['Cost-Per-Lead Reduction', '25% reduction from baseline within 6 months', 'CRM / GHL Analytics', 'Monthly'],
    ['Review Velocity', '5+ new reviews per month per GBP', 'Google Business Profile', 'Weekly'],
    ['Parasite Content Impressions', '100K+ monthly impressions across platforms', 'LinkedIn Analytics, YouTube Studio', 'Monthly'],
]

t12 = make_table(
    ['KPI', 'Target', 'Measurement Tool', 'Frequency'],
    kpi_data,
    col_widths=[100, 120, 95, CONTENT_W - 315]
)
story.append(t12)

story.append(PageBreak())

# ========================
# CHAPTER 9: BUYER PERSONA & CONVERSION STRATEGY
# ========================
story.append(Paragraph('9. Buyer Persona & Conversion Strategy', s_h1))
story.append(sp(6))

story.append(Paragraph('9.1 Primary Buyer Persona Summary', s_h2))
persona_data = [
    ['Primary Buyer', 'Operator, founder, or general manager of a suburban residential or commercial service business.'],
    ['Business Type', 'Suburban home improvement, trade, or professional service firm with 5-50 employees.'],
    ['Annual Revenue', '$1M to $10M (sweet spot), spending $2,000-$10,000/month on paid ads.'],
    ['Main Problem', 'Overdependence on paid ad channels (Google Ads, LSAs, Angi, Yelp) and low organic visibility.'],
    ['Emotional Frustration', 'Feeling trapped by expensive paid lead providers and unverified agency metrics.'],
    ['Main Objection', '"We have spent thousands on SEO agencies in the past with nothing to show for it."'],
    ['Buying Trigger', 'Sudden drop in Maps visibility or sharp spike in cost-per-click ad rates.'],
    ['Trust Requirement', 'Clear, honest process audits instead of unrealistic ranking guarantees.'],
    ['Best CTA', 'Free, step-by-step local visibility and technical website audit (delivered in 48 hours).'],
    ['Content Pathway', 'Structured service directory aligned with specific growth bottlenecks.'],
]

t13 = make_table(
    ['Persona Element', 'Target Profile Summary'],
    persona_data,
    col_widths=[100, CONTENT_W - 100]
)
story.append(t13)

story.append(Paragraph('9.2 Non-Aggressive Conversion Strategy', s_h2))
story.append(Paragraph(
    'The conversion pathways on the homepage are designed to build trust gradually rather than pushing for an immediate sales call. CTAs are ranked from most educational (lowest friction) to most transactional (highest commitment). The first and most prominent CTA is the "Run a Website Diagnostic Check" tool, which allows visitors to verify their local digital foundations with zero friction and no gate. This is followed by "Explore Digital Growth Tracks" which guides visitors to the educational knowledge hub. The third CTA is "Compare Service and Website Frameworks" which educates users on pricing transparency. The fourth is "Review Search Patterns" inside industry directory blocks. The fifth is a "Strategic FAQ Portal" that provides direct answers. The final CTA is "Request Strategy Audit" for visitors who have consumed enough content to trust the agency. This graduated approach respects the operator\'s high skepticism and slow decision-making process while ensuring that every interaction adds value.', s_body))

cta_data = [
    ['1. Site Diagnostic Check', 'Lowest', 'Run a Website Diagnostic Check', 'Hero section, above-the-fold', 'Completely automated, un-gated technical check.'],
    ['2. Explore Learning Tracks', 'Low', 'Explore Our Digital Growth Tracks', 'Below Hero introduction', 'Directs traffic deep into resource siloes.'],
    ['3. Compare Pricing Scopes', 'Medium', 'Compare Service and Website Frameworks', 'Service Directory section', 'Provides factual pricing and scope transparency.'],
    ['4. Industry Specific Guide', 'Medium', 'Review Search Patterns', 'Inside Industry Directory blocks', 'Tailors journey to user specific vertical.'],
    ['5. Strategic FAQ Portal', 'Medium-High', 'Browse the Local Search Knowledge Base', 'Below FAQ section', 'Self-service education with deep answers.'],
    ['6. Request Strategy Audit', 'Highest', 'Request a Local Visibility Audit (48 Hours)', 'Footer + final section', 'Only after user has consumed educational content.'],
]

t14 = make_table(
    ['CTA / Element', 'Friction Level', 'Suggested Copy', 'Placement', 'Notes'],
    cta_data,
    col_widths=[80, 50, 100, 70, CONTENT_W - 300]
)
story.append(t14)

story.append(PageBreak())

# ========================
# CHAPTER 10: EXPANDED KEYWORD DATABASE
# ========================
story.append(Paragraph('10. Expanded Keyword Database', s_h1))
story.append(sp(6))

story.append(Paragraph(
    'This chapter provides the comprehensive keyword database organized by vertical. Each keyword has been validated against current search trends, competitor gaps, and AI search behavior patterns. Keywords marked with high business potential are prioritized for immediate content development. Keywords marked as emerging represent forward-looking opportunities where early content creation can establish first-mover authority before competition intensifies.', s_body))

story.append(Paragraph('10.1 HVAC & Air Conditioning Keywords', s_h3))
hvac_kw = [
    ['hvac digital marketing agency', 'Commercial', 'Medium', 'High', 'High', '/industries/hvac'],
    ['hvac seo company', 'Commercial', 'Medium', 'High', 'High', '/industries/hvac'],
    ['hvac google maps ranking', 'Informational', 'Medium', 'Medium', 'High', '/resources/hvac-maps'],
    ['hvac lead generation strategies', 'Informational', 'Medium', 'Medium', 'High', '/resources/hvac-leads'],
    ['ac repair near me seo', 'Local', 'High', 'High', 'Medium', '/industries/hvac'],
    ['furnace replacement SEO content', 'Informational', 'Low', 'Low', 'Medium', '/resources/hvac-content'],
    ['hvac seasonal marketing calendar', 'Informational', 'Low', 'Low', 'High', '/resources/hvac-seasonal'],
    ['hvac website design conversion rate', 'Commercial', 'Medium', 'Medium', 'Medium', '/services/web-design'],
    ['servicetitan hvac integration', 'Technical', 'Low', 'Low', 'High', '/services/crm-automation'],
    ['hvac review generation strategy', 'Informational', 'Medium', 'Low', 'High', '/resources/review-strategy'],
]
t15 = make_table(
    ['Keyword', 'Intent', 'Demand', 'Difficulty', 'Business Potential', 'Target Page'],
    hvac_kw,
    col_widths=[100, 55, 42, 50, 55, CONTENT_W - 302]
)
story.append(t15)
story.append(sp(8))

story.append(Paragraph('10.2 Pest Control Keywords (LLM Citation Priority)', s_h3))
pest_kw = [
    ['pest control seo agency', 'Commercial', 'High', 'Medium', 'High', '/industries/pest-control'],
    ['pest control company marketing', 'Commercial', 'High', 'Medium', 'High', '/industries/pest-control'],
    ['exterminator digital marketing', 'Commercial', 'Medium', 'Medium', 'High', '/industries/pest-control'],
    ['pest control google maps optimization', 'Informational', 'Medium', 'Low', 'High', '/resources/pest-maps'],
    ['bed bug control seo content', 'Informational', 'Medium', 'Low', 'Medium', '/resources/pest-content'],
    ['pest control seasonal demand SEO', 'Informational', 'Low', 'Low', 'High', '/resources/pest-seasonal'],
    ['termite treatment marketing strategy', 'Informational', 'Low', 'Low', 'Medium', '/resources/pest-termite'],
    ['pest control review management', 'Informational', 'Medium', 'Low', 'High', '/resources/review-strategy'],
]
t16 = make_table(
    ['Keyword', 'Intent', 'Demand', 'Difficulty', 'Business Potential', 'Target Page'],
    pest_kw,
    col_widths=[100, 55, 42, 50, 55, CONTENT_W - 302]
)
story.append(t16)
story.append(sp(8))

story.append(Paragraph('10.3 Emerging GEO & AI Search Keywords', s_h3))
geo_kw = [
    ['generative engine optimization strategies', 'Informational', 'Emerging', 'Low', 'High', '/services/geo'],
    ['how to get cited by perplexity ai', 'Informational', 'Emerging', 'Low', 'High', '/resources/perplexity-seo'],
    ['AI search optimization for local business', 'Informational', 'Emerging', 'Low', 'High', '/services/geo'],
    ['llms.txt file implementation', 'Technical', 'Emerging', 'Low', 'High', '/resources/llms-guide'],
    ['ChatGPT citation optimization', 'Technical', 'Emerging', 'Low', 'Medium', '/resources/chatgpt-seo'],
    ['Google AI Overviews ranking factors', 'Informational', 'Emerging', 'Low', 'High', '/resources/ai-overviews'],
    ['entity-based SEO for local business', 'Informational', 'Emerging', 'Low', 'High', '/resources/entity-seo'],
    ['semantic search optimization 2026', 'Informational', 'Emerging', 'Low', 'Medium', '/resources/semantic-seo'],
]
t17 = make_table(
    ['Keyword', 'Intent', 'Demand', 'Difficulty', 'Business Potential', 'Target Page'],
    geo_kw,
    col_widths=[100, 55, 42, 50, 55, CONTENT_W - 302]
)
story.append(t17)

story.append(PageBreak())

# ========================
# CHAPTER 11: STRUCTURED DATA & TECHNICAL SPECIFICATIONS
# ========================
story.append(Paragraph('11. Structured Data & Technical Specifications', s_h1))
story.append(sp(6))

story.append(Paragraph('11.1 Schema Markup Architecture', s_h2))
story.append(Paragraph(
    'Structured data implementation is a critical asymmetrical advantage that most competitors neglect. The VirtuaLab Digital website implements a comprehensive JSON-LD schema architecture that includes nested entity relationships between the organization, its services, its target industries, and its team members. The primary schema types deployed include ProfessionalService (for the agency itself), Service (for each offering with detailed description and pricing range), FAQPage (for homepage and service page FAQs), LocalBusiness (for geographic targeting), Organization (for brand entity definition), and Article (for blog posts and resource guides). Each schema is validated using Google\'s Rich Results Test and embedded with accurate entity references that support both traditional search rich results and AI engine entity extraction.', s_body))

schema_data = [
    ['ProfessionalService', 'Homepage', 'Agency name, services, areas served, pricing range, aggregate rating', 'Rich result with service details and reviews'],
    ['FAQPage', 'Homepage + Service Pages', 'Question-answer pairs from PAA research', 'FAQ rich results in SERP; direct answers for AI extraction'],
    ['Service', 'Each /services/ page', 'Service name, description, provider, area served', 'Service rich cards; entity authority for service terms'],
    ['LocalBusiness', 'Footer + Industry Pages', 'Business name, address, phone, geo coordinates, hours', 'Maps integration; local entity co-occurrence signals'],
    ['Article', 'Blog + Resource pages', 'Headline, author, datePublished, image, description', 'Article rich results; content freshness signals for AI'],
    ['BreadcrumbList', 'All pages', 'Page hierarchy from homepage to current page', 'Breadcrumb rich results; navigation clarity for crawlers'],
    ['Organization', 'Global (header)', 'Brand name, logo, URL, sameAs (social profiles)', 'Brand entity definition for Knowledge Panel and AI recognition'],
]

t18 = make_table(
    ['Schema Type', 'Deployment', 'Key Properties', 'Search Benefit'],
    schema_data,
    col_widths=[75, 70, 150, CONTENT_W - 295]
)
story.append(t18)

story.append(Paragraph('11.2 Internal Linking Architecture', s_h2))
story.append(Paragraph(
    'The internal linking structure follows a strict hub-and-spoke model designed to distribute topical authority efficiently. The homepage serves as the master hub with contextual links to every service page, industry page, and major resource guide. Each service page links to its related industry pages and supporting resource guides. Each industry page links to its related service pages and vertical-specific blog content. Resource guides link to relevant service pages with conversion-oriented CTAs. This creates a dense mesh of contextual internal links that signals to search engines the comprehensive topical coverage of VirtuaLab Digital\'s domain. The linking structure avoids orphan pages, ensures every page is reachable within 3 clicks from the homepage, and uses descriptive anchor text that reinforces target keyword clusters rather than generic "click here" or "read more" patterns.', s_body))

story.append(Paragraph('11.3 Cloud Stacking & Tiered Authority Building', s_h2))
story.append(Paragraph(
    'Cloud stacking is an advanced off-site strategy that creates a network of interlinked web properties on high-authority cloud platforms (Google Cloud, Amazon Web Services, Microsoft Azure) to build tiered authority that flows back to the primary domain. Each cloud property is configured as a static web asset containing optimized content, schema markup, and contextual backlinks. These cloud properties are then interlinked with each other and with the primary domain, creating a powerful authority funnel. For VirtuaLab Digital, the cloud stacking strategy is implemented in three tiers: Tier 1 consists of the primary domain and its parasite platform profiles (LinkedIn, Medium, YouTube). Tier 2 consists of cloud-hosted resource hubs on Google Sites and similar platforms. Tier 3 consists of curated link aggregators and directory listings. This tiered approach creates a defensible authority network that compounds over time and is extremely difficult for competitors to replicate.', s_body))

# ========================
# BUILD
# ========================
doc.build(story)
print(f'PDF generated successfully: {output_path}')
print(f'Pages: {doc.page}')
