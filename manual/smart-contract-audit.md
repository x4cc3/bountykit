# Smart Contract Audit — Reference

> Bug classes, grep patterns, scoring, kill signals, and Foundry PoC template live in `../tracks/contracts/SKILL.md`. This file covers supplementary reference only.

---

## ATTACK SURFACE BY PROTOCOL TYPE

```
DEX/AMM: oracle manipulation, rounding in pool math, sandwich, fee-on-transfer, LP inflation
LENDING: collateral valuation, liquidation logic, interest rounding, flash loan inflate collateral
BRIDGE: message replay, validator set manipulation, uninitialized proxy, cross-chain sig replay
VAULT/YIELD: share price manipulation, ERC4626 first depositor, reward accounting, withdrawal queue
STABLECOIN: collateral depeg cascade, oracle depeg, liquidation rounding
GOVERNANCE: flash loan voting, quorum manipulation, timelock bypass, snapshot timing
ZK ROLLUP: unsound constraints, unconstrained witness, missing range checks, exodus mode bypass
```

---

## AUDIT METHODOLOGY (10 Steps)

1. Read docs — gap between intent and implementation = bugs
2. `cloc src/ --include-lang=Solidity`
3. `forge build && forge test && forge coverage` — note coverage gaps
4. Static analysis: `slither . --exclude-low`, `aderyn .`, `myth analyze src/X.sol`
5. Map architecture: contracts, value flows, privileged roles, oracle deps
6. Grep surface map — run patterns from contracts track (15 min)
7. Search Solodit for findings on similar protocol types
8. Line-by-line: first pass read everything, second pass investigate
9. Invariant testing: `forge test --match-test invariant_` / echidna
10. Write PoC for confirmed findings

---

## NON-EVM CHAINS

### Solana (Rust/Anchor)
1. Missing owner check — verify `.owner == program_id`
2. Missing signer check — `Signer<'info>` not `AccountInfo`
3. Type cosplay — discriminator not checked
4. PDA seed canonicalization — user bump allows non-canonical PDAs
5. Arbitrary CPI — unverified program ID
6. Integer overflow — RELEASE builds wrap silently → `.checked_add()`
7. Sysvar spoofing — fake Clock/Instructions (Wormhole $320M root cause)

Tools: sec3 X-Ray (static), Trident (fuzzer)

### CosmWasm (Rust)
1. Unsaved storage — `load()` without `save()` on every path
2. Missing access control in `execute` handlers
3. Address validation — `deps.api.addr_validate()` required

### Move (Aptos/Sui)
1. Wrong ability — `copy` on tokens = infinite mint, `drop` on loans = skip repay
2. Missing capability check on `public` functions
3. Bitshift overflow — `<<`/`>>` don't revert

### Cross-Chain Bridges ($2.8B+ stolen)
- Validator key mgmt — threshold too low?
- Sig verification bypass — threshold reducible to 0?
- Zero/default values as valid roots (Nomad $200M)
- Message replay, deprecated sysvar functions

---

## IMMUNEFI RULES

- **NEVER test on mainnet** — local fork ONLY (permanent ban)
- No AI-generated spray reports (permanent ban)
- 5 reports per 48h max
- PoC MUST be runnable Foundry/Hardhat code
- Don't contact project directly
- One bug per report

| Severity | Impact | Payout |
|---|---|---|
| Critical | Direct theft, permanent freeze, unauthorized mint | 10% TVL; min $10K |
| High | Temp freeze >24h, theft of unclaimed yield | $5K–$100K |
| Medium | Block stuffing, griefing | $1K–$5K |
| Low | Fails to deliver promised returns | $200–$1K |

### Rejects (don't submit)
Leaked private keys, centralization risk, DoS costlier than value, third-party dep bugs, known audit issues

---

## NOTABLE EXPLOITS

| Protocol | Loss | Root Cause | Year |
|---|---|---|---|
| Wormhole | $320M | Fake sysvar bypassed sig check (Solana) | 2022 |
| Ronin | $625M | 5/9 validator keys compromised | 2022 |
| Nomad | $200M | Zero hash = trusted root | 2022 |
| Beanstalk | $182M | Flash loan governance takeover | 2022 |
| Curve | $70M | Read-only reentrancy (Vyper) | 2023 |
| Mango | $117M | Oracle manipulation via own token | 2022 |
| Cetus (Sui) | $223M | Integer overflow missed | 2025 |
| ResupplyFi | $9.8M | ERC4626 near-empty vault | 2025 |

## TOP BOUNTY PAYOUTS

| Protocol | Payout | Root Cause |
|---|---|---|
| Wormhole | $10M | Uninitialized UUPS proxy |
| Aurora | $6M | DelegateCall to precompile |
| Polygon MRC20 | $2.2M | Missing balance + sig check |
| Optimism | $2M | SELFDESTRUCT duplication |
| Balancer | $1M | ERC4626 1-wei rounding |

---

## TOOLS

| Tool | Type | Install |
|---|---|---|
| Slither | Static (93 detectors) | `pip3 install slither-analyzer` |
| Aderyn | Static (Foundry-native) | cyfrinup |
| Mythril | Symbolic execution | `pip3 install mythril` |
| Echidna | Stateful fuzzing | `brew install echidna` |
| Medusa | Next-gen fuzzer | GitHub releases |
| Halmos | Symbolic testing | `pip install halmos` |
| Phalcon | Tx trace debugger | blocksec.com |
| Tenderly | Fork + simulate | tenderly.co |
| Solodit | 50K+ audit findings | solodit.cyfrin.io |
| DeFiHackLabs | 572+ real hacks | github.com/SunWeb3Sec/DeFiHackLabs |

## PLATFORMS

Immunefi, Code4rena, Sherlock, Cantina, CodeHawks
