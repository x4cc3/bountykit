---
name: verdict-gate
description: Finding validation — 7-Question Gate, evidence pack, confidence scoring, never-submit list, chain-required table, CVSS reference. Use BEFORE writing any report.
---

# VERDICT GATE

One wrong answer = STOP. Kill it. Move on. Default: fail closed.

---

## 7-QUESTION GATE (all YES or KILL)

1. **Exploitable NOW?** Can you write the exact HTTP request? If not → KILL
2. **In-scope impact?** Bug maps to program's accepted impact list? If excluded → KILL
3. **In-scope asset?** Production domain on scope list, not staging/third-party? If not → KILL
4. **No unrealistic access?** "Admin can do X" without boundary crossing = not a bug
5. **Not already known?** Search Hacktivity, GitHub issues, changelog, API docs
6. **Provable impact?** Show actual data theft/ATO/RCE, not just `alert(1)` or DNS ping
7. **Not on never-submit list?** Check below

---

## REQUIRED EVIDENCE (all 6 or no PASS)

1. Scope proof — exact scope entry or ownership proof
2. Attacker proof — which account performed the action
3. Victim/target proof — which other user/tenant/record was reached
4. Exact request + response — copy-pasteable
5. Negative control — what should have happened
6. Impact artifact — screenshot, response body, state diff

---

## CONFIDENCE

| Level | Meaning | PASS? |
|---|---|---|
| HIGH | All 6 evidence items. Reproduced from scratch. | Yes |
| MEDIUM | Bug real, one non-critical artifact missing. | Only if not scope/victim/request |
| LOW | Missing scope, victim, or request proof. | No — KILL or CHAIN REQUIRED |

---

## PRE-SUBMISSION GATES

**Gate 0 (30s):** Real bug + in scope + reproducible from scratch + evidence ready + not LOW confidence

**Gate 1 (2min):** Can answer "what can attacker DO?" + real victim + not relying on unlikely victim action

**Gate 2 (5min):** Searched Hacktivity + GitHub issues + changelog + Google. Compared with closest disclosed report.

**Gate 3 (10min):** Title follows formula + copy-pasteable request + evidence of impact + CVSS matches + remediation + no "could potentially"

---

## NEVER SUBMIT

Missing security headers · missing SPF/DKIM/DMARC · introspection alone · version disclosure without CVE · clickjacking non-sensitive · tabnabbing · CSV injection · CORS wildcard without cred exfil · logout CSRF · self-XSS · open redirect alone · OAuth client_secret in mobile · SSRF DNS-only · host header injection alone · rate limit non-critical · session not invalidated on logout · concurrent sessions · internal IP disclosure · mixed content · weak ciphers · missing cookie flags alone · broken links · pre-account takeover · autocomplete on passwords

---

## CHAIN-REQUIRED (prove end-to-end, then report)

| Standalone | + Chain | = Valid |
|---|---|---|
| Open redirect | OAuth code theft | ATO (Critical) |
| Clickjacking | Sensitive action + PoC | Medium |
| CORS wildcard | Credentialed PII exfil | High |
| CSRF | Transfer funds / change email | High |
| Rate limit bypass | OTP brute force succeeds | Medium/High |
| SSRF DNS-only | Internal service + data | Medium |
| Host header injection | Password reset poisoning | High |
| Prompt injection | IDOR / exfil / RCE | High |
| S3 listing | JS bundles with secrets | Medium/High |
| Self-XSS | CSRF triggers on victim | Medium |
| Subdomain takeover | OAuth redirect_uri | Critical |
| GraphQL introspection | Auth bypass / IDOR | High |

---

## CVSS 3.1 QUICK REF

| Bug | Score | Severity |
|---|---|---|
| IDOR read PII | 6.5 | Medium |
| IDOR write/delete | 7.5 | High |
| Auth bypass → admin | 9.8 | Critical |
| Stored XSS | 5.4-8.8 | Med-High |
| SQLi data exfil | 8.6 | High |
| SSRF cloud metadata | 9.1 | Critical |
| Race double spend | 7.5 | High |
| JWT none alg | 9.1 | Critical |

### Metric Picks
- **AV**: Network (internet) | Local (physical)
- **AC**: Low (repeatable) | High (race/timing)
- **PR**: None (no login) | Low (free account) | High (admin)
- **UI**: None (no victim action) | Required (click)
- **S**: Unchanged (in-app) | Changed (browser/OS/cloud)
- **C/I/A**: High (all data) | Low (limited)

---

## KILL FAST

1. Can't fill exploit template in 5 min → move on
2. More than 2 simultaneous preconditions → kill
3. "What does attacker walk away with?" Nothing tangible → kill
4. Admin-only path without boundary crossing → not a bug
5. Documented behavior → kill
6. 30+ min on PoC with no reproduction → kill

Load [references/proof-matrix.md](./references/proof-matrix.md) for class-specific proof requirements on IDOR, SSRF, XSS, SQLi, auth bypass, OAuth, race, GraphQL, AI, CSRF, file upload, subdomain takeover.
