# Phase 6 — Local Pilot Runner Contracts

## Summary

Phase 6 adds a dry-run-only local pilot runner API surface to the Eli-OS runtime foundation. The implementation stays in-process and does not execute live work; it only routes approved or blocked dry-run submissions through the existing runtime controller, audit sink, and pilot persistence abstractions.

## Added runtime contracts

- Pilot health and status response models
- Pilot dry-run submission model
- Pilot command result model
- Local pilot runner wrapper over the existing controller and persistence store

## Safety posture

- No live shell execution
- No networked server layer
- No external dependencies
- No execution outside the approved dry-run boundary

## Verification

The implementation was validated with:

- cargo test --workspace --all-features
