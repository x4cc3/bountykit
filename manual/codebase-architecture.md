# beta-ops Codebase Architecture

This repository is a bug bounty operations pack with two layers:

1. A documentation and routing layer for agent clients.
2. A helper-tool layer for recon, scanning, validation, and report drafting.

## Top-Level Layout

| Path | Role |
|---|---|
| `README.md` | Human-facing entrypoint and repo map |
| `AGENTS.md` | Codex/OpenCode operating contract |
| `SKILL.md` | Short router into tracks, roles, and playbooks |
| `manual/` | Neutral workflow guidance and reference docs |
| `guardrails/` | Always-on hunting and reporting constraints |
| `tracks/` | Knowledge lanes such as recon, exploit classes, validation, and disclosure |
| `playbooks/` | Procedure docs shaped like slash commands |
| `roles/` | Specialist role briefs for delegation |
| `clients/` | Bootstrap notes for Codex, Claude, and Opencode |
| `session-hooks/` | Optional lifecycle prompts |
| `wordlists/` | Local recon and fuzzing dictionaries |
| `automation/` | Legacy helper automation |
| `beta_ops_*.py`, `*.sh` | Direct execution tooling |

## Control Flow

The intended operating loop is:

1. `boundary`
2. `survey`
3. `probe`
4. `screen` / `gate`
5. `pivot`
6. `brief`

That loop is described in `manual/workflow.md`, repeated in `README.md`, and routed via `SKILL.md`.

## Runtime Data Flow

The direct tooling revolves around a small filesystem contract:

- `targets/` stores selected programs from `target_selector.py`
- `recon/<target>/` stores recon artifacts from `beta_ops_recon.sh`
- `findings/<target>/` stores scan outputs from `vuln_scanner.sh`, `cve_hunter.py`, and `zero_day_fuzzer.py`
- `reports/<target>/` stores generated write-ups from `beta_ops_report.py`

`beta_ops_hunt.py` is the orchestrator that ties those directories together.

## Script Review

| File | Purpose | Current Notes |
|---|---|---|
| `beta_ops_hunt.py` | Orchestrates target selection, recon, scanning, CVE hunting, fuzzing, and reporting | Core entrypoint; path drift fixed so it now resolves local scripts and local `wordlists/` correctly |
| `beta_ops_recon.sh` | Recon pipeline | Strongest shell entrypoint; now writes to repo-local `recon/` and uses repo-local `wordlists/` |
| `vuln_scanner.sh` | Bulk nuclei/manual heuristic pass over recon data | Output contract is clear; still high false-positive risk in heuristic checks |
| `target_selector.py` | Pulls public program metadata and ranks targets | Output location is now repo-local; scoring is simple and understandable |
| `cve_hunter.py` | Detects tech and correlates public CVEs | Useful enrichment; `/tmp/cfg_check.txt` temp-file approach is brittle under concurrent runs |
| `zero_day_fuzzer.py` | Opportunistic active fuzzing and edge-case probes | Broad but noisy; suitable for lab usage more than unattended automation |
| `beta_ops_report.py` | Converts findings into report drafts | Good for skeleton generation, but templates are intentionally generic and still need human proof |
| `beta_ops_validate.py` | Interactive validation gate and CVSS helper | Helpful operator workflow; output path is now repo-local |
| `beta_ops_learn.py` | Pulls advisories, CVEs, and Hacktivity examples | Useful pre-hunt intelligence; queries are network-dependent and not cached |
| `beta_ops_map.py` | Generates a checklist and Mermaid mind map | Lightweight planning tool; output path is now repo-local |

## What Was Fixed

- Root-level Python and shell scripts now resolve the repository root correctly instead of the parent directory.
- `beta_ops_hunt.py` now points at local helper scripts and local `wordlists/`.
- `target_selector.py`, `beta_ops_map.py`, `beta_ops_learn.py`, `beta_ops_validate.py`, `cve_hunter.py`, `zero_day_fuzzer.py`, and `beta_ops_report.py` now emit outputs under this repository instead of outside it.
- Recon docs no longer embed a token-looking Chaos API value; they now use `$CHAOS_API_KEY` placeholders.

## Structural Risks Still Present

- Workflow guidance is duplicated across `README.md`, `AGENTS.md`, `manual/workflow.md`, tracks, and playbooks, so future edits can drift.
- Tool dependencies are shell-first and implicit; there is still no Python or Node manifest at the repo root.
- Several scanners rely on heuristics that will over-report without manual review.
- Some scripts use shell commands through `subprocess.run(..., shell=True)`, which is flexible but makes quoting and portability harder.
- Temporary-file use in `cve_hunter.py` and similar one-off patterns make concurrent runs less safe.

## Recommended Cleanup Order

1. Add a shared path helper for Python tools and a single shell helper for repo-relative paths.
2. Add a small dependency manifest or setup doc for Python libraries actually required by the scripts.
3. Reduce duplicated workflow text by making `manual/workflow.md` the canonical source and linking to it elsewhere.
4. Split noisy automation into `safe-default` and `aggressive-lab` modes so unattended runs produce fewer weak leads.
5. Replace ad hoc temp-file handling with `tempfile` in Python and `mktemp` in shell where needed.
