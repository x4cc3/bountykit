# bountykit

`bountykit` is a markdown operations pack for scoped bug bounty work in Disposable, Codex, Opencode, Claude, and similar agent clients.

It does not ship scanner wrappers or local CLI tools. Use Disposable's CLI/tooling for execution; use this repo for workflow, guardrails, role routing, validation rules, and report discipline.

## Start Here

- Workflow: [manual/workflow.md](./manual/workflow.md)
- Guardrails: [guardrails/hunting.md](./guardrails/hunting.md)
- Reporting: [guardrails/reporting.md](./guardrails/reporting.md)
- Autonomous missions: [manual/autonomous-operations.md](./manual/autonomous-operations.md)
- Evidence packs: [manual/evidence-packs.md](./manual/evidence-packs.md)

## How To Use

1. Read the workflow and guardrails.
2. Pick the matching playbook or track at the repo root.
3. Run the needed Disposable CLI commands in your disposable workspace.
4. Bring exact evidence back through `/screen`, `/gate`, and `/brief` before reporting.

## Repository Map

| Area | Purpose |
|---|---|
| `manual/` | Canonical workflow and operating references |
| `guardrails/` | Always-on hunting and reporting constraints |
| `tracks/` | Doctrine for recon, exploit classes, payloads, validation, disclosure, and contracts |
| `playbooks/` | Command-shaped operating procedures |
| `roles/` | Specialist role briefs for delegation |
| `contract-notes/` | Long-form smart contract reference material |
| `clients/` | Client-specific setup notes |

## Non-Goals

- No bundled scanner wrappers.
- No local MCP servers.
- No repo-owned wordlists or generated findings directories.
- No replacement for Disposable's execution environment.

## Attribution

The methodology and source material originate from [shuvonsec/claude-bug-bounty](https://github.com/shuvonsec/claude-bug-bounty), but this repository now uses a docs-first workflow surface.
