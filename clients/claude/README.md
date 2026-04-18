# Claude Setup

Use beta-ops in Claude by installing the tracks and playbooks, then using the Claude-facing guide in this repository.

## Files

- Claude guide: [CLAUDE.md](../../CLAUDE.md)
- Generic workflow: [workflow.md](../../manual/workflow.md)
- Main full-loop track: [field-manual](../../tracks/field-manual/SKILL.md)

## Install

From the repo root:

```bash
./bootstrap.sh --client claude
```

If you want the repo's Python helpers to run with pinned packages, install them from the repo root with:

```bash
python3 -m pip install -r requirements.txt
```

That installs:

- tracks into `~/.claude/skills`
- playbooks into `~/.claude/commands`

## What Gets Installed

Tracks:

- `field-manual`
- `surface-mapping`
- `exploit-atlas`
- `payload-bank`
- `verdict-gate`
- `disclosure-lab`
- `contract-review`

Playbooks:

- every `playbooks/*.md` file, including `boundary`, `mission`, `survey`, `probe`, `screen`, `gate`, `pivot`, `brief`, `contract-sweep`, `pickup`, `recall`, `intel`, `cicd-scan`, and `autopilot`

For MCP wiring, merge entries from [mcp/mcp-config.json](../../mcp/mcp-config.json) into `~/.claude/config.json` if you want the Burp Suite or HackerOne integrations.

## How Claude Uses It

Use [CLAUDE.md](../../CLAUDE.md) as the client-facing doorway for this repository. The default working pattern is:

1. read [workflow.md](../../manual/workflow.md)
2. choose the right track
3. run the matching playbook
4. validate with [verdict-gate](../../tracks/verdict-gate/SKILL.md) before writing

## What Users Should Start With

For general bug bounty work:

- start from `field-manual`
- use `control-room` as the default mental model

Use narrower playbooks or tracks only when the task is clearly scoped:

- `/mission` for scope-first autonomous runs
- `/survey` for recon
- `/probe` for focused testing
- `/screen` or `/gate` for validation
- `/brief` for write-up
- [contract-review](../../tracks/contract-review/SKILL.md) for smart contracts

For autonomous runs, generate scope JSON first with `python3 beta_ops_scope.py --csv hackerone-scope.csv` or another supported source, then feed that file into `python3 beta_ops_autonomous.py`.

## Verification

Useful checks:

```bash
ls ~/.claude/skills
ls ~/.claude/commands
```

You should see the beta-ops tracks and playbooks after installation.
