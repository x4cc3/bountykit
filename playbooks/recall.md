---
description: "Quick-recall what you know about a target, bug class, or pattern from previous sessions. Usage: /recall target.com | /recall IDOR"
---

# /recall

Pull up hunt memory for a target, bug class, or cross-target pattern.

## What This Does

1. Searches the hunt memory database for matching findings, techniques, and sessions
2. Shows cross-target patterns detected across all hunts
3. Outputs actionable context for resuming work

## Usage

```bash
# Recall everything about a target
python3 core/memory.py --recall target.com

# Recall everything about a bug class across targets
python3 core/memory.py --recall IDOR

# Recall all findings and patterns
python3 core/memory.py --recall-all

# Show memory statistics
python3 core/memory.py --stats
```

## When to Use

- Starting a new session on a target you've hunted before
- Looking for patterns across multiple programs
- Before `/survey` to skip already-explored areas
- Before `/probe` to focus on known-weak endpoints

## Output

Returns a JSON summary with:
- Previous findings (severity, status, endpoints)
- Techniques that worked
- Session summaries
- Auto-detected cross-target patterns
