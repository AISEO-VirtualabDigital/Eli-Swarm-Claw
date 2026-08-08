'use strict';

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, PageBreak,
  HeadingLevel, AlignmentType, ShadingType,
  Table, TableRow, TableCell, WidthType,
  BorderStyle, PageNumber, NumberFormat,
  Header, Footer, Tab, TabStopPosition, TabStopType,
  SectionType, LineRuleType, VerticalAlign
} = require('docx');

// ── Palette CM-2 (Blue Orange tech) ──
const C = {
  bg:            '0F172A',
  titleColor:    'FFFFFF',
  subtitleColor: '94A3B8',
  metaColor:     '64748B',
  accent:        'FF862F',
  footerColor:   '475569',
  body:          '1E293B',
  secondary:     '64748B',
  surface:       'F1F9FC',
  table: {
    headerBg:    '1284BA',
    headerText:  'FFFFFF',
    accentLine:  '1284BA',
    innerLine:   'D8E4EC',
    surface:     'EDF9F9'
  }
};

const FONT = 'Times New Roman';
const BODY_SIZE = 24;          // 12pt in half-points
const LINE_SPACING = 1.3;     // 1.3x

// ── Helper: heading 1 (chapter) ──
function h1(text) {
  return new Paragraph({
    spacing: { before: 360, after: 200, line: 340 },
    children: [
      new TextRun({
        text: text,
        font: FONT,
        size: 36,
        bold: true,
        color: C.table.headerBg
      })
    ],
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 6, color: C.table.accentLine, space: 6 }
    }
  });
}

// ── Helper: heading 2 (section) ──
function h2(text) {
  return new Paragraph({
    spacing: { before: 280, after: 160, line: 340 },
    children: [
      new TextRun({
        text: text,
        font: FONT,
        size: 30,
        bold: true,
        color: C.accent
      })
    ]
  });
}

// ── Helper: heading 3 (sub-section) ──
function h3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 120, line: 320 },
    children: [
      new TextRun({
        text: text,
        font: FONT,
        size: 26,
        bold: true,
        color: C.body
      })
    ]
  });
}

// ── Helper: body paragraph ──
function body(text) {
  return new Paragraph({
    spacing: { after: 160, line: Math.round(BODY_SIZE * LINE_SPACING) },
    children: [
      new TextRun({
        text: text,
        font: FONT,
        size: BODY_SIZE,
        color: C.body
      })
    ]
  });
}

// ── Helper: body paragraph with bold lead-in ──
function bodyBold(boldText, normalText) {
  return new Paragraph({
    spacing: { after: 160, line: Math.round(BODY_SIZE * LINE_SPACING) },
    children: [
      new TextRun({ text: boldText, font: FONT, size: BODY_SIZE, color: C.body, bold: true }),
      new TextRun({ text: normalText, font: FONT, size: BODY_SIZE, color: C.body })
    ]
  });
}

// ── Helper: code block (monospace, shaded surface) ──
function codeBlock(codeStr) {
  return new Paragraph({
    spacing: { before: 120, after: 200, line: 260 },
    shading: { type: ShadingType.SOLID, color: C.surface, fill: C.surface },
    indent: { left: 360, right: 360 },
    children: [
      new TextRun({
        text: codeStr,
        font: 'Courier New',
        size: 20,
        color: C.body
      })
    ]
  });
}

// ── Helper: note / callout box ──
function note(label, text) {
  return new Paragraph({
    spacing: { before: 160, after: 200, line: Math.round(BODY_SIZE * LINE_SPACING) },
    indent: { left: 480 },
    border: {
      left: { style: BorderStyle.SINGLE, size: 12, color: C.accent, space: 8 }
    },
    children: [
      new TextRun({ text: label + ' ', font: FONT, size: BODY_SIZE, color: C.accent, bold: true }),
      new TextRun({ text: text, font: FONT, size: BODY_SIZE, color: C.secondary })
    ]
  });
}

// ── Helper: table ──
function makeTable(headers, rows) {
  const borderStyle = { style: BorderStyle.SINGLE, size: 1, color: C.table.innerLine };
  const noBorder = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };

  function makeCell(text, isHeader) {
    return new TableCell({
      shading: isHeader
        ? { type: ShadingType.SOLID, color: C.table.headerBg, fill: C.table.headerBg }
        : { type: ShadingType.SOLID, color: C.table.surface, fill: C.table.surface },
      verticalAlign: VerticalAlign.CENTER,
      borders: {
        top: borderStyle, bottom: borderStyle,
        left: isHeader ? noBorder : borderStyle,
        right: isHeader ? noBorder : borderStyle
      },
      children: [
        new Paragraph({
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({
              text: text,
              font: FONT,
              size: isHeader ? 22 : 20,
              bold: !!isHeader,
              color: isHeader ? C.table.headerText : C.body
            })
          ]
        })
      ]
    });
  }

  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map(function(h) { return makeCell(h, true); })
  });

  const dataRows = rows.map(function(row) {
    return new TableRow({
      children: row.map(function(cell) { return makeCell(cell, false); })
    });
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [headerRow].concat(dataRows)
  });
}

// ── Spacer ──
function spacer() {
  return new Paragraph({ spacing: { before: 80, after: 80 }, children: [] });
}

// ── Page break ──
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ══════════════════════════════════════════════════════════════
//  COVER SECTION (R1: Pure Paragraph Left, dark bg, margin 0)
// ══════════════════════════════════════════════════════════════
const coverSection = {
  properties: {
    page: {
      size: { width: 11906, height: 16838, orientation: 'portrait' },
      margin: { top: 0, bottom: 0, left: 0, right: 0 }
    },
    type: SectionType.CONTINUOUS
  },
  children: [
    // Top spacer
    new Paragraph({ spacing: { before: 4800 }, children: [] }),
    // Title
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { after: 200 },
      indent: { left: 1440 },
      children: [
        new TextRun({
          text: 'Eli Safety Parameter',
          font: FONT, size: 72, bold: true, color: C.titleColor
        })
      ]
    }),
    // Subtitle
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { after: 120 },
      indent: { left: 1440 },
      children: [
        new TextRun({
          text: 'Implementation Guidebook',
          font: FONT, size: 52, color: C.subtitleColor
        })
      ]
    }),
    // Accent line
    new Paragraph({
      spacing: { before: 200, after: 200 },
      indent: { left: 1440 },
      children: [
        new TextRun({
          text: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
          font: 'Courier New', size: 20, color: C.accent
        })
      ]
    }),
    // Meta line 1
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { after: 80 },
      indent: { left: 1440 },
      children: [
        new TextRun({
          text: 'Defense-in-Depth Security for AI Agent API Routes',
          font: FONT, size: 24, color: C.metaColor
        })
      ]
    }),
    // Meta line 2
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { after: 80 },
      indent: { left: 1440 },
      children: [
        new TextRun({
          text: 'Five Critical Parameters  |  Eight Chapters  |  Practice Projects',
          font: FONT, size: 22, color: C.metaColor
        })
      ]
    }),
    // Meta line 3
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { before: 600 },
      indent: { left: 1440 },
      children: [
        new TextRun({
          text: 'Version 1.0  |  2025',
          font: FONT, size: 20, color: C.metaColor
        })
      ]
    }),
    // Push to next section
    new Paragraph({ children: [new PageBreak()] })
  ]
};

