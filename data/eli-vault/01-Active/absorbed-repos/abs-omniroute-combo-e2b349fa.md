---
id: abs-omniroute-combo-e2b349fa
title: "OmniRoute Combo System — Unbreakable Multi-Model Fallback"
source: https://github.com/diegosouzapw/OmniRoute
category: omniroute
skillTags: ["fallback-pattern", "auto-rotation", "resilience", "circuit-breaker"]
createdAt: 2026-08-07T15:24:11.126Z
absorbedFrom: github-research
---

The OmniRoute Combo system is the flagship feature that makes the gateway unbreakable. A combo is a chain of models that OmniRoute routes across automatically.

## How Combos Work
1. User sets model to "auto" or specifies a combo name
2. OmniRoute tries the first model in the chain
3. If quota runs out → silently slides to next model
4. If provider fails → slides to next model
5. If costs spike → slides to next model
6. The user never sees a failure — the combo is transparent

## Technical Implementation
- Structured combo steps: provider + model + connection with runtime ordering by compositeTiers
- Account-level fallback: multiple accounts per provider
- Quota preflight: checks remaining quota BEFORE making the request
- Circuit breaker: if a provider fails repeatedly, it's temporarily removed from rotation
- Anti-thundering herd: mutex locking prevents cascading failures
- Context Relay: session handoff summaries for account rotation continuity
- Policy engine: centralized request evaluation (lockout → budget → fallback)
- Combo execution telemetry with p50/p95/p99 latency aggregation

## Mapping to Eli's Open Claw
- OmniRoute combo → Open Claw provider chain (guerrilla → mailtm → openinbox)
- Quota preflight → Inbox TTL check before use
- Circuit breaker → Provider error counting + temporary removal
- Anti-thundering herd → Mutex on email polling
- Context Relay → Key extraction callback chain
- The key insight: Eli's omni IS an OmniRoute-style combo, but for email/key generation instead of LLM inference.