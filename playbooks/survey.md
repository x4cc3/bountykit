---
description: Run scoped recon on a target and produce the next attack surface to probe. Usage: /survey target.com
---

# /survey

Run the recon phase and leave behind a prioritized surface, not a wall of raw output.

## Canonical Source

Treat `../tracks/surface/SKILL.md` as the authoritative recon doctrine.

Use that track for:

- the full recon pipeline
- exact command choices
- URL and endpoint classification
- JS analysis and follow-up checks
- 5-minute kill signals

This playbook is only the execution wrapper.

## Required Inputs

- one explicit target domain
- confirmed scope status from `/boundary` or equivalent proof
- any known focus lane, if already chosen

Optional focus examples:

- `api`
- `auth`
- `upload`
- `graphql`
- `fast`

## Execution Standard

1. confirm the target is in scope
2. load `../tracks/surface/SKILL.md`
3. run the narrowest recon pass that still supports the current mission
4. organize outputs under `recon/<target>/`
5. rank the best next surface instead of dumping every artifact equally

## Minimum Deliverable

Return:

1. the highest-value hosts or paths
2. the most promising bug-class lanes
3. one recommended next probe
4. one stop/rotate decision if the surface is cold

## Stop Rule

If the surface meets the kill signals from `../tracks/surface/SKILL.md`, stop and rotate instead of deepening recon.