// ══════════════════════════════════════════════════════════════
//  BODY SECTION (A4, margins, page numbers)
// ══════════════════════════════════════════════════════════════
const bodyChildren = [];

// ──────────────────────────────────────────────────────────────
//  CHAPTER 1: Why Safety Parameters Matter
// ──────────────────────────────────────────────────────────────
bodyChildren.push(h1('Chapter 1: Why Safety Parameters Matter'));

bodyChildren.push(h2('Eli\'s Pre-Safety State'));
bodyChildren.push(body(
  'Before the introduction of safety parameters, Eli operated in a dangerously open configuration that would be considered unacceptable in any production environment. All six API routes were completely unprotected, meaning anyone who discovered the endpoint URL could invoke any operation without presenting credentials of any kind. API keys for external services such as Google Gemini were auto-injected directly from email-based configuration messages, with no validation step to confirm that the key strings were genuine, active, or even formatted correctly for their intended service. There were no payload size limits enforced on incoming requests, which meant a malicious actor could submit arbitrarily large request bodies capable of exhausting server memory or causing denial-of-service conditions. Perhaps most critically, all operational logging was performed exclusively through console.log statements, which meant that once the output buffer scrolled past, the information was permanently lost with no persistence, no queryability, and no forensic trail available for incident response.'
));
bodyChildren.push(body(
  'This combination of vulnerabilities created an attack surface that was both wide and deep. An unauthenticated user could not only call the LLM backend at will, potentially consuming quota and running up costs, but could also submit fabricated API keys that would be accepted without any verification whatsoever. The lack of audit logging meant that even if an intrusion were detected, there would be no record of what happened, when it happened, or what data was accessed. In short, the system was functional but fundamentally fragile, operating on the assumption that the network perimeter alone would provide sufficient protection. This assumption fails the moment a single route is exposed to the internet, which is precisely the deployment model Eli was designed for as a cloud-hosted AI agent platform.'
));

bodyChildren.push(h2('The Defense-in-Depth Strategy'));
bodyChildren.push(body(
  'The safety parameter implementation adopts a defense-in-depth strategy, which is a security architecture principle that mandates multiple overlapping layers of protection. Rather than relying on a single security control such as a firewall or a single authentication check, defense-in-depth ensures that if one layer is compromised or bypassed, additional layers remain in place to limit the damage. This approach recognizes that no single security mechanism is perfect, and that attackers constantly find new ways to circumvent individual defenses. By stacking complementary controls, the system achieves a security posture where the failure of any one component does not result in a total breach of the system\'s integrity, confidentiality, or availability.'
));
bodyChildren.push(body(
  'In the context of Eli, this philosophy translates directly into five distinct safety parameters, each addressing a different category of risk. Authentication guards protect against unauthorized access. Key approval queues prevent the automatic injection of untrusted credentials. Fake key validation ensures that only genuine, working API keys enter the system. Payload size limits protect against resource exhaustion attacks. And audit logging provides the visibility needed to detect, investigate, and respond to security incidents. Each parameter is independently valuable, but together they form a comprehensive security fabric that dramatically reduces the attack surface while maintaining the operational flexibility that Eli needs to function as an AI agent platform. The key insight is that these parameters do not simply add security; they add security at different stages of the request lifecycle, creating interlocking barriers that an attacker would need to bypass simultaneously.'
));

bodyChildren.push(h2('What Each Parameter Protects Against'));
bodyChildren.push(body(
  'The five safety parameters were designed to address specific, concrete threats that were identified during a thorough security audit of the Eli codebase. The API Authentication Gate protects against unauthorized access to all API routes, ensuring that only callers who possess the correct Bearer token can invoke any endpoint operation. Without this gate, anyone on the network could call the LLM, submit keys, or trigger any API function. The Key Approval Queue protects against the automatic injection of untrusted API keys that arrive via email or other unverified channels, by requiring explicit human approval before any new key is added to the active vault. This prevents a scenario where a compromised email account could inject a malicious key that intercepts or redirects API traffic.'
));
bodyChildren.push(body(
  'The Fake Key Validation parameter protects against the use of invalid, expired, or fabricated API keys by performing a real API call to the target service before accepting the key. This is critical because a key that matches the expected format pattern, such as starting with "AIza" for Google Gemini, may still be revoked, expired, or entirely fabricated. The Payload Size Limits parameter protects against denial-of-service attacks that exploit the absence of body size constraints, capping incoming request bodies at a configurable threshold, typically ten kilobytes, and returning an HTTP 413 status when the limit is exceeded. Finally, the Audit Logging parameter protects against the invisibility of security events by writing structured, persistent, queryable log entries to a JSONL file on disk, creating a forensic trail that survives process restarts and enables retrospective analysis of any suspicious activity.'
));

bodyChildren.push(pageBreak());

// ──────────────────────────────────────────────────────────────
//  CHAPTER 2: Parameter 1 - API Authentication Gate
// ──────────────────────────────────────────────────────────────
bodyChildren.push(h1('Chapter 2: Parameter 1 - API Authentication Gate'));

bodyChildren.push(h2('The Problem: Six Unprotected API Routes'));
bodyChildren.push(body(
  'Eli\'s API surface consisted of six distinct routes, each serving a critical function in the agent\'s operation. These included the primary omni endpoint that handled LLM calls and key management, the audit log retrieval endpoint, the health check endpoint, and several supporting routes for configuration and status queries. In the pre-safety configuration, every single one of these routes was accessible without any form of authentication. This meant that the omni endpoint, which forwards requests to Google\'s Gemini API and has the potential to incur real costs with each invocation, could be called by any HTTP client that could reach the server. The key management functions, which handle the storage and retrieval of sensitive API credentials, were equally exposed. This represented a critical security vulnerability because it combined unrestricted access with high-value operations.'
));
bodyChildren.push(body(
  'The risk was not theoretical. In a cloud deployment scenario, API routes are typically exposed to the internet through a reverse proxy or direct port mapping. Once exposed, these routes become discoverable through port scanning, URL enumeration, or simple knowledge of the application\'s structure. An attacker who discovers an unprotected LLM endpoint can consume API quota rapidly, potentially running up substantial bills before the abuse is detected. More sophisticated attackers could use the exposed endpoints to extract stored API keys, inject their own keys for man-in-the-middle attacks, or probe the system for additional vulnerabilities. The health check endpoint, while less sensitive, still reveals information about the system\'s operational status and technology stack, which is valuable intelligence for reconnaissance. The fundamental issue was that Eli trusted the network to enforce access control, a responsibility that should never be delegated to the network layer alone.'
));

