# Pilot Control Panel Runner Wiring

## Summary

This document captures the wiring between the static subdomain pilot control panel and the Phase 6 local pilot runner contract.

## Current state

- The dashboard uses a small API client layer in the browser.
- A local mock adapter simulates the documented subdomain API contract.
- The UI updates health, status, audit, and pilot state from the mock adapter.

## Future direction

When the real Phase 6 runner-backed API exists, the mock adapter can be swapped for a thin client that calls the local pilot runner endpoints without changing the rest of the dashboard experience.
