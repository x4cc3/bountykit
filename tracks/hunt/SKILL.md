---
name: hunt
description: End-to-end bug bounty hunt loop. Use for full mission context when the task spans scope, recon, probing, validation, and reporting.
---

# HUNT

Use this as the full-loop coordinator, not as a payload list, scanner wrapper, or bug-class dump.

If the task is already narrow, load the smaller track instead:

- `../surface/SKILL.md` for recon and surface ranking
- `../exploit/SKILL.md` for bug-class tactics and root causes
- `../payloads/SKILL.md` for payloads and bypasses
- `../verdict/SKILL.md` for validation and evidence thresholds
- `../disclosure/SKILL.md` for report writing
- `../contracts/SKILL.md` for smart contracts

Canonical loop: `boundary` → `survey` → `probe` → `screen` → `gate` → `pivot` → `brief` from `../../manual/workflow.md`. Run commands through Disposable CLI/tools or approved workspace tooling.

## Hard Rules

1. Read full scope first.
2. No theoretical bugs.
3. One bug class at a time.
4. Validate before writing.
5. Rotate when the surface stays cold.
6. After bug A, check sibling endpoints before leaving the area.
7. Treat tool output as leads, not proof.

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
| Recon and prioritization | `surface` |
| IDOR, SSRF, XSS, OAuth, race, upload, GraphQL, AI classes | `exploit` |
| Payloads and bypass variants | `payloads` |
| Evidence threshold and PASS/KILL decision | `verdict` |
| Final report wording and CVSS framing | `disclosure` |
| Solidity/DeFi review | `contracts` |

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
5. next action: continue, screen, pivot, gate, brief, or rotate
