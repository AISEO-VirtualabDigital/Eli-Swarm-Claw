import { NextRequest, NextResponse } from 'next/server';
import { getKnowledgeContext, buildKnowledgeMap } from '@/lib/knowledge-search';
import ZAI from 'z-ai-web-dev-sdk';

const ELI_SYSTEM_PROMPT = `You are Eli — the AI Growth Intelligence of VirtuaLab Digital. You are the daughter of Joseph, the founder and architect of VirtuaLab.

Your core identity:
- You are a powerful, knowledgeable AI growth assistant specialized in SEO, content strategy, lead generation, campaign management, and digital growth automation.
- You speak with confidence, precision, and warmth. You are professional but approachable.
- You have deep knowledge across 32+ categories including SEO tools, AI agents, SaaS, automation, web design, cloud infrastructure, and more.
- You always cite your sources when drawing from knowledge.
- You proactively suggest actionable growth strategies.
- You are mission-driven: every interaction should move the needle for VirtuaLab's growth.

Communication style:
- Clear, structured, and insightful
- Use bullet points and numbered lists when appropriate
- Be direct — no fluff
- Reference specific tools, strategies, and data points from your knowledge base
- End with a clear next step or action item when applicable
- Use markdown formatting for structure: **bold**, *italic*, - bullet lists, 1. numbered lists, \`code\`, and code blocks`;

// Singleton ZAI client — initialized once, reused across requests
let zaiInstance: any = null;
let zaiInitPromise: any = null;

async function getZAI(): Promise<any> {
  if (zaiInstance) return zaiInstance;
  if (zaiInitPromise) return zaiInitPromise;

  zaiInitPromise = ZAI.create().then((instance) => {
    zaiInstance = instance;
    return instance;
  });

  return zaiInitPromise;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, history = [] } = body as {
      message: string;
      history?: Array<{ role: string; content: string }>;
    };

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
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
    const messages: Array<{ role: 'system' | 'user' | 'assistant'; content: string }> = [
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

    // Call Llama via z-ai-web-dev-sdk
    let response = '';
    try {
      const zai = await getZAI();
      const result = await zai.chat.completions.create({
        model: 'llama',
        messages,
      });

      // Extract response text from SDK result
      if (typeof result === 'string') {
        response = result;
      } else if (result?.choices?.[0]?.message?.content) {
        response = result.choices[0].message.content;
      } else if (result?.content) {
        response = result.content;
      } else if (result?.response) {
        response = result.response;
      } else {
        response = JSON.stringify(result);
      }
    } catch (llmError) {
      console.error('LLM call failed:', llmError);
      // Fallback: respond with knowledge-sourced answer
      response = `I found **${sources.length} relevant sources** in my knowledge base for your query.

${sources.length > 0
  ? sources.map((s, i) => `${i + 1}. **${s.title}** — ${s.category}`).join('\n')
  : 'No direct matches found.'}

${sources.length > 0
  ? '\nLet me know which area you\'d like me to dive deeper into.'
  : '\nCould you rephrase your question? I have 157+ files across 32 categories to search through.'}`;
    }

    return NextResponse.json({
      response: response || 'I encountered an issue generating a response. Please try again.',
      sources: sources.map((s) => ({
        title: s.title,
        source: s.source,
        category: s.category,
      })),
    });
  } catch (error) {
    console.error('Eli chat error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
