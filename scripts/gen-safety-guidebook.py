#!/usr/bin/env python3
"""Generate Eli Safety Parameter Guidebook PDF.
Report pipeline: ReportLab body + HTML cover via Template 01.
"""

import sys, os, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'skills', 'pdf', 'scripts'))

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus import SimpleDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ━━ Fonts ━━
FD = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('FSerif', f'{FD}/truetype/freefont/FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('FSerifB', f'{FD}/truetype/freefont/FreeSerifBold.ttf'))
pdfmetrics.registerFont(TTFont('FSerifI', f'{FD}/truetype/freefont/FreeSerifItalic.ttf'))
pdfmetrics.registerFont(TTFont('FSerifBI', f'{FD}/truetype/freefont/FreeSerifBoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu', f'{FD}/truetype/dejavu/DejaVuSansMono.ttf'))
registerFontFamily('FSerif', normal='FSerif', bold='FSerifB', italic='FSerifI', boldItalic='FSerifBI')
registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu')

# ━━ Palette ━━
C = colors
PAGE_BG = C.HexColor('#f4f4f3')
STRIPE = C.HexColor('#f1f1ef')
HDR = C.HexColor('#817349')
BDR = C.HexColor('#c4c0b3')
ICON_C = C.HexColor('#857239')
ACCENT = C.HexColor('#a58629')
TX = C.HexColor('#1a1a18')
TXM = C.HexColor('#817e77')
CARD = C.HexColor('#efeeea')

W, H = A4
M = 60
AW = W - 2 * M

# ━━ Styles ━━
toc_h1 = ParagraphStyle('t1', fontName='FSerifB', fontSize=12, leading=20, leftIndent=0, textColor=TX, spaceBefore=8, spaceAfter=4)
toc_h2 = ParagraphStyle('t2', fontName='FSerif', fontSize=10.5, leading=18, leftIndent=20, textColor=TXM, spaceBefore=2, spaceAfter=2)
h1 = ParagraphStyle('h1', fontName='FSerifB', fontSize=20, leading=28, textColor=HDR, spaceBefore=24, spaceAfter=12)
h2 = ParagraphStyle('h2', fontName='FSerifB', fontSize=14, leading=20, textColor=TX, spaceBefore=18, spaceAfter=8)
h3 = ParagraphStyle('h3', fontName='FSerifB', fontSize=11.5, leading=16, textColor=ICON_C, spaceBefore=12, spaceAfter=6)
bd = ParagraphStyle('bd', fontName='FSerif', fontSize=10.5, leading=18, alignment=TA_JUSTIFY, textColor=TX, spaceAfter=6)
code = ParagraphStyle('code', fontName='DejaVu', fontSize=8.5, leading=13, textColor=TX, backColor=CARD, leftIndent=12, rightIndent=12, spaceBefore=6, spaceAfter=6, borderPadding=6)
cap = ParagraphStyle('cap', fontName='FSerifI', fontSize=9, leading=14, textColor=TXM, spaceAfter=12)
callout = ParagraphStyle('cal', fontName='FSerif', fontSize=10, leading=16, textColor=ACCENT, leftIndent=18, borderLeftWidth=3, borderLeftColor=ACCENT, borderPadding=8, spaceBefore=8, spaceAfter=8)

MAX_KH = H * 0.4

def sk(els):
    t = sum(e.wrap(AW, H)[1] for e in els if hasattr(e, 'wrap'))
    if t <= MAX_KH: return [KeepTogether(els)]
    return [KeepTogether(els[:2])] + list(els[2:]) if len(els) >= 2 else list(els)

def ah(text, style, level=0):
    key = f'h_{hashlib.md5(text.encode()).hexdigest()[:8]}'
    p = Paragraph(f'<a name="{key}"/>{text}', style)
    p.bookmark_name = p.bookmark_text = p.bookmark_key = key
    p.bookmark_level = level
    return p

def tbl(headers, rows, cw=None):
    if cw is None: cw = [AW / len(headers)] * len(headers)
    th = ParagraphStyle('th', fontName='FSerifB', fontSize=9, leading=13, textColor=C.white)
    td = ParagraphStyle('td', fontName='FSerif', fontSize=9, leading=13, textColor=TX)
    data = [[Paragraph(h, th) for h in headers]] + [[Paragraph(str(c), td) for c in r] for r in rows]
    cmds = [('BACKGROUND', (0,0), (-1,0), HDR), ('TEXTCOLOR', (0,0), (-1,0), C.white),
            ('VALIGN', (0,0), (-1,-1), 'TOP'), ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6), ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, BDR)]
    for i in range(2, len(data), 2): cmds.append(('BACKGROUND', (0,i), (-1,i), STRIPE))
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(cmds))
    return t

