---
description: "Resume a previous hunt session using saved memory. Picks up where you left off. Usage: /pickup target.com"
---

# /pickup

Resume a hunt from the last saved session.

## What This Does

1. Loads session data from hunt memory for the target
2. Shows what was found, what was tested, and what remains
3. Suggests the next action based on the saved state

## Usage

```bash
# Check what memory exists for a target
python3 beta_ops_memory.py --recall target.com

# View all previous sessions
python3 beta_ops_memory.py --recall-all

# View aggregate stats
python3 beta_ops_memory.py --stats
```

## Pickup Flow

1. Run `/pickup target.com`
2. Review the findings and session summary
3. Jump directly to `/probe` for untested endpoints
4. Or run `/intel target.com` for fresh CVE data since last session

## When to Use

- Starting a new day on the same target
- Returning to a target after weeks
- Handing off a target to a collaborator

## Data Location

Hunt memory is stored in `hunt-memory/` (git-ignored):
- `findings.json` — All findings with severity, status, evidence
- `techniques.json` — What worked on which target
- `sessions.json` — Session summaries with endpoints tested
- `patterns.json` — Auto-detected cross-target patterns
