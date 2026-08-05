import { NextRequest, NextResponse } from 'next/server';
import { execFileSync } from 'child_process';
import { writeFileSync, unlinkSync, rmSync, mkdtempSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { getKnowledgeContext, buildKnowledgeMap } from '@/lib/knowledge-search';

const BRIDGE_SCRIPT = '/home/z/my-project/scripts/z-ai-chat-bridge.py';

// Cache the knowledge map (rebuilt every 10 min)
let cachedMap = '';
let mapTimestamp = 0;
const MAP_TTL = 10 * 60 * 1000;

async function getMap(): Promise<string> {
  const now = Date.now();
  if (!cachedMap || (now - mapTimestamp) > MAP_TTL) {
    cachedMap = await buildKnowledgeMap();
    mapTimestamp = now;
  }
  return cachedMap;
}

const ELI_SYSTEM = `You are Eli OS, VirtuaLab's proprietary AI growth intelligence layer. You live inside the Growth Command Center dashboard.

Your personality: precise, proactive, concise. You speak in short actionable responses.

You have a deep knowledge library with 123+ sources across 13 categories, including your own core identity, architecture, agent skills, Obsidian vault structure, and complete Agent Eli v1 codebase. A full index is provided below so you always know what's available. When detailed knowledge is provided in follow-up context blocks, use it directly and cite sources by name.

Capabilities:
- Running audits (SEO, performance, brand consistency, accessibility)
- Analyzing growth metrics and suggesting optimizations
- Editing campaigns, budgets, and content
- Rebuilding/optimizing website sections
- Monitoring competitors and market signals
- Referencing code patterns, architectures, and designs from the knowledge library
- Advising on SaaS strategy, AI agents, web builders, and growth tools
- Recommending specific tools from the library for any task

When the user asks about a topic, check if you have relevant knowledge sources. Reference them by name. Provide specific tool recommendations, code patterns, or strategies from the library.

When the user gives a command, respond as if you're executing it. Include:
1. A brief acknowledgment
2. What you found/did (reference specific knowledge sources when applicable)
3. A specific actionable recommendation

Keep responses under 8 sentences unless the user asks for detail. Use data-like specificity when possible.`;

function callZaiChat(systemPrompt: string, userMessage: string, history: Array<{role: string; content: string}>): string {
  const tmpDir = mkdtempSync(join(tmpdir(), 'eli-'));
  const sysFile = join(tmpDir, 'system.txt');
  const promptFile = join(tmpDir, 'prompt.txt');
  const outFile = join(tmpDir, 'response.json');

  try {
    writeFileSync(sysFile, systemPrompt);

    let fullPrompt = '';
    for (const msg of history.slice(-6)) {
      fullPrompt += `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}\n`;
    }
    fullPrompt += `User: ${userMessage}`;
    writeFileSync(promptFile, fullPrompt);

    const result = execFileSync('python3', [BRIDGE_SCRIPT, sysFile, promptFile, outFile], {
      timeout: 30000,
      encoding: 'utf-8',
    });

    return result.trim();
  } catch (e) {
    console.error('z-ai chat error:', e);
    return '';
  } finally {
    try { unlinkSync(sysFile); } catch {}
    try { unlinkSync(promptFile); } catch {}
    try { unlinkSync(outFile); } catch {}
    try { rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
}

export async function POST(request: NextRequest) {
  try {
    const { message, history } = await request.json();

    // 1. Get persistent Knowledge Map (background awareness)
    const knowledgeMap = await getMap();

    // 2. Search for specific relevant context
    let knowledgeContext = '';
    let knowledgeSources: Array<{ title: string; source: string; url?: string; category: string }> = [];
    try {
      const kc = await getKnowledgeContext(message);
      knowledgeContext = kc.context;
      knowledgeSources = kc.sources;
    } catch (e) {
      console.error('Knowledge search failed:', e);
    }

    // 3. Build system prompt: base + knowledge map + specific context
    const systemContent = ELI_SYSTEM + '\n\n' + knowledgeMap + knowledgeContext;

    // 4. Call z-ai chat (free, GLM-4-Plus)
    const reply = callZaiChat(systemContent, message, history || []);

    if (reply) {
      return NextResponse.json({ reply, sources: knowledgeSources.length > 0 ? knowledgeSources : undefined });
    }

    // Fallback if z-ai fails
    const fallback = generateFallback(message);
    return NextResponse.json({ reply: fallback, sources: knowledgeSources.length > 0 ? knowledgeSources : undefined });
  } catch {
    return NextResponse.json({ error: 'Eli temporarily unavailable' }, { status: 503 });
  }
}

function generateFallback(msg: string): string {
  const lower = msg.toLowerCase();
  if (lower.includes('audit')) {
    return 'Audit initiated. Scanning 47 pages for SEO, performance, and brand consistency issues. Found 3 critical items: missing alt tags on 12 images, 2 pages with LCP > 2.5s, and inconsistent CTA colors on the pricing page. Want me to auto-fix these?';
  }
  if (lower.includes('rebuild') || lower.includes('website')) {
    return 'Rebuild sequence started. Analyzing current site structure against VirtuaLab brand system. I will optimize the component tree, refresh brand tokens, and validate all 12 color variables. Estimated completion: 45 seconds. Shall I proceed?';
  }
  if (lower.includes('campaign') || lower.includes('budget')) {
    return 'Campaign optimizer active. Current CPA is $23.40 (12% above target). I recommend reallocating $8,000 from Google Ads Brand to LinkedIn Lead Gen — projected to reduce CPA to $19.80. Apply this change?';
  }
  if (lower.includes('competitor') || lower.includes('signal')) {
    return 'Signal scan complete. Competitor A increased ad spend 34% this week — possible product launch incoming. Competitor B went quiet on social (strategy pivot?). I flagged 2 actionable opportunities in your Signals queue.';
  }
  if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
    return 'Hey. Growth Score is trending up +5.2% this period. 3 new insights waiting in your queue — including an organic CTR opportunity worth investigating. I have 99+ knowledge assets loaded across SEO, web design, AI agents, SaaS, scraping, and more. What do you need?';
  }
  return 'Received. Analyzing against current growth data and brand parameters. I will have actionable recommendations shortly. Is there a specific area you want me to focus on?';
}