bodyChildren.push(h2('How It Works: Middleware, Tokens, and Exclusions'));
bodyChildren.push(body(
  'The API Authentication Gate is implemented as Next.js middleware that intercepts every incoming request before it reaches any route handler. The middleware inspects the Authorization header of each request, looking for a Bearer token scheme. If the header is missing, malformed, or does not match the expected token value stored in the ELI_API_KEY environment variable, the middleware immediately returns an HTTP 401 Unauthorized response, preventing the request from proceeding any further. This approach is effective because middleware in Next.js runs at the edge of the request pipeline, meaning that unauthorized requests are rejected before any application logic executes, before any database queries run, and before any external API calls are made. The only exception is the health check endpoint at /api/health, which is deliberately excluded from authentication to allow load balancers, monitoring systems, and container orchestration platforms to verify that the service is alive without needing to possess credentials.'
));
bodyChildren.push(body(
  'The implementation leverages the standard HTTP Authorization header with the Bearer token scheme, which is the widely accepted approach for API authentication. The ELI_API_KEY environment variable is used to store the expected token value, keeping the secret out of the codebase and allowing it to be configured independently per deployment environment. This is a crucial design decision because it means the authentication secret can be rotated without changing any code, simply by updating the environment variable and restarting the service. The middleware pattern also provides a clean separation of concerns, keeping authentication logic centralized in a single file rather than scattered across individual route handlers. This centralization makes security auditing easier and reduces the risk of a developer accidentally creating a new route without adding authentication checks, because the middleware catches all routes automatically.'
));

bodyChildren.push(h2('Code Example'));
bodyChildren.push(codeBlock(
  '// middleware.ts - API Authentication Gate\n' +
  'import { NextResponse } from "next/server";\n' +
  'import type { NextRequest } from "next/server";\n' +
  '\n' +
  'export function middleware(req) {\n' +
  '  const { pathname } = req.nextUrl;\n' +
  '\n' +
  '  // Exclude health check from auth\n' +
  '  if (pathname === "/api/health") {\n' +
  '    return NextResponse.next();\n' +
  '  }\n' +
  '\n' +
  '  const authHeader = req.headers.get("authorization");\n' +
  '  const expectedToken = process.env.ELI_API_KEY;\n' +
  '\n' +
  '  if (!authHeader || !authHeader.startsWith("Bearer ")) {\n' +
  '    return NextResponse.json(\n' +
  '      { error: "Missing or invalid Authorization header" },\n' +
  '      { status: 401 }\n' +
  '    );\n' +
  '  }\n' +
  '\n' +
  '  const token = authHeader.slice(7);\n' +
  '  if (token !== expectedToken) {\n' +
  '    return NextResponse.json(\n' +
  '      { error: "Invalid API key" },\n' +
  '      { status: 401 }\n' +
  '    );\n' +
  '  }\n' +
  '\n' +
  '  return NextResponse.next();\n' +
  '}\n' +
  '\n' +
  'export const config = {\n' +
  '  matcher: "/api/:path*"\n' +
  '};'
));

bodyChildren.push(h2('Learning Exercise: Build Auth Middleware for Express'));
bodyChildren.push(body(
  'To reinforce your understanding of API authentication, build an Express middleware function that replicates the behavior of the Next.js middleware shown above. Create a new Express application with at least three protected routes and one public health check route. Your middleware should read the expected token from an environment variable called EXPRESS_API_KEY, inspect the Authorization header on every incoming request, and return a 401 JSON response if the token is missing or incorrect. The health check route at /health must be excluded from authentication. After implementing the basic middleware, extend it to support multiple valid tokens stored in a comma-separated environment variable, and add a logging statement that records the source IP address and route path of every rejected request. Test your implementation using curl commands that demonstrate both successful authenticated requests and failed attempts with missing, malformed, and incorrect tokens. This exercise will give you hands-on experience with the middleware pattern in a different framework, helping you understand that the concepts are transferable regardless of the specific technology stack.'
));

bodyChildren.push(pageBreak());

// ──────────────────────────────────────────────────────────────
//  CHAPTER 3: Parameter 2 - Key Approval Queue
// ──────────────────────────────────────────────────────────────
bodyChildren.push(h1('Chapter 3: Parameter 2 - Key Approval Queue'));

bodyChildren.push(h2('The Problem: Auto-Injected Unvalidated Keys'));
bodyChildren.push(body(
  'In Eli\'s original design, API keys could be submitted via email messages and were automatically injected into the system\'s key vault without any human review or validation. This workflow was convenient for quick configuration but introduced a severe security vulnerability. If an attacker gained access to the email account that receives key submissions, or if they spoofed an email that appeared to come from a legitimate source, they could inject a fabricated API key into the vault. Once injected, that key would be used for all subsequent API calls, giving the attacker the ability to intercept requests, redirect traffic, or inject malicious content into LLM responses. The auto-injection model operated on the assumption that all incoming key submissions were trustworthy, which is an assumption that violates the principle of zero trust and creates a single point of failure at the email channel.'
));
bodyChildren.push(body(
  'The problem was compounded by the fact that keys submitted via email could not be verified in real time. Email is an asynchronous, store-and-forward protocol with no guarantee of authenticity. Even with SPF, DKIM, and DMARC protections in place, email spoofing remains a non-trivial threat, particularly for sophisticated attackers who understand how to navigate these security mechanisms. Furthermore, legitimate key submissions could contain typos, truncated values, or keys that had already been revoked by the service provider. By auto-injecting every received key, the system would blindly accept these invalid keys and only fail later when an actual API call was attempted, at which point the root cause would be difficult to trace because there was no audit trail connecting the failed call to the original key submission event. The auto-injection approach prioritized convenience over security, and the Key Approval Queue was introduced to restore the proper balance between these two concerns.'
));

