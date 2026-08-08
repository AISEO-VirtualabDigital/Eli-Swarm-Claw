/**
 * Air LLM — Multi-provider fallback for when Gemini is blocked/unavailable.
 *
 * Provider order:
 *   1. Groq  (free, fast, global — needs GROQ_API_KEY)
 *   2. OpenRouter (free tier — needs OPENROUTER_API_KEY)
 *   3. Z-AI SDK  (built-in, always available)
 */

// ─── Types ──────────────────────────────────────────────────────

type ChatMessage = { role: string; content: string };

interface ProviderResult {
  provider: string;
  available: boolean;
}

// ─── Provider 1: Groq ──────────────────────────────────────────

async function callGroq(messages: ChatMessage[]): Promise<string> {
  const key = process.env.GROQ_API_KEY;
  if (!key) throw new Error('GROQ_API_KEY not set');

  const systemMsg = messages.find(m => m.role === 'system');
  const chatMessages = messages
    .filter(m => m.role !== 'system')
    .map(m => ({ role: m.role, content: m.content }));

  const body: Record<string, unknown> = {
    model: 'llama-3.3-70b-versatile',
    messages: chatMessages,
    temperature: 0.8,
    max_tokens: 2048,
  };
  if (systemMsg) {
    body.messages = [{ role: 'system', content: systemMsg.content }, ...chatMessages];
  }

  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${key}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errBody = await res.text();
    throw new Error(`Groq HTTP ${res.status}: ${errBody.slice(0, 200)}`);
  }

  const data = await res.json();
  const text = data?.choices?.[0]?.message?.content;
  if (!text) throw new Error('Empty response from Groq');
  return text;
}

// ─── Provider 2: OpenRouter ─────────────────────────────────────

async function callOpenRouter(messages: ChatMessage[]): Promise<string> {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error('OPENROUTER_API_KEY not set');

  const systemMsg = messages.find(m => m.role === 'system');
  const chatMessages = messages
    .filter(m => m.role !== 'system')
    .map(m => ({ role: m.role, content: m.content }));

  const body: Record<string, unknown> = {
    model: 'meta-llama/llama-3.3-70b-instruct:free',
    messages: chatMessages,
    temperature: 0.8,
    max_tokens: 2048,
  };
  if (systemMsg) {
    body.messages = [{ role: 'system', content: systemMsg.content }, ...chatMessages];
  }

  const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${key}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errBody = await res.text();
    throw new Error(`OpenRouter HTTP ${res.status}: ${errBody.slice(0, 200)}`);
  }

  const data = await res.json();
  const text = data?.choices?.[0]?.message?.content;
  if (!text) throw new Error('Empty response from OpenRouter');
  return text;
}

// ─── Provider 3: Z-AI SDK (built-in, always available) ─────────

async function callZAI(messages: ChatMessage[]): Promise<string> {
  const systemMsg = messages.find(m => m.role === 'system');
  const chatMessages = messages
    .filter(m => m.role !== 'system')
    .map(m => ({ role: m.role as 'user' | 'assistant', content: m.content }));

  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const ZAI = (await import('z-ai-web-dev-sdk')).default;
    const zai = await ZAI.create();

    const completion = await zai.chat.completions.create({
      messages: [
        ...(systemMsg ? [{ role: 'system' as const, content: systemMsg.content }] : []),
        ...chatMessages,
      ],
    });

    const text = completion?.choices?.[0]?.message?.content;
    if (!text) throw new Error('Empty response from Z-AI SDK');
    return text;
  } catch (err) {
    throw new Error(`Z-AI SDK failed: ${(err as Error).message || err}`);
  }
}

// ─── Main entry point ──────────────────────────────────────────

/**
 * Try each Air LLM provider in sequence; return the first successful response.
 * Throws if every provider fails.
 */
export async function callAirLLM(messages: ChatMessage[]): Promise<string> {
  const providers = [
    { name: 'groq', fn: callGroq },
    { name: 'openrouter', fn: callOpenRouter },
    { name: 'z-ai-sdk', fn: callZAI },
  ];

  const errors: Array<{ provider: string; error: string }> = [];

  for (const { name, fn } of providers) {
    try {
      console.log(`[AIR-LLM] Trying provider: ${name}`);
      const result = await fn(messages);
      console.log(`[AIR-LLM] ✓ ${name} succeeded (${result.length} chars)`);
      return result;
    } catch (err: unknown) {
      const msg = (err as Error).message || String(err);
      console.warn(`[AIR-LLM] ✗ ${name} failed: ${msg}`);
      errors.push({ provider: name, error: msg });
    }
  }

  const summary = errors.map(e => `  ${e.provider}: ${e.error}`).join('\n');
  throw new Error(`All Air LLM providers failed:\n${summary}`);
}

// ─── Diagnostics ───────────────────────────────────────────────

/**
 * Returns the name of the highest-priority provider that is configured.
 */
export function getAirLLMProvider(): string {
  if (process.env.GROQ_API_KEY) return 'groq';
  if (process.env.OPENROUTER_API_KEY) return 'openrouter';
  return 'z-ai-sdk';
}

/**
 * Returns availability info for each provider.
 */
export function getAirLLMStats(): Array<ProviderResult> {
  return [
    { provider: 'groq', available: !!process.env.GROQ_API_KEY },
    { provider: 'openrouter', available: !!process.env.OPENROUTER_API_KEY },
    { provider: 'z-ai-sdk', available: true },
  ];
}