class TocDoc(SimpleDocTemplate):
    def afterFlowable(self, f):
        if hasattr(f, 'bookmark_name'):
            self.notify('TOCEntry', (f.bookmark_level, f.bookmark_text, self.page, f.bookmark_key))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('FSerifI', 8)
    canvas.setFillColor(TXM)
    canvas.drawRightString(W-M, 25, f'Page {doc.page}')
    canvas.drawString(M, 25, 'Eli Safety Parameter Guidebook')
    canvas.restoreState()

# Monospace helper
mono = lambda t: f'<font name="DejaVu">{t}</font>'

# ━━ Content ━━
story = []

# TOC
toc = TableOfContents()
toc.levelStyles = [toc_h1, toc_h2]
story.append(Paragraph('Table of Contents', h1))
story.append(Spacer(1, 12))
story.append(toc)
story.append(PageBreak())

# Ch1
story.append(ah('Chapter 1: Safety Architecture Overview', h1, 0))
story.append(ah('1.1 The Limited Key Model', h2, 1))
story.append(Paragraph('Eli operates on a fundamentally constrained resource model: a small, fixed pool of API keys managed by the OmniRoute rotation coordinator. Unlike traditional SaaS applications that can provision unlimited API credentials, Eli relies on a combination of long-lived Gemini keys (such as the primary AQ.-prefixed key) and temporary disposable keys generated by the OpenClaw email engine. This constraint shapes every safety decision in the system. When your key pool is finite and partially auto-generated, every request that reaches an LLM API consumes a scarce resource that cannot be arbitrarily replenished.', bd))
story.append(Paragraph('The OmniRoute coordinator maintains a penalty-tracked pool where each key carries a health score. Keys that return 429 rate-limit errors, 5xx server errors, or timeout failures accumulate penalty points. Once a key reaches the penalty ceiling, it is rotated out and the next healthiest key takes over. An attacker who attempts to drain keys through rapid requests triggers automatic rotation, but rotation itself consumes inboxes and provider capacity, which are also finite. The safety system must protect not just the active key but the entire key lifecycle.', bd))
story.append(Paragraph('OpenClaw generates temporary email inboxes across three providers: Guerrilla Mail, mail.tm, and OpenInbox. Each inbox has a 55-minute TTL, can hold at most one API key, and the system maintains a maximum of 10 concurrent inboxes with a hard cap of 20 pending keys. These numbers represent real resource constraints. A sustained attack forcing rapid rotation could exhaust email provider limits, leaving Eli without recovery paths.', bd))

story.append(ah('1.2 Three-Tier Safety Model', h2, 1))
story.append(Paragraph('The safety system is organized into three progressive tiers. Tier 1, the focus of this guidebook, provides essential guards that prevent immediate abuse: authentication, input validation, rate limiting, payload limits, key format validation, prompt injection blocking, and structured audit logging. These are the minimum viable safety parameters any API-facing system should implement.', bd))
story.extend(sk([tbl(['Tier','Scope','Key Mechanisms','Status'], [
    ['Tier 1','API gate, input, output','Auth, rate limit, payload, sanitization, key validation, audit','Implemented'],
    ['Tier 2','Session, identity, quota','Per-session keys, scoped rate limits, user identity, call gating','Planned'],
    ['Tier 3','Resource, tenant, expiry','Per-resource permissions, tenant isolation, key expiry, rotation schedules','Future'],
], [AW*0.08, AW*0.17, AW*0.52, AW*0.23]), Spacer(1,6),
    Paragraph('Table 1: Three-tier safety model with implementation status.', cap)]))
