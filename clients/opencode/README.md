# Opencode Setup

Use beta-ops in Opencode with one primary agent and explicit slash commands.

## Files

- Config template: [opencode.example.json](./opencode.example.json)
- Rendered local example after bootstrap: `~/.config/opencode/opencode-beta-ops.example.json`
- Your live config: `~/.config/opencode/opencode.json`

## Install

From the repo root:

```bash
./bootstrap.sh --client opencode
```

That writes a rendered example file with absolute paths to:

```bash
~/.config/opencode/opencode-beta-ops.example.json
```

Merge these sections from the rendered example into your live Opencode config:

- `default_agent`
- `skills`
- `agent`
- `command`

## Default Entry Point

Set beta-ops as the default Opencode agent:

```json
{
  "default_agent": "beta-ops"
}
```

The `beta-ops` agent is the main bug bounty operator. Start there unless you already know you only want a narrower lane like recon or report writing.

## Model Selection

Opencode supports both global and per-agent model selection.

### One model for everything

Set the top-level `model` field:

```json
{
  "model": "openai/gpt-5.4"
}
```

That becomes the default model for normal sessions unless you override it on the command line.

### Different model for a specific agent

Set `model` on that agent:

```json
{
  "agent": {
    "beta-ops": {
      "model": "openai/gpt-5.4"
    },
    "verdict_engine": {
      "model": "anthropic/claude-sonnet-4"
    }
  }
}
```

This is useful when you want:

- a stronger general model for `beta-ops`
- a cheaper or faster model for narrow roles
- a different provider for a specific lane

### Optional variant

Opencode also supports an agent-level `variant` field:

```json
{
  "agent": {
    "beta-ops": {
      "model": "openai/gpt-5.4",
      "variant": "fast"
    }
  }
}
```

Use `variant` only if your provider/model supports variants.

## Command Line Overrides

You can override both the agent and model per run:

```bash
opencode --agent beta-ops --model openai/gpt-5.4
```

Examples:

```bash
opencode --agent beta-ops
opencode --agent verdict_engine --model openai/gpt-5.4
opencode --agent surface_cartographer --model anthropic/claude-sonnet-4
```

## Recommended Starter Config

This is the simplest pattern:

```json
{
  "default_agent": "beta-ops",
  "model": "openai/gpt-5.4"
}
```

Then add agent-specific `model` overrides only if you have a reason.

## What Users Should Use

For normal bug bounty work:

- use the `beta-ops` agent
- or run the `/beta-ops` command

Use narrower commands only when you already know the task:

- `/survey` or `/surface-mapping`
- `/mission`
- `/probe`
- `/screen` or `/verdict-gate`
- `/brief` or `/disclosure-lab`
- `/contract-review`

## Verification

Useful checks:

```bash
opencode debug config
opencode debug skill
opencode debug agent beta-ops
```

If your skills are installed correctly, `opencode debug skill` should list the beta-ops tracks from this repo.

## Autonomous Missions

Use `/mission` when you want a long-running, scope-first autonomous workflow.

The repo also ships a direct runner:

```bash
python3 beta_ops_autonomous.py --target target.com --scope-file scope/target.json --quick
```

That writes mission state under `missions/` and lifecycle decisions under `findings/<target>/autonomous_verdict.*`.

To generate `scope/target.json` from a program page or pasted scope file:

```bash
python3 beta_ops_scope.py --csv hackerone-scope.csv
python3 beta_ops_scope.py --url "https://hackerone.com/example"
python3 beta_ops_scope.py --text-file scope-policy.txt
```
