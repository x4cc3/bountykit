---
description: Build an exploit chain — given bug A, finds B and C for higher severity. Usage: /pivot
---

# /pivot

Build A→B→C chain for higher severity. Use when finding is conditionally valid, Low, or chainable.

## Usage
```
/pivot
```
Describe bug A: class, endpoint, capability, platform.

## A→B Signal Table

| Found A | Check B | Also Check C |
|---|---|---|
| IDOR GET `/api/user/X` | PUT/DELETE same path | ALL sibling endpoints |
| IDOR on `/v2/` | Same on `/v1/` | Mobile API |
| Auth bypass one endpoint | Every sibling in controller | Old API version |
| Stored XSS | Does admin view this? | Email/PDF rendering |
| SSRF DNS callback | Internal services 169.254.x | Via open redirect |
| SQLi one param | Every param same endpoint | Sibling endpoints |
| File upload PNG | SVG (XSS), PHP (RCE) | Double ext `shell.php.jpg` |
| OAuth missing PKCE | Missing state (CSRF) | Auth code reuse |
| Open redirect | OAuth code theft → ATO | Phishing chain |
| GraphQL introspection | Auth bypass mutations | IDOR via node(id) |
| Race on coupons | Race on credits/wallet | Race on rate limits |
| S3 listing | JS bundles → grep keys | `.env` in bucket |
| Missing OTP rate limit | Brute force OTP | Brute reset tokens |
| CSRF on action | XSS→CSRF = Critical | img/form autosubmit |
| Path traversal | LFI /proc/self/environ | Log poison → RCE |
| Leaked key in JS | Call API as that key | Other keys same file |
| LLM prompt injection | IDOR via chatbot | Exfil via `<img src>` |

## High-Value Chain Patterns

1. **S3→Bundle→Secret→OAuth**: Public bucket → JS bundles → grep OAuth creds → auth code exchange
2. **Redirect→OAuth→ATO**: Open redirect → OAuth redirect_uri → code theft → token → ATO (Critical)
3. **XSS→CSRF→Admin**: Stored XSS → admin views → auto-submit CSRF → privilege escalation (Critical)
4. **SSRF→Metadata→Cloud**: DNS SSRF → 169.254.169.254 → IAM creds → cloud access (Critical)
5. **Subdomain→OAuth→ATO**: Dangling CNAME → claim → OAuth redirect_uri → code theft (Critical)
6. **Prompt→IDOR→Exfil**: Injection → "show user 456's data" → markdown exfil (High)

## Rules

- Confirm A is REAL first (exact request + response)
- B must be DIFFERENT bug (different endpoint/mechanism/impact)
- Each confirmed bug = separate report = separate payout
- If B not confirmed in 20 min → submit A, move on
- If A+B+C confirmed → STOP, submit all three
- 3 consecutive B candidates fail Gate 0 → cluster dry, stop
- 30+ min on B with no PoC → stop