story.append(Paragraph('Tier 2 will introduce per-session API keys generated for each authenticated user, eliminating the need to share the master key. The capability level system (public, user, operator, admin) will become fully enforced with per-session capability tokens. Tier 3 adds resource-level permissions, tenant isolation for multi-organization deployments, and automated key expiry policies.', bd))

story.append(ah('1.3 Centralized Safety Module', h2, 1))
story.append(Paragraph(f'All safety parameters live in a single source-of-truth module: {mono("src/lib/safety-gate.ts")}. Every constant, function, and type that route handlers need is exported from this file with JSDoc documentation explaining what it is, why it exists, and where it is used. No route file contains hardcoded safety values. This centralization means auditing the entire safety surface requires reading one file, and changing a limit requires editing exactly one place.', bd))
story.append(Paragraph(f'The audit log ({mono("src/lib/audit-log.ts")}) provides a structured, persistent record of every security-relevant event. Each entry includes an ISO timestamp, event type, detail, metadata, and caller IP. Events are buffered in memory (capped at 500 entries) and asynchronously appended to a JSONL file on disk. This is the forensic record that makes post-incident analysis possible.', bd))

# Ch2
story.append(ah('Chapter 2: API Authentication Gate', h1, 0))
story.append(ah('2.1 Design Philosophy', h2, 1))
story.append(Paragraph(f'The authentication gate is the outermost defense layer. In Tier 1, it uses a single shared bearer token checked against the {mono("ELI_API_KEY")} environment variable. This is intentionally simple: the Tier 1 threat model targets casual discovery and automated scanning. Someone who discovers the API URL should be met with a 401 response, not an open endpoint that drains LLM keys. The gate supports two methods: the standard {mono("Authorization: Bearer <key>")} header, and a {mono("?key=<key>")} query parameter for convenient curl testing.', bd))

story.append(ah('2.2 Defense-in-Depth Check Ordering', h2, 1))
story.append(Paragraph(f'The {mono("checkAuth()")} function accepts any object with {mono("headers")} and optional {mono("url")} properties, making it compatible with Next.js without framework coupling. Every route handler calls this first, before rate limiting, before payload parsing, before business logic. This ordering ensures a blocked request consumes zero server resources beyond the authentication check itself.', bd))
story.extend(sk([tbl(['Step','Check','Fail Response','Cost'], [
    ['1','checkAuth(request)','401 Unauthorized','Near-zero (string compare)'],
    ['2','checkRateLimit(ip, config)','429 Too Many Requests','Map lookup + array push'],
    ['3','Payload size (content-length)','413 Payload Too Large','Integer parse + compare'],
    ['4','Input validation / sanitization','400 Bad Request','Regex + string ops'],
    ['5','Business logic (LLM call)','Varies','High (network I/O)'],
], [AW*0.08, AW*0.32, AW*0.35, AW*0.25]), Spacer(1,6),
    Paragraph('Table 2: Defense-in-depth check ordering from cheapest to most expensive.', cap)]))

story.append(ah('2.3 Capability Gating', h2, 1))
story.append(Paragraph(f'The {mono("checkCapability()")} function adds a capability level system on top of auth. Four levels are defined: public (no auth, for health checks), user (read-only state), operator (modify non-sensitive state like rotating keys), and admin (full access including raw keys and audit logs). In Tier 1, all authenticated users are treated as admin since there is one master key. The {mono("OMNI_CAPABILITIES")} array maps every omni route action to its required level, making the permission model explicit and auditable for Tier 2 implementation.', bd))
story.extend(sk([tbl(['Level','Hierarchy','Access Scope','Example Actions'], [
    ['public','0','No auth required','Health check, GET /api/health'],
    ['user','1','Read-only system state','View omni state (masked keys), record usage'],
    ['operator','2','Modify non-sensitive state','Force rotation, create inbox, reject pending key'],
    ['admin','3','Full access including secrets','Read raw key, inject key, approve, read audit log'],
], [AW*0.12, AW*0.1, AW*0.33, AW*0.45]), Spacer(1,6),
    Paragraph('Table 3: Capability level hierarchy and access scope.', cap)]))