bodyChildren.push(h2('How It Works: Pending State and Explicit Approval'));
bodyChildren.push(body(
  'The Key Approval Queue introduces a pending state for all newly submitted API keys. When a key is received, instead of being immediately injected into the active vault, it is stored in a PendingKey data structure that captures the key value, the service it is intended for, the timestamp of submission, and the source of the submission. The key remains in this pending state until an authorized operator explicitly approves it through a dedicated API endpoint. The approval endpoint is itself protected by the API Authentication Gate, ensuring that only authenticated operators can approve keys. The POST /api/omni?action=approve endpoint accepts the key identifier and moves the key from the pending queue to the active vault, making it available for use in actual API calls.'
));
bodyChildren.push(body(
  'This architecture provides several important security benefits. First, it creates a human-in-the-loop checkpoint where an operator can review the key before it becomes active, checking for suspicious patterns, verifying the source, and confirming that the key is intended for the correct service. Second, it establishes a clear separation between the key submission channel, which may be low-trust, and the key activation channel, which is high-trust because it requires authentication. Third, it enables the implementation of additional policy controls at the approval stage, such as requiring that a key be submitted from a specific email domain, that it pass format validation before approval is allowed, or that only one key per service can be active at a time. The pending queue also serves as a natural audit point, recording every key submission regardless of whether it is ultimately approved, which provides valuable visibility into the key management lifecycle and helps detect patterns of abuse or attempted infiltration.'
));

bodyChildren.push(h2('Code Example'));
bodyChildren.push(codeBlock(
  '// types.ts - PendingKey type definition\n' +
  'type PendingKey = {\n' +
  '  id: string;\n' +
  '  service: string;\n' +
  '  key: string;\n' +
  '  submittedAt: string;\n' +
  '  source: string;\n' +
  '};\n' +
  '\n' +
  '// Key approval queue handler\n' +
  'const pendingKeys: PendingKey[] = [];\n' +
  'const activeKeys: Map<string, string> = new Map();\n' +
  '\n' +
  'function submitKey(service, key, source) {\n' +
  '  const entry = {\n' +
  '    id: "pk_" + Date.now(),\n' +
  '    service: service,\n' +
  '    key: key,\n' +
  '    submittedAt: new Date().toISOString(),\n' +
  '    source: source\n' +
  '  };\n' +
  '  pendingKeys.push(entry);\n' +
  '  return entry.id;\n' +
  '}\n' +
  '\n' +
  'function approveKey(pendingId) {\n' +
  '  const idx = pendingKeys.findIndex(\n' +
  '    function(k) { return k.id === pendingId; }\n' +
  '  );\n' +
  '  if (idx === -1) return null;\n' +
  '  const entry = pendingKeys.splice(idx, 1)[0];\n' +
  '  activeKeys.set(entry.service, entry.key);\n' +
  '  return entry;\n' +
  '}'
));

bodyChildren.push(h2('Learning Exercise: Build a Key Validation Pipeline'));
bodyChildren.push(body(
  'Build a key validation pipeline that goes beyond simple storage and retrieval. Create an Express application that accepts key submissions via a POST endpoint and stores them in a pending queue. Implement a separate GET endpoint that lists all pending keys with their metadata. Then create an approval endpoint that moves a pending key to active status, but only after the key passes a basic format check. The format check should verify that the key matches the expected pattern for its declared service, such as starting with "AIza" for Gemini or "sk-" for OpenAI. Extend the pipeline with a rejection endpoint that removes a key from the pending queue and records the reason for rejection. Finally, add a status endpoint that shows how many keys are pending, how many are active, and how many have been rejected, giving operators a dashboard view of the key management lifecycle. This exercise will teach you how to design state machines for security-critical workflows and how to enforce policy at each state transition.'
));

bodyChildren.push(pageBreak());

// ──────────────────────────────────────────────────────────────
//  CHAPTER 4: Parameter 3 - Fake Key Validation
// ──────────────────────────────────────────────────────────────
bodyChildren.push(h1('Chapter 4: Parameter 3 - Fake Key Validation'));

bodyChildren.push(h2('The Problem: Pattern-Matched Strings Are Not Real Keys'));
bodyChildren.push(body(
  'A key that looks like a Google Gemini API key is not necessarily a valid Google Gemini API key. The format check implemented as part of the Key Approval Queue can verify that a key string matches the expected pattern, such as beginning with the prefix "AIza" followed by a specific number of alphanumeric characters, but this check is purely syntactic and proves nothing about the key\'s actual validity. A revoked key, an expired key, a key from a different project, or a completely fabricated string that happens to match the pattern will all pass a format check while being completely useless for making API calls. In the context of Eli, where keys are used to make real API calls to external LLM services, accepting a fake key means that the system will appear to be configured correctly but will fail silently when it attempts to use the key, producing confusing error messages and degrading the user experience.'
));
bodyChildren.push(body(
  'More concerning than the operational inconvenience is the security implication. An attacker who understands the key format could submit a fabricated key that passes the format check, and if the approval process is not sufficiently rigorous, that key could be approved and injected into the active vault. Once active, every API call made by the system would fail, effectively creating a denial-of-service condition that is difficult to diagnose because the key appears valid at every level except the actual API call. Furthermore, if the system caches responses or falls back to alternative keys, the presence of a fake key in the vault could trigger unexpected failover behavior that exposes additional keys or creates race conditions. The fundamental problem is that syntactic validation is necessary but not sufficient, and the Fake Key Validation parameter was introduced to add the missing semantic validation layer.'
));

bodyChildren.push(h2('How It Works: Two-Step Validation with Live API Test'));
bodyChildren.push(body(
  'The Fake Key Validation parameter implements a two-step validation process. The first step is a format check using the SERVICES_MAP configuration, which defines the expected prefix pattern and length for each supported service. If the key fails this format check, it is immediately rejected with a descriptive error message explaining what format was expected. If the key passes the format check, the second step is executed: an actual API call to the target service using the candidate key. For Google Gemini, this test call sends a minimal request with the prompt "Say OK" to the Gemini API endpoint. If the API responds successfully, the key is confirmed as valid and can proceed to the approval queue. If the API responds with an authentication error, the key is flagged as invalid regardless of its format, and the submission is rejected with a message indicating that the key failed the live validation test.'
));
bodyChildren.push(body(
  'This two-step approach is both efficient and thorough. The format check is fast and cheap, catching obvious errors like truncated keys, wrong service prefixes, or keys with embedded whitespace before any network call is made. The live API test is slower and consumes a small amount of API quota, but it provides definitive proof that the key is valid, active, and associated with a project that has the necessary API enabled. The test prompt "Say OK" is deliberately minimal to reduce quota consumption while still exercising the full authentication path of the API. If the test call succeeds, we know with high confidence that the key will work for subsequent real requests. If it fails, we know the key is not usable regardless of how well-formatted it appears. This combination of fast syntactic validation followed by definitive semantic validation provides the strongest possible assurance of key validity without requiring manual testing by an operator.'
));

