#!/usr/bin/env python3
"""
Eli-OS Architecture White Paper: Fixing the Blocking Problem
Report-route PDF via ReportLab + Playwright cover
"""
import sys, os, hashlib, platform
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image, HRFlowable
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.pdfmetrics import _fonts

# ━━━ Paths ━━━
PDF_SKILL_DIR = "/home/z/my-project/skills/pdf"
OUTPUT_DIR = "/home/z/my-project/download/eli-os-delivery"

# ━━━ Font Setup ━━━
_IS_MAC = platform.system() == 'Darwin'
FONT_DIR = os.path.expanduser('~/.openclaw/workspace/fonts') if _IS_MAC else '/usr/share/fonts'

pdfmetrics.registerFont(TTFont('NotoSerifSC', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Bold', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf'))
pdfmetrics.registerFont(TTFont('SarasaMonoSC', f'{FONT_DIR}/truetype/chinese/SarasaMonoSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif', f'{FONT_DIR}/truetype/freefont/FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Bold', f'{FONT_DIR}/truetype/freefont/FreeSerifBold.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Italic', f'{FONT_DIR}/truetype/freefont/FreeSerifItalic.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-BoldItalic', f'{FONT_DIR}/truetype/freefont/FreeSerifBoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf'))

registerFontFamily('NotoSerifSC', normal='NotoSerifSC', bold='NotoSerifSC-Bold')
# Noto Sans SC variable font skipped (ReportLab compat); SarasaMonoSC used for monospace
registerFontFamily('FreeSerif', normal='FreeSerif', bold='FreeSerif-Bold', italic='FreeSerif-Italic', boldItalic='FreeSerif-BoldItalic')
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans')

# Install fallback
sys.path.insert(0, os.path.join(PDF_SKILL_DIR, 'scripts'))
from pdf import install_font_fallback
install_font_fallback()

# ━━━ Cascade Palette (dark mode, seed 42) ━━━
PAGE_BG       = colors.HexColor('#121210')
SECTION_BG    = colors.HexColor('#24231f')
CARD_BG       = colors.HexColor('#22211d')
TABLE_STRIPE  = colors.HexColor('#171715')
HEADER_FILL   = colors.HexColor('#3e3928')
COVER_BLOCK   = colors.HexColor('#3e3a2e')
BORDER        = colors.HexColor('#514b38')
ICON          = colors.HexColor('#caba8c')
ACCENT        = colors.HexColor('#d5c080')
ACCENT_2      = colors.HexColor('#4eabca')
TEXT_PRIMARY   = colors.HexColor('#e2e1df')
TEXT_MUTED     = colors.HexColor('#8b8881')
SEM_SUCCESS   = colors.HexColor('#8bbd9c')
SEM_WARNING   = colors.HexColor('#b69b67')
SEM_ERROR     = colors.HexColor('#bf8984')
SEM_INFO      = colors.HexColor('#80a0c0')

# ━━━ Styles ━━━
W, H = A4
MARGIN = 0.9 * inch

def make_styles():
    s = {}
    s['h1'] = ParagraphStyle('H1', fontName='FreeSerif-Bold', fontSize=22, leading=28, textColor=ACCENT, spaceAfter=12, spaceBefore=24)
    s['h2'] = ParagraphStyle('H2', fontName='FreeSerif-Bold', fontSize=16, leading=22, textColor=ICON, spaceAfter=8, spaceBefore=18)
    s['h3'] = ParagraphStyle('H3', fontName='FreeSerif-Bold', fontSize=13, leading=18, textColor=TEXT_PRIMARY, spaceAfter=6, spaceBefore=12)
    s['body'] = ParagraphStyle('Body', fontName='FreeSerif', fontSize=10.5, leading=17, textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=8)
    s['body_dark'] = ParagraphStyle('BodyDark', fontName='FreeSerif', fontSize=10.5, leading=17, textColor=TEXT_MUTED, alignment=TA_JUSTIFY, spaceAfter=8)
    s['bullet'] = ParagraphStyle('Bullet', fontName='FreeSerif', fontSize=10.5, leading=17, textColor=TEXT_PRIMARY, leftIndent=18, bulletIndent=6, spaceAfter=4, alignment=TA_LEFT)
    s['code'] = ParagraphStyle('Code', fontName='SarasaMonoSC', fontSize=9, leading=14, textColor=ACCENT_2, backColor=colors.HexColor('#0d0d0c'), leftIndent=12, rightIndent=12, spaceBefore=6, spaceAfter=6, borderPadding=6)
    s['caption'] = ParagraphStyle('Caption', fontName='FreeSerif-Italic', fontSize=9, leading=13, textColor=TEXT_MUTED, spaceAfter=12, alignment=TA_LEFT)
    s['toc_h1'] = ParagraphStyle('TOCH1', fontName='FreeSerif-Bold', fontSize=13, leading=20, leftIndent=0, textColor=ACCENT)
    s['toc_h2'] = ParagraphStyle('TOCH2', fontName='FreeSerif', fontSize=11, leading=18, leftIndent=20, textColor=TEXT_PRIMARY)
    return s

STY = make_styles()

# ━━━ TOC Template ━━━
class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            level = getattr(flowable, 'bookmark_level', 0)
            text = getattr(flowable, 'bookmark_text', '')
            key = getattr(flowable, 'bookmark_key', '')
            self.notify('TOCEntry', (level, text, self.page, key))

def add_heading(text, style, level=0):
    key = f'h_{hashlib.md5(text.encode()).hexdigest()[:8]}'
    p = Paragraph(f'<a name="{key}"/>{text}', style)
    p.bookmark_name = key
    p.bookmark_level = level
    p.bookmark_text = text
    p.bookmark_key = key
    return p

def safe_keep(elements):
    total = 0
    for el in elements:
        w, h = el.wrap(W - 2*MARGIN, H)
        total += h
    if total <= A4[1] * 0.4:
        return [KeepTogether(elements)]
    elif len(elements) >= 2:
        return [KeepTogether(elements[:2])] + list(elements[2:])
    return list(elements)

def make_table(headers, rows, col_widths=None):
    available = W - 2*MARGIN
    if not col_widths:
        n = len(headers)
        col_widths = [available / n] * n
    data = [[Paragraph(h, ParagraphStyle('TH', fontName='FreeSerif-Bold', fontSize=9.5, leading=14, textColor=colors.white)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), ParagraphStyle('TD', fontName='FreeSerif', fontSize=9, leading=13, textColor=TEXT_PRIMARY)) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_FILL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_STRIPE))
    t.setStyle(TableStyle(style_cmds))
    return t

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=12, spaceBefore=12)