# Ch3
story.append(ah('Chapter 3: Rate Limiting', h1, 0))
story.append(ah('3.1 Why Rate Limiting Is Critical', h2, 1))
story.append(Paragraph('Rate limiting in Eli serves a dual purpose: preventing server overload and protecting finite LLM API key quotas. A single Gemini free-tier key might allow 15 requests per minute and 1,500 per day. An attacker sending 100 requests per second would drain the daily quota in 15 seconds. The rate limiter acts as a resource preservation tool, not just a performance tool. The implementation uses an in-memory sliding window algorithm: each IP address maintains a list of request timestamps, pruned on each request to remove entries outside the configured window duration.', bd))

story.append(ah('3.2 Per-Route Configuration', h2, 1))
story.extend(sk([tbl(['Route','Limit','Window','Rationale'], [
    ['/api/eli-chat POST','15 req/min','60s','LLM key budget; Gemini free tier bottleneck'],
    ['/api/omni GET','30 req/min','60s','Monitoring reads are cheap; higher for dashboards'],
    ['/api/omni POST','5 req/min','60s','Write actions spawn inboxes, call providers'],
    ['/api/vault-sync GET','20 req/min','60s','File I/O bounded; prevent scraping 24K chunks'],
    ['/api/audit GET','10 req/min','60s','Admin endpoint; low tolerance for info disclosure'],
    ['/api/health GET','120 req/min','60s','Monitoring pings; very permissive'],
], [AW*0.25, AW*0.15, AW*0.12, AW*0.48]), Spacer(1,6),
    Paragraph('Table 4: Per-route rate limit configuration with rationale.', cap)]))

story.append(ah('3.3 Sliding Window Algorithm', h2, 1))
story.append(Paragraph(f'The {mono("checkRateLimit(ip, config)")} function maintains a global Map of IP-to-timestamp-array entries. Every 5 minutes, stale entries are pruned to prevent unbounded memory growth. The function returns true if the request is allowed, false if rejected. Crucially, rejected requests do not consume a slot; only allowed requests are recorded. The {mono("getRateLimitState()")} function provides a debug view showing request counts per IP for verification during testing.', bd))

# Ch4
story.append(ah('Chapter 4: Payload Size Limits', h1, 0))
story.append(ah('4.1 Per-Route Payload Caps', h2, 1))
story.append(Paragraph('Payload limits prevent memory exhaustion attacks and oversized payloads that could crash the server during JSON parsing. Each route has a specific limit tuned to its expected input size. The absolute maximum across all routes is 100KB, a hard ceiling that no route may exceed regardless of its individual limit. The limits are checked before the request body is parsed, using the Content-Length header, making the check nearly free. If Content-Length is missing or zero, the body is still parsed but the payload limit serves as a secondary defense.', bd))
story.extend(sk([tbl(['Route','Limit','Why This Size'], [
    ['eli-chat POST','10 KB','Chat messages are short; LLM context is the bottleneck, not bandwidth'],
    ['omni POST','10 KB','Action bodies are small JSON (action name + optional key/inboxId)'],
    ['vault-sync GET','4 KB','Query params only; no body expected'],
    ['Absolute ceiling','100 KB','No route may accept more, even if individually configured higher'],
], [AW*0.25, AW*0.15, AW*0.6]), Spacer(1,6),
    Paragraph('Table 5: Payload size limits per route with sizing rationale.', cap)]))

# Ch5
story.append(ah('Chapter 5: Input Sanitization', h1, 0))
story.append(ah('5.1 sanitizeInput(): Text Normalization', h2, 1))
story.append(Paragraph(f'The {mono("sanitizeInput()")} function processes all user-supplied text before it reaches the LLM or gets stored. It performs five operations: (1) removes null bytes that could truncate strings or cause downstream parsing errors; (2) normalizes Unicode to NFC canonical form, preventing homoglyph attacks where different Unicode representations of the same character bypass filters; (3) collapses excessive whitespace (more than 3 consecutive newlines or spaces); (4) removes non-printable control characters except newline, carriage return, and tab; (5) trims and enforces a maximum length (default 4000 characters). This does not HTML-escape content, as React handles XSS protection on the frontend.', bd))

