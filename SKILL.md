---
name: beta-ops-router
description: Entry skill for the beta-ops repository. Routes work to the right track, playbook, and role based on whether the task is scope checking, recon, active hunting, validation, reporting, exploit chaining, or smart contract review.
---

# beta-ops Router

This file is the short entrypoint for the repository.

## Use The Narrowest Track That Fits

- `tracks/field-manual/SKILL.md` for end-to-end hunting
- `tracks/surface-mapping/SKILL.md` for recon
- `tracks/exploit-atlas/SKILL.md` for bug-class deep dives
- `tracks/payload-bank/SKILL.md` for payloads and bypasses
- `tracks/verdict-gate/SKILL.md` for validation
- `tracks/disclosure-lab/SKILL.md` for report writing
- `tracks/contract-review/SKILL.md` for smart contracts

## Workflow and Coordinator

Use [manual/workflow.md](./manual/workflow.md) for the canonical mission loop and routing.
Start with `roles/control-room.md` unless the task is already narrow enough for a specialist role.
