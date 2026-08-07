import { NextRequest, NextResponse } from 'next/server';
import { getVaultContext, buildVaultKnowledgeMap, getVaultStats } from '@/lib/vault-search';

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

type LLMProvider = 'gemini' | 'fallback';

function getProvider(): LLMProvider {
  const key = process.env.GEMINI_API_KEY;
  if (key && (key.startsWith('AIza') || key.startsWith('AQ.')) && key.length > 20) return 'gemini';
  if (key && key.length > 10) return 'gemini';
  return 'fallback';
}

async function callGemini(messages: Array<{ role: string; content: string }>): Promise<string> {
  const { GoogleGenerativeAI } = await import('@google/generative-ai');
  let key = process.env.GEMINI_API_KEY;

  // Try Omni Route key if direct key fails
  if (!key || key.length < 20) {
    try {
      const { getOmniRoute } = await import('@/lib/omni-route');
      key = getOmniRoute().getActiveKey('gemini');
    } catch {}
  }

  if (!key) throw new Error('No Gemini API key available');

  const genAI = new GoogleGenerativeAI(key);
  const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

  const systemMsg = messages.find(m => m.role === 'system');
  const conversationMessages = messages
    .filter(m => m.role !== 'system')
    .map(m => ({
      role: m.role === 'assistant' ? 'model' as const : 'user' as const,
      parts: [{ text: m.content }],
    }));

  const result = await model.generateContent({
    systemInstruction: systemMsg?.content || '',
    contents: conversationMessages,
  });

  // Record usage for rotation tracking
  try {
    const { getOmniRoute } = await import('@/lib/omni-route');
    getOmniRoute().recordUsage();
  } catch {}

  return result.response.text();
}

// ─── Chat Endpoint ────────────────────────────────────────────

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, history = [] } = body as {
      message: string;
      history?: Array<{ role: string; content: string }>;
    };

    if (!message || typeof message !== 'string') {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    // ─── Retrieve from vault (micro-chunk engine) ──────────
    let context = '';
    let sources: Array<{ title: string; source: string; category: string }> = [];
    let containmentHits = 0;
    try {
      const vaultResult = await getVaultContext(message, {
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

    const recentHistory = history.slice(-6);
    for (const h of recentHistory) {
      messages.push({
        role: h.role === 'eli' ? 'assistant' : 'user',
        content: h.content,
      });
    }
    messages.push({ role: 'user', content: message });

    // ─── Call LLM ──────────────────────────────────────────
    let response = '';
    const provider = getProvider();

    if (provider === 'gemini') {
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
        } catch {}
        response = '';
      }
    }

    // Fallback: chunk-sourced response if no LLM
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
      provider: provider === 'gemini' ? 'gemini-2.0-flash' : 'vault-fallback',
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
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// ─── Health / Stats endpoint ───────────────────────────────────

export async function GET() {
  const stats = await getVaultStats();
  return NextResponse.json({
    status: 'ok',
    vault: stats,
    provider: getProvider(),
    timestamp: Date.now(),
  });
}
