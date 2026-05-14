# Autonomous Operations

This is the autonomous operating layer for bountykit. It keeps long-running hunts disciplined instead of turning the process into blind scanning.

## Goal

Move through a scoped mission loop:

1. enforce scope first
2. collect only enough surface to rank opportunities
3. hunt one narrow line at a time
4. kill weak findings early
5. report only when evidence is strong enough

## State Machine

Use these states when coordinating an autonomous run with your Disposable CLI/tools:

- `boundary` — load scope, verify explicit allowlist, refuse unknown targets
- `survey` — run recon and stop if the surface is cold or broken
- `probe` — run focused tests and optional enrichment
- `screen` — classify resulting artifacts into `PASS`, `KILL`, `DOWNGRADE`, or `CHAIN REQUIRED`
- `brief` — draft reports only when the lifecycle says the target is promotable
- `rotate` — stop work and move to a new surface when recon or findings do not justify continued effort

## Mission Contract

Every autonomous run needs explicit scope:

```json
{
  "program": "Example Program",
  "in_scope_domains": ["example.com", "*.example.com"],
  "out_of_scope": ["status.example.com"],
  "notes": "No auth brute force, stay under published rate limits"
}
```

The target must match the in-scope list and must not match an explicit exclusion. If that cannot be shown, stop before touching the target.

## Artifacts

Keep mission artifacts in the disposable workspace, not in this docs repo. Useful artifacts include:

- scope proof
- recon notes
- exact requests and responses
- negative controls
- screenshots or terminal logs when needed
- verdict notes from `screen` or `gate`

For best results, structure candidate findings using [evidence-packs.md](./evidence-packs.md).

## Lifecycle Heuristics

- required proof is bug-class aware and fail-closed
- `scope`, `request`, and `response` are always mandatory
- stronger or noisy classes also require victim/object proof, impact proof, and sometimes a negative control before promotion
- chain-prone classes without impact become `CHAIN REQUIRED`

This is not a replacement for full `/gate`; it is a way to keep unattended or long-running work proof-driven.

## Recommended Flow

1. `/boundary` with explicit scope text or a scope file excerpt
2. `/mission` to set the autonomous run plan
3. run focused Disposable/external-tool commands for the scoped target
4. `/screen` or `/gate` against the collected evidence
5. `/brief` only if the verdict is strong enough

## Stop Rules

Autonomy should stop when:

- the asset is not explicitly allowlisted
- recon fails or produces no useful surface
- findings are all downgraded or killed
- the best remaining lead requires a chain that cannot be proved in the current run

Stop behavior matters more than raw coverage.