story.append(ah('5.2 sanitizePromptInjection(): LLM Attack Prevention', h2, 1))
story.append(Paragraph(f'Prompt injection detection uses 12 regex patterns covering the most common attack vectors: system prompt override attempts ("ignore previous instructions"), delimiter injection ("---END SYSTEM---"), role hijacking ("you are now..."), output format manipulation ("respond only with JSON"), and known jailbreak markers ("DAN mode", "jailbreak"). In the current implementation, detection triggers an immediate 400 rejection with an {mono("injectionDetected: true")} flag. This is a deliberate choice: flag-only mode (where the message passes through but is logged) was the previous behavior, but it allowed potential injection attempts to reach the LLM. The blocking approach is defense-in-depth: even though the system prompt is designed to resist injection, there is no reason to give an attacker a free attempt.', bd))

# Ch6
story.append(ah('Chapter 6: Key Validation', h1, 0))
story.append(ah('6.1 Format Validation Patterns', h2, 1))
story.append(Paragraph(f'Every API key must pass format validation before it enters the key pool. The {mono("validateKeyFormat(service, key)")} function checks the key against a service-specific regex pattern, a minimum length, and a maximum length (500 characters). Keys that fail format validation are rejected at the injection point and logged to the audit trail. This prevents malformed keys from causing API errors, wasting rotation attempts, or being used as injection vectors against the target API service.', bd))
story.extend(sk([tbl(['Service','Pattern','Min Length','Example'], [
    ['gemini','AIza... or AQ....','20 chars','AIzaSyD... or AQ.Ab8RN6...'],
    ['openai','sk-...','25 chars','sk-proj-abc...'],
    ['anthropic','sk-ant-...','30 chars','sk-ant-api03-...'],
], [AW*0.15, AW*0.3, AW*0.15, AW*0.4]), Spacer(1,6),
    Paragraph('Table 6: Key format validation patterns by service.', cap)]))

story.append(ah('6.2 Approval Queue', h2, 1))
story.append(Paragraph('Keys extracted by OpenClaw from email do not automatically enter the active key pool. They enter a pending queue with a maximum capacity of 20 entries. By default, auto-approve is OFF, meaning each key must be manually approved via POST /api/omni?action=approve before it becomes active. The approval process includes a format check and a live API test call to the target service (e.g., a simple "Say OK" request to Gemini). Only keys that pass both checks are promoted to the active pool. This two-step validation (format + live test) catches keys that look valid but are actually revoked, rate-limited, or belong to a different project.', bd))

# Ch7
story.append(ah('Chapter 7: Audit Logging', h1, 0))
story.append(ah('7.1 Event Types and Structure', h2, 1))
story.append(Paragraph(f'The audit log records 14 event types covering the full lifecycle of security-relevant operations. Each entry is an object with an ISO timestamp, event type string, human-readable detail, optional structured metadata, and optional caller IP. Events are buffered in memory (capped at 500 entries by the {mono("MAX_AUDIT_MEMORY")} constant) and asynchronously appended to a JSONL file at {mono("data/audit/audit.jsonl")}. The async write ensures the audit call never blocks the request handler. The /api/audit endpoint (admin-only, rate-limited to 10 req/min) provides read access to the in-memory buffer.', bd))
story.extend(sk([tbl(['Event Type','Description','Typical Metadata'], [
    ['auth.blocked','Authentication failed','ip, action'],
    ['chat.ratelimited','Chat rate limit exceeded','ip'],
    ['prompt.injection.blocked','Prompt injection detected','ip, messagePreview'],
    ['key.extracted','OpenClaw pulled key from email','service, inboxEmail'],
    ['key.injected','Manual key injection','service, keyPreview'],
    ['key.rotation','Key rotation occurred','service, inboxEmail'],
    ['llm.call','LLM API called','ip'],
    ['llm.failure','LLM API call failed','ip, error'],
    ['vault.query','Vault search executed','query, resultCount'],
], [AW*0.3, AW*0.35, AW*0.35]), Spacer(1,6),
    Paragraph('Table 7: Core audit event types with descriptions and metadata.', cap)]))

