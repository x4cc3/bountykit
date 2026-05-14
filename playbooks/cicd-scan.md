---
description: Review CI/CD pipelines for security issues — expression injection, supply-chain risks, and secret leaks. Usage: /cicd-scan --repo owner/repo
---

# /cicd-scan

Review GitHub Actions or other CI/CD workflows for security vulnerabilities.

## What This Does

Check for:

- expression injection in shell steps
- unsafe `pull_request_target` workflows
- hardcoded secrets
- unpinned third-party actions
- secret exposure via env vars or logs
- self-hosted runner risks
- cache poisoning
- supply-chain trust gaps

## Execution

Use the Disposable CLI/tools. This repo does not ship a CI/CD scanner.

## Output

Return only evidence-backed issues:

- workflow file and line
- triggering event
- vulnerable step
- realistic exploit path
- smallest safe remediation

## When to Use

- During `/survey` when GitHub repos are in scope
- When looking for lateral movement paths in an org
- As part of supply-chain attack surface assessment