bodyChildren.push(h2('Code Example'));
bodyChildren.push(codeBlock(
  '// validate-key.ts - Two-step key validation\n' +
  'const SERVICES_MAP = {\n' +
  '  "gemini": { prefix: "AIza", minLength: 35 }\n' +
  '};\n' +
  '\n' +
  'async function validateKey(service, key) {\n' +
  '  // Step 1: Format check\n' +
  '  const rules = SERVICES_MAP[service];\n' +
  '  if (!key.startsWith(rules.prefix)) {\n' +
  '    return { valid: false, reason: "Bad prefix" };\n' +
  '  }\n' +
  '  if (key.length < rules.minLength) {\n' +
  '    return { valid: false, reason: "Too short" };\n' +
  '  }\n' +
  '\n' +
  '  // Step 2: Live API test\n' +
  '  try {\n' +
  '    const url = "https://generativelanguage.googleapis.com"\n'
 +
  '      + "/v1beta/models/gemini-pro:generateContent"\n' +
  '      + "?key=" + key;\n' +
  '    const resp = await fetch(url, {\n' +
  '      method: "POST",\n' +
  '      headers: { "Content-Type": "application/json" },\n' +
  '      body: JSON.stringify({\n' +
  '        contents: [{ parts: [{ text: "Say OK" }] }]\n' +
  '      })\n' +
  '    });\n' +
  '    if (!resp.ok) {\n' +
  '      return { valid: false, reason: "API rejected key" };\n' +
  '    }\n' +
  '    return { valid: true };\n' +
  '  } catch (err) {\n' +
  '    return { valid: false, reason: "Network error" };\n' +
  '  }\n' +
  '}'
));

bodyChildren.push(h2('Learning Exercise: Implement Two-Step Validation'));
bodyChildren.push(body(
  'Implement a two-step validation module that can be used with multiple API services. Start by defining a configuration object that maps service names to their key format rules, including prefix, minimum length, allowed characters, and a test endpoint URL. Write a generic validateKey function that accepts a service name and a key string, performs the format check using the configuration, and if the format check passes, makes a live API call to the service\'s test endpoint. Handle the case where the live test is unavailable by implementing a configurable fallback that either defaults to accepting the key with a warning or defaults to rejecting it, depending on the security posture. Add support for caching validation results so that the same key is not tested multiple times within a configurable time window. Finally, write unit tests that verify both the format check and the live validation logic using mocked HTTP responses. This exercise will give you practical experience with the pattern of combining cheap local checks with expensive but definitive remote checks, which is a fundamental pattern in security engineering.'
));

bodyChildren.push(pageBreak());

// ──────────────────────────────────────────────────────────────
//  CHAPTER 5: Parameter 4 - Payload Size Limits
// ──────────────────────────────────────────────────────────────
bodyChildren.push(h1('Chapter 5: Parameter 4 - Payload Size Limits'));

bodyChildren.push(h2('The Problem: Arbitrarily Large Request Bodies'));
bodyChildren.push(body(
  'Without payload size limits, an HTTP server will accept request bodies of any size, limited only by the available memory of the server process and the patience of the client. This creates a classic denial-of-service vulnerability where an attacker can submit a request with a body that is hundreds of megabytes or even gigabytes in size, causing the server to allocate massive amounts of memory to buffer the incoming data. In a Node.js environment, where the event loop is single-threaded and memory is shared across all concurrent requests, a single oversized payload can exhaust the available heap, trigger garbage collection storms, or cause the process to crash entirely with an out-of-memory error. Even if the server does not crash, the time spent buffering and parsing an enormous payload degrades performance for all other concurrent requests, effectively slowing the service to a crawl for the duration of the attack.'
));
bodyChildren.push(body(
  'The risk is especially acute for AI agent endpoints like Eli\'s omni route, which accepts JSON request bodies containing prompts, context, and configuration data. An attacker could craft a JSON payload that is technically valid but contains deeply nested structures, extremely long string values, or arrays with millions of elements, all of which would consume disproportionate amounts of memory during parsing. The JSON.parse operation itself can be weaponized through payload structures that create deeply nested objects, leading to stack overflow errors. Additionally, even if the server survives the parsing step, the resulting data structure might be passed to downstream components like the LLM API call or the audit logging system, amplifying the resource consumption throughout the entire request processing pipeline. The absence of payload size limits is a fundamental oversight that turns the server into an amplifier for resource exhaustion attacks, and the Payload Size Limits parameter was introduced to cap this risk at the earliest possible point in the request lifecycle.'
));

bodyChildren.push(h2('How It Works: Content-Length Check and 413 Response'));
bodyChildren.push(body(
  'The Payload Size Limits parameter is implemented as a check at the very beginning of the request handling pipeline, before any body parsing occurs. The handler reads the Content-Length header from the incoming request and compares it against a configurable limit, which is set to 10,240 bytes (10KB) by default. If the Content-Length header indicates that the request body exceeds this limit, the handler immediately returns an HTTP 413 Payload Too Large response with a JSON body explaining the limit and the actual size of the request. This approach is extremely efficient because it requires no body buffering, no parsing, and no memory allocation beyond reading a single HTTP header. The check completes in constant time and constant memory, making it immune to the very attack it is designed to prevent.'
));
bodyChildren.push(body(
  'The 10KB limit was chosen based on an analysis of the actual payload sizes that Eli\'s endpoints need to handle. A typical omni request containing a prompt, a few context documents, and configuration options rarely exceeds two kilobytes of JSON. Even with generous margins for longer prompts and additional metadata, ten kilobytes provides more than enough headroom for legitimate use cases while being small enough to prevent abuse. If a legitimate use case requires a larger payload in the future, the limit can be increased through a configuration change, but the principle of having a limit should never be removed. The 413 status code is the semantically correct HTTP response for this scenario, and it signals to well-behaved clients that they should reduce their payload size and retry. Combined with the authentication gate, this parameter ensures that only authenticated users can even attempt to submit payloads, and those payloads are bounded in size, dramatically reducing the attack surface for resource exhaustion attacks.'
));

