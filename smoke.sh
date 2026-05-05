#!/bin/bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CORE="$ROOT/core"
LABS="$ROOT/labs"
MCP="$ROOT/mcp"

export PYTHONPATH="$CORE:$LABS:$MCP${PYTHONPATH:+:$PYTHONPATH}"

echo "== Python compile =="
python3 -m py_compile "$CORE"/*.py "$LABS"/*.py "$MCP"/*.py

echo "== Shell syntax =="
bash -n "$CORE/recon.sh"
bash -n "$CORE/scan.sh"
bash -n "$ROOT/bootstrap.sh"
bash -n "$CORE/install.sh"
bash -n "$LABS/run.sh"

echo "== Target selector relative output =="
python3 "$CORE/targets.py" --top 1 --output "$ROOT/selected.json"
rm -f "$ROOT/selected.json"

echo "== Scope custom output =="
TMP_CSV="/tmp/bountykit-smoke-scope.csv"
TMP_SCOPE_OUT="/tmp/bountykit-smoke/out.json"
mkdir -p "/tmp/bountykit-smoke"
printf 'Asset,Asset Type,Eligible for Bounty,Instruction\n*.example.com,WILDCARD,Yes,Safe harbor applies\n' > "$TMP_CSV"
python3 "$CORE/scope.py" --csv "$TMP_CSV" --output "$TMP_SCOPE_OUT"
printf 'Asset,Asset Type,Eligible for Bounty,Instruction\nunknown.example.com,DOMAIN,,Needs manual review\n' > "$TMP_CSV"
python3 "$CORE/scope.py" --csv "$TMP_CSV" --output "$TMP_SCOPE_OUT" >/tmp/bountykit-scope.out
python3 - "$TMP_SCOPE_OUT" <<'PY'
import json, sys
scope = json.load(open(sys.argv[1]))
assert "unknown.example.com" not in scope["in_scope_domains"]
assert "unknown.example.com" in scope["review_required"]
PY
printf 'Asset,Asset Type,Eligible for Bounty,Instruction\nexample..com,DOMAIN,Yes,bad double dot\n-bad.com,DOMAIN,Yes,bad leading hyphen\ngood.example.com,DOMAIN,Yes,valid\n' > "$TMP_CSV"
python3 "$CORE/scope.py" --csv "$TMP_CSV" --output "$TMP_SCOPE_OUT" >/tmp/bountykit-scope-malformed.out
python3 - "$TMP_SCOPE_OUT" <<'PY'
import json, sys
scope = json.load(open(sys.argv[1]))
assert "good.example.com" in scope["in_scope_domains"]
assert "example..com" not in scope["in_scope_domains"]
assert "-bad.com" not in scope["in_scope_domains"]
PY
python3 - "$ROOT" <<'PY'
import os, sys
from common import safe_join, sanitize_name
root = os.path.join(sys.argv[1], "missions")
name = sanitize_name("../escape-test", fallback="fallback")
path = safe_join(root, name)
assert name == "escape-test"
assert path.startswith(os.path.abspath(root) + os.sep)
PY

echo "== Map custom output =="
python3 "$CORE/map.py" --target example.com --type website --tech nextjs --output "/tmp/bountykit-smoke/map.md"

echo "== Bootstrap arg handling =="
if "$ROOT/bootstrap.sh" --client >/tmp/bountykit-bootstrap.out 2>&1; then
  echo "bootstrap missing-arg test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Missing value for --client" /tmp/bountykit-bootstrap.out
"$ROOT/bootstrap.sh" --dry-run --client opencode >/tmp/bountykit-bootstrap-dry.out
if grep -q 'eval "\$@"' "$ROOT/bootstrap.sh"; then
  echo "bootstrap still uses eval" >&2
  exit 1
fi

echo "== Edge-case recon-dir no-op guard =="
mkdir -p /tmp/bountykit-empty-recon/live
if python3 "$CORE/fuzz.py" --recon-dir /tmp/bountykit-empty-recon >/tmp/bountykit-edge.out 2>&1; then
  echo "edge_case_fuzzer no-target test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "No targets resolved" /tmp/bountykit-edge.out

echo "== CVE hunter invalid-domain guard =="
if python3 "$CORE/cves.py" 'bad;domain' >/tmp/bountykit-cve.out 2>&1; then
  echo "cve_hunter invalid-domain test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Unsupported domain format" /tmp/bountykit-cve.out
if python3 "$CORE/cves.py" 'bad..example.com' >/tmp/bountykit-cve2.out 2>&1; then
  echo "cve_hunter double-dot test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Unsupported domain format" /tmp/bountykit-cve2.out

echo "== Shell entrypoint target guards =="
if bash "$CORE/recon.sh" 'bad;domain' >/tmp/bountykit-recon.out 2>&1; then
  echo "recon invalid-domain test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Unsupported target format" /tmp/bountykit-recon.out
if bash "$CORE/recon.sh" '-bad.example.com' >/tmp/bountykit-recon2.out 2>&1; then
  echo "recon leading-hyphen test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Unsupported target format" /tmp/bountykit-recon2.out
if bash "$CORE/scan.sh" /tmp/bountykit-empty-recon >/tmp/bountykit-scan.out 2>&1; then
  echo "scan out-of-tree recon test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Recon directory" /tmp/bountykit-scan.out

if grep -q 'SecLists/master' "$CORE/hunt.py"; then
  echo "hunt.py still uses floating SecLists master" >&2
  exit 1
fi
if grep -qE '@latest|@master' "$CORE/install.sh"; then
  echo "install.sh still uses floating Go versions" >&2
  exit 1
fi
if grep -qE 'results/.*/urls.txt|results/\{.*\}/urls.txt' "$CORE/mission.py"; then
  echo "mission.py still references stale results urls path" >&2
  exit 1
fi

mkdir -p "$ROOT/findings/smoke-empty/idor-empty"
touch "$ROOT/findings/smoke-empty/idor-empty/request.http" "$ROOT/findings/smoke-empty/idor-empty/response.http" "$ROOT/findings/smoke-empty/idor-empty/scope.txt" "$ROOT/findings/smoke-empty/idor-empty/victim.txt" "$ROOT/findings/smoke-empty/idor-empty/negative_control.txt"
printf '{"bug_class":"idor"}\n' > "$ROOT/findings/smoke-empty/idor-empty/metadata.json"
python3 "$CORE/lifecycle.py" smoke-empty >/tmp/bountykit-lifecycle.out
if grep -q '"decision": "PASS"' /tmp/bountykit-lifecycle.out; then
  echo "empty evidence pack unexpectedly passed" >&2
  exit 1
fi
rm -rf "$ROOT/findings/smoke-empty"


echo "== IDOR scanner invalid-id guard =="
if python3 "$LABS/idor.py" --token-a tokenA --token-b tokenB --report-id '12oops' >/tmp/bountykit-idor.out 2>&1; then
  echo "idor invalid-id test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "report-id must be numeric" /tmp/bountykit-idor.out

echo "== GraphQL IDOR battery invalid-id guard =="
if python3 "$LABS/graphql.py" --cookie-a a --cookie-b b --report-id 'oops' --report-gid gid >/tmp/bountykit-graphql-idor.out 2>&1; then
  echo "graphql invalid-id test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "report-id must be numeric" /tmp/bountykit-graphql-idor.out

echo "== Smoke tests passed =="
