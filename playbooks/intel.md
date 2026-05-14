---
description: Gather CVE, disclosure, and tech-stack intelligence for a target before hunting. Usage: /intel target.com
---

# /intel

Build an intelligence note for a target before hunting starts.

## What This Does

1. Identify the target's likely technologies from approved sources and scoped recon
2. Check for relevant high-severity CVEs and recent advisories
3. Review disclosed reports and known bug classes for similar targets
4. Check prior hunt notes when available
5. Produce a recommended approach for `/survey` and `/probe`

## Execution

Use the Disposable CLI/tools. This repo does not ship an intel script.

Keep the output concise:

- target
- detected or declared technologies
- strongest relevant advisories/disclosures
- likely bug classes to test first
- explicit dead ends or low-signal areas

## When to Use

- Before `/survey`
- Before `/probe`
- When switching to a new target
- When a target updates its stack

## Recommended Flow

```text
/boundary → /intel → /survey → /probe
```

Intel feeds directly into survey and probe decisions.
