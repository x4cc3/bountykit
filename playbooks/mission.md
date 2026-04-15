---
description: Prepare or run an autonomous beta-ops mission with explicit scope, stop conditions, and evidence gating. Usage: /mission target.com
---

# /mission

Run the repository like an autonomous mission system instead of a loose tool bundle.

## What This Does

1. Confirms explicit scope input exists
2. Chooses the minimum autonomous plan for the target
3. Writes or references a scope file
4. Runs `beta_ops_autonomous.py` or prepares the exact command
5. Forces the result back through `screen` or `gate`

## Required Inputs

- target domain
- program name
- exact in-scope domains or wildcard suffixes
- key exclusions or safety notes

## Mission Rule

Autonomy is only allowed when scope is explicit.

If scope is ambiguous:
- stop
- ask for the missing scope detail
- do not touch the target yet

## Recommended Run

```bash
python3 beta_ops_autonomous.py \
  --target target.com \
  --scope-file scope/target.json \
  --mission-name target-main \
  --quick
```

## Output Standard

At the end of the mission, return:

1. current phase reached
2. best surviving lead
3. lifecycle decision: `PASS`, `KILL`, `DOWNGRADE`, or `CHAIN REQUIRED`
4. next action: report, pivot, rotate, or stop
