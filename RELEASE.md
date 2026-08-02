# Eli Pilot RC1 Release Candidate

## Release status

- Name: eli-pilot-rc1
- Status: release candidate documentation package
- Scope: pilot control panel, dry-run wiring, static deployment scaffold

## Summary

This release candidate packages the pilot-ready documentation and validation materials for the Eli control surface. It captures the completed dry-run-only foundation across the runtime, pilot runner contracts, mock control panel wiring, and subdomain deployment scaffold.

## Included work

- Boundary security and audit foundation
- Runtime handoff foundation
- Dry-run execution boundary
- Runtime observability and controller
- Pilot persistence state
- Local pilot runner contracts
- Pilot control panel foundation
- Mock pilot API wiring
- Static subdomain deployment scaffold

## Known limitations

- Static/mock UI only
- No real backend API service yet
- No live execution
- No auth layer on the subdomain yet
- No production persistence backend
- No deployment secrets

## Validation commands

Run from the Eli OS workspace:

```bash
cargo fmt --all
cargo check --workspace --all-features
cargo test --workspace --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

Also verify the static panel scripts:

```bash
node --check apps/eli-pilot-control/app.js
node --check apps/eli-pilot-control/mock-api.js
```
