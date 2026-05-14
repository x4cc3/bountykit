# Claude Setup

Use bountykit in Claude as a docs pack.

## Files

- General agent guide: [AGENTS.md](../../AGENTS.md)
- Canonical workflow: [workflow.md](../../manual/workflow.md)
- Autonomous missions: [autonomous-operations.md](../../manual/autonomous-operations.md)
- Tracks: [tracks](../../tracks)
- Playbooks: [playbooks](../../playbooks)

## How Claude Uses It

1. Read [AGENTS.md](../../AGENTS.md).
2. Read [workflow.md](../../manual/workflow.md).
3. Confirm scope with `boundary`.
4. Choose the narrowest playbook or track.
5. Run Disposable CLI/tools when execution is needed.
6. Validate with [verdict](../../tracks/verdict/SKILL.md) before writing.

No client-specific `CLAUDE.md` or local wrapper scripts are required.