bodyChildren.push(h2('Code Example'));
bodyChildren.push(codeBlock(
  '// payload-guard.ts - Size limit enforcement\n' +
  'const MAX_PAYLOAD_BYTES = 10 * 1024; // 10 KB\n' +
  '\n' +
  'function enforcePayloadLimit(req, res, next) {\n' +
  '  const len = parseInt(\n' +
  '    req.headers["content-length"] || "0", 10\n' +
  '  );\n' +
  '\n' +
  '  if (len > MAX_PAYLOAD_BYTES) {\n' +
  '    res.status(413).json({\n' +
  '      error: "Payload too large",\n' +
  '      limit: MAX_PAYLOAD_BYTES + " bytes",\n' +
  '      received: len + " bytes"\n' +
  '    });\n' +
  '    return;\n' +
  '  }\n' +
  '\n' +
  '  next();\n' +
  '}'
));

bodyChildren.push(h2('Learning Exercise: Add Payload Limits to Express'));
bodyChildren.push(body(
  'Add payload size limiting to an Express application using both a custom middleware implementation and the built-in express.json limit option. First, implement the Content-Length header check as shown in the code example, but extend it to also handle the case where the Content-Length header is missing by wrapping the body parser in a stream that counts bytes as they arrive and aborts the request if the count exceeds the limit. This handles the edge case where a malicious client sends a body that is larger than the declared Content-Length or omits the header entirely. Next, configure express.json with a limit option and compare the behavior of both approaches. Document the differences in when each check triggers and what happens to the connection in each case. Finally, add logging to your payload limit middleware that records the source IP, the requested path, the declared size, and the configured limit for every rejected request, creating an early warning system that can detect patterns of abuse before they become critical. This exercise will teach you about the nuances of HTTP body handling and the importance of defense-in-depth at the transport level.'
));

bodyChildren.push(pageBreak());

// ──────────────────────────────────────────────────────────────
//  CHAPTER 6: Parameter 5 - Audit Logging
// ──────────────────────────────────────────────────────────────
bodyChildren.push(h1('Chapter 6: Parameter 5 - Audit Logging'));

bodyChildren.push(h2('The Problem: Console.log-Only, No Persistence'));
bodyChildren.push(body(
  'Before the introduction of structured audit logging, Eli\'s operational visibility depended entirely on console.log statements scattered throughout the codebase. This approach has several critical shortcomings that make it unsuitable for a production security environment. First, console output is ephemeral. Once the terminal buffer scrolls past or the process restarts, the log data is permanently lost. There is no way to review what happened yesterday, last week, or last month. Second, console.log output is unstructured, making it difficult or impossible to programmatically query for specific events, filter by severity, or aggregate statistics. A human operator must manually read through the output to find relevant information, which is impractical at any significant scale. Third, console output provides no guarantee of delivery. If the process crashes before the output buffer is flushed, the most recent log entries, which are often the most important for diagnosing the crash, may be lost.'
));
bodyChildren.push(body(
  'The absence of persistent, queryable audit logs is a particularly severe gap in a security context because security incidents often require retrospective analysis. When an intrusion is detected, the first question is always: what happened, and when? Without audit logs, there is no answer. When a key is rejected, the operator needs to know: how many times was this key submitted, from what sources, and were there other suspicious keys submitted around the same time? Without audit logs, these questions cannot be answered. When an API call fails unexpectedly, the operator needs to see the full history of requests leading up to the failure, including authentication decisions, payload sizes, and response codes. Without audit logs, the investigation relies on guesswork and speculation. The console.log approach was acceptable during early development when the system was running on a single machine with a developer watching the terminal, but it is fundamentally inadequate for a deployed service that needs to meet basic security observability requirements.'
));

bodyChildren.push(h2('How It Works: Structured JSONL with In-Memory Buffer'));
bodyChildren.push(body(
  'The audit logging system is built around three core components: the audit() function, a JSONL file writer, and an in-memory buffer. The audit() function is the public API that the rest of the system calls to record events. It accepts an event type string, a structured data object, and an optional severity level. Each call to audit() creates a log entry object containing a timestamp in ISO 8601 format, the event type, the severity level, the structured data, and a unique entry identifier generated from a combination of the timestamp and a counter. This entry is immediately pushed into the in-memory buffer, which acts as a write-ahead cache that smooths out disk I/O and ensures that logging does not become a bottleneck for request handling.'
));
bodyChildren.push(body(
  'The JSONL format, where each line is a self-contained JSON object, was chosen for its simplicity and queryability. Unlike a monolithic JSON array, a JSONL file can be appended to without reading or rewriting the entire file, making writes extremely efficient. Each line can be parsed independently, making it easy to process the log file with standard Unix tools like grep, jq, or awk, as well as with programmatic log analysis pipelines. The in-memory buffer holds the most recent entries and serves dual purposes: it provides fast access to recent events for the /api/audit endpoint without requiring a disk read, and it provides redundancy in case the disk write fails or is delayed. The buffer is periodically flushed to disk, and on process shutdown, any remaining buffered entries are written to the log file before the process exits, ensuring that no audit data is lost during normal operations. The /api/audit endpoint allows authenticated operators to query the audit log, filter by event type or severity, and retrieve the most recent entries, providing real-time operational visibility into the system\'s security posture.'
));

bodyChildren.push(h2('Code Example'));
bodyChildren.push(codeBlock(
  '// audit.ts - Structured audit logging system\n' +
  'const fs = require("fs");\n' +
  'const path = require("path");\n' +
  '\n' +
  'const AUDIT_FILE = path.join(process.cwd(), "audit.log");\n' +
  'const AUDIT_BUFFER_MAX = 500;\n' +
  'let auditBuffer = [];\n' +
  'let entryCounter = 0;\n' +
  '\n' +
  'function audit(event, data, level) {\n' +
  '  level = level || "info";\n' +
  '  const entry = {\n' +
  '    id: "evt_" + Date.now() + "_" + (entryCounter++),\n' +
  '    timestamp: new Date().toISOString(),\n' +
  '    event: event,\n' +
  '    level: level,\n' +
  '    data: data\n' +
  '  };\n' +
  '  auditBuffer.push(entry);\n' +
  '  if (auditBuffer.length >= AUDIT_BUFFER_MAX) {\n' +
  '    flushAuditBuffer();\n' +
  '  }\n' +
  '  return entry;\n' +
  '}\n' +
  '\n' +
  'function flushAuditBuffer() {\n' +
  '  if (auditBuffer.length === 0) return;\n' +
  '  const lines = auditBuffer.map(function(e) {\n' +
  '    return JSON.stringify(e);\n' +
  '  }).join("\n");\n' +
  '  fs.appendFileSync(AUDIT_FILE, lines + "\n");\n' +
  '  auditBuffer = [];\n' +
  '}'
));

