# bountykit Architecture

This repository is a markdown operations pack. It intentionally avoids local scanner wrappers and local MCP servers.

## Layers

1. **Control surface** — root files that tell agents where to start.
2. **Documentation and routing** — playbooks, roles, tracks, guardrails, and manual references at the repo root.
3. **Client notes** — optional setup notes for agent clients under `clients/`.

[workflow.md](./workflow.md) is the canonical routing source. Other docs should link to it instead of repeating workflow, role, track, or playbook lists.

## Top-Level Layout

| Path | Role |
|---|---|
| `AGENTS.md` | General agent-facing operating contract |
| `README.md` | Human-facing overview |
| `SKILL.md` | Tiny router into the canonical workflow |
| `manual/` | Canonical workflow and operating references |
| `guardrails/` | Always-on hunting and reporting constraints |
| `tracks/` | Doctrine for recon, exploit classes, payloads, validation, disclosure, and contracts |
| `playbooks/` | Command-shaped operating procedures |
| `roles/` | Specialist role briefs for delegation |
| `contract-notes/` | Long-form smart contract reference material |
| `clients/` | Client-specific usage notes |

## Execution Model

Use the Disposable CLI/tools for execution. bountykit describes what to do, what evidence to collect, and how to decide whether a result is reportable.

## Cleanup Bias

When simplifying this repo, prefer:

1. markdown over wrapper code
2. one general `AGENTS.md` over client-specific control files
3. links to canonical docs instead of repeated lists
4. playbooks that name required evidence and stop conditions
