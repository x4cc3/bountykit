#!/bin/bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "== Python compile =="
python3 -m py_compile \
  "$ROOT/beta_ops_paths.py" \
  "$ROOT/beta_ops_hunt.py" \
  "$ROOT/beta_ops_scope.py" \
  "$ROOT/beta_ops_lifecycle.py" \
  "$ROOT/beta_ops_autonomous.py" \
  "$ROOT/cve_hunter.py" \
  "$ROOT/zero_day_fuzzer.py" \
  "$ROOT/target_selector.py" \
  "$ROOT/beta_ops_map.py" \
  "$ROOT/beta_ops_graphql_idor.py" \
  "$ROOT/beta_ops_idor_scan.py"

echo "== Shell syntax =="
bash -n "$ROOT/beta_ops_recon.sh"
bash -n "$ROOT/vuln_scanner.sh"
bash -n "$ROOT/bootstrap.sh"
bash -n "$ROOT/install_tools.sh"
bash -n "$ROOT/automation/full_hunt.sh"
bash -n "$ROOT/beta_ops_lab.sh"

echo "== Target selector relative output =="
python3 "$ROOT/target_selector.py" --top 1 --output "$ROOT/selected.json"
rm -f "$ROOT/selected.json"

echo "== Scope custom output =="
TMP_CSV="/tmp/beta-ops-smoke-scope.csv"
TMP_SCOPE_OUT="/tmp/beta-ops-smoke/out.json"
mkdir -p "/tmp/beta-ops-smoke"
printf 'Asset,Asset Type,Eligible for Bounty,Instruction\n*.example.com,WILDCARD,Yes,Safe harbor applies\n' > "$TMP_CSV"
python3 "$ROOT/beta_ops_scope.py" --csv "$TMP_CSV" --output "$TMP_SCOPE_OUT"

echo "== Map custom output =="
python3 "$ROOT/beta_ops_map.py" --target example.com --type website --tech nextjs --output "/tmp/beta-ops-smoke/map.md"

echo "== Bootstrap arg handling =="
if "$ROOT/bootstrap.sh" --client >/tmp/beta-ops-bootstrap.out 2>&1; then
  echo "bootstrap missing-arg test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Missing value for --client" /tmp/beta-ops-bootstrap.out

echo "== Zero-day recon-dir no-op guard =="
mkdir -p /tmp/beta-ops-empty-recon/live
if python3 "$ROOT/zero_day_fuzzer.py" --recon-dir /tmp/beta-ops-empty-recon >/tmp/beta-ops-zdf.out 2>&1; then
  echo "zero_day_fuzzer no-target test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "No targets resolved" /tmp/beta-ops-zdf.out

echo "== CVE hunter invalid-domain guard =="
if python3 "$ROOT/cve_hunter.py" 'bad;domain' >/tmp/beta-ops-cve.out 2>&1; then
  echo "cve_hunter invalid-domain test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Unsupported domain format" /tmp/beta-ops-cve.out

echo "== IDOR scanner invalid-id guard =="
if python3 "$ROOT/beta_ops_idor_scan.py" --token-a tokenA --token-b tokenB --report-id '12oops' >/tmp/beta-ops-idor.out 2>&1; then
  echo "beta_ops_idor_scan invalid-id test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "report-id must be numeric" /tmp/beta-ops-idor.out

echo "== GraphQL IDOR battery invalid-id guard =="
if python3 "$ROOT/beta_ops_graphql_idor.py" --cookie-a a --cookie-b b --report-id 'oops' --report-gid gid >/tmp/beta-ops-graphql-idor.out 2>&1; then
  echo "beta_ops_graphql_idor invalid-id test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "report-id must be numeric" /tmp/beta-ops-graphql-idor.out

echo "== Smoke tests passed =="
