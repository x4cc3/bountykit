# Codex Setup

Use bountykit in Codex by installing the tracks and using the repo's `AGENTS.md` as the local operating guide.

## Files

- Codex control file: [AGENTS.md](../../AGENTS.md)
- Canonical workflow: [workflow.md](../../manual/workflow.md)
- Main full-loop track: [hunt](../../tracks/field-manual/SKILL.md)

## Install

From the repo root:

```bash
./bootstrap.sh --client codex
```

That copies the bountykit tracks into:

```bash
~/.codex/skills
```

## How Codex Uses It

Codex loads the installed tracks from `~/.codex/skills`, but repo-local work should follow [AGENTS.md](../../AGENTS.md) and [workflow.md](../../manual/workflow.md).

Recommended read order:

1. [AGENTS.md](../../AGENTS.md)
2. [workflow.md](../../manual/workflow.md)
3. [hunt](../../tracks/field-manual/SKILL.md) or the narrower track named by the workflow

For autonomous runs, use [playbooks/mission.md](../../playbooks/mission.md), generate scope JSON with `python3 core/scope.py --csv hackerone-scope.csv`, and run `python3 core/mission.py --target ... --scope-file ...`.

## Verification

Useful checks:

```bash
ls ~/.codex/skills
```

You should see the bountykit track directories listed there after installation.
