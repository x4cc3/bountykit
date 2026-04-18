---
name: disclosure-lab
description: Bug bounty report writing — single template for all platforms, CVSS scoring, severity guide, pre-submit checklist. Never use "could potentially."
---

# DISCLOSURE LAB

Write reports that get triaged fast and paid full. Never use "could potentially."

---

## TITLE FORMULA

`[BugClass] in [Feature] allows [attacker] to [impact] via [vector]`

Examples:
- `IDOR in /api/orders allows authenticated user to read other users' order data via order_id parameter`
- `Stored XSS in profile bio allows attacker to steal session cookies via crafted SVG upload`

---

## UNIVERSAL REPORT TEMPLATE

Works on HackerOne, Bugcrowd, Immunefi, Intigriti. Adjust field names per platform.

```markdown
## Summary
[BugClass] in [asset] allows [attacker role] to [concrete impact] via [mechanism].

## Severity
**CVSS**: [score] ([vector string])
**Platform severity**: [Critical/High/Medium/Low]

## Steps to Reproduce
1. Log in as [attacker account type]
2. Navigate to [URL]
3. Intercept request with Burp Suite / browser DevTools
4. Modify [parameter] from [original] to [malicious]
5. Observe [impact evidence]

### Request
\`\`\`http
[EXACT copy-pasteable request]
\`\`\`

### Response
\`\`\`http
[Response showing impact]
\`\`\`

## Impact
[What attacker walks away with. Concrete: "reads all user PII", not "could access data"]

## Negative Control
[What happens with correct authorization — proving the bypass]

## Remediation
[One specific fix. Code-level if possible.]

## Supporting Evidence
- [screenshot/video link]
- [scope entry reference]
```

### Platform-specific notes
- **HackerOne**: Use "Weakness" field for CWE. Impact section maps to their "Impact" field.
- **Bugcrowd**: Severity = P1-P4 (see below). Use VRT category.
- **Immunefi**: Must include on-chain PoC for smart contract bugs. Severity = Critical/High/Medium/Low.
- **Intigriti**: Attach evidence as files. Use their severity calculator.

---

## CVSS 3.1 SCORING

See verdict-gate for full CVSS quick reference table and metric guide.

### Severity Mapping

| CVSS | Severity | Bugcrowd |
|---|---|---|
| 9.0-10.0 | Critical | P1 |
| 7.0-8.9 | High | P2 |
| 4.0-6.9 | Medium | P3 |
| 0.1-3.9 | Low | P4 |

---

## SEVERITY SELF-ASSESSMENT

Before submitting, ask:
1. What does attacker walk away with? (data, money, access, nothing?)
2. How many users affected? (all, subset, just attacker?)
3. What access needed? (none, free account, admin?)
4. Victim interaction required? (none, click, complex social engineering?)

### DOWNGRADE COUNTERS

| Triage objection | Counter |
|---|---|
| "Requires victim interaction" | Show realistic phishing scenario + one-click exploit |
| "Low impact XSS" | Chain with cookie theft → ATO |
| "Only affects attacker" | Show it affects OTHER users via [mechanism] |
| "Rate limiting exists" | Show bypass or demonstrate brute force succeeds within limits |
| "Already documented" | Show docs say X but code does Y |

---

## 60-SECOND PRE-SUBMIT CHECKLIST

- [ ] Title follows formula (no "vulnerability found in...")
- [ ] Steps reproducible from scratch by someone who's never seen the app
- [ ] Exact request included (copy-pasteable)
- [ ] Impact states what attacker GETS, not what "could" happen
- [ ] Negative control included
- [ ] CVSS score matches actual impact
- [ ] No "could potentially" / "may allow" / "might be possible"
- [ ] Scope entry referenced
- [ ] Screenshots/video attached
- [ ] Remediation is specific (not "implement proper validation")

---

## HUMAN TONE

- Write like a security engineer, not a scanner
- First person: "I discovered" not "A vulnerability was identified"
- Be direct: "This allows reading all user emails" not "This could potentially allow access to sensitive information"
- One bug per report (unless chain is required)
- If duplicate, respond professionally with any new info you found
