# bountykit

`bountykit` is a mission-control repository for scoped bug bounty work across Codex, Opencode, Claude, and other agent clients.

The default path is intentionally small:

1. confirm scope
2. run the canonical workflow
3. validate evidence before reporting

Use [manual/workflow.md](./manual/workflow.md) as the canonical router for workflow order, roles, tracks, and playbooks.

## Start Here

- Workflow: [manual/workflow.md](./manual/workflow.md)
- Guardrails: [guardrails/hunting.md](./guardrails/hunting.md)
- Autonomous missions: [manual/autonomous-operations.md](./manual/autonomous-operations.md)
- Evidence packs: [manual/evidence-packs.md](./manual/evidence-packs.md)
- Architecture notes: [manual/codebase-architecture.md](./manual/codebase-architecture.md)

Client setup:

- Codex: [clients/codex/README.md](./clients/codex/README.md)
- Claude Code: [clients/claude/README.md](./clients/claude/README.md)
- Opencode: [clients/opencode/README.md](./clients/opencode/README.md)

Install client assets with:

```bash
chmod +x bootstrap.sh
./bootstrap.sh --client codex
./bootstrap.sh --client claude
./bootstrap.sh --client opencode
```

For Opencode, `bootstrap.sh` renders an example config with absolute repo paths into `~/.config/opencode/opencode-bountykit.example.json`. Follow [clients/opencode/README.md](./clients/opencode/README.md) and merge the rendered config into your live Opencode config.

## Public Entry Points

| Entry point | Purpose |
|---|---|
| `bootstrap.sh` | Install client assets |
| `core/scope.py` | Convert program scope into explicit allowlists |
| `core/mission.py` | Run a scoped autonomous mission |
| `core/hunt.py` | Run the manual hunt orchestrator |
| `smoke.sh` | Verify the repo locally |

Specialist utilities:

| Utility | Purpose |
|---|---|
| `core/intel.py` | CVE and disclosure intelligence |
| `core/cicd.py` | CI/CD pipeline checks |
| `core/memory.py` | Cross-session hunt memory |

Implementation scripts live under `core/`; lab-only probes live under `labs/`. The repo root stays focused on docs, setup, and verification.

## Repository Map

| Area | Purpose |
|---|---|
| `manual/` | Canonical workflow and operating references |
| `guardrails/` | Always-on hunting and reporting constraints |
| `tracks/` | Doctrine for recon, exploit classes, payloads, validation, disclosure, and contract review |
| `playbooks/` | Command-shaped wrappers around the canonical workflow |
| `roles/` | Specialist role briefs for delegation |
| `clients/` | Bootstrap notes for Codex, Claude, and Opencode |
| `mcp/` | Optional Burp and HackerOne integrations |
| `wordlists/` | Local recon and fuzzing dictionaries |
| `core/` | Main implementation scripts |
| `labs/` | Specialized probes and experiments |
| `contract-notes/` | Long-form smart contract reference material |

## Attribution

The methodology and source material originate from [shuvonsec/claude-bug-bounty](https://github.com/shuvonsec/claude-bug-bounty), but this repository now uses a different layout, naming scheme, and client workflow surface.
