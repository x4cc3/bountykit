---
description: Quick 7-Question Gate triage — fast go/no-go before full /gate. Usage: /screen
---

# /screen

Quick triage. Not a final PASS — only decides if the lead is worth deeper validation.

## Usage
```
/screen
```
Describe finding in one sentence with: endpoint, request sent, what was reached.

## Fast 7-Question Check

All from `../tracks/verdict/SKILL.md`. First NO = KILL.

1. Have real HTTP request RIGHT NOW?
2. Impact type accepted by program?
3. Asset in scope and owned by target?
4. Works without admin/privileged access?
5. Not already known/documented?
6. Provable impact beyond "technically possible"?
7. Not on never-submit list?

## Fast Kill

Kill if: admin-only + no boundary crossing | no PoC | no victim identified | scope unchecked | 3+ preconditions | missing header/flag/DMARC | SSRF DNS-only | open redirect alone | self-XSS | introspection only

## Chain Override

If on never-submit list but chain exists (open redirect→OAuth, SSRF→internal, CORS→exfil, prompt injection→IDOR) → report the chain.

## Output

- **GO (HIGH/MEDIUM):** "All 7 pass. Run `/gate` → `/brief`."
- **KILL [Q#]:** "[reason]"
- **DOWNGRADE:** "Q6 — needs actual victim data, not just 200 status."
