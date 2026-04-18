# Autonomous Operations

This is the autonomous layer for beta-ops. It exists to keep long-running hunts disciplined instead of turning the repo into a blind scanner.

## Goal

Move from tool bundle to autonomous mission loop:

1. enforce scope first
2. collect only enough surface to rank opportunities
3. hunt one narrow line at a time
4. kill weak findings early
5. report only when evidence is strong enough

## State Machine

The mission runner in `beta_ops_autonomous.py` uses these states:

- `boundary` - load scope, verify explicit allowlist, refuse unknown targets
- `survey` - run recon and stop if the surface is cold or broken
- `probe` - run focused scanners and optional enrichment
- `screen` - classify resulting artifacts into `PASS`, `KILL`, `DOWNGRADE`, or `CHAIN REQUIRED`
- `brief` - generate reports only when the lifecycle says the target is promotable
- `rotate` - stop work and move to a new surface when recon or findings do not justify continued effort

## Mission Contract

Every autonomous run should have a scope file like:

```json
{
  "program": "Example Program",
  "in_scope_domains": ["example.com", "*.example.com"],
  "out_of_scope": ["status.example.com"],
  "notes": "No auth brute force, stay under published rate limits"
}
```

The target must match `in_scope_domains` exactly or by wildcard suffix and must not match an explicit `out_of_scope` entry. If it does not pass both checks, the runner exits before any recon.

## Artifacts

Autonomous missions write to:

- `missions/<mission>/state.json` - run state, phase, timestamps, and final decision
- `findings/<target>/autonomous_verdict.json` - machine-readable lifecycle output
- `findings/<target>/autonomous_verdict.md` - quick human-readable summary

For best results, store candidate findings as structured evidence packs described in `manual/evidence-packs.md`.

## Lifecycle Heuristics

`beta_ops_lifecycle.py` now prefers actual evidence packs over category names alone.

- required proof is bug-class aware and fail-closed
- `scope`, `request`, and `response` are always mandatory
- stronger or noisy classes also require victim/object proof, impact proof, and sometimes a negative control before promotion
- chain-prone classes without impact become `CHAIN REQUIRED`

This is still not a replacement for full `/gate`, but it is much closer to proof-driven unattended triage.

## Scope Ingestion

You can generate `scope/*.json` from a program page or local scope text:

```bash
python3 beta_ops_scope.py --csv hackerone-scope.csv
python3 beta_ops_scope.py --url "https://hackerone.com/example"
python3 beta_ops_scope.py --text-file scope-policy.txt
```

That generated JSON can be passed directly into `beta_ops_autonomous.py`.

For HackerOne, prefer the CSV export when available. It is more stable than HTML scraping and carries asset-level scope data directly.

## Opencode Usage

Recommended flow inside Opencode:

1. `/boundary` with explicit scope text or a scope file excerpt
2. `/mission` to set the autonomous run plan
3. `/survey` or direct `python3 beta_ops_autonomous.py ...` execution for the scoped target
4. `/screen` or `/gate` against the generated autonomous verdict
5. `/brief` only if the verdict is strong enough

## Command Example

```bash
python3 beta_ops_autonomous.py \
  --target app.example.com \
  --scope-file scope/example.json \
  --mission-name example-app \
  --quick \
  --cve-hunt
```

## Stop Rules

Autonomy should stop when:

- the asset is not explicitly allowlisted
- recon fails or produces no useful surface
- findings are all downgraded or killed
- the best remaining lead requires a chain that cannot be proved in the current run

That stop behavior matters more than raw coverage.
