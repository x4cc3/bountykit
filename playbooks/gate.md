---
description: Validate a finding — 7-Question Gate, evidence pack, confidence scoring, 4-gate checklist. Usage: /gate
---

# /gate

Full validation before report writing. Kills weak findings. Prevents N/A submissions.

## Canonical Source

All validation logic lives in `../tracks/verdict/SKILL.md` and `../tracks/verdict/references/proof-matrix.md`. This playbook is the execution wrapper.

## Execution

1. Run 7-Question Gate — one wrong answer = KILL
2. Check required evidence pack (all 6 items)
3. Check never-submit list — if listed, require proved chain
4. Run 4 pre-submission gates (Gate 0→3)
5. Load `../tracks/verdict/references/proof-matrix.md` for class-specific proof before final PASS

## Input Required

- Endpoint, bug class, exact request + response
- Scope proof, victim/target proof, negative control

## Rules

- Never PASS at LOW confidence
- Missing scope/victim/request proof = no PASS
- Incomplete proof-matrix row = no PASS

## Output
```
DECISION: [PASS / KILL Q# / DOWNGRADE / CHAIN REQUIRED]
CONFIDENCE: [HIGH / MEDIUM / LOW]
FAILED_AT: [Q# / Gate # / N/A]
MISSING_PROOF: [artifact or none]
ACTION: [/brief / /pivot / kill]
```
