---
description: Compatibility alias for /mission. Use /mission for autonomous bountykit runs.
---

# /autopilot

`/autopilot` is deprecated as a separate command surface. Use [mission](./mission.md) for scoped autonomous runs.

The direct runner is unchanged:

```bash
python3 core/mission.py \
  --target target.com \
  --scope-file scope/target.json \
  --mission-name target-main \
  --quick
```

Safety rules, state artifacts, and output expectations are owned by [manual/autonomous-operations.md](../manual/autonomous-operations.md) and [playbooks/mission.md](./mission.md).
