---
description: Prepare an autonomous bountykit mission with explicit scope, stop conditions, and evidence gating. Usage: /mission target.com
---

# /mission

Run the work like an autonomous mission system instead of a loose tool bundle. This is the canonical autonomous playbook; `/autopilot` is only a compatibility alias.

## What This Does

1. Confirms explicit scope input exists
2. Chooses the minimum autonomous plan for the target
3. Names the external tool/Disposable commands to run
4. Forces the result back through `screen` or `gate`
5. Records mission state and evidence in the disposable workspace

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

## Recommended Pre-flight

```text
/boundary target.com
/intel target.com
/mission target.com
```

## Output Standard

At the end of the mission, return:

1. current phase reached
2. best surviving lead
3. lifecycle decision: `PASS`, `KILL`, `DOWNGRADE`, or `CHAIN REQUIRED`
4. next action: report, pivot, rotate, or stop
