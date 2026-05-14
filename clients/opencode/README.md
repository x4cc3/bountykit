# Opencode Setup

Use bountykit in Opencode as a docs-backed operating guide.

## Files

- Canonical workflow: [workflow.md](../../manual/workflow.md)
- Tracks: [tracks](../../tracks)
- Playbooks: [playbooks](../../playbooks)
- Roles: [roles](../../roles)

## Recommended Use

For normal bug bounty work, start with the `bountykit`/control-room pattern:

1. Read [workflow.md](../../manual/workflow.md).
2. Confirm scope with [boundary](../../playbooks/boundary.md).
3. Use the narrowest playbook or track for the current lane.
4. Run Disposable CLI/tools when execution is needed.
5. Bring evidence back through [screen](../../playbooks/screen.md), [gate](../../playbooks/gate.md), and [brief](../../playbooks/brief.md).

This repo no longer ships an Opencode JSON template or local wrapper commands. Configure Opencode to read these markdown files directly or copy the relevant prompts into your own config.
