---
description: "Gather CVE, hacktivity, and tech stack intelligence for a target before hunting. Usage: /intel target.com"
---

# /intel

Build an intelligence report for a target before hunting starts.

## What This Does

1. Probes the target to auto-detect technologies (Next.js, GraphQL, JWT, etc.)
2. Fetches high-severity CVEs (CVSS ≥ 7.0) from NVD for the detected stack
3. Pulls disclosed reports from HackerOne Hacktivity
4. Checks hunt memory for previous findings on this target
5. Generates a recommended approach based on the detected stack

## Usage

```bash
# Auto-detect tech and fetch intel
python3 core/intel.py --target target.com

# Specify tech manually
python3 core/intel.py --target target.com --tech nextjs,graphql,jwt

# Include HackerOne program-specific data
python3 core/intel.py --target target.com --program program-handle

# Save report
python3 core/intel.py --target target.com --output intel-report.md

# JSON output for piping
python3 core/intel.py --target target.com --json
```

## When to Use

- Before `/survey` — know what stack you're hitting
- Before `/probe` — know which CVEs to test for
- When switching to a new target
- When a target updates their stack

## Recommended Flow

```
/boundary → /intel → /survey → /probe
```

Intel feeds directly into survey and probe decisions.
