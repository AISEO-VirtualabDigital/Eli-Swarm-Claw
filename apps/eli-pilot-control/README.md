# Eli Pilot Control

A lightweight, subdomain-ready pilot control panel for Eli.

## Open the static panel locally

Open the file [apps/eli-pilot-control/index.html](apps/eli-pilot-control/index.html) directly in a browser, or serve the folder with any simple static file server from the repository root.

## How the mock API adapter works

The panel uses [apps/eli-pilot-control/mock-api.js](apps/eli-pilot-control/mock-api.js) as a local adapter that simulates the documented endpoints from [apps/eli-pilot-control/API_CONTRACT.md](apps/eli-pilot-control/API_CONTRACT.md):

- GET /health
- GET /status
- POST /dry-run
- GET /audit-report
- GET /pilot-state

The adapter keeps the request and response shape inspectable and simple while staying fully dry-run only.

## How it will connect to the real local pilot runner later

The adapter contains TODO markers showing where the mock responses should be replaced with calls to the real Phase 6 local pilot runner contract. The future wiring should remain a thin client layer so the UI stays unchanged while the underlying implementation switches from mock data to a real local API.