bodyChildren.push(h2('Learning Exercise: Build a Forensic Audit Trail'));
bodyChildren.push(body(
  'Build a standalone audit trail module that can be integrated into any Express or Node.js application. Your module should provide an audit() function with the same signature as the example, but extend it with additional features: support for multiple log files based on event severity, automatic log file rotation when a file exceeds a configurable size limit, and a query API that supports filtering by date range, event type, severity, and arbitrary data fields. Implement the query functionality using a simple in-memory index that maps field values to entry identifiers, making queries efficient without requiring a full scan of the log file. Add a compact operation that merges and compresses old log files to manage disk usage over time. Finally, create a real-time event stream using Server-Sent Events that pushes new audit entries to connected clients as they are recorded, enabling live monitoring dashboards. This exercise will teach you the fundamentals of observability engineering and give you a reusable module that you can integrate into future projects to provide professional-grade audit logging capabilities.'
));

bodyChildren.push(pageBreak());

// ──────────────────────────────────────────────────────────────
//  CHAPTER 7: How They Work Together
// ──────────────────────────────────────────────────────────────
bodyChildren.push(h1('Chapter 7: How They Work Together'));

bodyChildren.push(h2('Architecture Overview'));
bodyChildren.push(body(
  'The five safety parameters are not independent, isolated controls. They form an integrated security architecture where each parameter protects a specific stage of the request lifecycle and complements the protections provided by the others. Understanding how they interact is essential for maintaining and extending the system, because modifying one parameter can affect the behavior and effectiveness of the others. The following table provides a concise reference showing each parameter, the stage it protects, the mechanism it uses, and the threat it mitigates. Together, these parameters create a security pipeline that inspects, validates, limits, and records every interaction with the system, ensuring that no request reaches the core application logic without passing through multiple security gates.'
));

bodyChildren.push(makeTable(
  ['Parameter', 'Lifecycle Stage', 'Mechanism', 'Threat Mitigated'],
  [
    ['API Auth Gate', 'Request Entry', 'Bearer token check', 'Unauthorized access'],
    ['Key Approval Queue', 'Key Submission', 'Pending state + approval', 'Auto-injection of untrusted keys'],
    ['Fake Key Validation', 'Key Activation', 'Format check + live API test', 'Invalid or forged keys'],
    ['Payload Size Limits', 'Request Parsing', 'Content-Length header check', 'Denial-of-service via large bodies'],
    ['Audit Logging', 'All Stages', 'JSONL file + in-memory buffer', 'Lack of forensic visibility']
  ]
));

bodyChildren.push(spacer());

bodyChildren.push(h2('Request Lifecycle'));
bodyChildren.push(body(
  'When an incoming HTTP request arrives at Eli\'s server, it passes through a well-defined sequence of security checks before any application logic is executed. The first check is the API Authentication Gate, which runs as Next.js middleware and verifies the Bearer token in the Authorization header. If the token is missing or invalid, the request is rejected immediately with a 401 response, and the rejection is recorded in the audit log. If authentication succeeds, the request proceeds to the Payload Size Limits check, which inspects the Content-Length header and rejects the request with a 413 response if the body exceeds the 10KB limit. Again, the rejection is recorded in the audit log. If both checks pass, the request body is parsed and routed to the appropriate handler.'
));
bodyChildren.push(body(
  'For requests that require LLM calls, the handler searches the key vault for an active key for the requested service. If no active key is found, the request fails with an appropriate error. If a key is found, the handler uses it to make the API call to the external LLM service. The response from the LLM service is processed, formatted, and returned to the caller. Throughout this entire lifecycle, from initial authentication through payload validation, key lookup, API call, and response delivery, the audit logging system records every significant event. This includes the authentication decision, the payload size check, the key used for the API call, the request and response sizes, the latency of the external API call, and the final response status code. The result is a complete, timestamped record of every request from entry to exit, providing the forensic visibility needed for security monitoring, performance analysis, and incident investigation.'
));

bodyChildren.push(h2('Key Extraction Lifecycle'));
bodyChildren.push(body(
  'The key management lifecycle follows a separate but parallel path that interacts with the request lifecycle at specific points. When a new API key is submitted, typically via an email message or a direct API call, the system first extracts the key string and the declared service name from the submission. The key is then placed in the PendingKey queue, where it waits for explicit approval. Before approval can be granted, the Fake Key Validation parameter runs its two-step check: first verifying the key format against the SERVICES_MAP configuration, and then making a live API call to confirm that the key actually works. If validation fails at either step, the key remains in the pending queue with a rejection flag and a reason code, and the submission event is recorded in the audit log.'
));
bodyChildren.push(body(
  'If validation succeeds, an authenticated operator can approve the key through the POST /api/omni?action=approve endpoint. Approval moves the key from the pending queue to the active vault, making it available for use in actual API calls. The approval event, including the operator\'s identity, the key identifier, and the timestamp, is recorded in the audit log. Once active, the key is used by the request lifecycle whenever an LLM call is needed for the corresponding service. If a key is later found to be compromised or needs to be rotated, it can be deactivated through a revocation endpoint, which removes it from the active vault and records the revocation in the audit log. Throughout this entire lifecycle, from initial extraction through validation, approval, active use, and eventual revocation, the audit log provides a complete chain of custody for every key in the system, enabling operators to answer questions like: when was this key submitted? Who approved it? How many times has it been used? When was it last validated?'
));

bodyChildren.push(h2('Audit Log as Connective Tissue'));
bodyChildren.push(body(
  'The audit log is the connective tissue that binds all five safety parameters into a coherent security system. Every parameter generates audit events at its decision points: the auth gate logs every authentication attempt and its outcome, the key queue logs every submission, approval, and rejection, the validation system logs every format check and live test result, the payload limiter logs every size check and rejection, and the audit system itself logs its own operations including buffer flushes and file rotations. This comprehensive event stream creates a timeline that reconstructs the complete history of the system\'s security decisions, making it possible to trace any request from its arrival to its completion through every security checkpoint it passed or failed.'
));
bodyChildren.push(body(
  'The audit log\'s value extends beyond incident response. It enables proactive security monitoring by providing data that can be analyzed for patterns indicative of emerging threats. For example, a sudden spike in 401 responses from a specific IP address may indicate a brute-force authentication attempt. A cluster of key submission failures for the same service may indicate that someone is probing for valid keys. A series of 413 responses may indicate an ongoing denial-of-service attack. By making these patterns visible through structured, queryable log data, the audit log transforms security from a reactive, incident-driven process into a proactive, data-driven discipline. It is the single most important parameter for long-term security hygiene because it provides the visibility that all other parameters lack individually, and it ties their individual protections together into a system whose behavior can be understood, monitored, and improved over time.'
));

