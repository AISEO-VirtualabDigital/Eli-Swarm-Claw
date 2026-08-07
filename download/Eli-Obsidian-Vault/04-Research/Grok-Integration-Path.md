# Grok Integration Path

Research findings on integrating xAI's Grok models into Eli's LLM backend. See [[LLM-Backend]] for the current provider architecture.

## Grok Model Landscape

### grok-1 (xai-org/grok-1)
- **Architecture:** 314B parameter Mixture of Experts (MoE) model
- **Deployment requirement:** ~640GB VRAM for full inference
- **Practicality:** Not viable for a single-VPS deployment. Requires multi-GPU or cloud GPU infrastructure at significant cost. No practical path for Eli's current architecture.
- **Verdict:** Reference only. Not a deployment candidate.

### grok2api (chenyme/grok2api)
- **What it is:** An OpenAI-compatible API gateway that proxies requests to Grok models
- **Stack:** Go backend + React admin UI
- **Deployment:** Docker container, exposes endpoint on port 8000
- **Supported models:** grok-4.5, grok-4.3, grok-chat
- **API compatibility:** Implements OpenAI's chat completions format (`/v1/chat/completions`)
- **Authentication:** Configured via environment variable (API key passthrough)
- **Repository:** Fork maintained by chenyme, actively developed

### grok-build (xai-org/grok-build)
- **What it is:** A Rust-based TUI coding agent powered by Grok models
- **Purpose:** Interactive coding assistant, not an API server
- **Relevance:** Not applicable to Eli's use case. It's an end-user tool, not a backend service.
- **Verdict:** No integration path.

## Recommended Path: chenyme/grok2api via Docker

This is the clear integration choice:

1. **Deploy** grok2api as a Docker container alongside Eli on the same VPS or a nearby instance
2. **Configure** Eli's LLM abstraction layer with a new adapter that sends OpenAI-format requests to `localhost:8000`
3. **Add** Grok as a third provider option (primary: Gemini, secondary: z-ai-web-dev-sdk, tertiary: Grok) or replace the existing fallback
4. **Route strategically** — use Grok for tasks where its real-time knowledge or distinct reasoning style provides an advantage

## Integration Effort

- **New adapter code:** ~50-80 lines (OpenAI-compatible format is well-documented)
- **Docker setup:** Standard `docker run` with env vars for API key and model selection
- **Testing:** Verify response format compatibility, latency, and error handling
- **Monitoring:** Add provider-specific logging to track Grok's success rate and latency vs. Gemini

## Risk Considerations

- grok2api is a third-party proxy — depends on the maintainer keeping pace with xAI API changes
- xAI's API pricing and rate limits may differ significantly from Gemini's
- Grok's knowledge cutoff and behavior differ from Gemini — response quality may vary by domain