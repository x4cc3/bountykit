---
description: Write a submission-ready bug bounty report. Run /gate first. Usage: /brief
---

# /brief

Generate a submission-ready report. All 4 gates from `/gate` must pass first.

## Canonical Source

Report template, writing rules, CVSS guidance, and checklist live in `../tracks/disclosure/SKILL.md`. This playbook is the execution wrapper.

## Input Required

- Platform (HackerOne / Bugcrowd / Intigriti / Immunefi)
- Bug class, affected endpoint
- Two test accounts + IDs
- Exact request + response demonstrating the bug

## Execution

1. Load `../tracks/disclosure/SKILL.md`
2. Generate title using formula: `[BugClass] in [Feature] allows [attacker] to [impact] via [vector]`
3. Fill universal report template with exact evidence
4. Calculate CVSS (use verdict quick ref)
5. Write concrete remediation (code-level if possible)
6. Run 60-second pre-submit checklist

## Escalation Language (if payout downgraded)

- "Requires only a free account — no special privileges."
- "Exposed data includes [PII type], subject to GDPR/CCPA."
- "Attacker can automate: all [N] records in [X] minutes."
- "Exploitable externally without internal network access."
