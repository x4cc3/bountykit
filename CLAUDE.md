# bountykit — Claude Guide

This file is the Claude-specific doorway into the bountykit layout.

## Install

```bash
chmod +x bootstrap.sh
./bootstrap.sh --client claude
```

## Read First

- [workflow.md](./manual/workflow.md) — canonical loop, roles, tracks, and playbooks
- [hunting.md](./guardrails/hunting.md) — scope and validation rules
- [control-room](./roles/control-room.md) — default coordinator
- [clients/claude/README.md](./clients/claude/README.md) — Claude install details

## Operating Model

Use `control-room` as the default entrypoint. Switch to the narrower role only when the task is clearly bounded. The canonical role handoff rules live in [manual/workflow.md](./manual/workflow.md).

## Public Tools

Use the small public surface by default:

- `core/scope.py` for scope preflight
- `core/mission.py` for scoped autonomous missions
- `core/hunt.py` for manual orchestration
- `core/intel.py`, `core/cicd.py`, and `core/memory.py` for specialist utility work

Internal helpers live under `core/`; lab-only probes live under `labs/`.

## MCP Integrations

- `mcp/burp.py` — Burp Suite proxy history, site map, scan issues
- `mcp/hackerone.py` — HackerOne program scope, hacktivity, weaknesses

See [mcp/README.md](./mcp/README.md) for setup instructions.
