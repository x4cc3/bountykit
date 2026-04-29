# Claude Setup

Use bountykit in Claude by installing the tracks and playbooks, then using the Claude-facing guide in this repository.

## Files

- Claude guide: [CLAUDE.md](../../CLAUDE.md)
- Canonical workflow: [workflow.md](../../manual/workflow.md)
- Autonomous missions: [autonomous-operations.md](../../manual/autonomous-operations.md)

## Install

From the repo root:

```bash
./bootstrap.sh --client claude
```

That installs:

- tracks into `~/.claude/skills`
- playbooks into `~/.claude/commands`

`bootstrap.sh` copies every directory under `tracks/` and every file under `playbooks/`; use [workflow.md](../../manual/workflow.md) to decide which command or track fits.

## How Claude Uses It

Use [CLAUDE.md](../../CLAUDE.md) as the client-facing doorway. The default pattern is:

1. read [workflow.md](../../manual/workflow.md)
2. confirm scope with `boundary`
3. choose the narrowest playbook or track
4. validate with [verdict-gate](../../tracks/verdict-gate/SKILL.md) before writing

For autonomous runs, use `/mission`. Generate scope JSON first with `python3 core/scope.py --csv hackerone-scope.csv` or another supported source, then feed that file into `python3 core/mission.py`.

## Verification

Useful checks:

```bash
ls ~/.claude/skills
ls ~/.claude/commands
```

You should see the bountykit tracks and playbooks after installation.
