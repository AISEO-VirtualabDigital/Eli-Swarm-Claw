# LLM Backend Abstraction

## Design Principle

Eli decouples its intelligence layer from any single LLM provider. A thin abstraction layer handles provider selection, request formatting, and fallback logic so the core application never needs to know which model is serving a given response.

## Primary Provider: Google Gemini 2.0 Flash

- **SDK:** `@google/generative-ai` (Google's official Node/Bun SDK)
- **Model:** Gemini 2.0 Flash — optimized for speed and cost-efficiency with strong instruction-following
- **Authentication:** API key passed via the `GEMINI_API_KEY` environment variable
- **Use case:** All production inference — chat completions, knowledge-grounded responses, strategy generation
- **Selection rationale:** Best price-to-performance ratio for a high-volume conversational AI that needs sub-second responses

## Fallback Provider: z-ai-web-dev-sdk

- **Scope:** Sandbox environment only — used during development and as a resilience fallback
- **Behavior:** Automatically invoked if the Gemini endpoint returns an error or times out
- **Role:** Ensures Eli never returns a blank response, even during provider outages

## Provider Switching Logic

```
Request → Try Gemini
  ├─ Success → Return response
  └─ Failure → Try z-ai-web-dev-sdk fallback
       ├─ Success → Return response (optionally log degradation)
       └─ Failure → Return graceful error message
```

The switch is transparent to the user. Degradation events are logged for monitoring.

## Future: Grok via chenyme/grok2api

Planned integration path (see [[Grok-Integration-Path]]):

- **Gateway:** chenyme/grok2api — an OpenAI-compatible API wrapper for Grok models
- **Models:** grok-4.5, grok-4.3, grok-chat
- **Deployment:** Docker container exposing an OpenAI-compatible endpoint on port 8000
- **Benefit:** Adds a third provider option with potentially different strengths (real-time knowledge, distinct reasoning style)
- **Integration effort:** Minimal — since grok2api exposes an OpenAI-compatible API, only a new adapter in the abstraction layer is needed

## Architecture Reference

The LLM layer fits into the broader system described in [[MicroSaaS-Architecture]]. Knowledge retrieval via the RAG pipeline feeds context into whichever LLM provider is active for that request cycle.
