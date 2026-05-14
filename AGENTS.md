# AGENTS.md — bountykit Control Surface

Use this repository as an operations pack, not as a monolithic skill dump.

## Read First

1. [workflow.md](./manual/workflow.md) — canonical loop, role routing, track routing, and playbook routing
2. [hunting.md](./guardrails/hunting.md) — scope and validation rules
3. [reporting.md](./guardrails/reporting.md) — disclosure constraints
4. [control-room](./roles/control-room.md) — default coordinator

## Routing Rule

Start from [manual/workflow.md](./manual/workflow.md). It is the source of truth for:

- core mission order
- optional utility playbooks
- specialist role handoff
- track selection

Do not duplicate routing locally. If a task is clearly recon, validation, chaining, reporting, or contracts, hand it to the matching role listed in the workflow.

## Output Standard

- Lead with the best current surface, finding, or blocker.
- Prefer exact requests, responses, and exploit steps over general commentary.
- If proof is incomplete, name the missing check and stop there.
