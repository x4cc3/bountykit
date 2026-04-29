#!/usr/bin/env python3
"""
intel.py — On-demand CVE + disclosure intelligence engine.

Fetches CVEs, disclosed reports, and known patterns for a target domain.
Combines GitHub Advisory, NVD, and HackerOne Hacktivity data with
hunt memory patterns to provide actionable intelligence.

Usage:
  python3 core/intel.py --target target.com
  python3 core/intel.py --target target.com --tech nextjs,graphql
  python3 core/intel.py --target target.com --program hackerone-program-handle
  python3 core/intel.py --target target.com --output intel-report.md
"""

import argparse
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime

from common import repo_path

try:
    from memory import recall_target, recall_bug_class, _load_db, PATTERNS_DB
except ImportError:
    recall_target = None
    recall_bug_class = None

# ─── SSL ──────────────────────────────────────────────────────────────────────
_SSL_CTX = ssl.create_default_context()
try:
    import certifi

    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ─── Tech detection from response headers / content ──────────────────────────
TECH_SIGNALS = {
    "nextjs": [
        r"x-powered-by:\s*Next\.js",
        r"__next",
        r"_next/static",
    ],
    "react": [r"__react", r"react-root", r"reactRoot"],
    "express": [r"x-powered-by:\s*Express"],
    "django": [r"csrfmiddlewaretoken", r"django"],
    "flask": [r"werkzeug", r"flask"],
    "rails": [r"x-powered-by:\s*Phusion", r"csrf-token.*authenticity"],
    "spring": [r"x-application-context", r"whitelabel error page"],
    "laravel": [r"XSRF-TOKEN.*laravel_session", r"laravel"],
    "wordpress": [r"wp-content", r"wp-json"],
    "graphql": [r"/graphql", r'"errors":\[{"message"'],
    "jwt": [r"eyJ[a-zA-Z0-9_-]+\.eyJ"],
    "oauth": [r"oauth", r"redirect_uri", r"/authorize"],
}


def fetch_url(url, headers=None, data=None, timeout=10):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body) if resp.headers.get_content_type() == "application/json" else body
    except Exception:
        return None


def detect_tech(target: str) -> list[str]:
    """Detect technologies by probing the target."""
    detected = []
    url = f"https://{target}"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=8, context=_SSL_CTX) as resp:
            headers_str = str(resp.headers)
            body = resp.read(50_000).decode("utf-8", errors="replace")
            combined = headers_str + "\n" + body
            for tech, patterns in TECH_SIGNALS.items():
                for pat in patterns:
                    if re.search(pat, combined, re.IGNORECASE):
                        detected.append(tech)
                        break
    except Exception as e:
        print(f"  {YELLOW}Could not probe {target}: {e}{RESET}")

    return list(set(detected))


def fetch_hacktivity(program: str = "", keywords: list | None = None) -> list[dict]:
    """Fetch disclosed reports from HackerOne Hacktivity."""
    results = []
    if program:
        query = """query {
          team(handle: "%s") {
            name
            url
          }
        }""" % program
        # Simple hacktivity search
        url = f"https://hackerone.com/graphql"
        payload = json.dumps({
            "query": """query {
              hacktivity_items(first: 20, order_by: {field: popular, direction: DESC}) {
                nodes {
                  ... on HacktivityDocument {
                    report { title severity_rating }
                  }
                }
              }
            }"""
        }).encode()
        data = fetch_url(
            url,
            headers={"Content-Type": "application/json"},
            data=payload,
        )
        if data and isinstance(data, dict):
            nodes = (
                data.get("data", {})
                .get("hacktivity_items", {})
                .get("nodes", [])
            )
            for node in nodes:
                report = node.get("report", {})
                if report:
                    results.append({
                        "title": report.get("title", ""),
                        "severity": report.get("severity_rating", "unknown"),
                        "source": "HackerOne Hacktivity",
                    })
    return results


