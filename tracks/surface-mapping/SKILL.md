---
name: surface-mapping
description: Web2 recon pipeline — subdomain enum, tech fingerprint, attack surface triage, target scoring. Produces prioritized URL list for hunting.
---

# SURFACE MAPPING

Subdomain enum → live host probe → crawl → triage → hunt. 5-minute rule: if recon produces nothing interesting in 5 min, skip target.

---

## RECON PIPELINE

```bash
# 1. Subdomain enum (3 sources + DNS resolve)
chaos -d $DOMAIN -o chaos.txt 2>/dev/null
subfinder -d $DOMAIN -silent -o subfinder.txt
assetfinder --subs-only $DOMAIN > assetfinder.txt
cat chaos.txt subfinder.txt assetfinder.txt | sort -u > subs.txt

# 2. DNS resolve + live host probe
dnsx -l subs.txt -resp -o resolved.txt
httpx -l subs.txt -mc 200,301,302,403 -title -tech-detect -status-code -o live.txt

# 3. Crawl + wayback
katana -list live.txt -d 3 -jc -kf -o crawled.txt
echo $DOMAIN | waybackurls | sort -u > wayback.txt

# 4. Nuclei quick scan
nuclei -l live.txt -severity critical,high -o nuclei-hits.txt
```

Output structure: `recon/$DOMAIN/{subs,resolved,live,crawled,wayback,nuclei-hits}.txt`

---

## ATTACK SURFACE TRIAGE

```bash
# Interesting params
cat crawled.txt wayback.txt | grep -iE "id=|user=|account=|email=|token=|redirect=|url=|file=|path=|callback=" | sort -u > interesting-params.txt

# API endpoints
grep -iE "/api/|/v[0-9]/|/graphql|/rest/" crawled.txt | sort -u > api-endpoints.txt

# Upload / file endpoints
grep -iE "upload|file|import|export|download|attach" crawled.txt | sort -u > file-endpoints.txt

# Admin / auth
grep -iE "admin|dashboard|manage|login|auth|oauth|sso|saml" crawled.txt | sort -u > auth-endpoints.txt
```

GF patterns: `cat crawled.txt | gf xss > gf-xss.txt` — repeat for `sqli ssrf redirect lfi idor rce ssti cors debug_logic`

---

## JS ANALYSIS

```bash
# Find secrets in JS bundles
cat crawled.txt | grep "\.js$" | sort -u | while read url; do
  python3 SecretFinder.py -i "$url" -o cli
done

# Extract links from JS
python3 LinkFinder.py -i "$JS_URL" -o cli
```

---

## DIRECTORY FUZZING

```bash
ffuf -u "https://$TARGET/FUZZ" -w wordlists/raft-medium-dirs.txt -mc 200,301,302,403 -fc 404 -ac -o ffuf-results.json
```

---

## TARGET SCORING (go if >= 6/10)

| Signal | Points |
|---|---|
| Bounty >= $500 min payout | +2 |
| > 50 resolved reports (active program) | +2 |
| Large scope (*.domain.com, multiple apps) | +2 |
| Recently launched / updated | +1 |
| Complex app (auth, payments, multi-tenant) | +1 |
| < 100 hackers on program | +1 |
| Source code available | +1 |

### Kill signals (skip immediately)
- No bounty + no reputation gain
- VDP with no safe harbor
- Scope = single static page
- All subdomains return same CDN/parking page

---

## TECH FINGERPRINT → BUG CLASS

| Header/Signal | Tech | Priority bugs |
|---|---|---|
| `X-Powered-By: Express` | Node.js | Prototype pollution, SSRF, NoSQLi |
| `X-Powered-By: PHP` | PHP | SQLi, LFI, file upload, type juggling |
| `Server: gunicorn/uvicorn` | Python | SSTI, SSRF, deserialization |
| `X-Generator: WordPress` | WordPress | Plugin vulns, SQLi, XSS |
| `__next` in HTML | Next.js | SSRF in getServerSideProps, API routes |
| `csrf-token` meta tag | Rails | Mass assignment, IDOR |
| GraphQL endpoint | Any | Introspection, IDOR via node(), batching |
| `wp-json` in paths | WordPress | REST API user enum, plugin bugs |
| Firebase config in JS | Firebase | Insecure rules, data exfil |

---

## CONTINUOUS MONITORING

```bash
# Cron: new subdomain alerts
subfinder -d $DOMAIN -silent | anew subs.txt | notify -silent

# GitHub commit watch
github-subdomains -d $DOMAIN -t $GITHUB_TOKEN | anew subs.txt
```
