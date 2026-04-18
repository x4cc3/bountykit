#!/usr/bin/env python3
"""
beta_ops_memory.py — Cross-session hunt memory system.

Remembers targets, findings, techniques, and patterns across sessions.
Hunt memory feeds future target selection and technique prioritization.

Usage:
  python3 beta_ops_memory.py --save-finding --target target.com --bug-class idor \
      --endpoint /api/v2/users --severity high --notes "horizontal IDOR on user endpoint"
  python3 beta_ops_memory.py --save-technique --name "uuid-swap" --bug-class idor \
      --payload '{"user_id":"VICTIM_UUID"}' --notes "Works on UUID-based REST APIs"
  python3 beta_ops_memory.py --save-session --target target.com
  python3 beta_ops_memory.py --recall --target target.com
  python3 beta_ops_memory.py --recall --bug-class ssrf
  python3 beta_ops_memory.py --recall-all
  python3 beta_ops_memory.py --stats
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime

from beta_ops_paths import repo_path

MEMORY_DIR = repo_path("hunt-memory")
FINDINGS_DB = os.path.join(MEMORY_DIR, "findings.json")
TECHNIQUES_DB = os.path.join(MEMORY_DIR, "techniques.json")
SESSIONS_DB = os.path.join(MEMORY_DIR, "sessions.json")
PATTERNS_DB = os.path.join(MEMORY_DIR, "patterns.json")

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _ensure_dir():
    os.makedirs(MEMORY_DIR, exist_ok=True)


def _load_db(path: str) -> list:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_db(path: str, data: list):
    _ensure_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


# ─── Save operations ─────────────────────────────────────────────────────────

def save_finding(
    target: str,
    bug_class: str,
    endpoint: str = "",
    severity: str = "medium",
    notes: str = "",
    chain: str = "",
    reported: bool = False,
    payout: float = 0.0,
):
    """Record a confirmed finding to memory."""
    db = _load_db(FINDINGS_DB)
    entry = {
        "id": len(db) + 1,
        "target": target,
        "bug_class": bug_class.lower().replace(" ", "_"),
        "endpoint": endpoint,
        "severity": severity.lower(),
        "notes": notes,
        "chain": chain,
        "reported": reported,
        "payout": payout,
        "timestamp": _now(),
    }
    db.append(entry)
    _save_db(FINDINGS_DB, db)
    print(f"{GREEN}[+]{RESET} Finding #{entry['id']} saved: {bug_class} on {target}")
    _update_patterns(entry)
    return entry


def save_technique(
    name: str,
    bug_class: str,
    payload: str = "",
    notes: str = "",
    success_rate: str = "unknown",
):
    """Record a reusable technique or bypass."""
    db = _load_db(TECHNIQUES_DB)
    entry = {
        "id": len(db) + 1,
        "name": name,
        "bug_class": bug_class.lower().replace(" ", "_"),
        "payload": payload,
        "notes": notes,
        "success_rate": success_rate,
        "times_used": 0,
        "times_succeeded": 0,
        "timestamp": _now(),
    }
    db.append(entry)
    _save_db(TECHNIQUES_DB, db)
    print(f"{GREEN}[+]{RESET} Technique saved: {name}")
    return entry


def save_session(
    target: str,
    endpoints_tested: list | None = None,
    endpoints_untested: list | None = None,
    findings_count: int = 0,
    notes: str = "",
    bug_classes_tried: list | None = None,
):
    """Record a hunt session for later pickup."""
    db = _load_db(SESSIONS_DB)
    entry = {
        "id": len(db) + 1,
        "target": target,
        "endpoints_tested": endpoints_tested or [],
        "endpoints_untested": endpoints_untested or [],
        "bug_classes_tried": bug_classes_tried or [],
        "findings_count": findings_count,
        "notes": notes,
        "timestamp": _now(),
    }
    db.append(entry)
    _save_db(SESSIONS_DB, db)
    print(f"{GREEN}[+]{RESET} Session saved for {target} ({findings_count} findings)")
    return entry


def _update_patterns(finding: dict):
    """Auto-detect cross-target patterns from findings."""
    db = _load_db(PATTERNS_DB)
    findings = _load_db(FINDINGS_DB)

    bug_class = finding["bug_class"]
    endpoint_pattern = _extract_endpoint_pattern(finding["endpoint"])

    # Check if this bug class has appeared on multiple targets
    targets_with_class = set(
        f["target"] for f in findings if f["bug_class"] == bug_class
    )
    if len(targets_with_class) >= 2:
        pattern_key = f"cross-target:{bug_class}"
        existing = next((p for p in db if p["key"] == pattern_key), None)
        if existing:
            existing["targets"] = list(targets_with_class)
            existing["count"] = len(targets_with_class)
            existing["last_seen"] = _now()
        else:
            db.append(
                {
                    "key": pattern_key,
                    "type": "cross-target",
                    "bug_class": bug_class,
                    "targets": list(targets_with_class),
                    "count": len(targets_with_class),
                    "insight": f"{bug_class} found on {len(targets_with_class)} different targets — strong pattern",
                    "last_seen": _now(),
                }
            )

    # Check if same endpoint pattern repeats
    if endpoint_pattern:
        matching = [
            f
            for f in findings
            if _extract_endpoint_pattern(f["endpoint"]) == endpoint_pattern
            and f["target"] != finding["target"]
        ]
        if matching:
            pattern_key = f"endpoint-pattern:{endpoint_pattern}:{bug_class}"
            existing = next((p for p in db if p["key"] == pattern_key), None)
            if not existing:
                db.append(
                    {
                        "key": pattern_key,
                        "type": "endpoint-pattern",
                        "bug_class": bug_class,
                        "pattern": endpoint_pattern,
                        "insight": f"Endpoint pattern '{endpoint_pattern}' vulnerable to {bug_class} across targets",
                        "last_seen": _now(),
                    }
                )

    _save_db(PATTERNS_DB, db)


def _extract_endpoint_pattern(endpoint: str) -> str:
    """Normalize an endpoint to a pattern (strip IDs, UUIDs)."""
    import re

    if not endpoint:
        return ""
    # Replace UUIDs
    pattern = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "{uuid}",
        endpoint,
    )
    # Replace numeric IDs
    pattern = re.sub(r"/\d+", "/{id}", pattern)
    # Strip query strings
    pattern = pattern.split("?")[0]
    return pattern


# ─── Recall operations ────────────────────────────────────────────────────────

def recall_target(target: str) -> dict:
    """Get everything we know about a target."""
    findings = [f for f in _load_db(FINDINGS_DB) if f["target"] == target]
    sessions = [s for s in _load_db(SESSIONS_DB) if s["target"] == target]
    techniques = _load_db(TECHNIQUES_DB)

    # Find relevant techniques based on past bug classes
    bug_classes = set(f["bug_class"] for f in findings)
    relevant_techniques = [t for t in techniques if t["bug_class"] in bug_classes]

    # Find relevant patterns
    patterns = [
        p
        for p in _load_db(PATTERNS_DB)
        if target in p.get("targets", []) or p.get("bug_class", "") in bug_classes
    ]

    # Build untested endpoints from last session
    untested = []
    if sessions:
        last_session = max(sessions, key=lambda s: s["timestamp"])
        untested = last_session.get("endpoints_untested", [])

    return {
        "target": target,
        "findings": findings,
        "finding_count": len(findings),
        "sessions": sessions,
        "session_count": len(sessions),
        "bug_classes_found": list(bug_classes),
        "relevant_techniques": relevant_techniques,
        "patterns": patterns,
        "untested_endpoints": untested,
    }


def recall_bug_class(bug_class: str) -> dict:
    """Get all findings and techniques for a bug class."""
    bc = bug_class.lower().replace(" ", "_")
    findings = [f for f in _load_db(FINDINGS_DB) if f["bug_class"] == bc]
    techniques = [t for t in _load_db(TECHNIQUES_DB) if t["bug_class"] == bc]
    patterns = [p for p in _load_db(PATTERNS_DB) if p.get("bug_class") == bc]

    return {
        "bug_class": bc,
        "findings": findings,
        "finding_count": len(findings),
        "targets_affected": list(set(f["target"] for f in findings)),
        "techniques": techniques,
        "patterns": patterns,
    }


def recall_all() -> dict:
    """Full memory dump."""
    findings = _load_db(FINDINGS_DB)
    techniques = _load_db(TECHNIQUES_DB)
    sessions = _load_db(SESSIONS_DB)
    patterns = _load_db(PATTERNS_DB)
    return {
        "findings": findings,
        "techniques": techniques,
        "sessions": sessions,
        "patterns": patterns,
        "stats": {
            "total_findings": len(findings),
            "total_techniques": len(techniques),
            "total_sessions": len(sessions),
            "total_patterns": len(patterns),
            "targets_hunted": len(set(f["target"] for f in findings)),
            "bug_classes": list(set(f["bug_class"] for f in findings)),
        },
    }


def get_stats() -> dict:
    """Summary statistics."""
    findings = _load_db(FINDINGS_DB)
    techniques = _load_db(TECHNIQUES_DB)
    sessions = _load_db(SESSIONS_DB)
    patterns = _load_db(PATTERNS_DB)

    # Payout stats
    total_payout = sum(f.get("payout", 0) for f in findings)
    reported = [f for f in findings if f.get("reported")]

    # Bug class distribution
    class_counts = {}
    for f in findings:
        bc = f["bug_class"]
        class_counts[bc] = class_counts.get(bc, 0) + 1

    # Severity distribution
    sev_counts = {}
    for f in findings:
        sev = f.get("severity", "unknown")
        sev_counts[sev] = sev_counts.get(sev, 0) + 1

    return {
        "total_findings": len(findings),
        "total_reported": len(reported),
        "total_payout": total_payout,
        "total_techniques": len(techniques),
        "total_sessions": len(sessions),
        "total_patterns": len(patterns),
        "targets_hunted": len(set(f["target"] for f in findings)),
        "bug_class_distribution": class_counts,
        "severity_distribution": sev_counts,
        "top_bug_classes": sorted(class_counts.items(), key=lambda x: -x[1])[:5],
    }


def print_stats():
    """Pretty-print stats."""
    stats = get_stats()
    print(f"\n{BOLD}{'=' * 50}{RESET}")
    print(f"{BOLD}  Hunt Memory Stats{RESET}")
    print(f"{BOLD}{'=' * 50}{RESET}\n")
    print(f"  Findings:    {stats['total_findings']}")
    print(f"  Reported:    {stats['total_reported']}")
    print(f"  Payout:      ${stats['total_payout']:,.2f}")
    print(f"  Techniques:  {stats['total_techniques']}")
    print(f"  Sessions:    {stats['total_sessions']}")
    print(f"  Patterns:    {stats['total_patterns']}")
    print(f"  Targets:     {stats['targets_hunted']}")
    if stats["top_bug_classes"]:
        print(f"\n  Top bug classes:")
        for bc, count in stats["top_bug_classes"]:
            print(f"    {bc}: {count}")
    if stats["severity_distribution"]:
        print(f"\n  Severity breakdown:")
        for sev, count in sorted(stats["severity_distribution"].items()):
            print(f"    {sev}: {count}")
    print()


def print_recall(data: dict, label: str = ""):
    """Pretty-print recall results."""
    print(f"\n{BOLD}{'=' * 50}{RESET}")
    print(f"{BOLD}  Hunt Memory: {label}{RESET}")
    print(f"{BOLD}{'=' * 50}{RESET}")
    print(json.dumps(data, indent=2))
    print()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Hunt memory system")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--save-finding", action="store_true")
    group.add_argument("--save-technique", action="store_true")
    group.add_argument("--save-session", action="store_true")
    group.add_argument("--recall", action="store_true")
    group.add_argument("--recall-all", action="store_true")
    group.add_argument("--stats", action="store_true")

    parser.add_argument("--target", help="Target domain")
    parser.add_argument("--bug-class", help="Bug class (idor, ssrf, xss, etc.)")
    parser.add_argument("--endpoint", default="")
    parser.add_argument("--severity", default="medium")
    parser.add_argument("--notes", default="")
    parser.add_argument("--chain", default="")
    parser.add_argument("--reported", action="store_true")
    parser.add_argument("--payout", type=float, default=0.0)
    parser.add_argument("--name", help="Technique name")
    parser.add_argument("--payload", default="")
    parser.add_argument("--success-rate", default="unknown")
    parser.add_argument("--endpoints-tested", nargs="*", default=[])
    parser.add_argument("--endpoints-untested", nargs="*", default=[])
    parser.add_argument("--bug-classes-tried", nargs="*", default=[])
    parser.add_argument("--findings-count", type=int, default=0)

    args = parser.parse_args()

    if args.save_finding:
        if not args.target or not args.bug_class:
            parser.error("--save-finding requires --target and --bug-class")
        save_finding(
            target=args.target,
            bug_class=args.bug_class,
            endpoint=args.endpoint,
            severity=args.severity,
            notes=args.notes,
            chain=args.chain,
            reported=args.reported,
            payout=args.payout,
        )
    elif args.save_technique:
        if not args.name or not args.bug_class:
            parser.error("--save-technique requires --name and --bug-class")
        save_technique(
            name=args.name,
            bug_class=args.bug_class,
            payload=args.payload,
            notes=args.notes,
            success_rate=args.success_rate,
        )
    elif args.save_session:
        if not args.target:
            parser.error("--save-session requires --target")
        save_session(
            target=args.target,
            endpoints_tested=args.endpoints_tested,
            endpoints_untested=args.endpoints_untested,
            findings_count=args.findings_count,
            notes=args.notes,
            bug_classes_tried=args.bug_classes_tried,
        )
    elif args.recall:
        if args.target:
            data = recall_target(args.target)
            print_recall(data, f"Target: {args.target}")
        elif args.bug_class:
            data = recall_bug_class(args.bug_class)
            print_recall(data, f"Bug class: {args.bug_class}")
        else:
            parser.error("--recall requires --target or --bug-class")
    elif args.recall_all:
        data = recall_all()
        print_recall(data, "Full Memory")
    elif args.stats:
        print_stats()


if __name__ == "__main__":
    main()
