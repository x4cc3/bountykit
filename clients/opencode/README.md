# Opencode Setup

Use bountykit in Opencode with one primary agent and explicit slash commands.

## Files

- Config template: [opencode.example.json](./opencode.example.json)
- Rendered local example after bootstrap: `~/.config/opencode/opencode-bountykit.example.json`
- Your live config: `~/.config/opencode/opencode.json`

## Install

From the repo root:

```bash
./bootstrap.sh --client opencode
```

That writes a rendered example file with absolute paths to:

```bash
~/.config/opencode/opencode-bountykit.example.json
```

Merge these sections from the rendered example into your live Opencode config:

- `default_agent`
- `skills`
- `agent`
- `command`

## Default Entry Point

Set bountykit as the default Opencode agent:

```json
{
  "default_agent": "bountykit"
}
```

The `bountykit` agent is the main bug bounty operator. Start there unless you already know you only want a narrower lane like recon or report writing.

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
    "bountykit": {
      "model": "openai/gpt-5.4"
    },
    "verdict_engine": {
      "model": "anthropic/claude-sonnet-4"
    }
  }
}
```

This is useful when you want:

- a stronger general model for `bountykit`
- a cheaper or faster model for narrow roles
- a different provider for a specific lane

### Optional variant

Opencode also supports an agent-level `variant` field:

```json
{
  "agent": {
    "bountykit": {
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
opencode --agent bountykit --model openai/gpt-5.4
```

Examples:

```bash
opencode --agent bountykit
opencode --agent verdict_engine --model openai/gpt-5.4
opencode --agent surface_cartographer --model anthropic/claude-sonnet-4
```

## Recommended Starter Config

This is the simplest pattern:

```json
{
  "default_agent": "bountykit",
  "model": "openai/gpt-5.4"
}
```

Then add agent-specific `model` overrides only if you have a reason.

## What Users Should Use

For normal bug bounty work, use the `bountykit` agent or `/bountykit` command.

Use [workflow.md](../../manual/workflow.md) as the canonical command map. The Opencode template exposes the core workflow, `/mission` (plus compatibility `/autopilot`), utility commands `/intel`, `/pickup`, `/recall`, `/cicd-scan`, and the main track commands.

## Verification

Useful checks:

```bash
opencode debug config
opencode debug skill
opencode debug agent bountykit
```

If your skills are installed correctly, `opencode debug skill` should list the bountykit tracks from this repo.

## Autonomous Missions

Use `/mission` when you want a long-running, scope-first autonomous workflow. See [autonomous-operations.md](../../manual/autonomous-operations.md) for runner behavior, state files, and scope requirements.

To generate `scope/target.json` from a program page or pasted scope file:

```bash
python3 core/scope.py --csv hackerone-scope.csv
python3 core/scope.py --url "https://hackerone.com/example"
python3 core/scope.py --text-file scope-policy.txt
```
