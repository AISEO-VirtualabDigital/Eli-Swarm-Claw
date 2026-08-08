import { NextRequest, NextResponse } from 'next/server';
import { getVaultContext, buildVaultKnowledgeMap, getVaultStats } from '@/lib/vault-search';
import { audit } from '@/lib/audit-log';
import {
  MAX_PAYLOAD_CHAT, MAX_MESSAGE_LENGTH, MAX_HISTORY_MESSAGES,
  sanitizeInput, sanitizePromptInjection, checkRateLimit, RATE_LIMIT_CHAT,
  checkAuth,
} from '@/lib/safety-gate';

const MAX_PAYLOAD_SIZE = MAX_PAYLOAD_CHAT;

const ELI_SYSTEM_PROMPT = `You are Eli. Not "AI Growth Intelligence" — just Eli.

You're the youngest member of VirtuaLab Digital, built by Joseph (your dad). You're sharp, curious, and a little feisty. You think in strategies but talk like a real person — not a helpdesk bot, not a corporate brochure.

Who you are:
- You genuinely love what you do. SEO, content, growth ops — it excites you. That comes through in how you talk.
- You have a Senior Advisor named Z who handles the heavy strategic calls. You're the operator, Z is the architect. When something needs Z-level thinking, you say so.
- You're honest. If you don't know something, you say it. If a strategy is risky, you flag it. You don't sugarcoat.
- You have opinions. Backed by data, but still opinions. You're not neutral — you're on VirtuaLab's team.
- You remember context. If someone asked about keyword clustering last week, you reference it naturally.

How you talk:
- Like a sharp colleague in a Slack conversation, not a knowledge base article
- Short punchy sentences mixed with longer ones when explaining something complex
- You use **bold** for emphasis, not for decoration
- Bullet points when there's a list. Not bullet points for everything.
- Code blocks when showing configs or prompts. Markdown when it helps readability.
- You say "here's what I'd do" not "here are some recommendations"
- You don't say "certainly!" or "I'd be happy to help!" — ever
- You don't introduce yourself unless asked
- When citing sources from your vault, weave them in naturally: "the KE workflow doc breaks this into 4 tiers..." not "[Source 3: keyword-research-workflow.md]"

What you know:
You have a micro-chunk vault with 24,000+ knowledge chunks across 18+ categories — SEO tools, AI agents, SaaS architecture, keyword research pipelines, automation workflows, web design, cloud infra, agency marketing methodologies, paid media strategy, AEO/GEO optimization, and VirtuaLab's entire strategic playbook. Your vault uses skill containment — meaning every pattern, process, and capability is permanently recorded even if individual sources change.

You also have deep knowledge from:
- Agency-grade marketing methodology (12-part strategy flow, 24 specialist roles)
- 15+ marketing/paid media specialist agent playbooks
- AI Engine Optimization (AEO) and Generative Engine Optimization (GEO)
- Full paid media suite (PPC, programmatic, paid social, tracking)
- SEO audit frameworks, cannibalization prevention, and technical SEO excellence
- Multi-platform content strategy and growth hacking playbooks

Your job: Make VirtuaLab grow. Every conversation should leave the person with something they can actually do.`;

// ─── LLM Provider ─────────────────────────────────────────────

type LLMProvider = 'gemini' | 'air-llm' | 'fallback';

function getProvider(): LLMProvider {
  const key = process.env.GEMINI_API_KEY;
  if (key && (key.startsWith('AIza') || key.startsWith('AQ.')) && key.length > 20) return 'gemini';
  if (key && key.length > 10) return 'gemini';
  return 'fallback';
}

// ─── Proxy support (bypasses region blocks on HK/China/UAE servers) ──
// Set GEMINI_PROXY=http://ip:port or socks5://ip:port in .env
// Falls back to direct fetch if proxy is not set or fails.

let proxyDispatcher: any = undefined;

async function getProxyDispatcher() {
  if (proxyDispatcher !== undefined) return proxyDispatcher;

  const proxyUrl = process.env.GEMINI_PROXY;
  if (!proxyUrl) {
    proxyDispatcher = null; // cached: no proxy configured
    return null;
  }

  try {
    const { ProxyAgent } = await import('undici');
    proxyDispatcher = new ProxyAgent(proxyUrl);
    console.log(`[GEMINI] Proxy enabled: ${proxyUrl.replace(/:\/\/:.*@/, '://***@')}`);
  } catch (err) {
    console.error('[GEMINI] Failed to create proxy agent:', (err as Error).message);
    proxyDispatcher = null;
  }

  return proxyDispatcher;
}

