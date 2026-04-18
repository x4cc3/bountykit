---
description: Check if a target asset is in scope before hunting or submitting. Usage: /boundary <asset>
---

# /boundary

Verify an asset is in scope before hunting. Out-of-scope = instant close + possible ban.

## Usage
```
/boundary api.target.com
/boundary https://target.com/api/v2/users
```

## Process

1. **Read scope list** — extract in-scope domains, out-of-scope paths, exclusions
2. **Ownership check** — `whois`, `dig CNAME` — if CNAME to salesforce/zendesk/intercom → third-party → not in scope
3. **Wildcard rules:**

| Pattern | Covers | Does NOT Cover |
|---|---|---|
| `*.target.com` | `api.target.com` | `target.com` itself |
| `target.com` | `target.com` only | subdomains |

4. **Path exclusions** — check for `/admin/*`, `/api/v1/*`, feature exclusions
5. **Staging/dev** — `staging.*`, `dev.*`, `qa.*` = NOT in scope unless explicitly listed

## Output

- **IN SCOPE:** "asset is covered by [scope entry]. Owned by target. Clear to test."
- **OUT OF SCOPE:** "asset excluded by [rule]. Do not test."
- **UNCLEAR:** "CNAME to third-party. Do not test without explicit confirmation."

## Safe Harbor

Look for: "We will not pursue legal action..." — if absent, stick strictly to documented scope.
