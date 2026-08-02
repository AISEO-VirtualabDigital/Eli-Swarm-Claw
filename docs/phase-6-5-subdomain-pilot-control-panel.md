# Phase 6.5 — Subdomain Pilot Control Panel Foundation

## Summary

Phase 6.5 adds a lightweight pilot control surface for Eli so the system can be operated from a future subdomain experience such as app.<domain> or eli.<domain>.

## Included deliverables

- A simple in-repo pilot control app under apps/eli-pilot-control
- A static dashboard with health, command submission, approval controls, results, audit, and state summaries
- Placeholder API contract documentation for a future backend
- Placeholder deployment notes for a subdomain deployment

## Safety posture

- No live shell execution
- No Python execution
- No browser automation
- No autonomous loops
- No production secrets
- No real domains hardcoded
- All interactions remain dry-run only

## Future connection point

This UI is designed to connect to the Phase 6 local pilot runner later via a future subdomain backend. The first version stays self-contained and mock-backed so the subdomain experience can evolve without changing the underlying runtime safety posture.
