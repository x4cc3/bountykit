---
description: Resume previous context and continue from the best surviving lead. Usage: /pickup target
---

# /pickup

Resume a hunt from existing notes or evidence.

## What This Does

1. Load prior scope and evidence from the disposable workspace
2. Identify the current best surviving lead
3. Avoid repeated dead ends
4. Route to `/probe`, `/screen`, `/gate`, `/pivot`, or `/brief`

## Execution

Use available workspace notes, case files, transcripts, or the Disposable CLI/tools. This repo does not ship a pickup/memory script.

## Output

- resumed target
- best current lead
- what was already killed
- next playbook to run
