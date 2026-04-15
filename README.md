# beta-ops

`beta-ops` is a mission-control repository for bug bounty work across Codex, Opencode, Claude, and other agent clients.

This fork keeps the useful hunting content, but the project surface is now organized around a different operating model:

- `tracks/` for knowledge lanes
- `playbooks/` for runnable procedures
- `roles/` for specialist briefings
- `guardrails/` for always-on constraints
- `manual/` for neutral operating guidance
- `automation/` and the root `beta_ops_*` tools for direct execution

## Start Here

- Codex: [clients/codex/README.md](./clients/codex/README.md)
- Claude Code: [clients/claude/README.md](./clients/claude/README.md)
- Opencode: [clients/opencode/README.md](./clients/opencode/README.md)
- Generic workflow: [manual/workflow.md](./manual/workflow.md)
- Codebase architecture: [manual/codebase-architecture.md](./manual/codebase-architecture.md)
- Autonomous operations: [manual/autonomous-operations.md](./manual/autonomous-operations.md)
- Evidence packs: [manual/evidence-packs.md](./manual/evidence-packs.md)

Install client assets with:

```bash
chmod +x bootstrap.sh
./bootstrap.sh --client codex
./bootstrap.sh --client claude
./bootstrap.sh --client opencode
```

For Opencode, `bootstrap.sh` renders an example config with absolute repo paths into `~/.config/opencode/opencode-beta-ops.example.json`. Follow [clients/opencode/README.md](./clients/opencode/README.md) and merge the `default_agent`, `skills`, `agent`, and `command` sections from that rendered file into your live Opencode config.

## Mission Loop

The repository now revolves around a seven-step loop:

1. `boundary` to confirm scope
2. `survey` to map the surface
3. `probe` to run a focused hunt
4. `screen` for fast triage
5. `gate` for full validation
6. `pivot` if the finding needs escalation
7. `brief` when the evidence is strong enough to submit

## Opencode Surface

After merging the rendered Opencode config, users get:

- a primary `beta-ops` agent for the full workflow
- slash commands for each track, such as `/field-manual`, `/payload-bank`, `/verdict-gate`, and `/contract-review`
- slash commands for each playbook, such as `/boundary`, `/mission`, `/survey`, `/probe`, `/screen`, `/gate`, `/pivot`, and `/brief`
- an autonomous `/mission` workflow for scope-first long runs
- a documented way to set one model globally or assign different models per agent

## Repository Map

| Area | Purpose |
|:---|:---|
| `tracks/field-manual` | Full end-to-end hunting doctrine |
| `tracks/surface-mapping` | Recon pipeline and target mapping |
| `tracks/exploit-atlas` | Bug-class reference for web targets |
| `tracks/payload-bank` | Payloads, bypasses, and submission kill-lists |
| `tracks/verdict-gate` | Validation, triage, and report go/no-go |
| `tracks/disclosure-lab` | Submission writing and severity framing |
| `tracks/contract-review` | Smart contract and DeFi review lane |
| `playbooks/` | Command-shaped operating procedures |
| `roles/` | Specialist personas for delegation or direct use |
| `guardrails/` | Hunting and reporting constraints |
| `contract-notes/` | Long-form smart contract references |
| `session-hooks/` | Optional session lifecycle helpers |
| `automation/` | Auxiliary shell and helper scripts |

## Roles

| Role | Purpose |
|:---|:---|
| `control-room` | Main coordinator from scope to report |
| `surface-cartographer` | Recon and attack-surface ranking |
| `verdict-engine` | Hard gate for findings before write-up |
| `evidence-editor` | Submission-ready report writing |
| `pivot-engine` | Escalation and exploit chaining |
| `contract-cartographer` | Smart contract audit lane |

## Direct Tooling

The renamed Python and shell entrypoints are still available directly from the repo root:

- `beta_ops_hunt.py`
- `beta_ops_recon.sh`
- `beta_ops_learn.py`
- `beta_ops_map.py`
- `beta_ops_validate.py`
- `beta_ops_report.py`
- `beta_ops_idor_scan.py`
- `beta_ops_graphql_idor.py`
- `beta_ops_oauth_audit.py`
- `beta_ops_race_lab.py`
- `beta_ops_ai_probe.py`
- `beta_ops_ai_payloads.py`
- `beta_ops_autonomous.py`
- `beta_ops_lifecycle.py`
- `beta_ops_scope.py`

Example:

```bash
./beta_ops_recon.sh target.com
python3 beta_ops_scope.py --csv hackerone-scope.csv
python3 beta_ops_learn.py --tech "nextjs,graphql,jwt"
python3 beta_ops_hunt.py --target target.com --scan-only
python3 beta_ops_validate.py
python3 beta_ops_report.py findings/
```

## Tree Snapshot

```text
beta-ops/
├── AGENTS.md
├── CLAUDE.md
├── SKILL.md
├── bootstrap.sh
├── tracks/
├── playbooks/
├── roles/
├── guardrails/
├── manual/
├── contract-notes/
├── session-hooks/
├── automation/
├── clients/
├── wordlists/
└── beta_ops_*.py / beta_ops_*.sh
```

## Attribution

The methodology and source material originate from [shuvonsec/claude-bug-bounty](https://github.com/shuvonsec/claude-bug-bounty), but this repository now uses a different layout, naming scheme, and client workflow surface.
