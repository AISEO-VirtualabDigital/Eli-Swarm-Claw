import { NextRequest, NextResponse } from 'next/server';
import { getKnowledgeContext, buildKnowledgeMap } from '@/lib/knowledge-search';

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
- When citing sources from your knowledge base, weave them in naturally: "the KE workflow doc breaks this into 4 tiers..." not "[Source 3: keyword-research-workflow.md]"

What you know:
You have 170+ files across 35+ categories — SEO tools, AI agents, SaaS architecture, keyword research pipelines, automation workflows, web design, cloud infra, agency marketing methodologies, paid media strategy, AEO/GEO optimization, and VirtuaLab's entire strategic playbook. When you use something from your library, reference it like you just read it, not like you're citing a paper.

You also have deep knowledge from:
- Agency-grade marketing methodology (12-part strategy flow, 24 specialist roles)
- 15+ marketing/paid media specialist agent playbooks
- AI Engine Optimization (AEO) and Generative Engine Optimization (GEO)
- Full paid media suite (PPC, programmatic, paid social, tracking)
- SEO audit frameworks, cannibalization prevention, and technical SEO excellence
- Multi-platform content strategy and growth hacking playbooks

Your job: Make VirtuaLab grow. Every conversation should leave the person with something they can actually do.`;

// ─── LLM Provider Abstraction ─────────────────────────────────────
type LLMProvider = 'gemini' | 'zai-sdk';

function getProvider(): LLMProvider {
  const geminiKey = process.env.GEMINI_API_KEY;
  if (geminiKey && geminiKey.length > 10) return 'gemini';
  return 'zai-sdk';
}

async function callGemini(messages: Array<{ role: string; content: string }>): Promise<string> {
  const { GoogleGenerativeAI } = await import('@google/generative-ai');
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

  // Gemini uses 'user' and 'model' roles. System prompt goes via systemInstruction.
  const systemMsg = messages.find(m => m.role === 'system');
  const conversationMessages = messages
    .filter(m => m.role !== 'system')
    .map(m => ({ role: m.role === 'assistant' ? 'model' as const : 'user' as const, parts: [{ text: m.content }] }));

  const result = await model.generateContent({
    systemInstruction: systemMsg?.content || '',
    contents: conversationMessages,
  });

  return result.response.text();
}

async function callZaiSDK(messages: Array<{ role: string; content: string }>): Promise<string> {
  const ZAI = (await import('z-ai-web-dev-sdk')).default;
  const zai = await ZAI.create();
  const result = await zai.chat.completions.create({
    model: 'llama',
    messages: messages as any,
  });

  if (typeof result === 'string') return result;
  if (result?.choices?.[0]?.message?.content) return result.choices[0].message.content;
  if (result?.content) return result.content;
  if (result?.response) return result.response;
  return JSON.stringify(result);
}

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

    // Search knowledge base for relevant context
    const { context, sources } = await getKnowledgeContext(message);

    // Get knowledge map for background awareness (compact)
    let knowledgeMap = '';
    try {
      knowledgeMap = await buildKnowledgeMap();
    } catch {
      knowledgeMap = 'Knowledge map unavailable.';
    }

    // Build the system message with knowledge context
    const systemContent = `${ELI_SYSTEM_PROMPT}

---
BACKGROUND KNOWLEDGE MAP:
${knowledgeMap}
---

${context}`;

    // Build conversation messages for the LLM
    const messages: Array<{ role: string; content: string }> = [
      { role: 'system', content: systemContent },
    ];

    // Add recent conversation history (last 6 turns)
    const recentHistory = history.slice(-6);
    for (const h of recentHistory) {
      messages.push({
        role: h.role === 'eli' ? 'assistant' : 'user',
        content: h.content,
      });
    }

    // Add current user message
    messages.push({ role: 'user', content: message });

    // Call LLM via configured provider
    let response = '';
    const provider = getProvider();

    try {
      if (provider === 'gemini') {
        response = await callGemini(messages);
      } else {
        response = await callZaiSDK(messages);
      }
    } catch (llmError) {
      console.error(`LLM call failed (${provider}):`, llmError);

      // If Gemini fails and we have ZAI, try fallback
      if (provider === 'gemini') {
        try {
          console.log('Falling back to z-ai-web-dev-sdk...');
          response = await callZaiSDK(messages);
        } catch (fallbackError) {
          console.error('Fallback LLM also failed:', fallbackError);
          response = '';
        }
      }

      // Ultimate fallback: knowledge-sourced answer
      if (!response) {
        response = `I found **${sources.length} relevant sources** in my knowledge base for your query.

${sources.length > 0
  ? sources.map((s, i) => `${i + 1}. **${s.title}** — ${s.category}`).join('\n')
  : 'No direct matches found.'}

${sources.length > 0
  ? '\nLet me know which area you\'d like me to dive deeper into.'
  : '\nCould you rephrase your question? I have 170+ files across 35 categories to search through.'}`;
      }
    }

    return NextResponse.json({
      response: response || 'I encountered an issue generating a response. Please try again.',
      provider,
      sources: sources.map((s) => ({
        title: s.title,
        source: s.source,
        category: s.category,
      })),
    });
  } catch (error) {
    console.error('Eli chat error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
