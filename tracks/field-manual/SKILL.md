---
name: hunt
description: End-to-end bug bounty hunt loop. Use for full mission context when the task spans scope, recon, probing, validation, and reporting.
---

# HUNT

Use this as the full-loop coordinator, not as the payload or bug-class dump.

If the task is already narrow, load the smaller track instead:

- `../surface-mapping/SKILL.md` for recon and surface ranking
- `../exploit-atlas/SKILL.md` for bug-class tactics and root causes
- `../payload-bank/SKILL.md` for payloads and bypasses
- `../verdict-gate/SKILL.md` for validation and evidence thresholds
- `../disclosure-lab/SKILL.md` for report writing
- `../contract-review/SKILL.md` for smart contracts

Canonical loop: `boundary` → `survey` → `probe` → `screen` → `gate` → `pivot` → `brief` from `../../manual/workflow.md`.

## Hard Rules

1. Read full scope first.
2. No theoretical bugs.
3. One bug class at a time.
4. Validate before writing.
5. Rotate when the surface stays cold.
6. After bug A, check sibling endpoints before leaving the area.

## Use This Skill To

- choose the next hunting lane
- keep work narrow and evidence-first
- decide whether to continue, pivot, validate, or rotate
- route to the right specialized track

## Default Execution

1. `boundary` — confirm the asset, ownership, and program rules
2. `survey` — map the target and pick the highest-value surface
3. `probe` — test one feature or bug class at a time
4. `screen` — kill weak findings quickly
5. `gate` — require exact requests, responses, victim/object proof, and impact
6. `pivot` — test only the top 1–2 realistic chain partners
7. `brief` — write only after the finding survives validation

## Routing

| Need | Load |
|---|---|
| Recon and prioritization | `surface-mapping` |
| IDOR, SSRF, XSS, OAuth, race, upload, GraphQL, AI classes | `exploit-atlas` |
| Payloads and bypass variants | `payload-bank` |
| Evidence threshold and PASS/KILL decision | `verdict-gate` |
| Final report wording and CVSS framing | `disclosure-lab` |
| Solidity/DeFi review | `contract-review` |

## Kill Signals

- out of scope
- only theoretical impact remains
- too many attacker preconditions
- duplicate is likely and you have no differentiator
- the surface stays cold after a short disciplined pass

## Output

Return:

1. current target or feature
2. current lane
3. strongest signal or proof
4. missing proof, if any
5. next action: continue, pivot, gate, brief, or rotate
