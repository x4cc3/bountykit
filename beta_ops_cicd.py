#!/usr/bin/env python3
"""
beta_ops_cicd.py — CI/CD pipeline security scanner.

Scans GitHub Actions workflow files for common security issues:
expression injection, secret leaks, supply chain attacks, and more.

Usage:
  python3 beta_ops_cicd.py --org target-org
  python3 beta_ops_cicd.py --repo owner/repo
  python3 beta_ops_cicd.py --dir /path/to/workflows
  python3 beta_ops_cicd.py --org target-org --output cicd-findings.md
"""

import argparse
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime

from beta_ops_paths import repo_path

_SSL_CTX = ssl.create_default_context()
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ─── Rules ────────────────────────────────────────────────────────────────────

RULES = [
    {
        "id": "CICD-001",
        "name": "Expression injection in run",
        "severity": "critical",
        "pattern": r"run:.*\$\{\{\s*github\.event\.(issue|pull_request|comment|review|discussion)\.(title|body|head\.ref|label\.name)",
        "description": "User-controlled GitHub event data injected into shell command",
        "cwe": "CWE-78",
    },
    {
        "id": "CICD-002",
        "name": "pull_request_target with checkout",
        "severity": "critical",
        "pattern": r"on:\s*pull_request_target",
        "extra_check": r"actions/checkout.*ref.*\$\{\{\s*github\.event\.pull_request\.head",
        "description": "PR code checked out and executed with write token — full RCE on repo",
        "cwe": "CWE-94",
    },
    {
        "id": "CICD-003",
        "name": "Hardcoded secret in workflow",
        "severity": "high",
        "pattern": r"(password|token|secret|key|api_key)\s*[:=]\s*['\"][^$\s{][^'\"]{8,}['\"]",
        "description": "Potential hardcoded secret in workflow file",
        "cwe": "CWE-798",
    },
    {
        "id": "CICD-004",
        "name": "Unpinned third-party action",
        "severity": "medium",
        "pattern": r"uses:\s+(?!actions/|github/)[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+@(main|master|v\d+)\b",
        "description": "Third-party action referenced by mutable tag, not commit SHA",
        "cwe": "CWE-829",
    },
    {
        "id": "CICD-005",
        "name": "Secret in environment variable",
        "severity": "medium",
        "pattern": r"env:\s*\n\s+\w+:\s*\$\{\{\s*secrets\.\w+\s*\}\}",
        "description": "Secrets exposed as env vars may leak via /proc or debug output",
        "cwe": "CWE-200",
    },
    {
        "id": "CICD-006",
        "name": "Artifact upload without retention",
        "severity": "low",
        "pattern": r"actions/upload-artifact",
        "description": "Artifacts uploaded without explicit retention-days — may persist with secrets",
        "cwe": "CWE-922",
    },
    {
        "id": "CICD-007",
        "name": "Self-hosted runner",
        "severity": "medium",
        "pattern": r"runs-on:\s*self-hosted",
        "description": "Self-hosted runners have persistent state — previous job artifacts/creds may remain",
        "cwe": "CWE-269",
    },
    {
        "id": "CICD-008",
        "name": "GITHUB_TOKEN with write permissions",
        "severity": "medium",
        "pattern": r"permissions:\s*\n\s+(contents|packages|issues|pull-requests):\s*write",
        "description": "Workflow has write permissions that may be exploitable",
        "cwe": "CWE-250",
    },
    {
        "id": "CICD-009",
        "name": "Expression injection in name/title",
        "severity": "high",
        "pattern": r"(name|title):\s*.*\$\{\{\s*github\.event\.(issue|pull_request|comment)\.(title|body)",
        "description": "User-controlled data in workflow name — may appear in logs/notifications",
        "cwe": "CWE-79",
    },
    {
        "id": "CICD-010",
        "name": "Cache poisoning risk",
        "severity": "medium",
        "pattern": r"actions/cache",
        "extra_check": r"on:\s*(pull_request_target|issue_comment)",
        "description": "Cache used with untrusted trigger — cache may be poisoned by PR author",
        "cwe": "CWE-345",
    },
    {
        "id": "CICD-011",
        "name": "workflow_run chaining",
        "severity": "medium",
        "pattern": r"on:\s*workflow_run",
        "description": "Workflow triggered by another workflow — check if the triggering workflow is exploitable",
        "cwe": "CWE-284",
    },
    {
        "id": "CICD-012",
        "name": "Curl piped to shell",
        "severity": "high",
        "pattern": r"curl\s.*\|\s*(bash|sh|zsh)",
        "description": "Remote script downloaded and executed directly — supply chain risk",
        "cwe": "CWE-829",
    },
]


def scan_workflow_content(content: str, filename: str = "") -> list[dict]:
    """Scan a workflow YAML content against rules."""
    findings = []
    for rule in RULES:
        matches = list(re.finditer(rule["pattern"], content, re.IGNORECASE | re.MULTILINE))
        if matches:
            # Check extra_check if present
            if "extra_check" in rule:
                if not re.search(rule["extra_check"], content, re.IGNORECASE | re.MULTILINE):
                    continue

            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                findings.append({
                    "rule_id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "cwe": rule["cwe"],
                    "file": filename,
                    "line": line_num,
                    "match": match.group(0)[:120],
                })
    return findings