# Ch8
story.append(ah('Chapter 8: Route-by-Route Safety Wiring', h1, 0))
story.append(Paragraph('This chapter documents exactly which safety parameters are applied in each route handler, in execution order. Every route follows the same pattern: auth check, rate limit, payload check, input validation, then business logic. The table below summarizes the complete wiring across all four protected routes.', bd))
story.extend(sk([tbl(['Route','Auth','Rate Limit','Payload','Input Sanitization','Prompt Injection'], [
    ['/api/eli-chat POST','checkAuth()','15/min','10KB','sanitizeInput()','BLOCK + 400'],
    ['/api/omni GET','checkCapability()','30/min','N/A (GET)','N/A','N/A'],
    ['/api/omni POST','checkAuth()','5/min','10KB','validateKeyFormat()','N/A'],
    ['/api/vault-sync GET','checkAuth()','20/min','N/A (GET)','N/A','N/A'],
    ['/api/audit GET','checkAuth()','10/min','N/A (GET)','N/A','N/A'],
    ['/api/health GET','None','120/min','N/A','N/A','N/A'],
], [AW*0.2, AW*0.15, AW*0.12, AW*0.13, AW*0.2, AW*0.2]), Spacer(1,6),
    Paragraph('Table 8: Complete safety wiring matrix across all routes.', cap)]))
story.append(Paragraph('Note that /api/health is the only route without auth. This is intentional: health checks are used by monitoring systems and load balancers that cannot carry authentication credentials. The 120 req/min rate limit provides sufficient protection against abuse while allowing aggressive monitoring. If this becomes a concern, the health endpoint can be restricted to internal network ranges at the Caddy level.', bd))

# Ch9
story.append(ah('Chapter 9: Configuration Reference', h1, 0))
story.append(Paragraph('This chapter provides the complete configuration reference for all safety parameters. Every constant defined in safety-gate.ts is listed with its current value, type, and the rationale for why it is set to that specific value. This reference is intended for anyone who needs to tune the safety parameters for a different deployment environment or threat model.', bd))
story.extend(sk([tbl(['Parameter','Value','Type','Rationale'], [
    ['MAX_PAYLOAD_CHAT','10,240 bytes','int','Chat messages are short; prevents OOM in JSON parsing'],
    ['MAX_PAYLOAD_OMNI','10,240 bytes','int','Omni actions are small JSON payloads'],
    ['MAX_PAYLOAD_ABSOLUTE','100,000 bytes','int','Hard ceiling no route may exceed'],
    ['RATE_LIMIT_CHAT','15 req / 60s','object','Matches Gemini free-tier rate budget'],
    ['RATE_LIMIT_OMNI_POST','5 req / 60s','object','Write ops are expensive (rotation, injection)'],
    ['MAX_HISTORY_MESSAGES','20','int','LLM context window is limited; recent context only'],
    ['MAX_MESSAGE_LENGTH','4,000 chars','int','Prevents token budget exhaustion from single message'],
    ['MAX_PENDING_KEYS','20','int','Approval queue cap; oldest auto-rejected when full'],
    ['MAX_CLAW_INBOXES','10','int','Provider rate limit preservation'],
    ['MAX_AUDIT_MEMORY','500','int','Memory cap for in-memory audit buffer'],
    ['INBOX_TTL_MS','55 minutes','int','Provider TTL minus 5min safety margin'],
], [AW*0.25, AW*0.18, AW*0.1, AW*0.47]), Spacer(1,6),
    Paragraph('Table 9: Complete safety parameter reference.', cap)]))

story.append(ah('9.1 Environment Variables', h2, 1))
story.extend(sk([tbl(['Variable','Required','Description'], [
    ['ELI_API_KEY','No (enables auth)','Master bearer token. When set, all routes (except /health) require it'],
    ['GEMINI_API_KEY','Yes','Primary Gemini API key. Can be AIza... or AQ... format'],
], [AW*0.2, AW*0.15, AW*0.65]), Spacer(1,6),
    Paragraph('Table 10: Environment variables affecting safety behavior.', cap)]))
story.append(Paragraph('When ELI_API_KEY is not set, the authentication gate is disabled and all requests pass through. This is the correct behavior for local development but must never be the case in production. The deployment script does not set this variable; it must be configured on the server via systemd environment file or .env.', bd))

# Build
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'download', 'eli-safety-guidebook.pdf')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

doc = TocDoc(OUT, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
             title='Eli Safety Parameter Guidebook', author='Z.ai', subject='Tier 1 API Safety Parameters')
doc.multiBuild(story, onLaterPages=footer, onFirstPage=lambda c,d: None)
print(f'Body PDF: {OUT}')
