# verdict Proof Matrix

Use this file when the verdict is close, when the impact is easy to overclaim, or when the finding belongs to a noisy bug class.

Every final PASS should satisfy the bug-class row below.

| Bug Class | Minimum Proof Required | Common False-Positive Trap |
|---|---|---|
| IDOR / BOLA | Attacker account A, victim or object B, exact request using A against B, response showing B's private data or unauthorized action, negative control with allowed object | `200 OK` without sensitive data or without proving object B is not yours |
| SSRF | User-controlled fetch input, exact outbound target, response body or side effect from internal service or metadata, proof it is server-side | DNS callback only, redirect trick with no internal data, client-side fetch mislabeled as SSRF |
| XSS | Injection source, render sink, execution in the victim-relevant context, impact artifact tied to the program's policy | `alert(1)` only, self-XSS, browser extension behavior, non-persistent dev-only console output |
| SQLi | Injection point, payload-response delta, extracted row data or write primitive, reproducibility | Error message only, WAF page, reflected payload, timing noise without control |
| Auth bypass | Unauthorized request succeeds, expected denial captured as control, attacker reaches protected action or data | Missing auth on a public endpoint, cached response, misleading docs |
| OAuth / OIDC | Misvalidated `redirect_uri`, `state`, PKCE, or account binding plus proof of code/token theft or account takeover path | Open redirect alone, login CSRF with no account impact, theoretical token leakage |
| Race condition | Parallel request set, success rate over repeated runs, final inconsistent state, single-request control that fails | One flaky run, client retry artifact, eventual consistency mistaken for race |
| GraphQL auth issue | Unauthorized query, field, node, or mutation against another object or tenant, not just introspection | Introspection alone, schema leak alone, hidden field names without unauthorized data |
| AI / prompt injection | Untrusted prompt path, model follows attacker control, crosses a trust boundary into other-user data, secrets, tools, or sensitive actions | Model says weird things, jailbreak without data/action impact, prompt reflection only |
| CSRF | Sensitive state-changing action, no anti-CSRF control, victim-triggered request succeeds, business impact shown | Logout CSRF, cosmetic settings only, action requires attacker-controlled victim environment |
| File upload | Upload accepted, bypassed intended validation, then executed, parsed unsafely, or served in a dangerous way | Extension bypass only, stored but inert file, content-type mismatch without exploit path |
| Subdomain takeover | Dangling DNS record, successful claim of the target hostname, and trust impact such as cookies, OAuth, CSP, or user deception | Unclaimable service, parked provider page only, third-party hostname not actually controlled by target |

## Confidence Shortcuts

- HIGH: row satisfied completely, plus scope proof and negative control
- MEDIUM: row satisfied, but one supporting artifact is still rough
- LOW: row is incomplete or impact remains inferred

## Fail-Closed Reminders

- If you cannot identify the victim, object, or internal target, do not PASS.
- If you cannot show what should have happened without the bug, confidence drops.
- If the bug class is on the never-submit list, the proof matrix is not enough by itself; you still need the chain.
