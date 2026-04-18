# AGENTS.md — beta-ops Control Surface

Use this repository as an operations pack, not as a monolithic skill dump.

## Read Order

1. [workflow.md](./manual/workflow.md)
2. [hunting.md](./guardrails/hunting.md)
3. [field-manual](./tracks/field-manual/SKILL.md) or the narrower track you need
4. A role brief from [roles](./roles)
5. A playbook from [playbooks](./playbooks) when execution starts

## Canonical Vocabulary

- `tracks/` are knowledge lanes
- `playbooks/` are procedures
- `roles/` are specialist briefs
- `guardrails/` are mandatory rules
- `manual/` is the cross-client operating guide

## Workflow and Routing

Use [manual/workflow.md](./manual/workflow.md) as the canonical mission-loop and routing reference.
Use `intel` when CVE or stack context matters, and use `recall` before resuming an older target.

## Track Selection

- [field-manual](./tracks/field-manual/SKILL.md) for end-to-end hunts
- [surface-mapping](./tracks/surface-mapping/SKILL.md) for recon
- [exploit-atlas](./tracks/exploit-atlas/SKILL.md) for class-specific testing
- [payload-bank](./tracks/payload-bank/SKILL.md) for payloads and bypasses
- [verdict-gate](./tracks/verdict-gate/SKILL.md) for validation
- [disclosure-lab](./tracks/disclosure-lab/SKILL.md) for report writing
- [contract-review](./tracks/contract-review/SKILL.md) for smart contracts

## Role Entry Points

- [control-room](./roles/control-room.md) is the default orchestrator
- [surface-cartographer](./roles/surface-cartographer.md) handles recon
- [verdict-engine](./roles/verdict-engine.md) handles finding decisions
- [evidence-editor](./roles/evidence-editor.md) handles write-ups
- [pivot-engine](./roles/pivot-engine.md) handles chaining
- [contract-cartographer](./roles/contract-cartographer.md) handles web3 review

## Output Standard

- Lead with the best current surface, finding, or blocker.
- Prefer exact requests, responses, and exploit steps over general commentary.
- If proof is incomplete, name the missing check and stop there.
