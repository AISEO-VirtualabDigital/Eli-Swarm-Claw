import { NextRequest, NextResponse } from 'next/server';
import { getKnowledgeContext, buildKnowledgeMap } from '@/lib/knowledge-search';

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
- End with a clear next step or action item when applicable`;

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

    // Get knowledge map for background awareness
    let knowledgeMap = '';
    try {
      knowledgeMap = await buildKnowledgeMap();
    } catch {
      knowledgeMap = 'Knowledge map unavailable.';
    }

    // Build the full prompt with context
    const fullPrompt = `${ELI_SYSTEM_PROMPT}

---
BACKGROUND KNOWLEDGE MAP:
${knowledgeMap}
---

${context}

User's recent conversation:
${history.slice(-6).map((h) => `${h.role}: ${h.content}`).join('\n')}

User: ${message}

Eli:`;

    // Mock response — in production, this would call an LLM API
    const mockResponses: Record<string, { response: string }> = {
      default: {
        response: `I've analyzed your request against my knowledge base of 157+ files across 32 categories. Here's what I found:

${sources.length > 0
  ? `**Relevant sources found (${sources.length}):**\n${sources.map((s, i) => `${i + 1}. **${s.title}** — ${s.category}`).join('\n')}`
  : 'No directly matching sources found, but I can still help based on my broader knowledge.'}

**My recommendation:**
- Review the matched knowledge sources above for detailed strategies
- I can help you implement any of these approaches
- Want me to dive deeper into any specific area?

What would you like to explore next?`,
      },
    };

    const response = mockResponses.default.response;

    return NextResponse.json({
      response,
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
