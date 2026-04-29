---
description: "Scan CI/CD pipelines for security issues — expression injection, supply chain risks, secret leaks. Usage: /cicd-scan --repo owner/repo"
---

# /cicd-scan

Scan GitHub Actions workflows for security vulnerabilities.

## What This Does

1. Fetches workflow YAML files from a GitHub repo, org, or local directory
2. Checks against 12 security rules covering:
   - Expression injection (CICD-001, CICD-009)
   - pull_request_target RCE (CICD-002)
   - Hardcoded secrets (CICD-003)
   - Unpinned third-party actions (CICD-004)
   - Secret exposure via env vars (CICD-005)
   - Self-hosted runner risks (CICD-007)
   - Cache poisoning (CICD-010)
   - Supply chain (CICD-012)
3. Generates a severity-grouped markdown report

## Usage

```bash
# Scan a GitHub repository
python3 core/cicd.py --repo owner/repo

# Scan all repos in an org
python3 core/cicd.py --org target-org

# Scan local workflow files
python3 core/cicd.py --dir /path/to/repo

# Save report
python3 core/cicd.py --repo owner/repo --output cicd-findings.md
```

## Environment

Set `GITHUB_TOKEN` for authenticated API access (higher rate limits, private repos):

```bash
export GITHUB_TOKEN=ghp_xxx
```

## When to Use

- During `/survey` when GitHub repos are in scope
- When looking for lateral movement paths in an org
- As part of supply chain attack surface assessment
