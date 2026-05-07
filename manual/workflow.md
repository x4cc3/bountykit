# bountykit Workflow

This is the canonical mission-loop, playbook-order, role-routing, and track-routing reference for bountykit.

## Core Loop

1. `boundary` — confirm scope before touching an asset
2. `survey` — map the target surface
3. `probe` — test one feature or bug class at a time
4. `screen` — fast triage before deeper validation
5. `gate` — full validation and reportability decision
6. `pivot` — strengthen impact only when the evidence supports it
7. `brief` — write the submission-ready report

For unattended scoped runs, use [manual/autonomous-operations.md](../manual/autonomous-operations.md). It wraps the same loop in explicit scope checks, state tracking, and stop decisions.

## Playbook Routing

| Need | Playbook |
|---|---|
| Scope check | [boundary](../playbooks/boundary.md) |
| Recon and surface map | [survey](../playbooks/survey.md) |
| Focused active test | [probe](../playbooks/probe.md) |
| Fast triage | [screen](../playbooks/screen.md) |
| Full validation | [gate](../playbooks/gate.md) |
| Impact escalation | [pivot](../playbooks/pivot.md) |
| Final write-up | [brief](../playbooks/brief.md) |
| Scoped autonomous run | [mission](../playbooks/mission.md) |

Optional utilities:

| Need | Playbook |
|---|---|
| CVE and disclosure intelligence | [intel](../playbooks/intel.md) |
| Resume previous context | [pickup](../playbooks/pickup.md) |
| Recall hunt memory | [recall](../playbooks/recall.md) |
| CI/CD security checks | [cicd-scan](../playbooks/cicd-scan.md) |
| Smart contract lane | [contract-sweep](../playbooks/contract-sweep.md) |

## Role Routing

| Work type | Role |
|---|---|
| Default coordination | [control-room](../roles/control-room.md) |
| Recon and attack-surface ranking | [surface-cartographer](../roles/surface-cartographer.md) |
| Triage and validation decisions | [verdict-engine](../roles/verdict-engine.md) |
| Chain development | [pivot-engine](../roles/pivot-engine.md) |
| Report writing | [evidence-editor](../roles/evidence-editor.md) |
| Smart contract and DeFi review | [contract-cartographer](../roles/contract-cartographer.md) |

## Track Routing

| Need | Track |
|---|---|
| End-to-end hunting doctrine | [hunt](../tracks/field-manual/SKILL.md) |
| Recon and surface mapping | [surface-mapping](../tracks/surface-mapping/SKILL.md) |
| Bug-class tactics | [exploit-atlas](../tracks/exploit-atlas/SKILL.md) |
| Payloads and bypasses | [payload-bank](../tracks/payload-bank/SKILL.md) |
| Validation doctrine | [verdict-gate](../tracks/verdict-gate/SKILL.md) |
| Disclosure writing | [disclosure-lab](../tracks/disclosure-lab/SKILL.md) |
| Smart contract review | [contract-review](../tracks/contract-review/SKILL.md) |

## Stop Conditions

- Out of scope
- No real exploit path
- Only theoretical impact remains
- The surface stays cold after a short disciplined pass