def fetch_cves_for_tech(tech: str) -> list[dict]:
    """Fetch CVEs from NVD for a technology."""
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={urllib.parse.quote(tech)}&resultsPerPage=10"
    data = fetch_url(url, timeout=15)
    if not data or not isinstance(data, dict):
        return []

    results = []
    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id", "")
        desc = next(
            (d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"),
            "",
        )[:150]
        metrics = cve.get("metrics", {})
        score = None
        severity = "UNKNOWN"
        for key in ("cvssMetricV31", "cvssMetricV30"):
            if key in metrics and metrics[key]:
                m = metrics[key][0]
                score = m.get("cvssData", {}).get("baseScore")
                severity = m.get("cvssData", {}).get("baseSeverity", "UNKNOWN")
                break
        if score and score >= 7.0:
            results.append({
                "id": cve_id,
                "score": score,
                "severity": severity,
                "description": desc,
                "source": "NVD",
            })
    return results


def build_intel_report(
    target: str,
    tech_detected: list[str],
    cves: list[dict],
    hacktivity: list[dict],
    memory_data: dict | None = None,
) -> str:
    """Build a markdown intel report."""
    lines = [
        f"# Intel Report: {target}",
        f"Generated: {datetime.now(UTC).isoformat()[:19]}Z",
        "",
    ]

    # Tech stack
    lines.append("## Detected Technologies")
    if tech_detected:
        for t in tech_detected:
            lines.append(f"- {t}")
    else:
        lines.append("- None auto-detected (specify with --tech)")
    lines.append("")

    # CVEs
    lines.append("## Relevant CVEs (CVSS >= 7.0)")
    if cves:
        for c in cves:
            lines.append(f"- **{c['id']}** ({c['severity']}, {c['score']}): {c['description']}")
    else:
        lines.append("- No high-severity CVEs found for detected stack")
    lines.append("")

    # Hacktivity
    lines.append("## HackerOne Disclosed Reports")
    if hacktivity:
        for h in hacktivity:
            lines.append(f"- [{h['severity']}] {h['title']}")
    else:
        lines.append("- No disclosed reports found (try --program <handle>)")
    lines.append("")

    # Memory context
    if memory_data and memory_data.get("finding_count", 0) > 0:
        lines.append("## Hunt Memory (Previous Sessions)")
        lines.append(f"- Previous findings: {memory_data['finding_count']}")
        lines.append(f"- Bug classes found: {', '.join(memory_data.get('bug_classes_found', []))}")
        if memory_data.get("untested_endpoints"):
            lines.append(f"- Untested endpoints from last session:")
            for ep in memory_data["untested_endpoints"][:10]:
                lines.append(f"  - {ep}")
        if memory_data.get("patterns"):
            lines.append(f"- Patterns detected:")
            for p in memory_data["patterns"]:
                lines.append(f"  - {p.get('insight', '')}")
        lines.append("")

    # Recommended hunt approach
    lines.append("## Recommended Approach")
    if any(t in tech_detected for t in ["graphql"]):
        lines.append("- [ ] Run introspection query")
        lines.append("- [ ] Test node() for IDOR")
        lines.append("- [ ] Check batching for rate limit bypass")
    if any(t in tech_detected for t in ["nextjs", "react"]):
        lines.append("- [ ] Check API routes in /api/")
        lines.append("- [ ] Review getServerSideProps for SSRF")
        lines.append("- [ ] Look for middleware auth gaps")
    if any(t in tech_detected for t in ["jwt"]):
        lines.append("- [ ] Test alg:none")
        lines.append("- [ ] Test RS256→HS256 confusion")
        lines.append("- [ ] Check token expiration")
    if any(t in tech_detected for t in ["oauth"]):
        lines.append("- [ ] Check redirect_uri validation")
        lines.append("- [ ] Check for missing state/PKCE")
        lines.append("- [ ] Test open redirect chain")
    if not tech_detected:
        lines.append("- [ ] Run tech detection with httpx")
        lines.append("- [ ] Check standard quick wins (/.env, /.git, /graphql)")
        lines.append("- [ ] Run subdomain enumeration")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Intel engine for bountykit")
    parser.add_argument("--target", required=True, help="Target domain")
    parser.add_argument("--tech", help="Comma-separated tech hints (nextjs,graphql,jwt)")
    parser.add_argument("--program", default="", help="HackerOne program handle")
    parser.add_argument("--output", help="Write report to file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    print(f"\n{BOLD}[*]{RESET} Intel gathering for {CYAN}{args.target}{RESET}...\n")

    # Detect tech
    tech = []
    if args.tech:
        tech = [t.strip().lower() for t in args.tech.split(",")]
    else:
        print(f"  {CYAN}Auto-detecting tech stack...{RESET}")
        tech = detect_tech(args.target)
        if tech:
            print(f"  {GREEN}Detected: {', '.join(tech)}{RESET}")

    # Fetch CVEs
    cves = []
    for t in tech:
        print(f"  {CYAN}Fetching CVEs for {t}...{RESET}")
        cves.extend(fetch_cves_for_tech(t))

    # Fetch hacktivity
    hacktivity = fetch_hacktivity(program=args.program)

    # Memory context
    memory_data = None
    if recall_target:
        memory_data = recall_target(args.target)

    if args.json:
        print(json.dumps({
            "target": args.target,
            "tech": tech,
            "cves": cves,
            "hacktivity": hacktivity,
            "memory": memory_data,
        }, indent=2))
    else:
        report = build_intel_report(args.target, tech, cves, hacktivity, memory_data)
        print(report)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"{GREEN}[+]{RESET} Report written to {args.output}")


if __name__ == "__main__":
    main()
