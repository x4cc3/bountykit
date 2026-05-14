---
description: Start a focused hunt on a target or feature and keep the work narrow enough to prove or kill quickly. Usage: /probe target.com [--vuln-class <class>]
---

# /probe

Run one disciplined hunting lane at a time.

## Canonical Sources

Use these as the authoritative hunting references:

- `../tracks/hunt/SKILL.md` (`hunt`) for the mission loop and hunting rules
- `../tracks/exploit/SKILL.md` for bug-class tactics, root causes, and chaining
- `../tracks/payloads/SKILL.md` for payloads and bypass ideas

This playbook is only the execution wrapper.

## Required Inputs

- target domain, feature, or endpoint
- scope context
- recon context if available

Optional:

- `--vuln-class idor|ssrf|xss|sqli|oauth|race|graphql|llm|upload|business-logic`
- source code access

## Execution Standard

1. confirm the target and feature are in scope
2. read the current recon or surface summary if it exists
3. choose one attack lane
4. load the matching canonical track content
5. test narrowly until the finding is proved, downgraded, chained, or killed
6. record exact requests, responses, and object/victim proof as you go

## Deliverable

Return:

1. the single lane being tested
2. the strongest current signal
3. the exact proof captured so far
4. the next best move: continue, pivot, gate, or rotate

## Stop Rules

Stop and rotate when:

- the lane needs too many preconditions
- responses stay flat after disciplined variation
- the signal depends on theory rather than proof
- you are spending time broadening instead of proving

## Handoff Rules

- move to `/screen` or `/gate` when a finding has real proof
- move to `/pivot` when bug A is confirmed and a defensible chain is now the best next step
- move to `/brief` only after validation survives
