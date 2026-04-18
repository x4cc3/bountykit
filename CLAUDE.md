# beta-ops — Claude Guide

This file is the Claude-specific doorway into the beta-ops layout.

## Install

```bash
chmod +x bootstrap.sh
./bootstrap.sh --client claude
```

## Read First

- [workflow.md](./manual/workflow.md)
- [hunting.md](./guardrails/hunting.md)
- [control-room](./roles/control-room.md)

## Available Tracks

| Track | Purpose |
|---|---|
| `field-manual` | Full hunt loop |
| `surface-mapping` | Recon and surface ranking |
| `exploit-atlas` | Web bug-class reference |
| `payload-bank` | Payloads and bypasses |
| `verdict-gate` | Triage and validation |
| `disclosure-lab` | Report writing |
| `contract-review` | Smart contract review |

## Workflow

Use [workflow.md](./manual/workflow.md) as the canonical mission-loop, playbook-order, and role-routing reference.

## Extra Commands

- `/mission`
- `/contract-sweep`
- `/recall` — Pull up hunt memory for a target or bug class
- `/intel` — CVE + disclosure intelligence before hunting
- `/cicd-scan` — Scan CI/CD pipelines for security issues
- `/pickup` — Resume a previous hunt session
- `/autopilot` — Full autonomous hunt loop

## Direct Tools

- `beta_ops_hunt.py`
- `beta_ops_recon.sh`
- `beta_ops_learn.py`
- `beta_ops_map.py`
- `beta_ops_validate.py`
- `beta_ops_report.py`
- `beta_ops_scope.py`
- `beta_ops_lifecycle.py`
- `beta_ops_autonomous.py`
- `beta_ops_memory.py` — Cross-session hunt memory (save/recall findings, techniques, patterns)
- `beta_ops_intel.py` — CVE + disclosure intelligence engine
- `beta_ops_cicd.py` — CI/CD pipeline security scanner

## MCP Integrations

- `mcp/burp_mcp.py` — Burp Suite proxy history, site map, scan issues
- `mcp/hackerone_mcp.py` — HackerOne program scope, hacktivity, weaknesses

See `mcp/README.md` for setup instructions.

Use `control-room` as the default entrypoint. For specialist handoff and routing details, follow [workflow.md](./manual/workflow.md).
