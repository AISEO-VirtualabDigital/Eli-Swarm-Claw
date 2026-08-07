---
id: db4f7b1a1b0ed71c
source: "eli-obsidian-manual-rewiring.md"
"title: Eli-OS Manual Rewiring Policy"
category: obsidian
skillTags: ["process"]
containmentHash: 5988c60eb9269cb12d53
createdAt: 1786051353892
embeddingSig: "before:executing:newly|check:permissions:side|confirmation:before:executing|effect:policies:require|executing:newly:introduced|human:confirmation:before|introduced:destructive:paths|newly:introduced:destructive|permissions:side:effect|policies:require:human|require:human:confirmation|side:effect:policies"
---
e-check permissions and side-effect policies.
11. Require human confirmation before executing newly introduced destructive paths.
## Auto Mode Restrictions

Auto Mode may not silently:

- Reconnect removed edges
- Restore replaced providers
- Remove human approval nodes
- Remove validators
- Change protected destinations
- Bypass manual-only nodes
## REWIRING-LOG.md