# ━━━ Page Background ━━━
def page_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAGE_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # Accent bar at top
    canvas.setFillColor(HEADER_FILL)
    canvas.rect(0, H - 3, W, 3, fill=1, stroke=0)
    # Page number
    canvas.setFont('FreeSerif', 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawRightString(W - MARGIN, MARGIN - 16, f'{doc.page}')
    canvas.drawString(MARGIN, MARGIN - 16, 'Eli-OS Architecture v1.0')
    canvas.restoreState()

# ━━━ BUILD STORY ━━━
story = []

# --- TOC ---
toc = TableOfContents()
toc.levelStyles = [STY['toc_h1'], STY['toc_h2']]
story.append(toc)
story.append(PageBreak())

# ═══════════════════════════════════════════════════════
# CHAPTER 1: THE BLOCKING PROBLEM
# ═══════════════════════════════════════════════════════
story.append(add_heading('<b>1. The Blocking Problem: Diagnosis</b>', STY['h1'], 0))

story.append(add_heading('<b>1.1 Symptom Description</b>', STY['h2'], 1))
story.append(Paragraph(
    'The Eli-OS Rust control plane was designed as a fail-closed safety kernel that governs all interactions between the human operator, the Orchestrator AI, and the Python-based Eli Claw agent swarm. In practice, the control plane has become the single largest bottleneck in the system. When a human operator issues a command, or when the Orchestrator AI routes a task to a specialized agent, the Rust kernel intercepts the Inter-Process Communication (IPC) request and evaluates it against a set of hardcoded policy rules. If any rule fails, the kernel returns a <b>PermissionDenied</b> error and halts the operation entirely. This design was intentionally conservative to prevent rogue agent behavior, but it has created a regime where legitimate, well-intentioned operations are routinely blocked.', STY['body']))

story.append(Paragraph(
    'The blocking manifests in three distinct failure modes that have been observed during development and pilot testing. First, <b>over-scoped policy checks</b> occur when the kernel evaluates an IPC request against policy rules that were designed for a different agent or a different operational context. For example, when the Technical SEO agent requests access to the crawl_results table, the kernel may block the request because a separate policy rule intended for the Parasite SEO agent restricts write access to that same table. The kernel does not distinguish between agents; it applies a monolithic policy to all IPC traffic, resulting in false-positive denials that halt productive work.', STY['body']))

story.append(Paragraph(
    'Second, <b>cascading blocks</b> occur when a single blocked operation causes downstream failures across the swarm. When the Orchestrator AI decomposes a complex task and routes sub-tasks to multiple agents, a block on one agent can cause the entire workflow to stall. The Orchestrator has no mechanism to retry, reroute, or de-escalate a blocked operation. It simply receives a PermissionDenied error and reports failure to the human operator, who must then manually diagnose which policy rule caused the block and either override it or restructure the task. This manual intervention cycle defeats the purpose of an autonomous multi-agent system.', STY['body']))

story.append(Paragraph(
    'Third, <b>opaque error reporting</b> makes diagnosis difficult. When the kernel blocks an IPC request, it returns a generic PermissionDenied error without specifying which policy rule was violated, why the rule exists, or what the operator can do to resolve the conflict. This lack of transparency turns every block into a debugging session that requires the operator to inspect the Rust kernel source code, understand the policy engine internals, and manually trace the IPC request path. The result is a control plane that inspires frustration rather than confidence, and that actively undermines the velocity of the development and operations team.', STY['body']))

story.append(Spacer(1, 12))
story.append(add_heading('<b>1.2 Root Cause Analysis</b>', STY['h2'], 1))

story.append(Paragraph(
    'The root cause of the blocking problem is architectural: the Rust control plane uses a <b>monolithic, hardcoded policy engine</b> that was not designed for a multi-agent swarm. The original design assumed a single Python application (Eli Claw) communicating with a single Rust kernel. Policy rules were written as Rust match statements and if-else chains, embedded directly in the kernel binary. This approach provided strong safety guarantees for a single-agent system, but it does not scale to a swarm of twelve or more specialized agents, each with distinct capabilities, knowledge bases, and tool access requirements.', STY['body']))

story.append(Paragraph(
    'The fundamental architectural flaw is the <b>separation of policy from capability</b>. In the current system, the Rust kernel owns both the enforcement mechanism (the IPC interceptor) and the policy definition (the hardcoded rules). The Python agents have no way to declare their own capabilities or boundaries. They cannot tell the kernel what they are allowed to do; they can only discover what they are not allowed to do by attempting an operation and receiving a PermissionDenied error. This inverted model places the entire burden of policy management on the kernel, making it a single point of failure and a single point of bottleneck for the entire system.', STY['body']))

story.append(Paragraph(
    'Furthermore, the current IPC mechanism lacks a <b>tiered enforcement model</b>. Every IPC request, regardless of its risk level, is subjected to the same exhaustive policy evaluation. A low-risk read operation (such as an agent querying its own knowledge base) receives the same level of scrutiny as a high-risk write operation (such as an agent modifying shared state in the PostgreSQL database). This flat enforcement model introduces unnecessary latency for the vast majority of operations while providing no additional safety benefit, because the high-risk operations that actually warrant strict scrutiny are processed through the same fast path as everything else.', STY['body']))

# Failure mode table
story.append(Spacer(1, 12))
story.append(Paragraph('<b>Table 1: Blocking Failure Modes</b>', STY['caption']))
story.append(make_table(
    ['Failure Mode', 'Description', 'Impact', 'Current Mitigation'],
    [
        ['Over-scoped Policy', 'Monolithic rules applied across all agents regardless of context', 'False-positive denials on legitimate operations', 'None - manual kernel code change required'],
        ['Cascading Blocks', 'Single block stalls entire multi-agent workflow', 'Workflow failure requiring full restart', 'None - Orchestrator cannot retry or reroute'],
        ['Opaque Errors', 'PermissionDenied with no policy rule reference', 'Debugging requires source code inspection', 'None - no error detail in IPC response'],
        ['Flat Enforcement', 'All IPC requests undergo same scrutiny level', 'Unnecessary latency on low-risk reads', 'None - no risk-tier classification exists'],
        ['Static Policy', 'Rules compiled into Rust binary at build time', 'Policy changes require kernel recompilation', 'None - no runtime policy update mechanism'],
    ],
    [1.1*inch, 1.8*inch, 1.6*inch, 1.8*inch]
))

# ═══════════════════════════════════════════════════════
# CHAPTER 2: THE SKILL.MD PARADIGM
# ═══════════════════════════════════════════════════════
story.append(Spacer(1, 24))
story.append(add_heading('<b>2. The SKILL.md Paradigm: Declarative Agent Boundaries</b>', STY['h1'], 0))

story.append(add_heading('<b>2.1 Origin: OpenClaw Standard</b>', STY['h2'], 1))
story.append(Paragraph(
    'The solution to the blocking problem draws from the OpenClaw project, an open-source multi-channel gateway for AI agents. OpenClaw introduced the <b>SKILL.md</b> standard, a structured Markdown file that teaches an AI agent how to use a tool or perform a function. Each SKILL.md file serves as a declarative specification of an agent\'s identity, capabilities, knowledge base scope, forbidden actions, input/output schemas, system prompt invariants, and IPC policy. The critical innovation is that the agent\'s behavioral boundaries are defined in a machine-readable document that both the agent and the control plane can parse and enforce.', STY['body']))

story.append(Paragraph(
    'By adopting the SKILL.md paradigm, Eli-OS shifts from a model where the Rust kernel <i>imposes</i> boundaries on Python agents to a model where agents <i>declare</i> their own boundaries, and the kernel <i>verifies</i> compliance. This inversion of responsibility has profound implications for system architecture. The kernel no longer needs to contain hardcoded knowledge of what each agent is allowed to do. Instead, it reads the SKILL.md files at startup, builds a dynamic capability manifest, and uses that manifest as the basis for all policy enforcement decisions. When an agent needs to change its capabilities (for example, adding a new tool or accessing a new database table), the operator updates the SKILL.md file and signals the kernel to reload, without recompiling any Rust code.', STY['body']))

story.append(add_heading('<b>2.2 SKILL.md Schema Specification</b>', STY['h2'], 1))
story.append(Paragraph(
    'Each SKILL.md file in the Eli-Swarm-Claw project follows a standardized schema with eight mandatory sections. The <b>Identity</b> section declares the agent\'s name, role, domain, and version, providing the kernel with a unique identifier for policy lookups. The <b>Purpose</b> section provides a natural-language description of the agent\'s function, used by the Orchestrator AI for task routing decisions. The <b>Knowledge Base Scope</b> section defines the bounded corpus of information the agent is authorized to draw from, including specific data sources, explicit exclusions, and a refresh policy that determines how stale data is tolerated.', STY['body']))

story.append(Paragraph(
    'The <b>Capabilities (Tools)</b> section lists every tool, function, or API endpoint the agent is authorized to invoke, with a brief description of each. The <b>Forbidden Actions</b> section explicitly enumerates actions the agent must never perform, including cross-domain table access and cross-agent endpoint invocation. The <b>Input Schema</b> and <b>Output Schema</b> sections define the expected formats for agent communication. The <b>Constraints</b> section sets the system prompt invariant (which forces the agent to answer only from its authorized knowledge base), maximum output tokens, and temperature. Finally, the <b>IPC Policy</b> section specifies the exact PostgreSQL tables the agent can read from or write to, the API endpoints it can call, its resource limits (memory, CPU, maximum duration), and the conditions under which it must escalate to the Orchestrator or human operator.', STY['body']))

# Schema table
story.append(Spacer(1, 12))
story.append(Paragraph('<b>Table 2: SKILL.md Schema Sections</b>', STY['caption']))
story.append(make_table(
    ['Section', 'Purpose', 'Enforced By', 'Modifiable At Runtime'],
    [
        ['Identity', 'Unique agent identifier, role, domain, version', 'Rust kernel (manifest key)', 'No (requires reload)'],
        ['Knowledge Base Scope', 'Authorized data sources, exclusions, refresh policy', 'Rust kernel (RAG guard)', 'Yes (hot reload)'],
        ['Capabilities (Tools)', 'List of authorized tools with descriptions', 'Rust kernel (tool whitelist)', 'Yes (hot reload)'],
        ['Forbidden Actions', 'Explicit action prohibitions', 'Rust kernel (deny list)', 'Yes (hot reload)'],
        ['Input/Output Schema', 'Communication format definitions', 'Python agent (validation)', 'Yes (hot reload)'],
        ['Constraints', 'System prompt invariant, tokens, temperature', 'Python agent (SLM config)', 'Yes (hot reload)'],
        ['IPC Policy', 'Table access, endpoints, resource limits', 'Rust kernel (policy engine)', 'Yes (hot reload)'],
        ['Escalation Triggers', 'Conditions requiring Orchestrator/human intervention', 'Rust kernel (escalation)', 'Yes (hot reload)'],
    ],
    [1.2*inch, 2.0*inch, 1.5*inch, 1.5*inch]
))

story.append(add_heading('<b>2.3 How SKILL.md Solves the Blocking Problem</b>', STY['h2'], 1))
story.append(Paragraph(
    'The SKILL.md paradigm directly addresses all five failure modes identified in the diagnosis. <b>Over-scoped policies</b> are eliminated because each agent\'s policy is defined in its own SKILL.md file, scoped exclusively to its domain. The Technical SEO agent\'s SKILL.md declares access to technical_seo_audits and crawl_results tables; the Parasite SEO agent\'s SKILL.md declares access to parasite_analyses and backlink_profiles. The kernel no longer applies a monolithic policy; it evaluates each IPC request against the requesting agent\'s specific SKILL.md manifest. A request from the Technical SEO agent to write to the backlink_profiles table is immediately denied not because of a global rule, but because the Technical SEO agent\'s own SKILL.md does not list that table in its IPC Policy.', STY['body']))

story.append(Paragraph(
    '<b>Cascading blocks</b> are mitigated because the SKILL.md schema includes Escalation Triggers, which define the conditions under which an agent should escalate to the Orchestrator rather than failing silently. When an agent encounters an operation it cannot perform, it raises an escalation event with structured context (what it tried to do, why it failed, what it needs). The Orchestrator can then make an intelligent decision: retry with modified parameters, reroute to a different agent, compose a multi-agent response, or escalate to the human operator with a clear diagnosis. This replaces the current binary block/pass model with a gradient of responses that keeps workflows moving.', STY['body']))

story.append(Paragraph(
    '<b>Opaque errors</b> are replaced by structured IPC responses that include the specific SKILL.md section that was violated, the agent\'s declared capability, and the requested action. When the kernel denies an IPC request, it returns a PolicyViolation response (not a generic PermissionDenied) that contains: the agent identity, the violated policy section, the exact rule text from the SKILL.md file, and a suggested resolution. This transforms debugging from a source-code archaeology exercise into a straightforward policy adjustment.', STY['body']))

# ═══════════════════════════════════════════════════════
# CHAPTER 3: TIERED POLICY ENGINE
# ═══════════════════════════════════════════════════════
story.append(Spacer(1, 24))
story.append(add_heading('<b>3. The Tiered Policy Engine</b>', STY['h1'], 0))

story.append(add_heading('<b>3.1 Three-Tier Enforcement Model</b>', STY['h2'], 1))
story.append(Paragraph(
    'The redesigned Eli-OS control plane replaces the flat enforcement model with a three-tier system that classifies every IPC request by risk level and applies proportionate scrutiny. This ensures that low-risk operations (the vast majority of agent traffic) are processed with minimal latency, while high-risk operations receive the thorough evaluation they warrant. The three tiers are: <b>Green (autonomous pass)</b>, <b>Amber (logged and sampled)</b>, and <b>Red (mandatory human approval)</b>. Each tier has distinct processing rules, latency characteristics, and audit requirements.', STY['body']))

story.append(Paragraph(
    'The <b>Green tier</b> handles read-only operations within an agent\'s declared domain. When the Keyword Agent queries the keyword_clusters table to retrieve previously computed clusters, the kernel verifies that keyword_clusters is listed in the Keyword Agent\'s SKILL.md IPC Policy under allowed read tables, confirms the operation is read-only, and passes the request through without further evaluation. Green tier operations complete in under one millisecond of added latency, which is negligible compared to the PostgreSQL query time. The kernel logs the operation for audit purposes but does not generate an alert. Green tier operations account for an estimated 80-85% of all IPC traffic in a typical SEO workflow.', STY['body']))

story.append(Paragraph(
    'The <b>Amber tier</b> handles write operations and cross-agent data access. When the Technical SEO Agent writes a new audit result to the tech_seo_audits table, the kernel verifies the write permission, checks resource limits (is the agent within its memory and CPU allocation?), validates the data schema against the SKILL.md output schema, and logs the operation with full context. The kernel also applies statistical sampling: a configurable percentage (default 10%) of Amber operations are flagged for asynchronous review by the QA Agent. This provides continuous quality assurance without blocking the workflow. Amber tier operations add approximately 5-10 milliseconds of latency, which is acceptable for write operations that already incur PostgreSQL write latency.', STY['body']))

story.append(Paragraph(
    'The <b>Red tier</b> handles operations that are irreversible, high-impact, or cross-domain. Examples include: deleting data from shared tables, modifying another agent\'s records, executing external API calls that have cost implications (such as paid SERP API queries), or any operation that exceeds the agent\'s declared resource limits. Red tier operations are not automatically blocked; instead, they are routed to the human operator\'s approval queue with full context: the agent identity, the requested operation, the SKILL.md policy section, the risk classification rationale, and a recommended action (approve, deny, or modify). The human operator can approve the operation with a single click, deny it with a reason that feeds back into the agent\'s learning loop, or modify the parameters and return it to the agent for re-execution.', STY['body']))

# Tier table
story.append(Spacer(1, 12))
story.append(Paragraph('<b>Table 3: Tiered Enforcement Specification</b>', STY['caption']))
story.append(make_table(
    ['Tier', 'Trigger Conditions', 'Processing', 'Latency', 'Audit'],
    [
        ['Green', 'Read-only, within agent domain, within resource limits', 'Verify SKILL.md read permission, pass', '<1ms added', 'Log only, no alert'],
        ['Amber', 'Write operations, cross-agent reads, resource threshold approaching', 'Verify write permission, check limits, validate schema, sample for QA', '5-10ms added', 'Full context log, 10% async QA review'],
        ['Red', 'Irreversible ops, cross-domain writes, external paid APIs, resource limit exceeded', 'Halt, route to human approval queue with full context', 'Blocking (human-in-loop)', 'Full audit trail, escalation record, approval receipt'],
    ],
    [0.7*inch, 1.6*inch, 1.8*inch, 0.9*inch, 1.4*inch]
))

story.append(add_heading('<b>3.2 Policy Engine Implementation in Rust</b>', STY['h2'], 1))
story.append(Paragraph(
    'The policy engine is implemented as a dedicated Rust crate within the eli-os workspace: <b>eli-policy</b>. This crate is responsible for parsing SKILL.md files into a structured CapabilityManifest data structure, evaluating IPC requests against the manifest, classifying requests into enforcement tiers, and generating structured PolicyViolation responses when a request is denied. The manifest is loaded at kernel startup and can be hot-reloaded at runtime by sending a SIGUSR1 signal to the kernel process or by calling the /api/v1/kernel/reload-manifest endpoint.', STY['body']))

story.append(Paragraph(
    'The core data structure, CapabilityManifest, is a Serde-serializable struct that maps each agent identity to its parsed SKILL.md sections. The SkillParser module reads each SKILL.md file from a configured directory (default: /etc/eli-os/skills/), extracts the structured sections using a combination of regex-based line parsers and a lightweight Markdown AST, and constructs the CapabilityManifest. If any SKILL.md file fails to parse (missing mandatory sections, malformed IPC Policy, etc.), the parser logs a structured error and excludes that agent from the manifest, rather than failing the entire kernel startup. This ensures that a syntax error in one agent\'s SKILL.md does not prevent the rest of the swarm from operating.', STY['body']))

story.append(Paragraph(
    'The PolicyEvaluator module is the heart of the tiered enforcement system. It receives an IpcRequest (containing the agent identity, the requested operation type, the target resource, and the payload), looks up the agent\'s CapabilityManifest entry, and executes a three-step evaluation. First, it checks the operation against the agent\'s Forbidden Actions list; if the operation matches any forbidden pattern, it returns an immediate Red-tier denial. Second, it checks the operation against the IPC Policy (allowed tables, endpoints, resource limits); if the operation is outside the declared policy, it returns an Amber-tier denial with the specific policy section reference. Third, it classifies the operation into Green, Amber, or Red based on the tier rules described above. The entire evaluation path is deterministic, has O(1) complexity for manifest lookups, and O(n) complexity for forbidden action matching (where n is the number of forbidden actions per agent, typically fewer than ten).', STY['body']))

# ═══════════════════════════════════════════════════════
# CHAPTER 4: IPC PROTOCOL REDESIGN
# ═══════════════════════════════════════════════════════
story.append(Spacer(1, 24))
story.append(add_heading('<b>4. IPC Protocol Redesign</b>', STY['h1'], 0))

story.append(add_heading('<b>4.1 Transport Layer: gRPC over Unix Domain Sockets</b>', STY['h2'], 1))
story.append(Paragraph(
    'The current Eli-OS prototype uses a basic HTTP-based IPC mechanism between the Rust kernel and the Python Eli Claw application. This approach has two critical limitations: serialization overhead (JSON encoding/decoding adds 2-5ms per request) and lack of strong typing (JSON does not enforce schema compliance at the transport level). The redesigned IPC protocol uses <b>gRPC over Unix Domain Sockets</b> (UDS) as the transport layer. gRPC provides Protocol Buffer-based serialization, which is 3-10x faster than JSON for structured data and enforces schema compliance at compile time. Unix Domain Sockets provide inter-process communication on the same machine with lower latency than TCP loopback (no network stack traversal) and built-in file-system-level access control.', STY['body']))

story.append(Paragraph(
    'The gRPC service definition (in protobuf format) specifies four core RPC methods. The <b>EvaluateRequest</b> method accepts an IpcRequest message and returns an IpcResponse message containing either an approval (with optional rate-limit metadata) or a PolicyViolation with structured error details. The <b>ReportResult</b> method allows agents to report operation results back to the kernel for audit logging and event broadcasting. The <b>Escalate</b> method allows agents to raise escalation events when they encounter conditions defined in their SKILL.md Escalation Triggers. The <b>Heartbeat</b> method provides a lightweight keep-alive mechanism that the kernel uses to monitor agent health and detect stalled operations.', STY['body']))

story.append(Paragraph(
    'The choice of gRPC over alternative IPC mechanisms was driven by several factors specific to the Eli-Swarm-Claw architecture. First, gRPC\'s streaming support enables the kernel to push policy updates to agents in real time without requiring polling. When a SKILL.md file is updated and the manifest is reloaded, the kernel can stream the updated capability definition to the affected agent, which then adjusts its behavior without restarting. Second, gRPC\'s built-in deadline and cancellation semantics allow the kernel to enforce the max_duration_seconds resource limit from the SKILL.md IPC Policy. When an agent\'s operation exceeds its time allocation, the kernel cancels the gRPC stream and returns a ResourceExceeded response. Third, Protocol Buffer\'s backward compatibility guarantees ensure that the IPC protocol can evolve independently of the kernel and agent codebases, supporting incremental rollout of new features without breaking existing deployments.', STY['body']))

story.append(add_heading('<b>4.2 Structured Error Responses</b>', STY['h2'], 1))
story.append(Paragraph(
    'The redesigned IPC protocol replaces the generic PermissionDenied error with a structured <b>PolicyViolation</b> response that provides full diagnostic context. Every denial includes: the agent identity that made the request, the operation type (read, write, execute, delete), the target resource (table name, endpoint URL, or tool identifier), the violated SKILL.md section name (e.g., "IPC Policy: Allowed Tables"), the exact rule text from the SKILL.md file that was violated, the enforcement tier that evaluated the request (Green, Amber, or Red), a human-readable explanation of why the violation occurred, and a suggested resolution (update SKILL.md, escalate to Orchestrator, request human override, or modify the operation parameters). This structured response format transforms every policy denial from a debugging obstacle into an actionable diagnostic.', STY['body']))

# IPC comparison table
story.append(Spacer(1, 12))
story.append(Paragraph('<b>Table 4: IPC Mechanism Comparison</b>', STY['caption']))
story.append(make_table(
    ['Mechanism', 'Serialization', 'Latency (Local)', 'Schema Enforcement', 'Streaming', 'Access Control'],
    [
        ['HTTP/JSON (current)', 'JSON', '2-5ms overhead', 'Runtime only', 'No', 'Application-level'],
        ['gRPC/UDS (proposed)', 'Protocol Buffers', '0.2-0.5ms overhead', 'Compile-time + runtime', 'Bidirectional', 'File-system + protocol'],
        ['Shared Memory', 'Raw bytes', '<0.1ms overhead', 'None (manual)', 'No', 'OS process isolation'],
        ['TCP Sockets', 'Protocol Buffers', '0.5-1ms overhead', 'Compile-time + runtime', 'Bidirectional', 'Network-level'],
    ],
    [1.1*inch, 1.1*inch, 1.1*inch, 1.2*inch, 0.8*inch, 1.2*inch]
))

# ═══════════════════════════════════════════════════════
# CHAPTER 5: THE ORCHESTRATOR AI
# ═══════════════════════════════════════════════════════
story.append(Spacer(1, 24))
story.append(add_heading('<b>5. The Orchestrator AI: Kimi K2.7 Code Integration</b>', STY['h1'], 0))

story.append(add_heading('<b>5.1 Why Kimi K2.7 Code</b>', STY['h2'], 1))
story.append(Paragraph(
    'The Orchestrator AI is the "second AI" in the Eli-OS architecture, responsible for decomposing complex full-stack SEO tasks, routing sub-tasks to the appropriate specialized agents, synthesizing multi-agent outputs into unified responses, and handling escalation events from the swarm. The selection of <b>Kimi K2.7 Code</b> as the Orchestrator model is driven by four key technical capabilities that align precisely with the Eli-OS requirements.', STY['body']))

story.append(Paragraph(
    'First, Kimi K2.7 Code is an <b>open-weight model</b> released under permissive licensing by Moonshot AI. This means the Orchestrator can be hosted entirely within VirtuaLab Digital\'s sovereign infrastructure, without sending sensitive SEO data, client URLs, or competitive intelligence to closed-source API providers. The model weights are fully auditable, allowing the team to inspect and modify the model\'s behavior if needed. Second, Kimi K2.7 Code is explicitly designed as a <b>terminal-first agentic model</b>, optimized for executing multi-step workflows, managing tool calls, and handling complex decision trees. This makes it ideally suited for the Orchestrator role, which requires precisely these capabilities: receiving a high-level task, breaking it into sub-tasks, executing tool calls to delegate to agents, and handling the results.', STY['body']))

story.append(Paragraph(
    'Third, Kimi K2.7 Code supports a <b>1-million-token context window</b> (via the Kimi-Linear architecture), which is critical for the Orchestrator\'s role. A full-stack SEO audit of a large website can generate hundreds of pages of crawl data, keyword research, entity analysis, and competitor intelligence. The Orchestrator must be able to hold this context in memory while making routing and synthesis decisions. With a 1M token context, the Orchestrator can ingest the complete output of multiple agents simultaneously without truncation or summarization loss. Fourth, the model is the first open-weight model available in <b>GitHub Copilot\'s model picker</b>, demonstrating production readiness and broad community validation.', STY['body']))

story.append(add_heading('<b>5.2 Orchestrator Architecture</b>', STY['h2'], 1))
story.append(Paragraph(
    'The Orchestrator operates as a stateful decision engine within the Eli Claw Python application plane. It is not a separate process; it is a Python class (EliOrchestrator) that wraps the Kimi K2.7 Code model (served locally via vLLM or SGLang for high-throughput inference) and provides four core methods: <b>decompose</b>, <b>route</b>, <b>synthesize</b>, and <b>handle_escalation</b>. The decompose method accepts a high-level task from the human operator or the API, uses the Kimi model to break it into a directed acyclic graph (DAG) of sub-tasks, and returns the DAG with dependency edges. The route method accepts a sub-task, evaluates it against each agent\'s SKILL.md Purpose section, and selects the most capable agent. The synthesize method accepts the outputs of completed sub-tasks and merges them into a unified response. The handle_escalation method accepts an escalation event from an agent or the Rust kernel and decides whether to retry, reroute, compose, or escalate to the human operator.', STY['body']))

story.append(Paragraph(
    'The Orchestrator does not bypass the Rust control plane. Every sub-task delegation and agent invocation passes through the kernel\'s IPC evaluation. The Orchestrator\'s advantage is intelligence, not authority. It can make routing decisions that the kernel cannot (because routing requires semantic understanding of task intent, which is beyond the kernel\'s scope), but it cannot override the kernel\'s policy enforcement. This separation of concerns is critical: the Orchestrator provides <b>semantic safety</b> (ensuring tasks are routed to the right agent and outputs are coherent), while the kernel provides <b>hard safety</b> (ensuring agents stay within their declared boundaries). Neither layer is sufficient alone; together, they provide comprehensive governance without the blocking problem.', STY['body']))

# ═══════════════════════════════════════════════════════
# CHAPTER 6: FULL-STACK SEO SWARM
# ═══════════════════════════════════════════════════════
story.append(Spacer(1, 24))
story.append(add_heading('<b>6. Full-Stack SEO Swarm: Agent Inventory</b>', STY['h1'], 0))

story.append(add_heading('<b>6.1 The 12-Agent Architecture</b>', STY['h2'], 1))
story.append(Paragraph(
    'The Eli Claw application plane hosts twelve specialized agents, each defined by its own SKILL.md file and governed by the tiered policy engine. The swarm is designed so that the full-stack SEO capability emerges from the composition of these specialized agents, orchestrated by the Kimi K2.7 Code Orchestrator. No single agent is "gigantic"; each is a constrained Micro-RAG system with a bounded knowledge base, a specific tool set, and clear escalation paths. The "full-stack" capability is achieved through coordination, not through a single monolithic model.', STY['body']))

# Agent inventory table
story.append(Spacer(1, 12))
story.append(Paragraph('<b>Table 5: Agent Inventory and Domain Mapping</b>', STY['caption']))
story.append(make_table(
    ['Agent', 'Domain', 'Knowledge Base', 'Primary Tools', 'Tier Focus'],
    [
        ['Technical SEO', 'Crawlability, HTTP, CWV', 'Google Search Central, W3C, Core Web Vitals specs', 'Sitemap parser, HTTP inspector, robots.txt analyzer', 'Green reads, Amber writes'],
        ['On-Page SEO', 'Meta tags, schema, content', 'Schema.org, NLP keyword semantics', 'DOM parser, meta-tag generator, readability scorer', 'Green reads, Amber writes'],
        ['Parasite SEO', 'High-DA platforms, backlinks', 'Platform TOS, backlink velocity data', 'DA checker, platform API wrappers, SERP tracker', 'Amber reads, Red writes'],
        ['GEO', 'AI citations, entity salience', 'SGE/Perplexity patterns, citation data', 'Citation tracker, entity-salience analyzer', 'Green reads, Amber writes'],
        ['AI Citation', 'Brand mentions in AI', 'AI answer logs, citation source data', 'Citation probe, mention-frequency analyzer', 'Green reads, Green writes'],
        ['Keyword', 'Seed expansion, clustering', 'Search demand data, SERP features', 'Keyword expander, intent classifier, clusterer', 'Green reads, Amber writes'],
        ['Entity', 'Entity extraction, semantics', 'Knowledge graph data, semantic web', 'Entity extractor, relationship mapper', 'Green reads, Amber writes'],
        ['Competitor', 'Keyword/content/visibility gaps', 'Competitor crawl data, SERP snapshots', 'Gap analyzer, visibility benchmark', 'Green reads, Amber writes'],
        ['Local SEO', 'Service areas, NAP, GBP', 'GBP signals, local SERP data', 'NAP checker, service-area mapper', 'Green reads, Amber writes'],
        ['Indexing', 'Sitemaps, IndexNow, feeds', 'GSC coverage data, feed specs', 'Sitemap generator, IndexNow pusher', 'Amber reads, Red writes'],
        ['QA', 'Data quality, compliance', 'Policy rules, validation schemas', 'Data validator, output checker', 'Green reads (all tables, read-only)'],
        ['Report', 'Client-facing summaries', 'All agent outputs (read-only)', 'Report generator, chart builder', 'Green reads, Amber writes'],
    ],
    [0.9*inch, 1.2*inch, 1.4*inch, 1.4*inch, 1.2*inch]
))

story.append(add_heading('<b>6.2 Cross-Agent Communication Protocol</b>', STY['h2'], 1))
story.append(Paragraph(
    'Agents do not communicate directly with each other. All inter-agent communication is mediated by the Rust kernel through an <b>event bus</b> architecture. When an agent completes a task, it publishes a result event to the kernel\'s event bus. The kernel logs the event, evaluates it against the QA Agent\'s sampling policy, and broadcasts it to any subscribers. The Orchestrator subscribes to all agent result events and uses them to update its task DAG. Other agents may subscribe to specific event types (for example, the Entity Agent subscribes to Keyword Agent results to enrich its knowledge graph), but they never receive direct messages from other agents.', STY['body']))

story.append(Paragraph(
    'This event bus architecture prevents several failure modes that are common in direct agent-to-agent communication systems. First, it eliminates <b>message amplification loops</b>, where Agent A sends a message to Agent B, which triggers a response to Agent A, which triggers another response, creating an unbounded cycle. The kernel\'s event bus is a one-directional publish-subscribe system; agents can publish results and subscribe to events, but they cannot reply to events. If an agent needs to act on another agent\'s output, it must create a new task (which goes through the kernel\'s IPC evaluation) rather than sending a direct response. Second, it provides a <b>single audit trail</b> for all inter-agent communication. Every event is logged with a ULID, a timestamp, the publisher identity, the subscriber identities, and the payload. This audit trail is critical for debugging, compliance, and the QA Agent\'s asynchronous review process.', STY['body']))

# ═══════════════════════════════════════════════════════
# CHAPTER 7: RISK ANALYSIS
# ═══════════════════════════════════════════════════════
story.append(Spacer(1, 24))
story.append(add_heading('<b>7. Risk Analysis and Mitigation</b>', STY['h1'], 0))

story.append(add_heading('<b>7.1 Residual Risks After Redesign</b>', STY['h2'], 1))
story.append(Paragraph(
    'While the SKILL.md paradigm and tiered policy engine eliminate the five identified failure modes, they introduce new risks that must be acknowledged and mitigated. The most significant residual risk is <b>SKILL.md drift</b>: the possibility that an agent\'s SKILL.md file becomes outdated relative to its actual behavior. If an agent is updated to use a new database table but its SKILL.md is not updated accordingly, the kernel will deny the legitimate IPC request, reproducing the original blocking problem through a different mechanism. Mitigation: the CI/CD pipeline must include a SKILL.md validation step that compares the agent\'s actual database queries (extracted from integration tests) against its declared IPC Policy. Any discrepancy blocks the deployment.', STY['body']))

story.append(Paragraph(
    'A second residual risk is <b>Orchestrator hallucination in routing</b>. The Kimi K2.7 Code model, like all large language models, can produce incorrect outputs. If the Orchestrator routes a technical SEO task to the Parasite SEO agent, the Parasite agent will either refuse (because the task is outside its declared Purpose) or produce a low-quality result. The kernel does not validate the Orchestrator\'s routing decisions because routing is a semantic operation that requires understanding task intent. Mitigation: the QA Agent asynchronously reviews a sample of routing decisions and flags anomalies. Additionally, each agent\'s system prompt invariant forces it to refuse tasks outside its domain, providing a secondary safety net.', STY['body']))

story.append(Paragraph(
    'A third residual risk is <b>gRPC serialization bottleneck</b> under high concurrency. While gRPC is significantly faster than JSON for individual requests, the Python gRPC client has a higher per-connection overhead than the current HTTP client. If the swarm scales to hundreds of concurrent agents, the gRPC connection pool may become a bottleneck. Mitigation: the IPC architecture supports connection multiplexing through gRPC\'s HTTP/2 transport, and the kernel can shard the IPC load across multiple Unix Domain Socket listeners if needed. Performance benchmarks should be conducted at the target scale before production deployment.', STY['body']))

# Risk table
story.append(Spacer(1, 12))
story.append(Paragraph('<b>Table 6: Residual Risk Register</b>', STY['caption']))
story.append(make_table(
    ['Risk', 'Probability', 'Impact', 'Mitigation Strategy', 'Owner'],
    [
        ['SKILL.md drift', 'Medium', 'High', 'CI/CD validation step comparing test queries to IPC Policy', 'DevOps'],
        ['Orchestrator routing hallucination', 'Medium', 'Medium', 'QA Agent sampling + agent domain refusal invariant', 'ML Engineering'],
        ['gRPC bottleneck at scale', 'Low', 'High', 'Connection multiplexing + UDS sharding + benchmarks', 'Platform Engineering'],
        ['Hot-reload race condition', 'Low', 'Medium', 'Atomic manifest swap with read-copy-update pattern', 'Rust Kernel Team'],
        ['Kimi K2.7 inference latency', 'Medium', 'Medium', 'vLLM/SGLang batching + model quantization (INT4)', 'ML Engineering'],
    ],
    [1.2*inch, 0.8*inch, 0.7*inch, 2.0*inch, 1.1*inch]
))

# ═══════════════════════════════════════════════════════
# CHAPTER 8: IMPLEMENTATION ROADMAP
# ═══════════════════════════════════════════════════════
story.append(Spacer(1, 24))
story.append(add_heading('<b>8. Implementation Roadmap</b>', STY['h1'], 0))

story.append(add_heading('<b>8.1 Phase 1: Foundation (Weeks 1-3)</b>', STY['h2'], 1))
story.append(Paragraph(
    'The first phase establishes the foundational components that all subsequent work depends on. The primary deliverables are: the SKILL.md schema parser in Rust (eli-skill-parser crate), the CapabilityManifest data structure with Serde serialization, and a minimal policy evaluator that supports Green-tier enforcement only. This phase also includes writing the SKILL.md files for three pilot agents (Technical SEO, Keyword, and QA) and integrating them into the existing Eli Claw FastAPI scaffold. The acceptance criterion for Phase 1 is a successful end-to-end test where a Python agent makes a gRPC IPC request to the Rust kernel, the kernel evaluates it against the agent\'s SKILL.md manifest, and returns an approval or a structured PolicyViolation response.', STY['body']))

story.append(add_heading('<b>8.2 Phase 2: Tiered Enforcement (Weeks 4-6)</b>', STY['h2'], 1))
story.append(Paragraph(
    'The second phase extends the policy evaluator to support all three enforcement tiers (Green, Amber, Red) and implements the human approval queue for Red-tier operations. This phase also includes the structured error response format, the event bus architecture for cross-agent communication, and the SIGUSR1 hot-reload mechanism for SKILL.md files. The remaining nine SKILL.md files are written and integrated. The acceptance criterion is a multi-agent workflow where the Orchestrator decomposes a task, routes sub-tasks to three different agents, one of which triggers an Amber-tier log and another triggers a Red-tier human approval, and the workflow completes successfully with full audit trail.', STY['body']))

story.append(add_heading('<b>8.3 Phase 3: Orchestrator Integration (Weeks 7-9)</b>', STY['h2'], 1))
story.append(Paragraph(
    'The third phase integrates the Kimi K2.7 Code model as the Orchestrator AI. This phase includes setting up the vLLM inference server, implementing the EliOrchestrator Python class with its four core methods (decompose, route, synthesize, handle_escalation), connecting the Orchestrator to the kernel\'s event bus, and implementing the escalation handling flow. The acceptance criterion is a full-stack SEO workflow triggered by a natural-language prompt (for example, "Audit example.com for technical SEO issues, research keywords, and generate a content brief"), which the Orchestrator decomposes, routes to the appropriate agents, and synthesizes into a unified report without human intervention.', STY['body']))

story.append(add_heading('<b>8.4 Phase 4: Hardening and Production (Weeks 10-12)</b>', STY['h2'], 1))
story.append(Paragraph(
    'The final phase focuses on production readiness: performance benchmarking of the gRPC IPC layer under load, security audit of the policy engine and SKILL.md parser, comprehensive integration testing across all twelve agents, documentation of the SKILL.md authoring guide for future agent developers, and deployment of the complete system to the VirtuaLab Digital infrastructure with Docker Compose orchestration. The acceptance criterion is a 72-hour soak test where the system processes a continuous stream of SEO tasks across all twelve agents without a single false-positive block or policy engine failure.', STY['body']))

# Roadmap table
story.append(Spacer(1, 12))
story.append(Paragraph('<b>Table 7: Implementation Timeline</b>', STY['caption']))
story.append(make_table(
    ['Phase', 'Duration', 'Key Deliverables', 'Acceptance Criterion'],
    [
        ['1: Foundation', 'Weeks 1-3', 'SKILL.md parser, CapabilityManifest, 3 pilot agents, gRPC IPC', 'End-to-end Green-tier IPC test passes'],
        ['2: Tiered Enforcement', 'Weeks 4-6', 'Amber/Red tiers, event bus, hot-reload, 12 SKILL.md files', 'Multi-agent workflow with all three tiers'],
        ['3: Orchestrator', 'Weeks 7-9', 'Kimi K2.7 Code integration, EliOrchestrator, escalation flow', 'Natural-language full-stack SEO workflow'],
        ['4: Production', 'Weeks 10-12', 'Benchmarks, security audit, docs, 72-hour soak test', 'Zero false-positive blocks in 72-hour test'],
    ],
    [1.2*inch, 0.9*inch, 2.0*inch, 2.0*inch]
))

# ═══════════════════════════════════════════════════════
# CHAPTER 9: DIRECTORY MAP
# ═══════════════════════════════════════════════════════
story.append(Spacer(1, 24))
story.append(add_heading('<b>9. Deliverable File Map</b>', STY['h1'], 0))
story.append(Paragraph(
    'This white paper is accompanied by a set of implementation deliverables that provide the concrete code artifacts needed to execute the architectural redesign described in this document. The deliverables are organized into four directories: the SKILL.md templates (twelve files, one per agent), the Rust control plane code (three crates: skill parser, policy engine, and IPC handler), the Python integration code (agent base class, IPC client, and Orchestrator), and integration notes that map the OpenClaw and Kimi K2.7 Code ecosystems to the Eli-OS architecture.', STY['body']))

story.append(Spacer(1, 12))
story.append(Paragraph('<b>Table 8: Deliverable File Structure</b>', STY['caption']))
story.append(make_table(
    ['Path', 'Description', 'Language'],
    [
        ['skill-templates/technical_seo.md', 'Technical SEO Agent SKILL.md', 'Markdown'],
        ['skill-templates/on_page_seo.md', 'On-Page SEO Agent SKILL.md', 'Markdown'],
        ['skill-templates/parasite_seo.md', 'Parasite SEO Agent SKILL.md', 'Markdown'],
        ['skill-templates/geo_agent.md', 'GEO Agent SKILL.md', 'Markdown'],
        ['skill-templates/ai_citation.md', 'AI Citation Agent SKILL.md', 'Markdown'],
        ['skill-templates/keyword_agent.md', 'Keyword Agent SKILL.md', 'Markdown'],
        ['skill-templates/entity_agent.md', 'Entity Agent SKILL.md', 'Markdown'],
        ['skill-templates/competitor_agent.md', 'Competitor Agent SKILL.md', 'Markdown'],
        ['skill-templates/local_seo.md', 'Local SEO Agent SKILL.md', 'Markdown'],
        ['skill-templates/indexing_agent.md', 'Indexing Agent SKILL.md', 'Markdown'],
        ['skill-templates/qa_agent.md', 'QA Agent SKILL.md', 'Markdown'],
        ['skill-templates/report_agent.md', 'Report Agent SKILL.md', 'Markdown'],
        ['rust-control-plane/eli-skill-parser/', 'Rust SKILL.md parser crate', 'Rust'],
        ['rust-control-plane/eli-policy-engine/', 'Rust tiered policy engine crate', 'Rust'],
        ['rust-control-plane/eli-ipc-handler/', 'Rust gRPC IPC handler crate', 'Rust'],
        ['python-integration/agents/', 'Python agent base class + examples', 'Python'],
        ['python-integration/orchestrator/', 'Python EliOrchestrator implementation', 'Python'],
        ['integration-notes/', 'OpenClaw + Kimi K2.7 mapping document', 'Markdown'],
    ],
    [2.5*inch, 2.5*inch, 0.8*inch]
))

# ━━━ BUILD PDF ━━━
output_body = os.path.join(OUTPUT_DIR, 'Eli-OS-Architecture-Body.pdf')
doc = TocDocTemplate(
    output_body,
    pagesize=A4,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    topMargin=MARGIN,
    bottomMargin=MARGIN,
    title='Eli-OS Architecture: Fixing the Blocking Problem',
    author='Joseph Rainer - VirtuaLab Digital',
    subject='AI Agent OS Control Plane Redesign',
)

doc.multiBuild(story, onFirstPage=page_bg, onLaterPages=page_bg)
print(f'Body PDF generated: {output_body}')
