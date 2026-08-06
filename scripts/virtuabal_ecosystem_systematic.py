#!/usr/bin/env python3
"""
VirtuaLab Digital Ecosystem Systematic Architecture PDF
Generates a comprehensive system blueprint document.
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.graphics.shapes import Drawing, Line, Rect, String, Circle
from reportlab.graphics import renderPDF

# ── Font Registration ──
FONT_DIR = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('LibSans', f'{FONT_DIR}/truetype/liberation/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LibSans-Bold', f'{FONT_DIR}/truetype/liberation/LiberationSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LibSans-Italic', f'{FONT_DIR}/truetype/liberation/LiberationSans-Italic.ttf'))
pdfmetrics.registerFont(TTFont('LibSans-BoldItalic', f'{FONT_DIR}/truetype/liberation/LiberationSans-BoldItalic.ttf'))
registerFontFamily('LibSans', normal='LibSans', bold='LibSans-Bold', italic='LibSans-Italic', boldItalic='LibSans-BoldItalic')

# ── Cascade Palette ──
PAGE_BG       = colors.HexColor('#f3f4f4')
SECTION_BG    = colors.HexColor('#edeeef')
CARD_BG       = colors.HexColor('#e3e6e8')
TABLE_STRIPE  = colors.HexColor('#eff1f2')
HEADER_FILL   = colors.HexColor('#486a7b')
COVER_BLOCK   = colors.HexColor('#567482')
BORDER        = colors.HexColor('#c8d3d8')
ICON          = colors.HexColor('#3d7692')
ACCENT        = colors.HexColor('#3787af')
ACCENT_2      = colors.HexColor('#d07556')
TEXT_PRIMARY   = colors.HexColor('#191b1c')
TEXT_MUTED     = colors.HexColor('#757c7f')
SEM_SUCCESS   = colors.HexColor('#42995f')
SEM_WARNING   = colors.HexColor('#a48443')
SEM_ERROR     = colors.HexColor('#a15852')
SEM_INFO      = colors.HexColor('#557da6')
WHITE         = colors.white

# ── Styles ──
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    'CoverTitle', fontName='LibSans-Bold', fontSize=36, leading=42,
    textColor=WHITE, alignment=TA_LEFT, spaceAfter=6
))
styles.add(ParagraphStyle(
    'CoverSubtitle', fontName='LibSans', fontSize=16, leading=22,
    textColor=colors.HexColor('#b0c4d0'), alignment=TA_LEFT, spaceAfter=4
))
styles.add(ParagraphStyle(
    'CoverMeta', fontName='LibSans', fontSize=12, leading=16,
    textColor=colors.HexColor('#8aa8b8'), alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    'H1', fontName='LibSans-Bold', fontSize=22, leading=28,
    textColor=HEADER_FILL, spaceBefore=20, spaceAfter=10,
    borderPadding=(0, 0, 4, 0)
))
styles.add(ParagraphStyle(
    'H2', fontName='LibSans-Bold', fontSize=16, leading=22,
    textColor=ACCENT, spaceBefore=14, spaceAfter=8
))
styles.add(ParagraphStyle(
    'H3', fontName='LibSans-Bold', fontSize=12, leading=16,
    textColor=ICON, spaceBefore=10, spaceAfter=6
))
styles.add(ParagraphStyle(
    'Body', fontName='LibSans', fontSize=10, leading=15,
    textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=6
))
styles.add(ParagraphStyle(
    'BodyBold', fontName='LibSans-Bold', fontSize=10, leading=15,
    textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=6
))
styles.add(ParagraphStyle(
    'BulletItem', fontName='LibSans', fontSize=10, leading=14,
    textColor=TEXT_PRIMARY, leftIndent=20, bulletIndent=8,
    spaceAfter=3, bulletFontName='LibSans', bulletFontSize=10
))
styles.add(ParagraphStyle(
    'SmallText', fontName='LibSans', fontSize=8, leading=11,
    textColor=TEXT_MUTED, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    'TableHeader', fontName='LibSans-Bold', fontSize=9, leading=12,
    textColor=WHITE, alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    'TableCell', fontName='LibSans', fontSize=8.5, leading=12,
    textColor=TEXT_PRIMARY, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    'TableCellCenter', fontName='LibSans', fontSize=8.5, leading=12,
    textColor=TEXT_PRIMARY, alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    'CodeBlock', fontName='LibSans', fontSize=8, leading=11,
    textColor=colors.HexColor('#2d3748'), backColor=colors.HexColor('#f7f8fa'),
    leftIndent=12, rightIndent=12, spaceBefore=6, spaceAfter=6,
    borderPadding=(6, 6, 6, 6)
))
styles.add(ParagraphStyle(
    'Caption', fontName='LibSans-Italic', fontSize=8, leading=11,
    textColor=TEXT_MUTED, alignment=TA_LEFT, spaceBefore=4, spaceAfter=8
))
styles.add(ParagraphStyle(
    'TOCEntry', fontName='LibSans', fontSize=11, leading=18,
    textColor=TEXT_PRIMARY, leftIndent=0, spaceAfter=2
))
styles.add(ParagraphStyle(
    'TOCEntry2', fontName='LibSans', fontSize=10, leading=16,
    textColor=TEXT_MUTED, leftIndent=20, spaceAfter=1
))

# ── Helpers ──
def make_table(headers, rows, col_widths=None):
    """Create a styled table with header row."""
    avail_w = 460
    if col_widths is None:
        n = len(headers)
        col_widths = [avail_w / n] * n
    
    hdr_cells = [Paragraph(h, styles['TableHeader']) for h in headers]
    data = [hdr_cells]
    for row in rows:
        data.append([Paragraph(str(c), styles['TableCell']) if i == 0 else Paragraph(str(c), styles['TableCellCenter']) if len(str(c)) < 20 else Paragraph(str(c), styles['TableCell']) for i, c in enumerate(row)])
    
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_FILL),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'LibSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_STRIPE))
    t.setStyle(TableStyle(style_cmds))
    return t

def h1(text):
    return Paragraph(text, styles['H1'])

def h2(text):
    return Paragraph(text, styles['H2'])

def h3(text):
    return Paragraph(text, styles['H3'])

def body(text):
    return Paragraph(text, styles['Body'])

def bullet(text):
    return Paragraph(text, styles['BulletItem'])

def bold_body(text):
    return Paragraph(text, styles['BodyBold'])

def small(text):
    return Paragraph(text, styles['SmallText'])

def code(text):
    return Paragraph(text, styles['CodeBlock'])

def caption(text):
    return Paragraph(text, styles['Caption'])

def spacer(h=6):
    return Spacer(1, h)

def section_divider():
    return HRFlowable(width="100%", thickness=1, color=BORDER, spaceBefore=12, spaceAfter=12)

# ── Page numbering ──
def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('LibSans', 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawRightString(A4[0] - 40*mm, 15*mm, f"Page {doc.page}")
    canvas.drawString(40*mm, 15*mm, "VirtuaLab Digital | Ecosystem Systematic Architecture")
    canvas.restoreState()

# ── Cover Page (ReportLab-based) ──
def build_cover():
    elements = []
    d = Drawing(460, 670)
    # Background
    d.add(Rect(0, 0, 460, 670, fillColor=HEADER_FILL, strokeColor=None))
    # Decorative block
    d.add(Rect(0, 350, 460, 320, fillColor=COVER_BLOCK, strokeColor=None))
    # Accent line
    d.add(Line(50, 375, 410, 375, strokeColor=ACCENT, strokeWidth=3))
    # Grid dots
    for x in range(50, 460, 30):
        for y in range(30, 670, 30):
            d.add(Circle(x, y, 0.8, fillColor=colors.HexColor('#ffffff10'), strokeColor=None))
    
    d.add(String(60, 580, "SYSTEMATIC ARCHITECTURE", fontName='LibSans', fontSize=12, fillColor=colors.HexColor('#8ab8d0')))
    d.add(String(60, 520, "VirtuaLab Digital", fontName='LibSans-Bold', fontSize=38, fillColor=WHITE))
    d.add(String(60, 475, "Ecosystem Blueprint", fontName='LibSans-Bold', fontSize=38, fillColor=WHITE))
    d.add(String(60, 420, "AISEO Framework | Eli-OS Agent Mesh | Baserow + n8n + GHL", fontName='LibSans', fontSize=13, fillColor=colors.HexColor('#b0c4d0')))
    d.add(String(60, 320, 'Converting 75-tab strategic blueprint into a repeatable, data-driven operating system for asymmetric and parasitic SEO.', fontName='LibSans', fontSize=11, fillColor=colors.HexColor('#c0d4e0')))
    d.add(String(60, 60, "Prepared by: Asymmetric SEO Strategist & Parasite SEO Strategist", fontName='LibSans', fontSize=9, fillColor=colors.HexColor('#8aa8b8')))
    d.add(String(60, 42, "Date: August 2026 | Classification: Internal Operations", fontName='LibSans', fontSize=9, fillColor=colors.HexColor('#8aa8b8')))
    d.add(String(60, 24, "Version: 1.0 | Status: SYSTEMATIC APPROACH FOUNDATION", fontName='LibSans', fontSize=9, fillColor=colors.HexColor('#8aa8b8')))
    elements.append(d)
    elements.append(PageBreak())
    return elements

# ── TOC ──
def build_toc():
    elements = []
    elements.append(h1("Table of Contents"))
    elements.append(spacer(8))
    toc_entries = [
        ("1", "Executive Summary: Why Systematic, Not Guessing"),
        ("2", "Current State Assessment: The 75-Tab Blueprint Dissection"),
        ("3", "The Eli-OS Agent Operating System"),
        ("  3.1", "12-Agent Fleet Architecture"),
        ("  3.2", "Rust Control Plane: Policy Engine & IPC"),
        ("  3.3", "SKILL.md Governance Paradigm"),
        ("4", "Baserow Database Schema: Single Source of Truth"),
        ("  4.1", "Master Data Tables"),
        ("  4.2", "Client & Campaign Management"),
        ("  4.3", "Content Operations Tables"),
        ("  4.4", "Off-Page & Parasite SEO Tables"),
        ("  4.5", "Technical SEO & Indexing Tables"),
        ("  4.6", "GEO & AI Citation Tracking Tables"),
        ("  4.7", "Reporting & Analytics Tables"),
        ("5", "n8n Workflow Automation: The Nervous System"),
        ("  5.1", "Client Onboarding Pipeline"),
        ("  5.2", "Keyword Research & Clustering Pipeline"),
        ("  5.3", "Content Production & Publishing Pipeline"),
        ("  5.4", "Parasite SEO Distribution Pipeline"),
        ("  5.5", "GEO Citation Monitoring Pipeline"),
        ("  5.6", "Client Reporting Pipeline"),
        ("6", "GHL / GoHighLevel CRM Integration"),
        ("  6.1", "Lead Attribution Architecture"),
        ("  6.2", "Automated Follow-Up Sequences"),
        ("  6.3", "Pipeline Stage Tracking"),
        ("7", "Asymmetric SEO Systematic Methodology"),
        ("  7.1", "Structural Gap Exploitation Framework"),
        ("  7.2", "Non-Linear Competitive Advantage Model"),
        ("8", "Parasite SEO Systematic Methodology"),
        ("  8.1", "Platform Scoring & TOS Compliance"),
        ("  8.2", "Content Distribution Orchestration"),
        ("9", "GEO (Generative Engine Optimization) System"),
        ("  9.1", "Citation Probability Model"),
        ("  9.2", "BLUF Content Formatting Standard"),
        ("  9.3", "llms.txt Implementation"),
        ("10", "Content Operations System"),
        ("  10.1", "7-Platform AI Review Workflow"),
        ("  10.2", "Semantic Writing Standards"),
        ("11", "Free Tools Ecosystem"),
        ("12", "Implementation Roadmap: 6-Week Deployment"),
        ("13", "Data Flow Architecture"),
        ("14", "Governance, Escalation & Quality Assurance"),
    ]
    for num, title in toc_entries:
        if num.strip().startswith("  "):
            elements.append(Paragraph(f"{num.strip()} {title}", styles['TOCEntry2']))
        else:
            elements.append(Paragraph(f"<b>{num}.</b>  {title}", styles['TOCEntry']))
    elements.append(PageBreak())
    return elements

# ── Main Content ──
def build_content():
    e = []  # elements

    # ══════════════════════════════════════════════════
    # CHAPTER 1: EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════
    e.append(h1("1. Executive Summary: Why Systematic, Not Guessing"))
    e.append(body(
        "The VirtuaLab Digital ecosystem has reached a critical inflection point. The current operational model relies on "
        "manual execution of strategic blueprints spread across 75 Google Doc tabs, multiple AI platform conversations, "
        "and tribal knowledge held by individual operators. This approach produces outputs that are, by definition, "
        "non-repeatable and non-scalable. Each new client engagement requires starting from scratch, re-analyzing the same "
        "competitor landscapes, re-mapping the same keyword universes, and re-creating the same content briefs. "
        "The result is what the principal correctly identified as 'guessing' rather than systematic operations."
    ))
    e.append(body(
        "This document establishes the <b>SYSTEMATIC APPROACH</b> foundation. It transforms the 75-tab AISEO Framework, "
        "the Eli-OS agent delivery package, and all strategic research into a single, unified, machine-executable operating system. "
        "Every strategic decision, every keyword cluster, every content brief, and every client deliverable traces back to "
        "structured data in Baserow, automated workflows in n8n, and CRM tracking in GoHighLevel. The system eliminates "
        "ad-hoc reasoning by replacing it with data pipelines that produce consistent, auditable, and improvable outputs."
    ))
    e.append(body(
        "The architecture described herein comprises four interlocking layers. First, the <b>Eli-OS Agent Fleet</b> provides "
        "12 specialized AI agents governed by a Rust-based control plane with SKILL.md manifests that define exact "
        "permissions, escalation triggers, and resource limits for each agent. Second, a <b>Baserow Database Schema</b> of "
        "40+ tables serves as the single source of truth for all client data, keyword research, content operations, competitor "
        "intelligence, and performance metrics. Third, <b>n8n Workflow Automation</b> connects these data stores into "
        "repeatable pipelines that execute the content production, parasite SEO distribution, GEO monitoring, and client "
        "reporting cycles without manual intervention. Fourth, <b>GHL CRM Integration</b> closes the loop between "
        "search visibility work and actual business outcomes by attributing leads, tracking pipeline stages, and automating "
        "client communications."
    ))
    e.append(spacer(8))
    e.append(bold_body("The Core Problem This Solves:"))
    e.append(body(
        "Without this systematic foundation, every strategy document is a one-time artifact based on assumptions. "
        "With this foundation, every strategy document is an output of a data pipeline that incorporates real competitor "
        "data, verified search volumes, tracked citation rates, and measured business outcomes. The difference is "
        "the difference between guessing and knowing."
    ))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 2: CURRENT STATE ASSESSMENT
    # ══════════════════════════════════════════════════
    e.append(h1("2. Current State Assessment: The 75-Tab Blueprint Dissection"))
    e.append(body(
        "The AISEO-VirtuaLab Digital Framework Google Doc contains 75 tabs organized into 11 top-level sections. "
        "Each tab represents a strategic component, but the connections between them are implicit and undocumented. "
        "The following dissection maps every tab to its functional category, identifies the data dependencies, and "
        "specifies the exact Baserow table and n8n workflow that will systematize it. This mapping ensures zero knowledge "
        "loss during the transition from document-based to system-based operations."
    ))
    e.append(spacer(4))
    e.append(h2("2.1 Complete Tab-to-System Mapping"))
    
    tab_data = [
        ("VirtuaLab Digital the SEO AI Scientist", "Brand Identity", "brand_settings", "Static config", "Defines core positioning, 6 AI agent roles, tech stack"),
        ("Proposed Home Page", "Website Architecture", "page_templates", "Content Pipeline", "14-section semantic knowledge hub blueprint"),
        ("Tools to Offer As Free", "Lead Generation", "free_tools_registry", "n8n: Tool Deploy", "ROI Calculator, Proximity Visualizer, Lead Matrix"),
        ("Case Study Narrative", "Social Proof", "case_studies", "Content Pipeline", "Photo recommendations, narrative templates per niche"),
        ("VirtuaLab Tools Repository", "Product Suite", "tool_configs", "Static config", "7 tools: All-in-One SEO, Semantic Writing, Technical SEO, etc."),
        ("Off Page Foundation", "Off-Page SEO", "off_page_strategies", "Parasite Pipeline", "YouTube SEO, platform strategies, asset management"),
        ("Growth Campaign", "Campaign Mgmt", "campaigns", "Campaign Pipeline", "GHL integration, AI Citation, Month 2-3 content calendars"),
        ("White Label Parasite SEO", "Parasite SEO", "parasite_campaigns", "Parasite Pipeline", "Soc Med Strat, Google Discover, Platform Optimizer"),
        ("Data Ingestion for Citation", "GEO", "geo_data_ingestion", "GEO Pipeline", "Global Footer JS, citation data collection"),
        ("Core Industry Pages Optimization", "On-Page", "industry_pages", "Content Pipeline", "Programmatic Hub Pages, page templates"),
        ("Core Service Pages Configuration", "Services", "service_pages", "Content Pipeline", "Automation Pages, service configurations"),
        ("Final Home Configuration", "Website", "page_templates", "Content Pipeline", "Final homepage layout specifications"),
        ("Technical Integration", "Tech Stack", "tech_integrations", "n8n: Tech Audit", "API connections, webhook configs"),
        ("Internal Link Structure", "Site Architecture", "internal_links", "n8n: Link Audit", "Slug patterns, link hierarchy"),
        ("Visibility Page Architecture", "Architecture", "visibility_pages", "Content Pipeline", "Programmatic hub page design"),
        ("Conversion Page", "CRO", "conversion_pages", "Content Pipeline", "Conversion optimization templates"),
    ]
    
    e.append(make_table(
        ["Tab Name", "Category", "Baserow Table", "n8n Workflow", "Key Content"],
        tab_data,
        [95, 65, 75, 65, 160]
    ))
    e.append(caption("Table 2.1: Primary Tab-to-System Mapping (16 of 75 tabs shown; remaining tabs are sub-tabs)"))
    
    e.append(h2("2.2 Identified Gaps in the Current Blueprint"))
    e.append(body(
        "The current 75-tab framework, while comprehensive in strategic vision, contains several critical gaps that "
        "prevent systematic execution. These gaps are not oversights in strategy but rather the natural result of "
        "a document-based approach that relies on human operators to bridge between intent and execution. "
        "The systematic architecture addresses each gap explicitly."
    ))
    e.append(bullet("<b>No centralized client database:</b> Client ICPs, buyer personas, and market research live in isolated "
                     "doc tabs rather than a queryable relational database. The system introduces a Baserow-based "
                     "client management layer with structured ICP fields."))
    e.append(bullet("<b>No keyword data persistence:</b> Keyword research is conducted per-engagement using Claude/Gemini "
                     "skills but results are not stored for cross-client pattern analysis. The system introduces "
                     "persistent keyword tables with search volume tracking over time."))
    e.append(bullet("<b>No workflow automation:</b> The 9-step execution process (Buyer Persona, Keyword Research, SEMrush "
                     "import, Clustering, ICP Research, SERP Research, Market Research, SEO Brief, Content Optimization) "
                     "is entirely manual. The system introduces n8n workflows that automate 7 of these 9 steps."))
    e.append(bullet("<b>No citation tracking:</b> AI citation monitoring is described conceptually (7-platform testing suite) "
                     "but has no persistent data store. The system introduces structured citation logging in Baserow "
                     "with automated n8n monitoring workflows."))
    e.append(bullet("<b>No lead attribution:</b> GHL CRM integration is mentioned as a service offering but has no defined "
                     "technical integration architecture. The system specifies exact webhook, API, and pipeline stage "
                     "configurations for end-to-end lead attribution."))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 3: ELI-OS AGENT OPERATING SYSTEM
    # ══════════════════════════════════════════════════
    e.append(h1("3. The Eli-OS Agent Operating System"))
    e.append(body(
        "Eli-OS is VirtuaLab Digital's proprietary multi-agent orchestration system. It decomposes high-level SEO tasks "
        "into directed acyclic graphs (DAGs) of sub-tasks, routes each sub-task to a specialized agent from a 12-agent "
        "fleet, executes them in dependency-respecting order, and synthesizes the results into unified outputs. The "
        "system is governed by a Rust-based control plane that enforces a three-tier policy model (Green/Amber/Red) "
        "at the inter-process communication level, ensuring that no agent can exceed its defined boundaries."
    ))
    e.append(body(
        "The orchestration layer uses Kimi K2.7 Code (Moonshot AI, 1T parameters, INT4 quantized) served via vLLM or "
        "SGLang on a dedicated GPU node (1x NVIDIA A100 80GB or 2x NVIDIA L40S). The model handles four core functions: "
        "task decomposition into DAGs, agent routing, result synthesis, and escalation decision-making. Each function "
        "has a dedicated system prompt that constrains the model's output to structured JSON formats."
    ))
    
    e.append(h2("3.1 The 12-Agent Fleet Architecture"))
    e.append(body(
        "Each agent in the fleet is defined by a SKILL.md manifest that specifies its identity, purpose, knowledge base "
        "scope, 8 capabilities (tools), forbidden actions, input/output schemas, constraints, IPC policy (allowed tables "
        "and endpoints), resource limits, and escalation triggers. The following table catalogs the complete fleet."
    ))
    
    agent_data = [
        ("keyword_agent", "Keyword Research", "8", "640MB", "Seed expansion, intent classification, clustering, volume estimation, gap analysis"),
        ("technical_seo", "Technical SEO Specialist", "8", "512MB", "HTTP diagnostics, robots/sitemap audit, CWV scanning, schema validation"),
        ("on_page_seo", "On-Page & Content SEO", "8", "512MB", "Meta analysis, heading structure, content quality, internal links, duplicate check"),
        ("entity_agent", "Entity & Topic Graph", "8", "768MB", "Entity extraction, relationship mapping, knowledge graph, salience scoring"),
        ("competitor_agent", "Competitor Intelligence", "8", "512MB", "Keyword gaps, content gaps, visibility benchmarking, SERP overlap"),
        ("local_seo", "Local SEO Specialist", "8", "512MB", "NAP audit, GBP signals, local pack ranking, review monitoring"),
        ("parasite_seo", "Off-Page & Parasite SEO", "8", "512MB", "TOS analysis, backlink velocity, anchor analysis, opportunity scoring"),
        ("geo_agent", "GEO Specialist", "8", "512MB", "SGE probing, Perplexity tracking, entity salience, citation gap analysis"),
        ("ai_citation", "AI Citation Monitoring", "8", "768MB", "Citation probing across 5 LLMs, trend analysis, competitor comparison"),
        ("indexing_agent", "Indexing & Discovery", "8", "512MB", "Sitemap generation, IndexNow pushing, GSC coverage, noindex audit"),
        ("qa_agent", "QA & Validation", "8", "384MB", "Schema conformance, hallucination detection, cross-agent consistency"),
        ("report_agent", "Report Generation", "8", "512MB", "Template selection, data aggregation, narrative generation, chart specs"),
    ]
    
    e.append(make_table(
        ["Agent Name", "Role", "Tools", "Memory", "Key Capabilities"],
        agent_data,
        [70, 80, 35, 45, 230]
    ))
    e.append(caption("Table 3.1: Complete 12-Agent Fleet Specification"))
    
    e.append(h2("3.2 Rust Control Plane: Policy Engine & IPC"))
    e.append(body(
        "The control plane is implemented in three Rust crates that enforce agent governance at the operating system "
        "level, not at the application level. This architectural decision means that agent policy violations are "
        "caught before they reach the data layer, eliminating entire classes of security and data integrity risks "
        "that application-level checks would miss."
    ))
    e.append(bold_body("Three-Tier Enforcement Model:"))
    e.append(bullet("<b>GREEN (Auto-Approve):</b> Low-risk read operations within the agent's declared IPC policy. "
                     "These execute immediately with no human review. Examples: keyword_agent reading from "
                     "keyword_expansions table."))
    e.append(bullet("<b>AMBER (Conditional):</b> Write operations within policy, or reads approaching resource limits. "
                     "Approved but logged for audit; may trigger soft throttling. Examples: competitor_agent "
                     "writing new keyword_gap_results."))
    e.append(bullet("<b>RED (Block & Escalate):</b> Forbidden actions, cross-domain writes, deletes, external paid API "
                     "calls, or resource limit violations. Blocked immediately and escalated to the human operator. "
                     "Examples: keyword_agent attempting to modify on_page_audits tables."))
    e.append(spacer(4))
    e.append(body(
        "The IPC handler exposes four gRPC methods: EvaluateRequest (pre-flight policy check), ReportResult (post-execution "
        "auditing), Escalate (out-of-band escalation events), and Heartbeat (liveness telemetry with resource "
        "monitoring). Agents communicate with the control plane over gRPC via Unix Domain Sockets, with each agent "
        "running as an independent Python process that sends heartbeat telemetry every 30 seconds."
    ))
    
    e.append(h2("3.3 SKILL.md Governance Paradigm"))
    e.append(body(
        "The SKILL.md paradigm replaces implicit knowledge with explicit, parseable declarations. Each of the 12 agents "
        "ships with a SKILL.md file that the Rust control plane parses into a CapabilityManifest. This manifest defines "
        "exactly what the agent can and cannot do, which database tables it can access, which API endpoints it can call, "
        "and under what conditions it must escalate to the orchestrator or human operator."
    ))
    e.append(body(
        "The SKILL.md parser extracts seven structured sections: Identity (name, role, domain, version), Purpose, "
        "Knowledge Base Scope (sources, exclusions, refresh policy), Capabilities (8 tools each), Forbidden Actions, "
        "Input/Output JSON Schemas, Constraints (temperature, max tokens, system prompt invariant), IPC Policy "
        "(allowed tables with R/W granularity, allowed endpoints, resource limits), and Escalation Triggers. This "
        "declarative approach enables pre-flight validation instead of post-hoc sandboxing, and tiered enforcement "
        "instead of all-or-nothing blocking."
    ))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 4: BASEROW DATABASE SCHEMA
    # ══════════════════════════════════════════════════
    e.append(h1("4. Baserow Database Schema: Single Source of Truth"))
    e.append(body(
        "Baserow serves as the operational database layer for the VirtuaLab Digital ecosystem. While Eli-OS agents "
        "use PostgreSQL tables for their internal IPC operations, Baserow provides the human-readable, team-accessible "
        "data layer that bridges strategic planning with operational execution. Every client engagement, keyword "
        "research cycle, content production run, and performance report traces back to structured records in Baserow. "
        "The following schema defines 40+ tables organized into 7 functional domains."
    ))
    
    e.append(h2("4.1 Master Data Tables"))
    master_tables = [
        ("brand_settings", "Singleton", "Brand name, tagline, positioning, target markets, service taxonomy, brand voice rules, claims allowed/avoided"),
        ("competitor_registry", "Growing", "Competitor name, domain, type (national/niche/boutique), pricing model, key differentiators, notes"),
        ("team_members", "Growing", "Name, role, specializations, agent assignments, capacity allocation"),
        ("tech_stack", "Static", "Tool name, category (SEO/CMS/CRM/Automation), API keys reference, integration status"),
        ("icp_templates", "Growing", "ICP name, vertical, business size range, revenue range, digital maturity, pain points, messaging angles"),
    ]
    e.append(make_table(
        ["Table Name", "Growth", "Key Fields"],
        master_tables,
        [90, 55, 315]
    ))
    e.append(caption("Table 4.1: Master Data Tables"))
    
    e.append(h2("4.2 Client & Campaign Management"))
    client_tables = [
        ("clients", "Name, company, email, phone, industry vertical, service area, contract start/end, GHL contact ID"),
        ("client_icp_profiles", "Linked client, ICP archetype (A/B/C), verified pain points, digital maturity score, ad dependency level"),
        ("campaigns", "Linked client, campaign name, type (SEO/Local/GEO/Parasite), start date, status, budget allocation"),
        ("campaign_goals", "Linked campaign, metric (calls/bookings/revenue/visibility), target value, current value, deadline"),
        ("gbp_profiles", "Linked client, GBP ID, primary category, NAP data, review count, rating, last audit date"),
        ("service_area_targets", "Linked client, city, state, zip codes, priority tier, assigned content cluster"),
    ]
    e.append(make_table(
        ["Table Name", "Key Fields"],
        client_tables,
        [100, 360]
    ))
    e.append(caption("Table 4.2: Client & Campaign Management Tables"))
    
    e.append(h2("4.3 Content Operations Tables"))
    content_tables = [
        ("keyword_research_jobs", "Client, seed keywords, analysis type, status, created date, completed date"),
        ("keywords", "Keyword, search volume (monthly), difficulty (0-100), intent (info/nav/commercial/transactional), cluster ID"),
        ("keyword_clusters", "Cluster label, keyword count, total volume, target page URL, content status, priority"),
        ("content_briefs", "Linked cluster, target keyword, word count target, H-tag structure, schema requirements, assigned writer"),
        ("content_pieces", "Linked brief, title, URL, word count, publish date, status (draft/review/published), AI review scores"),
        ("ai_review_log", "Linked content piece, platform (ChatGPT/Claude/Perplexity/etc.), review date, score, recommendations"),
        ("page_templates", "Template name, type (visibility/conversion/hub/service-area), H-tag blueprint, schema template"),
    ]
    e.append(make_table(
        ["Table Name", "Key Fields"],
        content_tables,
        [100, 360]
    ))
    e.append(caption("Table 4.3: Content Operations Tables"))
    
    e.append(h2("4.4 Off-Page & Parasite SEO Tables"))
    offpage_tables = [
        ("parasite_platforms", "Platform name, DA score, TOS risk level, topical relevance, indexing speed, editorial barrier, status"),
        ("parasite_campaigns", "Client, platform, content title, publish URL, publish date, backlink obtained, index status"),
        ("backlink_profile", "Client, source URL, DA, anchor text (type), follow status, acquired date, loss date"),
        ("anchor_text_log", "Client, anchor text, type (exact/partial/branded/naked/generic), occurrence count, risk flag"),
        ("youtube_videos", "Client, title, URL, publish date, views, transcript status, embedded on site, schema markup"),
        ("social_media_assets", "Platform, profile URL, follower count, posting frequency, content type mix, linked client"),
    ]
    e.append(make_table(
        ["Table Name", "Key Fields"],
        offpage_tables,
        [100, 360]
    ))
    e.append(caption("Table 4.4: Off-Page & Parasite SEO Tables"))
    
    e.append(h2("4.5 Technical SEO & Indexing Tables"))
    tech_tables = [
        ("tech_seo_audits", "Client, URL, audit date, HTTP status codes, CWV scores (LCP/FID/CLS), robots issues, canonical issues"),
        ("schema_deployments", "Client, URL, schema type (FAQPage/HowTo/LocalBusiness/Service), deployment date, validation status"),
        ("indexing_log", "Client, URL, submission method (IndexNow/GSC/Sitemap), submission date, indexed date, status"),
        ("crawl_issues", "Client, URL, issue type (noindex/redirect/soft404/canonical), discovered date, resolved date, severity"),
        ("internal_link_map", "Client, source URL, target URL, anchor text, link type (navigational/contextual), created date"),
    ]
    e.append(make_table(
        ["Table Name", "Key Fields"],
        tech_tables,
        [100, 360]
    ))
    e.append(caption("Table 4.5: Technical SEO & Indexing Tables"))
    
    e.append(h2("4.6 GEO & AI Citation Tracking Tables"))
    geo_tables = [
        ("geo_citation_probes", "Client, query, platform (ChatGPT/Perplexity/Claude/Copilot/SGE), probe date, brand cited (Y/N)"),
        ("geo_citation_logs", "Linked probe, citation URL, citation text excerpt, competitor cited, salience score"),
        ("geo_citation_trends", "Client, platform, monthly citation rate, trend direction, competitor benchmark rate"),
        ("geo_recommendations", "Client, priority, action, rationale, target queries, status (open/in_progress/resolved)"),
        ("llms_txt_config", "Client, version, content, deployment URL, last updated"),
    ]
    e.append(make_table(
        ["Table Name", "Key Fields"],
        geo_tables,
        [100, 360]
    ))
    e.append(caption("Table 4.6: GEO & AI Citation Tracking Tables"))
    
    e.append(h2("4.7 Reporting & Analytics Tables"))
    report_tables = [
        ("report_registry", "Client, report type, generation date, period, format (PDF/HTML), file path"),
        ("kpi_snapshots", "Client, date, organic sessions, map pack impressions, calls tracked, leads generated, revenue"),
        ("competitor_visibility_benchmarks", "Client, competitor, metric (visibility/keyword gap/content gap), value, date"),
        ("quality_audit_log", "Agent name, check type, result (pass/fail/warn), details, timestamp"),
    ]
    e.append(make_table(
        ["Table Name", "Key Fields"],
        report_tables,
        [115, 345]
    ))
    e.append(caption("Table 4.7: Reporting & Analytics Tables"))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 5: N8N WORKFLOW AUTOMATION
    # ══════════════════════════════════════════════════
    e.append(h1("5. n8n Workflow Automation: The Nervous System"))
    e.append(body(
        "n8n serves as the workflow automation layer that connects Baserow data stores, external APIs (SEMrush, Ahrefs, "
        "Google Search Console, AI platforms), GHL CRM, and the Eli-OS agent fleet into repeatable pipelines. "
        "Each workflow is triggered either manually, on a schedule, or by a webhook event, and executes a "
        "deterministic sequence of operations that eliminates manual handoffs between strategic phases. "
        "The following six workflows form the core operational backbone of the systematic approach."
    ))
    
    e.append(h2("5.1 Client Onboarding Pipeline"))
    e.append(body(
        "This workflow executes automatically when a new client record is created in Baserow. It orchestrates the "
        "initial diagnostic phase that previously required 3-5 days of manual work across multiple platforms. "
        "The pipeline runs 14 sequential and parallel steps, producing a complete client intelligence dossier "
        "that feeds all subsequent strategy and content workflows."
    ))
    e.append(bold_body("Trigger: Baserow webhook on client record creation"))
    e.append(bullet("<b>Step 1:</b> Pull client URL, industry, and service area from Baserow clients table."))
    e.append(bullet("<b>Step 2:</b> Run HTTP status check and robots.txt parse via Eli-OS technical_seo agent."))
    e.append(bullet("<b>Step 3:</b> Fetch GBP data from Google Business Profile API (if available) and log to gbp_profiles table."))
    e.append(bullet("<b>Step 4:</b> Generate buyer persona using Claude /local-seo-market-icp-research skill, store in client_icp_profiles."))
    e.append(bullet("<b>Step 5:</b> Run keyword_agent seed expansion from ICP-derived pain points, store in keyword_research_jobs."))
    e.append(bullet("<b>Step 6:</b> Query SEMrush API for verified search volumes on expanded keywords, update keywords table."))
    e.append(bullet("<b>Step 7:</b> Cluster keywords via keyword_agent, write clusters to keyword_clusters table."))
    e.append(bullet("<b>Step 8:</b> Run competitor_agent visibility benchmarking against 3 nearest competitors."))
    e.append(bullet("<b>Step 9:</b> Run geo_agent citation probe set across 5 AI platforms for 10 seed queries."))
    e.append(bullet("<b>Step 10:</b> Generate initial technical SEO audit report via report_agent, save to Baserow."))
    e.append(bullet("<b>Step 11:</b> Create GHL contact and pipeline stage via GHL API integration."))
    e.append(bullet("<b>Step 12:</b> Send onboarding summary email to team via GHL or SMTP node."))
    e.append(bullet("<b>Step 13:</b> Schedule 30-day review follow-up in n8n cron trigger."))
    e.append(bullet("<b>Step 14:</b> Update campaign_goals with initial KPI baselines from audit data."))
    
    e.append(h2("5.2 Keyword Research & Clustering Pipeline"))
    e.append(body(
        "This pipeline runs on demand (manual trigger) or on a weekly schedule for active campaigns. It takes "
        "seed keywords from Baserow, expands them through multiple data sources (Autocomplete, PAA, SEMrush, Ahrefs), "
        "classifies intent, clusters semantically, and writes all results back to Baserow. This replaces the "
        "manual 4-step process described in the execution doc (Claude skill, SEMrush import, Claude clustering, "
        "manual analysis) with a single automated pipeline that produces richer, more consistent output."
    ))
    e.append(bullet("<b>Input:</b> Read seed keywords from keyword_research_jobs table (status = pending)."))
    e.append(bullet("<b>Expand:</b> Run keyword_agent.seed_expander for each seed (100 variants per seed max)."))
    e.append(bullet("<b>Enrich:</b> Query SEMrush API for search volume, difficulty, CPC for each expanded keyword."))
    e.append(bullet("<b>Classify:</b> Run keyword_agent.intent_classifier to assign informational/navigational/commercial/transactional labels."))
    e.append(bullet("<b>Cluster:</b> Run keyword_agent.keyword_clusterer using embedding-based similarity."))
    e.append(bullet("<b>Gap:</b> Run keyword_agent.keyword_gap_finder against competitor_domains from competitor_registry."))
    e.append(bullet("<b>Output:</b> Write all results to keywords, keyword_clusters, keyword_gap_results tables. Update job status."))
    
    e.append(h2("5.3 Content Production & Publishing Pipeline"))
    e.append(body(
        "This pipeline bridges the gap between keyword clusters and published content. It generates SEO briefs from "
        "cluster data, routes them through the 7-platform AI review workflow, and publishes optimized content. "
        "This systematizes the 9-step content creation process documented in the execution doc, reducing "
        "human involvement to final editorial approval only."
    ))
    e.append(bullet("<b>Brief Generation:</b> Read keyword cluster from Baserow, generate content brief via Claude /seo-brief-architect skill. "
                     "Brief includes: target keyword, secondary keywords, H-tag structure, word count target, schema requirements, "
                     "internal link targets, and BLUF answer capsule."))
    e.append(bullet("<b>Content Drafting:</b> Route brief to content writer (human or AI). Writer produces draft following semantic "
                     "writing standards (answer-first structure, 8th-10th grade readability, GEO-optimized formatting)."))
    e.append(bullet("<b>7-Platform AI Review:</b> Submit draft to Gemini (structure/entities), ChatGPT (clarity/AI readability), "
                     "Perplexity (citation opportunities), Google AIO (manual query test), Bing/Copilot (citation patterns), "
                     "Claude (final merge). Each platform's recommendations are logged in ai_review_log table."))
    e.append(bullet("<b>Final Optimization:</b> Merge all AI recommendations, apply to draft, validate schema markup, check internal links."))
    e.append(bullet("<b>Publishing:</b> Publish to CMS via API, deploy schema markup, submit to IndexNow, log in content_pieces table."))
    
    e.append(h2("5.4 Parasite SEO Distribution Pipeline"))
    e.append(body(
        "This pipeline automates the creation and distribution of parasitic content across high-DA platforms. "
        "It reads from the parasite_platforms table to select appropriate targets based on TOS compliance, "
        "topical relevance, and DA score, then orchestrates content adaptation and publication."
    ))
    e.append(bullet("<b>Platform Selection:</b> Query parasite_platforms for active platforms with TOS risk = low/medium, "
                     "DA greater than 50, and topical relevance score above 0.6 for the client's vertical."))
    e.append(bullet("<b>Content Adaptation:</b> Take published content_pieces marked for parasite distribution, adapt for platform "
                     "requirements (word count, formatting, link placement rules)."))
    e.append(bullet("<b>Publication:</b> Publish via platform API or manual queue (for platforms requiring human accounts)."))
    e.append(bullet("<b>Backlink Tracking:</b> Log publication in parasite_campaigns, monitor for backlink acquisition, "
                     "update backlink_profile table."))
    e.append(bullet("<b>TOS Compliance Monitor:</b> Weekly check of parasite_platforms for TOS changes via parasite_seo agent."))
    
    e.append(h2("5.5 GEO Citation Monitoring Pipeline"))
    e.append(body(
        "This pipeline implements the 7-platform AI testing suite described in the strategic blueprint as an "
        "automated, recurring workflow. It probes ChatGPT, Claude, Perplexity, Bing Copilot, and Google AI Overview "
        "with standardized query sets and logs all findings for trend analysis and competitor comparison."
    ))
    e.append(bullet("<b>Trigger:</b> Cron schedule (high-priority brands: every 6 hours; standard: every 24 hours)."))
    e.append(bullet("<b>Query Set:</b> For each active client, load 10-20 target queries from keyword_clusters (priority = high)."))
    e.append(bullet("<b>Probing:</b> Run geo_agent.sge_response_analyzer, geo_agent.perplexity_citation_tracker, and ai_citation agents."))
    e.append(bullet("<b>Logging:</b> Write citation results to geo_citation_probes and geo_citation_logs tables."))
    e.append(bullet("<b>Trend Analysis:</b> Calculate citation rates, compare against competitor_citation_rates, update geo_citation_trends."))
    e.append(bullet("<b>Alerting:</b> If citation rate drops below 5% or competitor exceeds 60% where brand is absent, trigger escalation."))
    
    e.append(h2("5.6 Client Reporting Pipeline"))
    e.append(body(
        "This pipeline generates monthly client reports by aggregating data from all other tables. It replaces "
        "manual report compilation with an automated process that produces consistent, data-rich deliverables. "
        "Reports are generated as PDF via the report_agent and stored in the report_registry table."
    ))
    e.append(bullet("<b>Trigger:</b> Monthly cron (1st of each month) or manual trigger."))
    e.append(bullet("<b>Data Aggregation:</b> Pull KPI snapshots, keyword ranking changes, citation trends, backlink velocity, "
                     "and technical audit summaries from respective Baserow tables."))
    e.append(bullet("<b>Report Generation:</b> Route aggregated data to report_agent, which selects template, generates "
                     "narrative, prioritizes recommendations, and formats output."))
    e.append(bullet("<b>Delivery:</b> Upload PDF to Baserow, send notification to client via GHL, log in report_registry."))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 6: GHL INTEGRATION
    # ══════════════════════════════════════════════════
    e.append(h1("6. GHL / GoHighLevel CRM Integration"))
    e.append(body(
        "GoHighLevel serves as the client-facing CRM and lead management layer that connects VirtuaLab Digital's "
        "SEO operations to actual business outcomes for clients. The integration architecture ensures that every "
        "phone call, form submission, and booking can be attributed back to the specific search query, content piece, "
        "or parasite SEO placement that generated it. This closes the loop between visibility work and revenue."
    ))
    
    e.append(h2("6.1 Lead Attribution Architecture"))
    e.append(body(
        "The lead attribution system tracks the complete journey from search query to booked job. When a user "
        "clicks a search result or AI citation link, lands on a client's site, and submits a contact form or calls "
        "a tracking number, the system records the full chain: search query, landing page, content piece, "
        "keyword cluster, and conversion event. This data flows into GHL via webhooks and API calls."
    ))
    e.append(bullet("<b>UTM Parameter Capture:</b> All internal links from content pieces to conversion pages include UTM parameters "
                     "(utm_source, utm_medium, utm_campaign, utm_content, utm_term) that identify the source keyword cluster."))
    e.append(bullet("<b>GHL Form Webhook:</b> Client website contact forms trigger GHL webhooks that create/update contacts "
                     "with UTM data attached as custom fields."))
    e.append(bullet("<b>Call Tracking:</b> GHL's call tracking numbers are assigned per campaign, enabling attribution of phone "
                     "calls to specific service area pages or content pieces."))
    e.append(bullet("<b>Pipeline Stage Mapping:</b> GHL pipeline stages map to the buyer journey phases defined in the ICP: "
                     "Problem Awareness, Agency Comparison, Solution Evaluation, Trust Validation, Commitment."))
    
    e.append(h2("6.2 Automated Follow-Up Sequences"))
    e.append(body(
        "GHL workflows automate client communication sequences that nurture leads from initial contact through "
        "to booked appointment. These sequences are triggered by pipeline stage changes and use templates that "
        "reflect the brand voice rules defined in Baserow's brand_settings table. The sequences incorporate "
        "educational content (linking to published guides from the content pipeline) rather than aggressive "
        "sales pitches, aligning with the 'education-first' approach defined in the strategic blueprint."
    ))
    
    e.append(h2("6.3 Pipeline Stage Tracking"))
    e.append(body(
        "GHL pipeline stages are synchronized with Baserow's campaign_goals table via n8n webhooks. When a deal "
        "moves to a new stage in GHL, the webhook updates the corresponding campaign goal record with the stage "
        "transition date and value. This enables the reporting pipeline to produce reports that show not just "
        "SEO metrics (rankings, traffic, citations) but also business outcomes (leads generated, appointments "
        "booked, jobs closed, revenue attributed) in a single, unified view."
    ))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 7: ASYMMETRIC SEO
    # ══════════════════════════════════════════════════
    e.append(h1("7. Asymmetric SEO Systematic Methodology"))
    e.append(body(
        "Asymmetric SEO is the practice of identifying and exploiting structural deficiencies in competitor "
        "strategies to achieve disproportionate visibility gains with less resource expenditure. Rather than "
        "competing head-to-head on the same metrics (backlink volume, content depth, ad spend), asymmetric "
        "strategies target the specific vulnerabilities that competitors cannot easily fix due to business model "
        "constraints, technical debt, or strategic blind spots. The systematic approach transforms this from "
        "an intuitive art into a data-driven, repeatable process."
    ))
    
    e.append(h2("7.1 Structural Gap Exploitation Framework"))
    e.append(body(
        "The framework operates through a four-phase cycle that runs continuously for each active campaign. "
        "Each phase produces structured data that feeds the next, creating a self-reinforcing intelligence loop. "
        "The competitor_agent and keyword_agent work together to identify gaps, while the on_page_seo and "
        "content pipelines exploit them."
    ))
    e.append(bullet("<b>Phase 1 - Detect:</b> Run competitor_agent.keyword_gap_analyzer against competitor_registry entries. "
                     "Cross-reference with keyword_clusters to find high-volume, low-competition gaps. "
                     "Store results in keyword_gap_results table with opportunity score."))
    e.append(bullet("<b>Phase 2 - Classify:</b> Classify each gap by exploitation type: (a) Content gap (competitor has no page), "
                     "(b) Depth gap (competitor's page is thin), (c) Format gap (competitor lacks schema/video/FAQ), "
                     "(d) Local gap (competitor has no service area page for target suburb)."))
    e.append(bullet("<b>Phase 3 - Exploit:</b> Route classified gaps to appropriate pipeline: content gaps to Content Production, "
                     "format gaps to Technical SEO, local gaps to Programmatic Hub Page generator. Set priority based on "
                     "opportunity score multiplied by estimated effort."))
    e.append(bullet("<b>Phase 4 - Measure:</b> Track ranking changes for exploited keywords in kpi_snapshots. Compare against "
                     "pre-exploitation baseline. Feed results back into Phase 1 to refine gap detection."))
    
    e.append(h2("7.2 Non-Linear Competitive Advantage Model"))
    e.append(body(
        "The non-linear model recognizes that certain SEO investments produce exponentially greater returns than "
        "others. The systematic approach quantifies this by tracking the cost-per-visibility-unit for each strategy "
        "type and prioritizing investments that produce the highest asymmetric returns. For example, the strategic "
        "blueprint identifies that adding a single FAQPage schema to a service page can increase AI citation "
        "probability by 30-115.1% (Princeton KDD 2024 data), while building 10 new backlinks might only increase "
        "organic ranking by 2-5 positions. The system tracks these multipliers in the Baserow strategy_multipliers "
        "table and uses them to automatically rank recommended actions in client reports."
    ))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 8: PARASITE SEO
    # ══════════════════════════════════════════════════
    e.append(h1("8. Parasite SEO Systematic Methodology"))
    e.append(body(
        "Parasite SEO leverages high-domain-authority third-party platforms to rank content that drives traffic "
        "and backlinks to client properties. The systematic approach transforms this from ad-hoc content placement "
        "into a structured program with platform scoring, TOS compliance monitoring, and performance tracking. "
        "The parasite_seo agent's 8 tools provide the analytical backbone, while n8n workflows handle distribution."
    ))
    
    e.append(h2("8.1 Platform Scoring and TOS Compliance"))
    e.append(body(
        "Each potential parasitic platform is scored on five dimensions, with automated TOS monitoring to ensure "
        "compliance boundaries are never violated. The parasite_seo agent's platform_tos_analyzer parses platform "
        "terms of service documents and flags restrictive clauses related to link policies, self-promotion rules, "
        "and monetization restrictions. Scores are stored in the parasite_platforms table and refreshed weekly."
    ))
    e.append(make_table(
        ["Dimension", "Weight", "Data Source", "Update Frequency"],
        [
            ("Domain Authority", "30%", "Moz API / Cached index", "Monthly"),
            ("Topical Relevance", "25%", "NLP topic similarity to client vertical", "On-demand"),
            ("TOS Risk Level", "20%", "parasite_seo agent TOS parser", "Weekly"),
            ("Indexing Speed", "15%", "Historical publish-to-index measurements", "Monthly"),
            ("Editorial Barrier", "10%", "Manual assessment (low/medium/high)", "Quarterly"),
        ],
        [100, 50, 180, 130]
    ))
    e.append(caption("Table 8.1: Parasite Platform Scoring Dimensions"))
    
    e.append(h2("8.2 Content Distribution Orchestration"))
    e.append(body(
        "The parasite distribution pipeline reads published content_pieces marked for distribution, selects "
        "optimal platforms based on scoring, adapts content for each platform's requirements, and tracks "
        "publication outcomes. The orchestration layer ensures that content is distributed across a diverse "
        "platform mix (not concentrated on a single platform), anchor text distribution remains natural "
        "(exact match below 30%), and backlink velocity stays within safe thresholds (below 300% of "
        "trailing 90-day average). When any threshold is breached, the parasite_seo agent automatically "
        "escalates to the orchestrator for strategy review."
    ))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 9: GEO SYSTEM
    # ══════════════════════════════════════════════════
    e.append(h1("9. GEO (Generative Engine Optimization) System"))
    e.append(body(
        "Generative Engine Optimization is the practice of structuring content so that large language models "
        "can retrieve, synthesize, and cite it within conversational search interfaces. The systematic approach "
        "implements the theoretical frameworks documented in the strategic blueprint (Princeton KDD 2024 GEO paper, "
        "Zyppy 2025 citation analysis, Sadasivan et al. 2025 AI retrieval bias study) as measurable, trackable, "
        "and improvable system components. The geo_agent and ai_citation agents provide the analytical "
        "infrastructure, while content operations implement the recommendations."
    ))
    
    e.append(h2("9.1 Citation Probability Model"))
    e.append(body(
        "The strategic blueprint defines the AI visibility model as V(ai) = a * S(density) + b * Q(addition) + "
        "g * C(sources) + d * F(fluency). The systematic approach operationalizes each variable as a measurable "
        "content score stored in Baserow and tracked over time. Content pieces receive a GEO score on each of these "
        "four dimensions, calculated by the geo_agent's content_quoteability_scorer tool, and stored in a "
        "geo_content_scores table. The qa_agent validates that published content meets minimum threshold "
        "scores before approval."
    ))
    e.append(make_table(
        ["Variable", "Full Name", "Measurement Method", "Target Threshold"],
        [
            ("S(density)", "Statistics Density", "Count of verifiable numeric data points per 1000 words", "Greater than 5"),
            ("Q(addition)", "Quotation Addition", "Count of attributed expert quotes per article", "Greater than 2"),
            ("C(sources)", "Citation Sources", "Count of hyperlinked authoritative external references", "Greater than 3"),
            ("F(fluency)", "Fluency Optimization", "Flesch-Kincaid readability grade level", "8-10 grade"),
        ],
        [60, 80, 200, 120]
    ))
    e.append(caption("Table 9.1: GEO Citation Probability Variables (Operationalized)"))
    
    e.append(h2("9.2 BLUF Content Formatting Standard"))
    e.append(body(
        "BLUF (Bottom Line Up Front) formatting places a 40-60 word concise, fact-dense answer capsule directly "
        "beneath each major H2 and H3 heading. The Zyppy 2025 analysis found that 44.2% of all AI citations are "
        "extracted from the first 30% of a page's content, making the answer-first structure the single "
        "highest-impact GEO tactic. The systematic approach enforces BLUF formatting through the content "
        "brief template: every brief generated by the Content Production Pipeline includes a mandatory BLUF "
        "capsule field that the writer must complete before the rest of the content. The qa_agent validates "
        "BLUF presence and word count during quality review."
    ))
    
    e.append(h2("9.3 llms.txt Implementation"))
    e.append(body(
        "llms.txt is a machine-readable file placed at the root of each client's domain that provides LLM crawlers "
        "with structured information about the site's content, authority, and preferred citation format. The systematic "
        "approach generates llms.txt files from Baserow data (brand_settings, keyword_clusters, content_pieces) "
        "and deploys them via n8n workflow. The file follows the emerging llms.txt specification and includes: "
        "site name and description, authority signals, key topic areas with links, and preferred citation format. "
        "The geo_agent monitors LLM crawler access to llms.txt via server log analysis and tracks whether "
        "citation rates improve after deployment."
    ))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 10: CONTENT OPERATIONS
    # ══════════════════════════════════════════════════
    e.append(h1("10. Content Operations System"))
    
    e.append(h2("10.1 7-Platform AI Review Workflow"))
    e.append(body(
        "The strategic blueprint defines a 7-step content review process that routes content through multiple AI "
        "platforms to maximize quality and citation-readiness. The systematic approach automates the logistics "
        "of this process while preserving the human editorial approval gate. The workflow executes as follows: "
        "content draft is submitted to Gemini (Flash 3.5, Extended Mode, Deep Research) for structure, entity, and "
        "topic coverage review; then to ChatGPT for clarity and AI readability analysis; then to Perplexity for "
        "source-backed citation opportunities; then to Google AI Overview for manual query testing; then to "
        "Bing/Copilot for Microsoft-style answer pattern review; and finally back to Claude for merging all "
        "recommendations into a final publishing plan. Each platform's review is logged in the ai_review_log "
        "table with scores and specific recommendations."
    ))
    
    e.append(h2("10.2 Semantic Writing Standards"))
    e.append(body(
        "All content produced through the system must comply with the semantic writing standards derived from "
        "the strategic blueprint and the VirtuaLab Tools Repository. These standards are codified in Baserow's "
        "brand_settings table as enforceable rules that the qa_agent checks during quality review. Key standards "
        "include: answer-first structure with BLUF capsules beneath every H2/H3 heading; 8th-to-10th grade "
        "reading level as measured by Flesch-Kincaid; minimum 3 verifiable statistics per 1000 words; "
        "minimum 2 attributed expert quotes per article; minimum 3 hyperlinked authoritative external "
        "citations per article; FAQPage schema for any page containing 3 or more questions; and LocalBusiness "
        "schema with nested Service and Offer objects for all service area pages."
    ))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 11: FREE TOOLS
    # ══════════════════════════════════════════════════
    e.append(h1("11. Free Tools Ecosystem"))
    e.append(body(
        "The strategic blueprint specifies three free tools to be offered on the VirtuaLab Digital website as "
        "lead generation mechanisms. Each tool is registered in the Baserow free_tools_registry table with "
        "its configuration, embedding code, and lead capture settings. The tools serve dual purposes: they provide "
        "genuine value to prospects (building trust per the education-first philosophy) and they capture "
        "contact information for GHL follow-up sequences."
    ))
    e.append(make_table(
        ["Tool", "Purpose", "Lead Capture", "Baserow Table"],
        [
            ("Local Marketing ROI Calculator", "Compare paid lead costs vs. organic asset building ROI", "Email required to see results", "tool_configs"),
            ("Local Proximity Visualizer", "Show service area radius maps and centroid optimization", "Email for full report", "tool_configs"),
            ("Lead Prioritization Matrix", "Score and rank leads by service type, urgency, and value", "GHL contact creation", "tool_configs"),
        ],
        [110, 170, 100, 80]
    ))
    e.append(caption("Table 11.1: Free Lead Generation Tools"))
    
    e.append(body(
        "Additionally, the VirtuaLab Tools Repository specifies seven internal tools used in client delivery: "
        "All-in-One SEO Tools, Semantic Writing Assistant, Technical SEO Auditor, Sitemap Generator, "
        "Conversion Rate Optimizer, Zero-Code Jasper AI Integration, and the Autonomous Agent (Eli-OS) itself. "
        "These tools are configured in Baserow's tool_configs table and accessible to team members through "
        "the internal operations dashboard. Each tool's output feeds back into the relevant Baserow tables, "
        "ensuring that tool usage data is captured and actionable."
    ))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 12: IMPLEMENTATION ROADMAP
    # ══════════════════════════════════════════════════
    e.append(h1("12. Implementation Roadmap: 6-Week Deployment"))
    e.append(body(
        "The following roadmap is derived from the Eli-OS integration notes (OPENCLAW_KIMI_INTEGRATION.md) "
        "and adapted for the VirtuaLab Digital context. It prioritizes establishing the data foundation (Baserow) "
        "before building automation (n8n) and finally connecting intelligence (Eli-OS agents). Each week has "
        "explicit deliverables, dependencies, and validation criteria."
    ))
    e.append(make_table(
        ["Week", "Focus", "Deliverables", "Dependencies", "Validation"],
        [
            ("Week 1", "Data Foundation", "Create all 40+ Baserow tables with fields, views, and filters. Import existing client data. Populate brand_settings and competitor_registry from Google Docs.", "None (starting point)", "All tables created. Sample data queryable. Views accessible to team."),
            ("Week 2", "Client Onboarding", "Build n8n Client Onboarding Pipeline (14 steps). Configure GHL webhook integration. Test with one existing client.", "Week 1 tables", "End-to-end test: new client record triggers full pipeline, produces dossier."),
            ("Week 3", "Keyword & Content", "Build n8n Keyword Research Pipeline. Build Content Production Pipeline (brief generation + 7-platform AI review). Configure Claude/Gemini API nodes.", "Week 1 tables, Week 2 GHL", "Pipeline produces keyword clusters and content briefs from seed keywords."),
            ("Week 4", "Off-Page & GEO", "Build Parasite SEO Distribution Pipeline. Build GEO Citation Monitoring Pipeline. Deploy parasite_platforms and geo_citation_probes tables.", "Week 1 tables, Week 3 content", "Parasite content published to 2+ platforms. Citation probes logging data."),
            ("Week 5", "Eli-OS Integration", "Deploy Eli-OS SKILL.md files. Start Kimi K2.7 Code inference server. Connect Eli-OS agents to Baserow via IPC. Test agent policy enforcement.", "Week 1-4 pipelines", "Agent completes task with policy check. Escalation triggers work correctly."),
            ("Week 6", "Reporting & QA", "Build Client Reporting Pipeline. Run qa_agent cross-agent consistency checks. Performance benchmarking. Documentation.", "Week 1-5 complete", "Monthly report generates automatically. QA passes all checks. System runs unattended for 48h."),
        ],
        [40, 60, 150, 70, 140]
    ))
    e.append(caption("Table 12.1: 6-Week Implementation Roadmap"))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 13: DATA FLOW
    # ══════════════════════════════════════════════════
    e.append(h1("13. Data Flow Architecture"))
    e.append(body(
        "The following describes the complete data flow through the VirtuaLab Digital ecosystem, from initial "
        "client contact to monthly reporting. Every data touchpoint maps to a specific Baserow table, n8n workflow, "
        "or Eli-OS agent, ensuring complete traceability and eliminating any step that relies on tribal knowledge "
        "or undocumented processes."
    ))
    e.append(bold_body("Primary Data Flow (Client Lifecycle):"))
    e.append(bullet("<b>1. Client Contact:</b> Website form or referral creates GHL contact via webhook. n8n triggers Client "
                     "Onboarding Pipeline. Baserow clients table record created."))
    e.append(bullet("<b>2. Intelligence Gathering:</b> technical_seo agent audits site. keyword_agent expands seeds. "
                     "competitor_agent benchmarks visibility. geo_agent probes AI citations. All results to Baserow."))
    e.append(bullet("<b>3. Strategy Formation:</b> Keyword clusters, content briefs, and campaign goals created in Baserow. "
                     "Prioritized execution roadmap generated from keyword gap analysis."))
    e.append(bullet("<b>4. Content Production:</b> Content Pipeline generates briefs, routes through 7-platform AI review, "
                     "publishes optimized content. Schema deployed. IndexNow submitted."))
    e.append(bullet("<b>5. Off-Page Distribution:</b> Parasite Pipeline distributes content to scored platforms. "
                     "Backlink profile updated. YouTube videos published. Social assets managed."))
    e.append(bullet("<b>6. GEO Monitoring:</b> Citation probes run on schedule. Trends tracked. Recommendations generated. "
                     "llms.txt deployed and monitored."))
    e.append(bullet("<b>7. Lead Attribution:</b> GHL captures conversions with UTM data. Pipeline stages tracked. "
                     "Revenue attributed to SEO activities."))
    e.append(bullet("<b>8. Reporting:</b> Monthly pipeline aggregates all data. PDF report generated. Delivered to client. "
                     "KPI trends analyzed. Strategy adjusted for next cycle."))
    e.append(spacer(8))
    e.append(bold_body("Secondary Data Flow (Internal Operations):"))
    e.append(bullet("<b>Quality Assurance:</b> qa_agent runs cross-agent consistency checks after every multi-agent task. "
                     "Results logged in quality_audit_log."))
    e.append(bullet("<b>Escalation Handling:</b> Eli-OS policy engine routes violations to orchestrator. Kimi K2.7 decides "
                     "escalation action (retry/reroute/compose/escalate_to_human). Human review queue in Baserow."))
    e.append(bullet("<b>System Monitoring:</b> Agent heartbeats monitored every 30 seconds. Resource usage tracked. "
                     "n8n workflow execution logs captured. System health dashboard updated."))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════
    # CHAPTER 14: GOVERNANCE
    # ══════════════════════════════════════════════════
    e.append(h1("14. Governance, Escalation & Quality Assurance"))
    e.append(body(
        "The governance layer ensures that the systematic approach maintains quality over time and adapts to "
        "changing conditions without manual intervention. It operates at three levels: agent-level governance "
        "enforced by the Rust control plane, workflow-level governance enforced by n8n error handling and "
        "retry logic, and strategic-level governance enforced by human review of escalation events and "
        "monthly performance reviews."
    ))
    
    e.append(h2("14.1 Agent-Level Governance"))
    e.append(body(
        "Each Eli-OS agent operates within strict boundaries defined by its SKILL.md manifest. The Rust "
        "control plane enforces these boundaries at the IPC level, before any data operation reaches the "
        "database layer. The three-tier enforcement model (Green/Amber/Red) ensures that routine operations "
        "execute without friction while risky operations are logged or blocked. Key governance rules include: "
        "no cross-domain table access (each agent can only read/write its designated tables), no hallucination "
        "(system prompt invariant requires answers to come only from retrieved context), resource limits "
        "enforced per agent (memory, CPU, duration), and defined escalation triggers that route "
        "anomalies to the orchestrator for decision-making."
    ))
    
    e.append(h2("14.2 Workflow-Level Governance"))
    e.append(body(
        "n8n workflows implement error handling at every node. External API calls include retry logic "
        "with exponential backoff. Failed workflow executions are logged with full context for debugging. "
        "Workflow executions that exceed defined timeout thresholds trigger alerts. Data validation nodes "
        "check that Baserow writes succeed and that data formats match expected schemas before proceeding "
        "to the next step. This ensures that partial failures do not corrupt downstream data."
    ))
    
    e.append(h2("14.3 Strategic-Level Governance"))
    e.append(body(
        "Human operators review escalation events daily. The Baserow quality_audit_log table surfaces "
        "all QA failures, policy violations, and escalation decisions for review. Monthly performance "
        "reviews compare KPI trends across clients and identify systemic issues (e.g., citation rates "
        "declining across all clients may indicate a platform algorithm change requiring strategy adjustment). "
        "The competitor_registry is reviewed quarterly to add new competitors and update scoring. Brand settings, "
        "ICP templates, and content standards are reviewed and updated based on accumulated performance data."
    ))
    
    return e

# ── Build PDF ──
OUTPUT_PATH = '/home/z/my-project/download/VirtuaLab_Digital_Ecosystem_Systematic_Architecture.pdf'

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    leftMargin=40*mm,
    rightMargin=40*mm,
    topMargin=30*mm,
    bottomMargin=25*mm,
    title="VirtuaLab Digital Ecosystem Systematic Architecture",
    author="VirtuaLab Digital",
    subject="AISEO Framework Systematic Approach Foundation",
)

elements = build_cover()
elements.extend(build_toc())
elements.extend(build_content())

doc.build(elements, onFirstPage=page_footer, onLaterPages=page_footer)
print(f"PDF generated: {OUTPUT_PATH}")

# Get page count
import subprocess, os
result = subprocess.run(['python3', '-c', 'import fitz, os\ndoc = fitz.open("' + OUTPUT_PATH + '")\nprint(f"Pages: {doc.page_count}")\nprint(f"Size: {os.path.getsize("' + OUTPUT_PATH + '") / 1024:.1f} KB")\ndoc.close()'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(f"Warning: {result.stderr}")
