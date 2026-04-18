---
description: "Run a fully autonomous hunt loop — boundary, survey, probe, screen, brief — with no manual intervention. Usage: /autopilot target.com"
---

# /autopilot

Execute the full hunt loop autonomously with explicit scope.

## What This Does

1. Validates scope (refuses to start without explicit scope)
2. Runs recon and surface mapping
3. Probes identified attack surfaces
4. Screens findings for validity
5. Gates valid findings
6. Generates brief for reportable findings
7. Saves session to hunt memory on exit

## Usage

```bash
# Run with scope file
python3 beta_ops_autonomous.py \
  --target target.com \
  --scope-file scope/target.json \
  --mission-name target-full \
  --quick

# Run with explicit scope on command line
python3 beta_ops_autonomous.py \
  --target target.com \
  --scope-file scope/target.json
```

## Differences from /mission

- `/mission` prepares the mission parameters and may pause for confirmation
- `/autopilot` executes end-to-end without stopping (assuming scope is set)
- `/autopilot` integrates with hunt memory — saves findings/sessions on exit

## Safety Guardrails

- Will not start without explicit scope file
- Stops immediately on scope violation
- All findings go through `screen` and `gate` before brief
- Destructive tests are never run automatically

## Recommended Pre-flight

```
/boundary target.com
/intel target.com
/autopilot target.com
```
