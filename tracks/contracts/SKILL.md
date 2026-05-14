---
name: contracts
description: Smart contract security audit — 10 DeFi bug classes, pre-dive kill signals, Foundry PoC template, grep patterns. Use for Solidity/Rust contract audit.
---

# CONTRACTS

10 bug classes. Pre-dive kill signals. Foundry PoC template. Treat static findings as hypotheses until a PoC or invariant proof confirms impact.

---

## PRE-DIVE KILL SIGNALS

1. **TVL < $500K** → max payout too low
2. **2+ top-tier audits** (Halborn, ToB, Cyfrin, OZ) on simple protocol → skip
3. **< 500 lines, single flow** → minimal surface
4. **Formula**: `max_payout = min(10% × TVL, program_cap)` — if < $10K, skip

**Target scoring (go if >= 6/10):** TVL>$10M (+2) | Critical>=$50K (+2) | No audit on current version (+2) | <30d since deploy (+1) | Hunted before (+1) | Source+natspec (+1) | Upgradeable proxies (+1)

If the score is low, stop early and record why instead of forcing a deep audit.

---

## THE ONE RULE

> Read ALL sibling functions. If `vote()` has a modifier, check `poke()`, `reset()`, `harvest()`. The missing modifier IS the bug. (19% of all Criticals)

---

## 1. ACCOUNTING DESYNC (#1 Critical — 28%)

Two state vars must stay in sync. One code path updates A but forgets B.

**Variants:**
- Phantom yield: `totalSupply` decremented before `aToken.balanceOf` changes
- Fast path early return: `return` before updating `cumulativeEarmarked`, `totalDebt`
- Wrong order: shares calculated BEFORE assets added → wrong rate

```bash
grep -rn "totalSupply\|totalShares\|totalAssets\|totalDebt\|rewardPerShare" contracts/
grep -rn "\breturn\b" contracts/ -B3 | grep -B3 "if\b"
```

## 2. ACCESS CONTROL (#2 — 19%, $953M lost 2024)

| Variant | Pattern |
|---|---|
| Missing modifier on sibling | `poke()` lacks `onlyNewEpoch` that `vote()` has |
| Existence vs ownership | `_requireOwned()` checks exists, not caller owns |
| Silent modifier | `if` instead of `require` → non-admin passes silently |
| Uninitialized proxy | `initialize()` missing `initializer` modifier |

```bash
grep -rn "function vote\|function poke\|function reset\|function claim\|function harvest" contracts/ -A2
grep -rn "_requireOwned\|ownerOf\|_isApprovedOrOwner" contracts/ -B5
grep -rn "modifier\b" contracts/ -A8 | grep -B3 "if (" | grep -v "require\|revert"
grep -rn "function initialize\b" contracts/ -A3
```

## 3. INCOMPLETE CODE PATH (#3 — 17%)

**Test:** List state changes in function A (deposit/create). List state changes in B (withdraw/cancel). If A does X but B doesn't reverse X → BUG.

Variants: update missing refund, partial fill token stuck, `mint()` bypasses check that `deposit()` has.

```bash
grep -rn "function place_\|function create_\|function open_" contracts/ -A5
grep -rn "function update_\|function cancel_" contracts/ -A5
grep -rn "function deposit\|function mint\|function withdraw\|function redeem" contracts/ -A10
```

## 4. OFF-BY-ONE (#4 High — 22%)

> For every `if (A > B)`: "What happens when A == B?" Is that correct?

6 locations: period/epoch boundaries, time-based locks, loop breaks, array index, amount boundaries, rounding to zero.

```bash
grep -rn "Period\|Epoch\|Deadline\|period\|epoch\|deadline" contracts/ -A3 | grep "[<>][^=]"
grep -rn "\bbreak\b" contracts/ -B10
grep -rn "\.length\s*-\s*1\|i\s*<=\s*.*\.length\b" contracts/
```

## 5. ORACLE / PRICE (12%, largest payouts — $117M Mango)

| Bug | Pattern |
|---|---|
| Missing staleness | `latestRoundData()` without checking `updatedAt` |
| Missing confidence | Pyth `getPriceUnsafe()` without checking `conf` |
| Short TWAP | 60s TWAP manipulatable by flash loan (need 1800s+) |
| Single source | Only Uniswap spot price (flash loan manipulatable) |

```bash
grep -rn "latestRoundData" contracts/ -A5 | grep -v "updatedAt\|timestamp"
grep -rn "getPriceUnsafe\|getPrice\b" contracts/ -A8 | grep -v "conf"
grep -rn "getReserves\|getAmountsOut\|slot0\b" contracts/ -A5
```

## 6. ERC4626 VAULT

- **First depositor attack**: deposit 1 wei → donate large amount → victim's shares round to 0. Fix: virtual shares offset
- **Transfer breaks locks**: shares transferred but lock records stay with original owner

```bash
grep -rn "function transfer\|function transferFrom" contracts/ -A15
grep -rn "function deposit\|function mint\|function withdraw\|function redeem" contracts/ -A10
```

## 7. REENTRANCY (CEI pattern prevents)

Variants: single-function, cross-function (sibling with stale state), cross-contract (callback), read-only (stale view data).

```bash
grep -rn "\.call{value\|safeTransfer\|transfer(" contracts/ -B10 | grep -v "require\|revert"
grep -rn "function withdraw\|function redeem\|function claim" contracts/ -A2 | grep -v "nonReentrant"
```

## 8. FLASH LOAN

Attack: borrow → crash spot price in pool → protocol reads bad price → borrow max against cheap collateral → repay.

```bash
grep -rn "getReserves\|getAmountsOut\|slot0\b" contracts/ -A5  # spot price = manipulatable
```

## 9. SIGNATURE REPLAY

Missing nonce → same signature reusable. Missing chainId → works on any chain/fork. Check: does signed hash include nonce + chainId + contract address?

```bash
grep -rn "ecrecover\|ECDSA\.recover" contracts/ -B20
grep -rn "nonce\|_nonces\|nonces\[" contracts/
```

## 10. PROXY / UPGRADE

- **Storage collision**: proxy slot 0 vs impl slot 0 overlap
- **Uninitialized impl**: call `initialize()` on impl directly → become owner
- **delegatecall to user-controlled address**: unchecked target

```bash
grep -rn "function initialize\b\|_disableInitializers\|initializer" contracts/
grep -rn "delegatecall\b" contracts/ -B3 -A5
grep -rn "0x360894\|EIP1967\|_IMPLEMENTATION_SLOT" contracts/
```

---

## FOUNDRY POC TEMPLATE

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "forge-std/Test.sol";

contract ExploitTest is Test {
    address attacker = makeAddr("attacker");
    address victim = makeAddr("victim");

    function setUp() public {
        vm.createSelectFork("mainnet", BLOCK_NUMBER);
        deal(address(token), attacker, INITIAL_BALANCE);
    }

    function test_exploit() public {
        console.log("Before:", token.balanceOf(attacker));
        vm.startPrank(attacker);
        // exploit steps
        vm.stopPrank();
        console.log("After:", token.balanceOf(attacker));
        assertGt(token.balanceOf(attacker), INITIAL_BALANCE);
    }
}
```

Key cheatcodes: `vm.prank()` `vm.deal()` `vm.warp()` `vm.roll()` `vm.createSelectFork()` `vm.expectRevert()` `vm.label()`

A reportable contract finding needs the vulnerable path, the violated invariant, and a minimal PoC or trace that shows loss or unauthorized state change.

```bash
forge test --match-test test_exploit -vvvv --fork-url $MAINNET_RPC
```
