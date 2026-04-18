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

## Recommended Loop

1. Run `boundary` before touching an asset.
2. Use `intel` for CVE and tech stack intelligence.
3. Use `survey` to build a target map.
4. Use `probe` for one bug class or one feature at a time.
5. Use `screen` or `gate` before writing anything.
6. Use `pivot` only when the finding needs stronger impact.
7. Use `brief` after the evidence is real and reproducible.
8. Use `recall` to pull previous session data before resuming.

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

## Explicit Routing

- Start in [control-room](./roles/control-room.md) by default.
- Hand recon and attack-surface work to [surface-cartographer](./roles/surface-cartographer.md).
- Hand triage and validation work to [verdict-engine](./roles/verdict-engine.md).
- Hand exploit-chain work to [pivot-engine](./roles/pivot-engine.md).
- Hand report-writing work to [evidence-editor](./roles/evidence-editor.md) only after validation passes.
- Hand smart contract and DeFi work to [contract-cartographer](./roles/contract-cartographer.md).
- Do not keep specialist work in the default orchestrator when a matching specialist exists.

## Output Standard

- Lead with the best current surface, finding, or blocker.
- Prefer exact requests, responses, and exploit steps over general commentary.
- If proof is incomplete, name the missing check and stop there.
