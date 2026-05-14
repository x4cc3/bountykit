---
description: Recall prior hunt context, patterns, or known dead ends. Usage: /recall target-or-bug-class
---

# /recall

Recall prior context before repeating work.

## What This Does

1. Searches available notes, evidence packs, reports, and memory from the disposable workspace
2. Identifies repeated bug classes, targets, endpoints, or dead ends
3. Returns the narrowest high-signal next action

## Execution

Use workspace notes or Disposable CLI/tools. This repo does not ship a memory database wrapper.

## Output

- remembered target or bug class
- strongest reusable evidence
- dead ends to avoid
- next action