bodyChildren.push(pageBreak());

// ──────────────────────────────────────────────────────────────
//  CHAPTER 8: Learning Guide - Practice Projects
// ──────────────────────────────────────────────────────────────
bodyChildren.push(h1('Chapter 8: Learning Guide - Practice Projects'));

bodyChildren.push(body(
  'This chapter provides five progressive practice projects designed to consolidate your understanding of the safety parameters described in this guidebook. Each project builds on the concepts introduced in the previous chapters and adds new complexity that prepares you for real-world security engineering challenges. The projects are ordered by difficulty, starting with a focused single-concept implementation and culminating in a comprehensive safety layer that integrates all four preceding projects into a unified system. For each project, a detailed description of the requirements is provided along with guidance on the key design decisions you will need to make. Complete all five projects to develop a thorough, practical understanding of how to build security controls that are robust, maintainable, and effective in production environments.'
));

bodyChildren.push(h2('Project 1: Express Auth Shield'));
bodyChildren.push(body(
  'Build an Express middleware module that provides API authentication for a multi-route Express application. Your module should export a single function that accepts a configuration object with the expected token, an optional array of excluded paths, and an optional logging callback. The middleware should check the Authorization header on every request, compare the Bearer token against the configured value, and return a 401 JSON response with a standard error format if authentication fails. Excluded paths should bypass authentication entirely. The logging callback should be invoked for every authentication decision, receiving the request path, the source IP, the outcome, and the timestamp. Write comprehensive tests using a testing framework of your choice that verify correct behavior for authenticated requests, unauthenticated requests, missing headers, malformed headers, and excluded paths. This project focuses on the middleware pattern, environment-based configuration, and structured error responses, which are foundational skills for building any API security control.'
));

bodyChildren.push(h2('Project 2: Key Pipeline'));
bodyChildren.push(body(
  'Build a key management pipeline that implements the submission, validation, approval, and activation lifecycle described in Chapters 3 and 4. Create a KeyPipeline class that manages three internal data structures: a pending queue, an active vault, and a rejection log. The class should provide methods for submitting a new key with a service identifier, listing pending keys, approving a key by its identifier, rejecting a key with a reason, and retrieving the active key for a given service. Integrate a two-step validation process that first checks the key format against a configurable rules map and then performs a live API test using a configurable test function. The test function should be injectable to facilitate testing without making real API calls. Add event emission so that external code can subscribe to lifecycle events like key.submitted, key.approved, key.rejected, and key.activated. This project teaches you how to design stateful security components with clean interfaces and extensible validation logic.'
));

bodyChildren.push(h2('Project 3: Audit Trail'));
bodyChildren.push(body(
  'Build a standalone audit trail module based on the design described in Chapter 6. Your module should export an audit() function and a createAuditReader() function. The audit() function should accept an event type, a data object, and an optional severity level, and should write structured JSONL entries to a configurable log file. Implement an in-memory buffer with a configurable maximum size and a flush policy that writes buffered entries to disk when the buffer is full or after a configurable time interval. The createAuditReader() function should return an object with methods for querying the audit log by date range, event type, and severity level. Implement log file rotation based on file size, with a configurable maximum file size and a configurable number of retained files. Add a compact operation that merges and optionally compresses rotated files. Write integration tests that verify end-to-end behavior including writing entries, flushing the buffer, querying the log, and rotating files. This project develops your skills in persistent storage, file I/O, query interfaces, and data lifecycle management.'
));

bodyChildren.push(h2('Project 4: Rate Limiter'));
bodyChildren.push(body(
  'Build a rate limiting middleware that protects API endpoints from abuse by enforcing request rate limits using a sliding window algorithm. Your middleware should track requests per IP address using an in-memory data structure that stores timestamps of recent requests. For each incoming request, the middleware should count the number of requests from the same IP address within the current sliding window period, which should be configurable in milliseconds. If the count exceeds a configurable maximum, the middleware should return an HTTP 429 Too Many Requests response with a JSON body that includes the limit, the remaining time until the window resets, and a Retry-After header indicating how many seconds the client should wait before retrying. Implement window cleanup to prevent memory leaks from accumulating stale entries for IPs that have stopped making requests. Add support for different rate limits for different routes, allowing more permissive limits for lightweight endpoints like health checks and stricter limits for expensive endpoints like LLM calls. This project teaches you about algorithm design for concurrent systems, HTTP status codes for rate limiting, and memory management for long-running server processes.'
));

bodyChildren.push(h2('Project 5: Full Safety Layer'));
bodyChildren.push(body(
  'Combine all four preceding projects into a unified safety layer that can be applied to any Express application with a single function call. Create a createSafetyLayer() function that accepts a configuration object containing all necessary parameters: the API key for authentication, the payload size limit, the rate limit configuration, the audit log file path, and the key pipeline configuration. The function should return an Express router or middleware array that applies all four layers in the correct order: authentication first, then rate limiting, then payload size checking, then the application routes, with audit logging wrapping the entire pipeline to record events at every stage. The safety layer should be configurable enough to be used in different environments with different security requirements, from lenient development settings to strict production configurations. Write a demonstration application that uses the safety layer to protect a simple API with three routes: a public health check, an authenticated data endpoint, and an authenticated admin endpoint that uses the key pipeline. Add a monitoring dashboard endpoint that displays real-time statistics from the audit log, including request counts, authentication success and failure rates, rate limit violations, and payload rejections. This capstone project integrates everything you have learned into a production-ready security module that demonstrates the defense-in-depth philosophy in action.'
));

// ══════════════════════════════════════════════════════════════
//  BUILD DOCUMENT
// ══════════════════════════════════════════════════════════════
const bodySection = {
  properties: {
    page: {
      size: { width: 11906, height: 16838, orientation: 'portrait' },
      margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 }
    }
  },
  footers: {
    default: new Footer({
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 100 },
          children: [
            new TextRun({
              children: [PageNumber.CURRENT],
              font: FONT,
              size: 18,
              color: C.footerColor
            })
          ]
        })
      ]
    })
  },
  children: bodyChildren
};

const doc = new Document({
  sections: [coverSection, bodySection]
});

// ── Write file ──
const OUTPUT = '/home/z/my-project/download/Eli-Safety-Parameter-Guidebook.docx';

Packer.toBuffer(doc).then(function(buffer) {
  fs.writeFileSync(OUTPUT, buffer);
  console.log('Guidebook saved to: ' + OUTPUT);
  console.log('Size: ' + (buffer.length / 1024).toFixed(1) + ' KB');
}).catch(function(err) {
  console.error('Error generating docx:', err);
  process.exit(1);
});
