---
absorbedFrom: https://github.com/Felix-au/OmniKey-AI-Unified-Key-Manager
absorbedAt: 2026-08-08
chunkType: architecture-pattern
tags: [omnikey, key-management, provider-registry, penalty-system, round-robin, circuit-breaker, zod-validation, gemini-proxy, openai-compat]
---

# OmniKey AI — Unified Key Manager Architecture

## Core Concept
OmniKey wraps **17 free-tier LLM providers** (Gemini, Groq, Cerebras, SambaNova, OpenRouter, GitHub Models, Mistral, NVIDIA, Cohere, Cloudflare, Zhipu, Ollama Cloud, Kilo, Pollinations, LLM7, HuggingFace, OpenCode) into two unified endpoints:
- `/v1` — OpenAI-compatible (chat completions, vision, transcription, TTS, image generation)
- `/v1beta` — Gemini-compatible (generateContent, streamGenerateContent, generateImages)

Users get twin unified master keys (`omnikey-` for OpenAI format, `omnikey-g-` for Gemini format) and project-scoped sub-keys.

## Pattern 1: Parametric Provider Registration
One `OpenAICompatProvider` class serves 14+ providers by accepting `baseUrl` + `extraHeaders` in the constructor. Custom providers (Google, Cohere, Cloudflare) only register when they need fundamentally different request/response translation.

```typescript
register(new OpenAICompatProvider({ platform: 'groq', name: 'Groq', baseUrl: 'https://api.groq.com/openai/v1' }));
register(new OpenAICompatProvider({ platform: 'cerebras', name: 'Cerebras', baseUrl: 'https://api.cerebras.ai/v1' }));
register(new GoogleProvider()); // Custom Gemini adapter
```

**Absorb into Eli**: Extend Omni Route's SERVICES config to use a provider registry pattern. Instead of hardcoded services object, use a Map<Platform, ProviderConfig> that can be dynamically extended.

## Pattern 2: Dynamic Priority Penalty System
Instead of static priority, the router maintains a penalty score per model:
- 429 hits: +3 penalty (max 10)
- Success: -1 penalty
- Time decay: -1 every 2 minutes
- Self-healing routing that avoids flaky providers without manual intervention

```typescript
export function recordRateLimitHit(modelDbId) {
  entry.penalty = Math.min(entry.penalty + 3, 10);
}
export function recordSuccess(modelDbId) {
  entry.penalty = Math.max(0, entry.penalty - 1);
}
```

**Absorb into Eli**: Add penalty scoring to Omni Route's provider selection. When Guerrilla Mail fails, increase its penalty so mail.tm is tried first next time.

## Pattern 3: Round-Robin Key Selection
When multiple keys exist for the same platform+model, `roundRobinIndex` cycles through them. Combined with cooldown windows (429 → 60s cooldown), this prevents any single key from bearing all traffic.

**Absorb into Eli**: Add round-robin to Omni Route when multiple active inboxes exist.

## Pattern 4: AES-256-GCM Envelope Encryption
Keys stored as 3 columns: `encrypted_key`, `iv`, `auth_tag`. Key init priority: env var → SQLite settings table → auto-generate. Duplicate detection by decrypting ALL keys and comparing.

**Absorb into Eli**: Future — when Eli gets persistent key storage, use envelope encryption instead of plaintext env vars.

## Pattern 5: Key Health Checking
Every 5 minutes, validate keys against providers. Auto-disable after 3 consecutive failures. `ConsecutiveFailuresToDisable = 3`.

**Absorb into Eli**: Add periodic key validation to Omni Route's checkAndRotate loop.

## Pattern 6: Gemini-OpenAI Bidirectional Translation
Full translation layer: Gemini `contents`/`systemInstruction`/`generationConfig` ↔ OpenAI `ChatMessage[]`. The proxy accepts native Gemini SDK payloads, converts internally, routes through the same engine, then translates response back.

**Absorb into Eli**: Eli's air-llm already uses Gemini SDK directly. This pattern is a reference for if we ever need multi-provider chat proxying.

## Pattern 7: Timing-Safe Key Comparison
Uses `crypto.timingSafeEqual` for API key authentication to prevent timing attacks.

## Pattern 8: Zod Schema Validation with Discriminated Unions
Chat completion validation uses `z.union([systemMessageSchema, userMessageSchema, ...])` for per-role validation before hitting providers.

## Pattern 9: AsyncLocalStorage for Per-Request DB Context
`AsyncLocalStorage` makes `isLocalDbEnabled()` context-aware without parameter threading. Supports both SQLite (local) and MongoDB (cloud) simultaneously.

## Pattern 10: Sticky Sessions for Multi-Turn
SHA-1 hash of first user message → 30-min TTL sticky routing to same model. Prevents model-switching mid-conversation.

**Absorb into Eli**: Apply sticky session pattern to Eli's chat so the same LLM provider handles the whole conversation.