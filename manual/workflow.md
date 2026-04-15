# beta-ops Workflow

This repository uses a control-room model:

1. `boundary`
2. `survey`
3. `probe`
4. `screen`
5. `gate`
6. `pivot`
7. `brief`

For unattended runs, use [manual/autonomous-operations.md](../manual/autonomous-operations.md). It wraps the same loop in explicit scope checks, state tracking, and stop decisions.

## Routing

- [playbooks/boundary.md](../playbooks/boundary.md) for scope checks
- [playbooks/survey.md](../playbooks/survey.md) for recon
- [playbooks/probe.md](../playbooks/probe.md) for active testing
- [playbooks/screen.md](../playbooks/screen.md) for fast triage
- [playbooks/gate.md](../playbooks/gate.md) for full validation
- [playbooks/pivot.md](../playbooks/pivot.md) for chaining
- [playbooks/brief.md](../playbooks/brief.md) for final write-up
- [playbooks/contract-sweep.md](../playbooks/contract-sweep.md) for smart contracts

## Role Routing

- [roles/control-room.md](../roles/control-room.md) as the default driver
- [roles/surface-cartographer.md](../roles/surface-cartographer.md) for mapping
- [roles/verdict-engine.md](../roles/verdict-engine.md) for decisions
- [roles/evidence-editor.md](../roles/evidence-editor.md) for write-ups
- [roles/pivot-engine.md](../roles/pivot-engine.md) for escalation
- [roles/contract-cartographer.md](../roles/contract-cartographer.md) for DeFi work

## Track Routing

- [tracks/field-manual/SKILL.md](../tracks/field-manual/SKILL.md)
- [tracks/surface-mapping/SKILL.md](../tracks/surface-mapping/SKILL.md)
- [tracks/exploit-atlas/SKILL.md](../tracks/exploit-atlas/SKILL.md)
- [tracks/payload-bank/SKILL.md](../tracks/payload-bank/SKILL.md)
- [tracks/verdict-gate/SKILL.md](../tracks/verdict-gate/SKILL.md)
- [tracks/disclosure-lab/SKILL.md](../tracks/disclosure-lab/SKILL.md)
- [tracks/contract-review/SKILL.md](../tracks/contract-review/SKILL.md)

## Stop Conditions

- Out of scope
- No real exploit path
- Only theoretical impact remains
- The surface stays cold after a short disciplined pass