def scan_directory(path: str) -> list[dict]:
    """Scan a directory of workflow files."""
    findings = []
    workflow_dir = path
    if os.path.isdir(os.path.join(path, ".github", "workflows")):
        workflow_dir = os.path.join(path, ".github", "workflows")

    if not os.path.isdir(workflow_dir):
        print(f"{YELLOW}[!]{RESET} No workflows directory found at {workflow_dir}")
        return findings

    for filename in os.listdir(workflow_dir):
        if filename.endswith((".yml", ".yaml")):
            filepath = os.path.join(workflow_dir, filename)
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            file_findings = scan_workflow_content(content, filename)
            findings.extend(file_findings)
            if file_findings:
                print(f"  {RED}[!]{RESET} {filename}: {len(file_findings)} finding(s)")
            else:
                print(f"  {GREEN}[✓]{RESET} {filename}: clean")
    return findings


def fetch_github_workflows(owner_repo: str) -> list[tuple[str, str]]:
    """Fetch workflow files from a GitHub repo."""
    url = f"https://api.github.com/repos/{owner_repo}/contents/.github/workflows"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10, context=_SSL_CTX) as resp:
            files = json.loads(resp.read().decode())
    except Exception as e:
        print(f"{RED}[-]{RESET} Could not fetch workflows: {e}")
        return []

    results = []
    for f in files:
        if f.get("name", "").endswith((".yml", ".yaml")):
            dl_url = f.get("download_url", "")
            if dl_url:
                try:
                    r = urllib.request.Request(dl_url, headers=headers)
                    with urllib.request.urlopen(r, timeout=10, context=_SSL_CTX) as resp:
                        content = resp.read().decode()
                    results.append((f["name"], content))
                except Exception:
                    pass
    return results


def scan_repo(owner_repo: str) -> list[dict]:
    """Scan a GitHub repo's workflows."""
    print(f"  {CYAN}Fetching workflows for {owner_repo}...{RESET}")
    workflows = fetch_github_workflows(owner_repo)
    if not workflows:
        print(f"  {YELLOW}No workflows found{RESET}")
        return []

    findings = []
    for filename, content in workflows:
        file_findings = scan_workflow_content(content, f"{owner_repo}/.github/workflows/{filename}")
        findings.extend(file_findings)
        if file_findings:
            print(f"  {RED}[!]{RESET} {filename}: {len(file_findings)} finding(s)")
        else:
            print(f"  {GREEN}[✓]{RESET} {filename}: clean")
    return findings


def scan_org(org: str) -> list[dict]:
    """Scan all repos in a GitHub org."""
    print(f"  {CYAN}Fetching repos for org {org}...{RESET}")
    url = f"https://api.github.com/orgs/{org}/repos?per_page=30&sort=updated"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10, context=_SSL_CTX) as resp:
            repos = json.loads(resp.read().decode())
    except Exception as e:
        print(f"{RED}[-]{RESET} Could not fetch org repos: {e}")
        return []

    findings = []
    for repo in repos:
        full_name = repo.get("full_name", "")
        if full_name:
            findings.extend(scan_repo(full_name))
    return findings


def format_report(findings: list[dict], target: str) -> str:
    """Format findings as a markdown report."""
    lines = [
        f"# CI/CD Security Scan: {target}",
        f"Generated: {datetime.now(UTC).isoformat()[:19]}Z",
        f"Rules checked: {len(RULES)}",
        f"Findings: {len(findings)}",
        "",
    ]

    if not findings:
        lines.append("No security issues found in CI/CD workflows.")
        return "\n".join(lines)

    # Group by severity
    by_sev = {}
    for f in findings:
        by_sev.setdefault(f["severity"], []).append(f)

    for sev in ["critical", "high", "medium", "low"]:
        items = by_sev.get(sev, [])
        if items:
            lines.append(f"## {sev.upper()} ({len(items)})")
            for item in items:
                lines.append(f"### {item['rule_id']}: {item['name']}")
                lines.append(f"- **File:** {item['file']}:{item['line']}")
                lines.append(f"- **CWE:** {item['cwe']}")
                lines.append(f"- **Description:** {item['description']}")
                lines.append(f"- **Match:** `{item['match']}`")
                lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="CI/CD pipeline security scanner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--org", help="GitHub organization to scan")
    group.add_argument("--repo", help="GitHub repo (owner/repo) to scan")
    group.add_argument("--dir", help="Local directory with workflow files")
    parser.add_argument("--output", help="Write report to file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    print(f"\n{BOLD}[*]{RESET} CI/CD Security Scanner\n")

    if args.dir:
        findings = scan_directory(args.dir)
        target = args.dir
    elif args.repo:
        findings = scan_repo(args.repo)
        target = args.repo
    else:
        findings = scan_org(args.org)
        target = args.org

    crit = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    med = sum(1 for f in findings if f["severity"] == "medium")

    print(f"\n{BOLD}Results:{RESET} {len(findings)} findings ({RED}{crit} critical{RESET}, {YELLOW}{high} high{RESET}, {CYAN}{med} medium{RESET})")

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        report = format_report(findings, target)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"{GREEN}[+]{RESET} Report written to {args.output}")
        elif findings:
            print(f"\n{report}")


if __name__ == "__main__":
    main()
