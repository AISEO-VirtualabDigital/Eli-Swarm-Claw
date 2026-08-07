---
id: absorbed-omnikey-20250808
source: https://github.com/Felix-au/OmniKey-AI-Unified-Key-Manager
title: OmniKey AI — Key Management Patterns
category: ai-agent
skillTags: ["pattern", "code", "tool"]
containmentHash: sha256-absorbed-omnikey
embeddingSig: trigram:penalty:fallback:provider
---

# OmniKey AI — Absorbed Patterns

## 1. Dynamic Penalty Tracker with Decay
- PENALTY_PER_429 = +3, MAX_PENALTY = 10
- Time-based decay: -1 every 2 minutes
- Successful requests: -1 penalty
- Fallback chain re-sorted on every request by effectivePriority = base_priority + penalty

→ WIRED into: omni-route.ts PenaltyTracker class

## 2. Sticky Sessions
- SHA-1(first_user_message):message_count → model affinity, 30min TTL
- Promotes previously-used model to top of chain
- LRU eviction at 500 entries

→ NOT YET WIRED (future: chat session stickiness)

## 3. Round-Robin Key Selection
- Per platform:modelId rotating index
- skipKeys set accumulates failed keys across retries

→ WIRED into: open-claw.ts roundRobinIdx + omni-route.ts skipProviders

## 4. Provider Adapter (Strategy Pattern)
- BaseProvider abstract class + OpenAICompatProvider generic adapter
- Registry via Map<Platform, BaseProvider>
- 80%+ providers covered by generic adapter with config only

→ WIRED into: open-claw.ts getBestProvider(skipProviders) overload

## 5. Response Decision Headers
- X-Routed-Via: platform/modelId
- X-Key-Used: Key #id or label
- X-Fallback-Attempts: N

→ WIRED into: eli-chat route headers via getDecisionHeaders()

## 6. Retryable Error Classification
- 429, 500, 503, timeout, connection refused, payload too large, 404
- Non-retryable: 401, 400, malformed responses
- Mid-stream errors: send error chunk + [DONE], no retry

→ WIRED into: omni-route.ts isRetryableError() + open-claw.ts _clawRetryable flag

## 7. Fallback Chain
- MAX_RETRIES = 20, iterates through providers
- On retryable error: record penalty, add to skip set, try next
- On non-retryable: stop immediately

→ WIRED into: omni-route.ts rotate() with maxAttempts loop

## 8. Key Validation
- Hits provider /models endpoint, checks for 401/403
- Transport errors (DNS/timeout) do NOT mark keys invalid
- timingSafeStringEqual for key comparison

→ PARTIALLY WIRED: omni-route.ts hasValidKey() uses regex (weaker than endpoint check)