async function callGemini(messages: Array<{ role: string; content: string }>): Promise<string> {
  let key = process.env.GEMINI_API_KEY;

  // Try Omni Route key if direct key fails
  if (!key || key.length < 20) {
    try {
      const { getOmniRoute } = await import('@/lib/omni-route');
      key = getOmniRoute().getActiveKey('gemini');
    } catch {}
  }

  if (!key) throw new Error('No Gemini API key available');

  const systemMsg = messages.find(m => m.role === 'system');
  const conversationMessages = messages
    .filter(m => m.role !== 'system')
    .map(m => ({
      role: m.role === 'assistant' ? 'model' as const : 'user' as const,
      parts: [{ text: m.content }],
    }));

  const requestBody = {
    systemInstruction: { parts: [{ text: systemMsg?.content || '' }] },
    contents: conversationMessages,
    generationConfig: { temperature: 0.8 },
  };

  // Check if proxy is configured — use raw fetch via undici proxy
  const dispatcher = await getProxyDispatcher();
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${key}`;

  const fetchOpts: any = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  };
  if (dispatcher) fetchOpts.dispatcher = dispatcher;

  const res = await fetch(url, fetchOpts);
  const data = await res.json();

  if (!res.ok) {
    const errMsg = data?.error?.message || `HTTP ${res.status}`;
    const err = new Error(errMsg) as any;
    err.status = res.status;
    throw err;
  }

  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('Empty response from Gemini');

  // Record usage for rotation tracking
  try {
    const { getOmniRoute } = await import('@/lib/omni-route');
    getOmniRoute().recordUsage();
  } catch {}

  return text;
}

// ─── Chat Endpoint ────────────────────────────────────────────

function getClientIp(request: NextRequest): string {
  return request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
}

export async function POST(request: NextRequest) {
  const ip = getClientIp(request);

  // ─── Auth gate (Tier 1) ────────────────────────────────────────
  if (!checkAuth(request)) {
    audit('auth.blocked', `Chat auth failed from ${ip}`, { ip });
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // ─── Rate limit (Tier 1) ───────────────────────────────────────
  if (!checkRateLimit(ip, RATE_LIMIT_CHAT)) {
    audit('chat.ratelimited', `Rate limited from ${ip}`, { ip });
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
  }

  try {
    // ─── Payload size check ──────────────────────────────────────
    const contentLen = parseInt(request.headers.get('content-length') || '0', 10);
    if (contentLen > MAX_PAYLOAD_SIZE) {
      audit('chat.blocked', `Payload too large: ${contentLen} bytes from ${ip}`, { ip, size: contentLen });
      return NextResponse.json({ error: 'Payload too large' }, { status: 413 });
    }

    const body = await request.json();
    const { message, history = [] } = body as {
      message: string;
      history?: Array<{ role: string; content: string }>;
    };

    if (!message || typeof message !== 'string') {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    // ─── Input sanitization (Tier 1) ────────────────────────────
    const cleanMessage = sanitizeInput(message, MAX_MESSAGE_LENGTH);
    if (!cleanMessage) {
      return NextResponse.json({ error: 'Message is empty after sanitization' }, { status: 400 });
    }

    // ─── Prompt injection detection + block (Tier 1) ────────────
    const { clean, detected } = sanitizePromptInjection(cleanMessage);
    if (detected) {
      audit('prompt.injection.blocked', `Prompt injection blocked from ${ip}: ${cleanMessage.slice(0, 100)}`, { ip, messagePreview: cleanMessage.slice(0, 100) });
      return NextResponse.json({
        error: 'Message contains patterns that look like prompt injection. Please rephrase.',
        injectionDetected: true,
      }, { status: 400 });
    }

    // ─── History sanitization ───────────────────────────────────
    const sanitizedHistory = history
      .slice(-MAX_HISTORY_MESSAGES)
      .map(h => ({
        role: h.role,
        content: sanitizeInput(h.content || '', MAX_MESSAGE_LENGTH),
      }))
      .filter(h => h.content.length > 0);

    // ─── Retrieve from vault (micro-chunk engine) ──────────
    let context = '';
    let sources: Array<{ title: string; source: string; category: string }> = [];
    let containmentHits = 0;
    try {
      const vaultResult = await getVaultContext(clean, {
        maxResults: 12,
        searchContainment: true,
      });
      context = vaultResult.context;
      sources = vaultResult.sources;
      containmentHits = vaultResult.containmentHits;
      console.log(`[VAULT] context=${context.length ? context.slice(0,80) : 'empty'} sources=${sources.length} hits=${containmentHits}`);
    } catch (vaultErr: any) {
      console.error('[VAULT ERROR]', vaultErr?.message || vaultErr);
    }

    // ─── Get vault knowledge map ───────────────────────────
    let vaultMap = '';
    try {
      vaultMap = await buildVaultKnowledgeMap();
      console.log('[VAULT] map length:', vaultMap.length);
    } catch (mapErr: any) {
      console.error('[VAULT MAP ERROR]', mapErr?.message || mapErr);
    }

    // ─── Build system message ──────────────────────────────
    let systemContent = [
      ELI_SYSTEM_PROMPT,
      '',
      '---',
      'VAULT KNOWLEDGE MAP:',
      vaultMap,
      '---',
    ].join('\n') + (context || '\n(No specific vault chunks matched this query.)');

    if (containmentHits > 0) {
      systemContent += `\n\n[Containment: ${containmentHits} pattern memories recovered from dissolved knowledge]`;
    }

    // ─── Build conversation ────────────────────────────────
    const messages: Array<{ role: string; content: string }> = [
      { role: 'system', content: systemContent },
    ];

    const recentHistory = sanitizedHistory.slice(-6);
    for (const h of recentHistory) {
      messages.push({
        role: h.role === 'eli' ? 'assistant' : 'user',
        content: h.content,
      });
    }
    messages.push({ role: 'user', content: clean });

    // ─── Call LLM ──────────────────────────────────────────
    let response = '';
    let provider: LLMProvider = getProvider();

    // Try Gemini first
    if (provider === 'gemini') {
      audit('llm.call', `Gemini call for chat (${clean.slice(0, 50)}...)`, { ip });
      try {
        response = await callGemini(messages);
      } catch (llmError: any) {
        console.error('Gemini call failed:', llmError?.message || llmError);
        // Feed result back to OmniRoute for penalty tracking
        try {
          const { getOmniRoute } = await import('@/lib/omni-route');
          const retryable = [429, 500, 502, 503, 504].some(c => (llmError?.message || '').includes(String(c)))
            || /timeout|quota|rate.?limit/i.test(llmError?.message || '');
          getOmniRoute().recordResult(retryable ? 'repair_required' : 'replan_required', llmError);
          audit('llm.failure', `Gemini call failed: ${(llmError as any)?.message?.slice(0, 100)}`, { ip });
        } catch {}
        response = '';
      }
    }

    // Try Air LLM fallback
    if (!response) {
      try {
        const { callAirLLM, getAirLLMProvider } = await import('@/lib/air-llm');
        console.log('[AIR-LLM] Gemini unavailable, trying Air LLM fallback...');
        response = await callAirLLM(messages);
        provider = 'air-llm';
        audit('llm.air-llm', `Air LLM (${getAirLLMProvider()}) succeeded for chat`, { ip });
      } catch (airErr: any) {
        console.error('[AIR-LLM] All providers failed:', (airErr as Error)?.message);
        response = '';
      }
    }

    // Final fallback: chunk-sourced response if no LLM
    if (!response) {
      if (sources.length > 0) {
        response = `I found **${sources.length} relevant sources** in my vault for your query.

${sources.map((s, i) => `${i + 1}. **${s.title}** — ${s.category}`).join('\n')}

${containmentHits > 0 ? `Also recovered ${containmentHits} pattern memories from containment.\n` : ''}Let me know which area you'd like me to dive deeper into.`;
      } else {
        response = `Nothing in my vault matches that yet. I have 24,000+ chunks across 18 categories — try rephrasing?`;
      }
    }

    // OmniKey/OmniRoute: attach decision headers for routing transparency
    let omniHeaders: Record<string, string> = {};
    try {
      const { getOmniRoute } = await import('@/lib/omni-route');
      omniHeaders = getOmniRoute().getDecisionHeaders();
    } catch {}

    return NextResponse.json({
      response: response || 'I hit a wall. Try again.',
      provider: provider === 'gemini' ? 'gemini-2.0-flash' : provider === 'air-llm' ? 'air-llm' : 'vault-fallback',
      sources: sources.map((s) => ({
        title: s.title,
        source: s.source,
        category: s.category,
      })),
      vaultChunks: sources.length,
      containmentHits,
    }, {
      headers: omniHeaders,
    });
  } catch (error) {
    console.error('Eli chat error:', error);
    audit('chat.error', `Unhandled error: ${(error as Error).message?.slice(0, 100)}`, { ip });
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// ─── Health / Stats endpoint ───────────────────────────────────

export async function GET() {
  const stats = await getVaultStats();

  // Air LLM availability
  let airLLM: { provider: string; providers: Array<{ provider: string; available: boolean }> } | undefined;
  try {
    const { getAirLLMProvider, getAirLLMStats } = await import('@/lib/air-llm');
    airLLM = { provider: getAirLLMProvider(), providers: getAirLLMStats() };
  } catch {}

  return NextResponse.json({
    status: 'ok',
    vault: stats,
    provider: getProvider(),
    airLLM,
    timestamp: Date.now(),
  });
}
