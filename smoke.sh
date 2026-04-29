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

echo "== Map custom output =="
python3 "$CORE/map.py" --target example.com --type website --tech nextjs --output "/tmp/bountykit-smoke/map.md"

echo "== Bootstrap arg handling =="
if "$ROOT/bootstrap.sh" --client >/tmp/bountykit-bootstrap.out 2>&1; then
  echo "bootstrap missing-arg test unexpectedly succeeded" >&2
  exit 1
fi
grep -q "Missing value for --client" /tmp/bountykit-bootstrap.out

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
