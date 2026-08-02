# Eli Pilot Control

A lightweight, subdomain-ready pilot control panel for Eli.

## Open the static panel locally

Open the file [apps/eli-pilot-control/index.html](apps/eli-pilot-control/index.html) directly in a browser, or serve the folder with any simple static file server from the repository root.

For a minimal local preview, run:

```bash
python3 apps/eli-pilot-control/static-server.py
```

Then open http://127.0.0.1:8080.

## Static deployment scaffold

This folder now includes placeholder-only deployment files for a future subdomain:

- [.env.example](.env.example) for placeholder domain and API settings
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for the deployment checklist
- [nginx-subdomain.conf](nginx-subdomain.conf) as a reverse-proxy template
- [static-server.py](static-server.py) for simple local previewing

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
