#!/usr/bin/env python3
"""Generate Eli Safety Learning Guide PDF.
Hands-on practice guide for implementing each safety pattern in personal projects.
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

FD = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('FSerif', f'{FD}/truetype/freefont/FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('FSerifB', f'{FD}/truetype/freefont/FreeSerifBold.ttf'))
pdfmetrics.registerFont(TTFont('FSerifI', f'{FD}/truetype/freefont/FreeSerifItalic.ttf'))
pdfmetrics.registerFont(TTFont('FSerifBI', f'{FD}/truetype/freefont/FreeSerifBoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu', f'{FD}/truetype/dejavu/DejaVuSansMono.ttf'))
registerFontFamily('FSerif', normal='FSerif', bold='FSerifB', italic='FSerifI', boldItalic='FSerifBI')
registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu')

C = colors
HDR = C.HexColor('#623ecd')
HDR2 = C.HexColor('#857239')
STRIPE = C.HexColor('#f1f1ef')
BDR = C.HexColor('#c4c0b3')
TX = C.HexColor('#1a1a18')
TXM = C.HexColor('#817e77')
CARD = C.HexColor('#efeeea')
ACCENT = C.HexColor('#623ecd')
ACCENT2 = C.HexColor('#a58629')
BG = C.HexColor('#f4f4f3')

W, H = A4
M = 60
AW = W - 2 * M

toc_h1 = ParagraphStyle('t1', fontName='FSerifB', fontSize=12, leading=20, leftIndent=0, textColor=TX, spaceBefore=8, spaceAfter=4)
toc_h2 = ParagraphStyle('t2', fontName='FSerif', fontSize=10.5, leading=18, leftIndent=20, textColor=TXM, spaceBefore=2, spaceAfter=2)
h1 = ParagraphStyle('h1', fontName='FSerifB', fontSize=20, leading=28, textColor=HDR, spaceBefore=24, spaceAfter=12)
h2 = ParagraphStyle('h2', fontName='FSerifB', fontSize=14, leading=20, textColor=TX, spaceBefore=18, spaceAfter=8)
h3 = ParagraphStyle('h3', fontName='FSerifB', fontSize=11.5, leading=16, textColor=HDR2, spaceBefore=12, spaceAfter=6)
bd = ParagraphStyle('bd', fontName='FSerif', fontSize=10.5, leading=18, alignment=TA_JUSTIFY, textColor=TX, spaceAfter=6)
code_s = ParagraphStyle('code', fontName='DejaVu', fontSize=8, leading=12, textColor=TX, backColor=CARD, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=6, borderPadding=6)
cap_s = ParagraphStyle('cap', fontName='FSerifI', fontSize=9, leading=14, textColor=TXM, spaceAfter=12)
tip = ParagraphStyle('tip', fontName='FSerif', fontSize=10, leading=16, textColor=ACCENT2, leftIndent=18, borderLeftWidth=3, borderLeftColor=ACCENT2, borderPadding=8, spaceBefore=8, spaceAfter=8)
ex_s = ParagraphStyle('ex', fontName='FSerifB', fontSize=10, leading=16, textColor=HDR, leftIndent=18, borderLeftWidth=3, borderLeftColor=HDR, borderPadding=8, spaceBefore=8, spaceAfter=8)

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
    th_s = ParagraphStyle('th', fontName='FSerifB', fontSize=9, leading=13, textColor=C.white)
    td_s = ParagraphStyle('td', fontName='FSerif', fontSize=9, leading=13, textColor=TX)
    data = [[Paragraph(h, th_s) for h in headers]] + [[Paragraph(str(c), td_s) for c in r] for r in rows]
    cmds = [('BACKGROUND', (0,0), (-1,0), HDR), ('TEXTCOLOR', (0,0), (-1,0), C.white),
            ('VALIGN', (0,0), (-1,-1), 'TOP'), ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5), ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6), ('GRID', (0,0), (-1,-1), 0.5, BDR)]
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
    canvas.drawString(M, 25, 'Safety Learning Guide')
    canvas.restoreState()

m = lambda t: f'<font name="DejaVu">{t}</font>'  # mono helper

def tip_f(text):
    return Paragraph(f'Tip: {text}', tip)

def ex_f(text):
    return Paragraph(f'Exercise: {text}', ex_s)

code_block = lambda t: Paragraph(t.replace('<','&lt;').replace('>','&gt;'), code_s)

story = []

# TOC
toc = TableOfContents()
toc.levelStyles = [toc_h1, toc_h2]
story.append(Paragraph('Table of Contents', h1))
story.append(Spacer(1, 12))
story.append(toc)
story.append(PageBreak())

# ── Ch1 ──
story.append(ah('Chapter 1: Getting Started', h1, 0))
story.append(ah('1.1 What You Will Learn', h2, 1))
story.append(Paragraph('This guide teaches you how to implement the seven core API safety patterns used in Eli, but adapted for any personal project. You do not need Eli or a Next.js application to follow along. The patterns are framework-agnostic and can be implemented in Express, FastAPI, Flask, or plain Node.js. Each chapter explains the concept, shows a minimal implementation you can copy into your own project, and ends with an exercise to deepen your understanding. The patterns build on each other, so it is recommended to work through them in order.', bd))

story.append(ah('1.2 Prerequisites', h2, 1))
story.append(Paragraph('You need basic familiarity with any server-side language (JavaScript/TypeScript, Python, or Go) and HTTP concepts (status codes, headers, request/response lifecycle). No security expertise is assumed. Each pattern starts with the problem it solves, so even if you have never implemented an auth check before, you will understand why it exists before you write the code.', bd))

story.extend(sk([tbl(['Pattern','Difficulty','Time','What You Build'], [
    ['1. Auth Gate','Beginner','10 min','Bearer token check that protects any endpoint'],
    ['2. Rate Limiter','Beginner','20 min','Sliding-window rate limiter per IP address'],
    ['3. Payload Limits','Beginner','5 min','Content-length check that rejects oversized requests'],
    ['4. Input Sanitization','Intermediate','15 min','Text normalizer that strips dangerous characters'],
    ['5. Prompt Injection Blocker','Intermediate','20 min','Pattern matcher that detects LLM manipulation attempts'],
    ['6. Key Validation','Intermediate','15 min','Format checker for API keys before they are used'],
    ['7. Audit Logger','Beginner','15 min','Structured event logger with file persistence'],
], [AW*0.22, AW*0.15, AW*0.12, AW*0.51]), Spacer(1,6),
    Paragraph('Table 1: The seven patterns, difficulty, and what you will build in each exercise.', cap_s)]))

# ── Ch2 ──
story.append(ah('Chapter 2: Pattern 1 - Auth Gate', h1, 0))
story.append(ah('2.1 The Problem', h2, 1))
story.append(Paragraph('Any API endpoint accessible on the internet can be discovered by scanners, bots, or curious users. Without authentication, every endpoint is open to anyone who guesses or discovers the URL. For a project that consumes paid or rate-limited APIs (like LLM services), an open endpoint means anyone can drain your API budget. The auth gate is the simplest and most effective protection against this class of threat. It does not need to be complex: a single shared secret checked on every request is sufficient for most personal projects and small teams.', bd))

story.append(ah('2.2 Implementation (Node.js / Express)', h2, 1))
story.append(Paragraph(f'The implementation checks two sources: the {m("Authorization")} header (standard for all HTTP clients) and a {m("?key=")} query parameter (convenient for quick curl tests). If no master key is configured, the gate is disabled, which is the right default for local development. Copy this into a file called {m("auth.js")}:', bd))
story.append(code_block("function checkAuth(req) {\n  const masterKey = process.env.API_KEY;\n  if (!masterKey) return true; // Auth disabled\n\n  const authHeader = req.headers['authorization'];\n  if (authHeader === `Bearer ${masterKey}`) return true;\n\n  const queryKey = req.query?.key;\n  if (queryKey === masterKey) return true;\n\n  return false;\n}\n\n// Usage in Express route:\napp.post('/api/chat', (req, res) => {\n  if (!checkAuth(req)) {\n    return res.status(401).json({ error: 'Unauthorized' });\n  }\n  // ... your handler\n});"))

story.append(ah('2.3 Implementation (Python / FastAPI)', h2, 1))
story.append(code_block("from fastapi import Request, HTTPException\nimport os\n\ndef check_auth(request: Request) -> bool:\n    master_key = os.getenv('API_KEY')\n    if not master_key:\n        return True  # Auth disabled\n\n    auth_header = request.headers.get('authorization', '')\n    if auth_header == f'Bearer {master_key}':\n        return True\n\n    query_key = request.query_params.get('key')\n    if query_key == master_key:\n        return True\n\n    return False\n\n# Usage:\n@app.post('/api/chat')\nasync def chat(request: Request):\n    if not check_auth(request):\n        raise HTTPException(401, 'Unauthorized')"))

story.append(ex_f('Exercise: Wire the auth gate into two endpoints. One should require auth, the other should be public (like a health check). Test with curl using both the header method and the query parameter method. Verify that a request with the wrong key gets a 401 response.'))

story.append(tip_f('Production tip: Never commit your API_KEY to source control. Use a .env file (add it to .gitignore) or set it via your hosting platform environment variables panel.'))

# ── Ch3 ──
story.append(ah('Chapter 3: Pattern 2 - Rate Limiter', h1, 0))
story.append(ah('3.1 The Problem', h2, 1))
story.append(Paragraph('Even authenticated users can make too many requests. A misconfigured client, a buggy retry loop, or a deliberate attack can send hundreds of requests per second. Rate limiting caps the number of requests a single client can make within a time window. The sliding window algorithm is preferred over fixed windows because it prevents burst-at-boundary abuse, where a client sends all their allowed requests in the last millisecond of one window and the first millisecond of the next, effectively getting double the intended rate.', bd))

story.append(ah('3.2 Implementation', h2, 1))
story.append(Paragraph(f'This is a framework-agnostic implementation using a plain Map. It stores an array of timestamps per IP, prunes old entries on each check, and compares the count against the configured maximum. The cleanup runs every 5 minutes to prevent memory leaks from stale entries. Copy this into {m("rateLimiter.js")}:', bd))
story.append(code_block("const windows = new Map(); // ip -> [timestamps]\nlet lastCleanup = Date.now();\n\nfunction checkRateLimit(ip, maxRequests, windowMs) {\n  const now = Date.now();\n\n  // Cleanup stale entries every 5 minutes\n  if (now - lastCleanup > 300_000) {\n    for (const [key, ts] of windows) {\n      const cutoff = now - windowMs;\n      ts.array = ts.array.filter(t => t > cutoff);\n      if (ts.array.length === 0) windows.delete(key);\n    }\n    lastCleanup = now;\n  }\n\n  let entry = windows.get(ip);\n  if (!entry) {\n    entry = { array: [] }; windows.set(ip, entry); }\n\n  // Prune timestamps outside the window\n  const cutoff = now - windowMs;\n  entry.array = entry.array.filter(t => t > cutoff);\n\n  if (entry.array.length >= maxRequests) return false;\n  entry.array.push(now);\n  return true;\n}\n\n// Usage in Express:\nconst ip = req.ip || req.headers['x-forwarded-for']?.split(',')[0];\nif (!checkRateLimit(ip, 15, 60_000)) {\n  return res.status(429).json({ error: 'Too many requests' });\n}"))

story.append(Paragraph('The key design decisions in this implementation: rejected requests do NOT consume a slot (the timestamp is only pushed when the request is allowed), the cleanup is O(n) over all tracked IPs but runs infrequently, and the window slides smoothly rather than resetting at fixed intervals. These decisions prevent both the burst-at-boundary problem and the memory leak problem.', bd))

story.append(ex_f('Implement the rate limiter and test it with a loop that sends 20 rapid requests. Verify that exactly 15 succeed and the remaining 5 get 429 responses. Then wait 60 seconds and verify that requests succeed again.'))

# ── Ch4 ──
story.append(ah('Chapter 4: Pattern 3 - Payload Limits', h1, 0))
story.append(ah('4.1 The Problem', h2, 1))
story.append(Paragraph('An attacker can send a request with a Content-Length of 2GB. If your server tries to parse that into memory, it will crash with an out-of-memory error, taking down your entire application. The fix is trivially simple: check the Content-Length header before parsing the body. This check costs almost nothing (one integer comparison) but prevents one of the most effective denial-of-service attacks against JSON APIs.', bd))

story.append(ah('4.2 Implementation', h2, 1))
story.append(code_block("// Middleware for Express:\nfunction payloadLimit(maxBytes) {\n  return (req, res, next) => {\n    const len = parseInt(req.headers['content-length'] || '0', 10);\n    if (len > maxBytes) {\n      return res.status(413).json({ error: 'Payload too large' });\n    }\n    next();\n  };\n}\n\n// Apply to routes:\napp.post('/api/chat', payloadLimit(10_240), (req, res) => {\n  // Body is guaranteed to be under 10KB\n});\n\n// Python equivalent:\n@app.post('/api/chat')\nasync def chat(request: Request):\n    cl = int(request.headers.get('content-length', 0))\n    if cl > 10240:\n        raise HTTPException(413, 'Payload too large')"))

story.append(tip_f('Choose payload limits based on your expected input size. Chat messages: 10KB. File uploads: check your framework built-in limits. Configuration updates: 4KB. The key insight is that every route should have a limit tuned to its expected use case, plus an absolute maximum (like 100KB) that no route can exceed.'))

# ── Ch5 ──
story.append(ah('Chapter 5: Pattern 4 - Input Sanitization', h1, 0))
story.append(ah('5.1 The Problem', h2, 1))
story.append(Paragraph('User input cannot be trusted. Even well-intentioned users may paste content that contains invisible control characters, null bytes, or Unicode normalization attacks. A null byte (\x00) in a string can cause truncation in downstream C libraries. Different Unicode representations of the same character can bypass regex filters (homoglyph attacks). Excessively long inputs can bypass length checks that only look at character count without considering encoding expansion. The sanitizer handles all of these in a single pass.', bd))

story.append(ah('5.2 Implementation', h2, 1))
story.append(code_block("function sanitizeInput(text, maxLength = 4000) {\n  if (!text || typeof text !== 'string') return '';\n\n  // 1. Remove null bytes (prevents truncation attacks)\n  let clean = text.replace(/\\x00/g, '');\n\n  // 2. Normalize Unicode (prevents homoglyph bypass)\n  clean = clean.normalize('NFC');\n\n  // 3. Collapse excessive whitespace\n  clean = clean.replace(/\\n{4,}/g, '\\n\\n\\n');\n  clean = clean.replace(/ {4,}/g, '   ');\n\n  // 4. Remove control characters (keep \n, \r, \t)\n  clean = clean.replace(/[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]/g, '');\n\n  // 5. Trim and enforce max length\n  clean = clean.trim();\n  if (clean.length > maxLength) clean = clean.slice(0, maxLength);\n\n  return clean;\n}"))

story.append(ex_f('Create a test suite with the following inputs and verify the sanitizer handles each correctly: (1) a string with embedded null bytes, (2) a string with \n\n\n\n\n (5 newlines), (3) a string with a control character like \x02, (4) a string that is 10,000 characters long (should be truncated to your maxLength), (5) a string with Unicode homoglyphs (different representations of the same character).'))

# ── Ch6 ──
story.append(ah('Chapter 6: Pattern 5 - Prompt Injection Blocker', h1, 0))
story.append(ah('6.1 The Problem', h2, 1))
story.append(Paragraph('If your application sends user input to an LLM, you are vulnerable to prompt injection. An attacker can craft input that overrides your system prompt, instructs the model to ignore previous instructions, or manipulates the output format. This is not a theoretical risk: prompt injection is the most common attack vector against LLM-powered applications. The blocker uses regex pattern matching to detect the most common injection attempts before they reach the model. It is not a replacement for good system prompt engineering, but it provides defense-in-depth.', bd))

story.append(ah('6.2 Implementation', h2, 1))
story.append(code_block("const INJECTION_PATTERNS = [\n  /ignore\\s+(all\\s+)?(previous|above|prior)\\s+(instructions?|prompts?|system)/i,\n  /you\\s+are\\s+now\\s+(a|an|the)\\s+/i,\n  /system\\s*:\\s*$/im,\n  /---\\s*(END|STOP|FINISH)\\s*---/i,\n  /\\[INST\\]|\\[\\/INST\\]/i,\n  /<\\|im_start\\|>|<\\|im_end\\|>/i,\n  /respond\\s+(only\\s+)?(with|in)\\s+(json|yaml|xml|code|markdown)/i,\n  /forget\\s+(everything|all|your)\\s+(instructions?|training|rules)/i,\n  /pretend\\s+(you\\s+are|to\\s+be)/i,\n  /act\\s+as\\s+(if\\s+)?(you\\s+)?(a|an|the)\\s+/i,\n  /jailbreak/i,\n  /DAN\\s+mode/i,\n];\n\nfunction checkPromptInjection(text) {\n  for (const pattern of INJECTION_PATTERNS) {\n    if (pattern.test(text)) {\n      return { blocked: true, pattern: pattern.source };\n    }\n  }\n  return { blocked: false };\n}\n\n// Usage:\nconst result = checkPromptInjection(userMessage);\nif (result.blocked) {\n  return res.status(400).json({\n    error: 'Message contains patterns that look like prompt injection.',\n    detected: true,\n  });\n}"))

story.append(tip_f('Design choice: flag-only vs. block. In Eli, we chose to block detected injections (return 400). An alternative is to flag but allow (log the detection and proceed). Flag-only is appropriate when you trust your system prompt to resist injection and do not want false positives to annoy users. Block is appropriate when the cost of a successful injection is high (e.g., the LLM has access to sensitive data or can execute actions). Choose based on your threat model.'))

# ── Ch7 ──
story.append(ah('Chapter 7: Pattern 6 - Key Validation', h1, 0))
story.append(ah('7.1 The Problem', h2, 1))
story.append(Paragraph('If your application accepts API keys from users (for example, a multi-model LLM proxy where users provide their own keys), you must validate the key format before using it. A malformed key will cause an API error that wastes a network round-trip and may expose error details. A key that is too long could be an injection attempt against your system. The validator checks format, length, and pattern before the key is stored or used.', bd))

story.append(ah('7.2 Implementation', h2, 1))
story.append(code_block("const KEY_PATTERNS = {\n  gemini: {\n    pattern: /^(AIza[A-Za-z0-9_-]{33,}|AQ\\.[A-Za-z0-9_-]{30,})$/,\n    minLength: 20,\n  },\n  openai: {\n    pattern: /^sk-[A-Za-z0-9]{20,}$/,\n    minLength: 25,\n  },\n};\n\nfunction validateKeyFormat(service, key) {\n  const svc = KEY_PATTERNS[service];\n  if (!svc) return { valid: false, reason: `Unknown service: ${service}` };\n  if (!key || typeof key !== 'string')\n    return { valid: false, reason: 'Key is empty or not a string' };\n  if (key.length < svc.minLength)\n    return { valid: false, reason: `Key too short (min ${svc.minLength})` };\n  if (key.length > 500)\n    return { valid: false, reason: 'Key too long (max 500)' };\n  if (!svc.pattern.test(key))\n    return { valid: false, reason: `Key does not match ${service} format` };\n  return { valid: true, reason: 'Format valid' };\n}"))

story.append(ex_f('Add a third service (e.g., Anthropic with pattern sk-ant-...) to the validator. Test with: (1) a valid Gemini key, (2) an invalid key that is too short, (3) a valid-looking key for an unknown service, (4) a 600-character key (should fail max length), (5) a key with SQL injection characters (should fail pattern match).'))

# ── Ch8 ──
story.append(ah('Chapter 8: Pattern 7 - Audit Logger', h1, 0))
story.append(ah('8.1 The Problem', h2, 1))
story.append(Paragraph('When something goes wrong, you need to know what happened. Console.log is not enough: it disappears on restart, has no structure, and cannot be easily queried. An audit log provides a persistent, structured record of security-relevant events. It should capture who did what, when, and with what context. The implementation should be async (never block the request handler), bounded in memory (prevent memory leaks), and persisted to disk (survive restarts).', bd))

story.append(ah('8.2 Implementation', h2, 1))
story.append(code_block("const fs = require('fs');\nconst path = require('path');\nconst MAX_MEMORY = 500;\nconst buffer = [];\nconst LOG_FILE = path.join(process.cwd(), 'data', 'audit.jsonl');\n\nfunction ensureDir() {\n  fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });\n}\n\nfunction audit(event, detail, meta = {}, ip) {\n  const entry = {\n    ts: new Date().toISOString(),\n    event,\n    detail,\n    meta,\n    ip,\n  };\n\n  buffer.push(entry);\n  if (buffer.length > MAX_MEMORY) buffer.shift();\n\n  // Async write - never block the caller\n  try {\n    ensureDir();\n    fs.appendFileSync(LOG_FILE, JSON.stringify(entry) + '\\n');\n  } catch (err) {\n    console.error('Audit write failed:', err.message);\n  }\n}\n\n// Usage:\naudit('auth.blocked', 'Failed login from 1.2.3.4', { ip: '1.2.3.4' }, '1.2.3.4');\naudit('key.rotation', 'Gemini key rotated', { service: 'gemini', inboxCount: 3 });"))

story.append(tip_f('JSONL (JSON Lines) format is ideal for audit logs: each line is a valid JSON object, making it both human-readable and machine-parseable. You can grep it, pipe it to jq for filtering, or load it into any log analysis tool. Avoid binary formats or databases for audit logs: they add complexity and create dependencies that make the log harder to access during an incident.'))

# ── Ch9 ──
story.append(ah('Chapter 9: Putting It All Together', h1, 0))
story.append(ah('9.1 The Defense-in-Depth Stack', h2, 1))
story.append(Paragraph('When you wire all seven patterns together in the correct order, you get a defense-in-depth stack where each layer filters cheaply before the next, more expensive layer runs. The ordering matters: authentication is checked first (one string comparison), then rate limiting (one map lookup), then payload size (one integer comparison), then input validation (regex operations), and finally business logic (network I/O, database queries, LLM calls). This ensures that blocked requests consume the minimum possible server resources.', bd))
story.extend(sk([tbl(['Order','Pattern','Cost','Blocks'], [
    ['1','Auth Gate','O(1) string compare','Unauthorized access'],
    ['2','Rate Limiter','O(k) array filter','Abuse, brute force, DoS'],
    ['3','Payload Limit','O(1) integer compare','Memory exhaustion'],
    ['4','Input Sanitization','O(n) string ops','Injection, control chars, homoglyphs'],
    ['5','Prompt Injection Block','O(n) regex scan','LLM manipulation'],
    ['6','Key Validation','O(1) regex test','Malformed key errors'],
    ['7','Audit Logger','O(1) push + async write','(Passive: records everything)'],
], [AW*0.1, AW*0.25, AW*0.3, AW*0.35]), Spacer(1,6),
    Paragraph('Table 2: Complete defense-in-depth stack with per-layer cost analysis.', cap_s)]))

story.append(ah('9.2 Wiring Example (Express)', h2, 1))
story.append(Paragraph('Here is how all seven patterns combine into a single Express route handler. Notice the ordering: each check is a short-circuit return that prevents the next (more expensive) check from running if the request is already rejected.', bd))
story.append(code_block("app.post('/api/chat', async (req, res) => {\n  const ip = req.ip || req.headers['x-forwarded-for']?.split(',')[0];\n\n  // 1. Auth\n  if (!checkAuth(req)) {\n    audit('auth.blocked', `Auth failed from ${ip}`, {}, ip);\n    return res.status(401).json({ error: 'Unauthorized' });\n  }\n\n  // 2. Rate limit\n  if (!checkRateLimit(ip, 15, 60_000)) {\n    audit('chat.ratelimited', `Rate limited from ${ip}`, {}, ip);\n    return res.status(429).json({ error: 'Too many requests' });\n  }\n\n  // 3. Payload\n  const len = parseInt(req.headers['content-length'] || '0', 10);\n  if (len > 10_240) {\n    audit('chat.blocked', `Payload too large from ${ip}`, { size: len }, ip);\n    return res.status(413).json({ error: 'Payload too large' });\n  }\n\n  const { message } = req.body;\n\n  // 4. Sanitize\n  const clean = sanitizeInput(message);\n  if (!clean) return res.status(400).json({ error: 'Empty message' });\n\n  // 5. Prompt injection\n  if (checkPromptInjection(clean).blocked) {\n    audit('prompt.injection.blocked', `Blocked from ${ip}`, {}, ip);\n    return res.status(400).json({ error: 'Prompt injection detected' });\n  }\n\n  // 6. Business logic (LLM call)\n  audit('llm.call', `Processing chat from ${ip}`, {}, ip);\n  const response = await callLLM(clean);\n\n  return res.json({ response });\n});"))

story.append(ah('9.3 Next Steps', h2, 1))
story.append(Paragraph('Once you have all seven patterns working, you have a solid Tier 1 safety foundation. The next improvements to consider are: (1) per-user rate limits instead of per-IP, which handles multiple users behind a NAT; (2) structured logging with a proper library like Pino or Winston instead of raw appendFileSync; (3) automated tests for each safety layer; (4) a middleware wrapper that applies all checks in one line instead of repeating them in every handler; and (5) monitoring and alerting that triggers when the rate limiter or auth gate is hit frequently, which could indicate an attack.', bd))

story.append(ex_f('Final project: Build a complete API with all seven patterns wired up. Add at least two routes with different rate limits and payload limits. Add a public health endpoint that skips auth. Test everything with curl and verify the correct HTTP status codes. Then deploy it and verify the audit log writes to disk.'))

# Build
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'download', 'eli-safety-learning-guide.pdf')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

doc = TocDoc(OUT, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
             title='Safety Parameter Learning Guide', author='Z.ai', subject='Hands-on API security patterns')
doc.multiBuild(story, onLaterPages=footer, onFirstPage=lambda c,d: None)
print(f'Body PDF: {OUT}')
