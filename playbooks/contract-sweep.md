---
description: Smart contract security audit — runs 10 bug class checklist from contracts track with Foundry PoC. Usage: /contract-sweep <contract.sol>
---

# /contract-sweep

## Usage
```
/contract-sweep VulnerableContract.sol
/contract-sweep https://github.com/protocol/contracts
```

## Execution

1. Run pre-dive kill signals from `../tracks/contracts/SKILL.md` — skip if score < 6/10
2. Walk all 10 bug classes in order (accounting desync → proxy/upgrade)
3. For each class: run the grep commands, apply the mental test, check variants
4. On confirmed finding: apply 7-Question Gate, quantify $ impact, write Foundry PoC
5. Run: `forge test --match-test test_exploit -vvvv`

## Canonical Source

ALL bug class details, grep patterns, variants, and PoC template live in `../tracks/contracts/SKILL.md`. This playbook is the execution wrapper only.

## Confirming a Finding

1. Can I demonstrate with a Foundry test?
2. What is the financial impact (quantify in $)?
3. Is this in the Immunefi scope?
4. Is it a known issue or acknowledged behavior?
5. Does my PoC actually run?

If all yes → `/gate` → `/brief`
