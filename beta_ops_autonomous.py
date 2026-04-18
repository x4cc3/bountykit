#!/usr/bin/env python3

import argparse
import json
import os
import re
from datetime import UTC, datetime

import beta_ops_hunt
from beta_ops_lifecycle import evaluate_target, write_outputs
from beta_ops_paths import repo_path

try:
    from beta_ops_memory import save_finding, save_session, recall_target
except ImportError:
    save_finding = None
    save_session = None
    recall_target = None


MISSIONS_ROOT = repo_path("missions")
TARGET_PATTERN = re.compile(r"^[a-zA-Z0-9.-]+$")


def utcnow() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def load_scope(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def target_in_scope(target: str, scope: dict) -> bool:
    denied = scope.get("out_of_scope", [])

    for item in denied:
        if item.startswith("*."):
            suffix = item[1:]
            if target.endswith(suffix):
                return False
        elif target == item:
            return False

    allowed = scope.get("in_scope_domains", [])
    for item in allowed:
        if item.startswith("*."):
            suffix = item[1:]
            if target.endswith(suffix):
                return True
        elif target == item:
            return True
    return False


def update_state(state_path: str, state: dict) -> None:
    with open(state_path, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Autonomous mission runner for beta-ops"
    )
    parser.add_argument("--target", required=True, help="In-scope target domain")
    parser.add_argument(
        "--scope-file", required=True, help="JSON file with explicit scope allowlist"
    )
    parser.add_argument("--mission-name", help="Stable mission name")
    parser.add_argument(
        "--quick", action="store_true", help="Use quicker recon/scan settings"
    )
    parser.add_argument("--cve-hunt", action="store_true", help="Include CVE hunter")
    parser.add_argument(
        "--zero-day", action="store_true", help="Include zero-day fuzzer"
    )
    args = parser.parse_args()

    if not TARGET_PATTERN.match(args.target):
        raise SystemExit("Refusing target with unsupported characters")

    scope = load_scope(args.scope_file)
    if not target_in_scope(args.target, scope):
        raise SystemExit(
            f"Target {args.target} is not explicitly listed in {args.scope_file}"
        )

    mission_name = (
        args.mission_name
        or f"{args.target}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    )
    mission_dir = os.path.join(MISSIONS_ROOT, mission_name)
    os.makedirs(mission_dir, exist_ok=True)
    state_path = os.path.join(mission_dir, "state.json")

    state = {
        "mission": mission_name,
        "target": args.target,
        "scope_file": os.path.abspath(args.scope_file),
        "started_at": utcnow(),
        "phase": "boundary",
        "decision": "RUNNING",
        "notes": [],
    }
    update_state(state_path, state)

    state["notes"].append("Scope file loaded and target allowlisted")

    # ── Recall previous hunt memory ──────────────────────────────────────
    if recall_target:
        memory = recall_target(args.target)
        if memory and memory.get("finding_count", 0) > 0:
            state["notes"].append(
                f"Hunt memory: {memory['finding_count']} previous finding(s), "
                f"bug classes: {', '.join(memory.get('bug_classes_found', []))}"
            )
            state["prior_memory"] = memory

    state["phase"] = "survey"
    update_state(state_path, state)

    recon_ok = beta_ops_hunt.run_recon(args.target, quick=args.quick)
    state["recon_ok"] = recon_ok
    if not recon_ok:
        state["decision"] = "ROTATE"
        state["phase"] = "survey"
        state["notes"].append("Recon failed or yielded unusable output")
        update_state(state_path, state)
        raise SystemExit("Mission stopped after recon failure")

    state["phase"] = "probe"
    update_state(state_path, state)

    scan_ok = beta_ops_hunt.run_vuln_scan(args.target, quick=args.quick)
    state["scan_ok"] = scan_ok

    if args.cve_hunt:
        state["phase"] = "probe:cve"
        update_state(state_path, state)
        state["cve_ok"] = beta_ops_hunt.run_cve_hunt(args.target)

    if args.zero_day:
        state["phase"] = "probe:zero-day"
        update_state(state_path, state)
        state["zero_day_ok"] = beta_ops_hunt.run_zero_day_fuzzer(
            args.target, deep=not args.quick
        )

    state["phase"] = "screen"
    verdict = evaluate_target(args.target)
    json_path, md_path = write_outputs(args.target, verdict)
    state["verdict"] = verdict
    state["verdict_json"] = json_path
    state["verdict_markdown"] = md_path

    if verdict["decision"] == "PASS":
        state["phase"] = "brief"
        state["reports_generated"] = beta_ops_hunt.generate_reports(args.target)
        state["decision"] = "REPORT READY"
    elif verdict["decision"] in {"CHAIN REQUIRED", "DOWNGRADE"}:
        state["decision"] = verdict["decision"]
    else:
        state["decision"] = "ROTATE"

    state["finished_at"] = utcnow()
    update_state(state_path, state)

    # ── Save session to hunt memory ──────────────────────────────────────
    if save_session:
        endpoints_tested = []
        if os.path.exists(f"results/{args.target}/urls.txt"):
            try:
                with open(f"results/{args.target}/urls.txt") as f:
                    endpoints_tested = [l.strip() for l in f if l.strip()][:50]
            except Exception:
                pass
        save_session(
            target=args.target,
            summary=f"Autonomous mission '{mission_name}' — decision: {state['decision']}",
            endpoints_tested=endpoints_tested,
            findings_count=len(verdict.get("findings", [])),
            notes="; ".join(state["notes"]),
        )

    # Save individual findings to memory
    if save_finding and verdict.get("findings"):
        for finding in verdict["findings"]:
            save_finding(
                target=args.target,
                bug_class=finding.get("bug_class", "unknown"),
                severity=finding.get("severity", "info"),
                endpoint=finding.get("endpoint", ""),
                evidence=finding.get("evidence", ""),
                status=finding.get("status", "unverified"),
            )

    print(json.dumps(state, indent=2))
    print(f"\nMission state: {state_path}")


if __name__ == "__main__":
    main()
