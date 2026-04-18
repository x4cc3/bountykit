# Codex Setup

Use beta-ops in Codex by installing the tracks and using the repo's `AGENTS.md` as the local operating guide.

## Files

- Codex control file: [AGENTS.md](../../AGENTS.md)
- Generic workflow: [workflow.md](../../manual/workflow.md)
- Main full-loop track: [field-manual](../../tracks/field-manual/SKILL.md)

## Install

From the repo root:

```bash
./bootstrap.sh --client codex
```

That copies the beta-ops tracks into:

```bash
~/.codex/skills
```

If you want the repo's Python helpers to run with pinned packages, install them from the repo root with:

```bash
python3 -m pip install -r requirements.txt
```

Installed tracks:

- `field-manual`
- `surface-mapping`
- `exploit-atlas`
- `payload-bank`
- `verdict-gate`
- `disclosure-lab`
- `contract-review`

## How Codex Uses It

Codex loads the installed tracks from `~/.codex/skills`, but the repo-local guidance should come from [AGENTS.md](../../AGENTS.md) when you are working inside this repository.

Recommended read order:

1. [AGENTS.md](../../AGENTS.md)
2. [workflow.md](../../manual/workflow.md)
3. [field-manual](../../tracks/field-manual/SKILL.md) or the narrower track you need

## What Users Should Start With

For general bug bounty work:

- start with `field-manual` when you want the full hunt loop
- switch to narrower tracks only when the task is already bounded

Useful narrower tracks:

- [surface-mapping](../../tracks/surface-mapping/SKILL.md) for recon
- [exploit-atlas](../../tracks/exploit-atlas/SKILL.md) for bug-class tactics
- [payload-bank](../../tracks/payload-bank/SKILL.md) for payloads and bypasses
- [verdict-gate](../../tracks/verdict-gate/SKILL.md) for false-positive filtering
- [disclosure-lab](../../tracks/disclosure-lab/SKILL.md) for report writing
- [contract-review](../../tracks/contract-review/SKILL.md) for smart contracts

For autonomous runs, use the repo-local mission workflow in [playbooks/mission.md](../../playbooks/mission.md), generate scope JSON with `python3 beta_ops_scope.py --csv hackerone-scope.csv`, and run `python3 beta_ops_autonomous.py --target ... --scope-file ...`.

## Verification

Useful checks:

```bash
ls ~/.codex/skills
```

You should see the beta-ops track directories listed there after installation.
