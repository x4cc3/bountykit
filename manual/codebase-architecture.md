# bountykit Codebase Architecture

This repository has two layers:

1. a documentation and routing layer for agent clients
2. a helper-tool layer for recon, scanning, validation, and report drafting

[workflow.md](./workflow.md) is the canonical routing source. Other docs should link to it instead of repeating the workflow, role, track, or playbook lists.

## Top-Level Layout

| Path | Role |
|---|---|
| `README.md` | Human-facing overview and small public entrypoint list |
| `AGENTS.md` | Agent-facing operating contract |
| `CLAUDE.md` | Claude-specific setup doorway |
| `SKILL.md` | Tiny router into the canonical workflow |
| `manual/` | Canonical workflow and operating references |
| `guardrails/` | Always-on hunting and reporting constraints |
| `tracks/` | Doctrine for recon, exploit classes, payloads, validation, disclosure, and contract review |
| `playbooks/` | Command-shaped wrappers around the canonical workflow |
| `roles/` | Specialist role briefs for delegation |
| `clients/` | Bootstrap notes for Codex, Claude, and Opencode |
| `mcp/` | Optional Burp and HackerOne integrations |
| `wordlists/` | Local recon and fuzzing dictionaries |
| `automation/` | Legacy or auxiliary shell helpers |

## Runtime Data Flow

The direct tooling revolves around a small filesystem contract:

- `targets/` stores selected programs from `core/targets.py`
- `recon/<target>/` stores recon artifacts from `core/recon.sh`
- `findings/<target>/` stores scan outputs from `core/scan.sh`, `core/cves.py`, and `core/fuzz.py`
- `reports/<target>/` stores generated write-ups from `core/report.py`

`core/hunt.py` is the manual orchestrator that ties those directories together. `core/mission.py` wraps the same flow with explicit scope, lifecycle, and stop decisions.

## Entrypoint Model

| Tier | Files | Notes |
|---|---|---|
| Setup | `bootstrap.sh` | Installs client assets |
| Primary | `core/scope.py`, `core/mission.py`, `core/hunt.py` | Default public CLI surface |
| Verification | `smoke.sh` | Local repo checks |
| Specialist utilities | `core/intel.py`, `core/cicd.py`, `core/memory.py` | Use when the workflow calls for them |
| Internal helpers | `core/recon.sh`, `core/scan.sh`, `core/report.py`, `core/lifecycle.py`, `core/map.py`, `core/learn.py`, `core/validate.py`, `core/cves.py`, `core/fuzz.py`, `core/targets.py`, `core/common.py` | Implementation details behind the primary entrypoints |
| Lab-only probes | `labs/run.sh`, `labs/idor.py`, `labs/graphql.py`, `labs/oauth.py`, `labs/race.py`, `labs/aiprobe.py`, `labs/payloads.py`, `labs/support.py`, `labs/unicode.py` | Specialized tools; use deliberately |

## Cleanup Bias

When simplifying this repo, prefer:

1. fewer public entrypoints
2. links to canonical docs instead of repeated lists
3. compatibility-preserving demotion before moving scripts
4. lab-only labeling for aggressive or target-specific probes
