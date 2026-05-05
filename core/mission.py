#!/usr/bin/env python3

import argparse
import json
import os
from datetime import UTC, datetime

import hunt
from lifecycle import evaluate_target, write_outputs
from common import normalize_domain, repo_path, safe_join, sanitize_name, utcnow, validate_domain

try:
    from memory import save_finding, save_session, recall_target
except ImportError:
    save_finding = None
    save_session = None
    recall_target = None


MISSIONS_ROOT = repo_path("missions")


def load_scope(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def target_in_scope(target: str, scope: dict) -> bool:
    target = normalize_domain(target)
    denied = []
    for item in scope.get("out_of_scope", []):
        try:
            denied.append(normalize_domain(item, allow_wildcard=True))
        except ValueError:
            continue

    for item in denied:
        if item.startswith("*."):
            suffix = item[1:]
            if target.endswith(suffix):
                return False
        elif target == item:
            return False

    allowed = []
    for item in scope.get("in_scope_domains", []):
        try:
            allowed.append(normalize_domain(item, allow_wildcard=True))
        except ValueError:
            continue
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
        description="Autonomous mission runner for bountykit"
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
        "--edge-case", "--zero-day", dest="edge_case", action="store_true", help="Include edge-case fuzzer"
    )
    args = parser.parse_args()

    try:
        target = validate_domain(args.target, name="target")
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    scope = load_scope(args.scope_file)
    if not target_in_scope(target, scope):
        raise SystemExit(
            f"Target {target} is not explicitly listed in {args.scope_file}"
        )

    default_mission_name = f"{target}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    raw_mission_name = args.mission_name or default_mission_name
    mission_name = sanitize_name(raw_mission_name, fallback=default_mission_name)
    try:
        mission_dir = safe_join(MISSIONS_ROOT, mission_name)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    os.makedirs(mission_dir, exist_ok=True)
    state_path = os.path.join(mission_dir, "state.json")

    state = {
        "mission": mission_name,
        "target": target,
        "scope_file": os.path.abspath(args.scope_file),
        "started_at": utcnow(),
        "phase": "boundary",
        "decision": "RUNNING",
        "notes": [],
    }
    update_state(state_path, state)

    state["notes"].append("Scope file loaded and target allowlisted")
    if mission_name != raw_mission_name:
        state["notes"].append(f"Mission name sanitized from {raw_mission_name!r}")

    # ── Recall previous hunt memory ──────────────────────────────────────
    if recall_target:
        memory = recall_target(target)
        if memory and memory.get("finding_count", 0) > 0:
            state["notes"].append(
                f"Hunt memory: {memory['finding_count']} previous finding(s), "
                f"bug classes: {', '.join(memory.get('bug_classes_found', []))}"
            )
            state["prior_memory"] = memory

    state["phase"] = "survey"
    update_state(state_path, state)

    recon_ok = hunt.run_recon(target, quick=args.quick)
    state["recon_ok"] = recon_ok
    if not recon_ok:
        state["decision"] = "ROTATE"
        state["phase"] = "survey"
        state["notes"].append("Recon failed or yielded unusable output")
        update_state(state_path, state)
        raise SystemExit("Mission stopped after recon failure")

    state["phase"] = "probe"
    update_state(state_path, state)

    scan_ok = hunt.run_vuln_scan(target, quick=args.quick)
    state["scan_ok"] = scan_ok

    if args.cve_hunt:
        state["phase"] = "probe:cve"
        update_state(state_path, state)
        state["cve_ok"] = hunt.run_cve_hunt(target)

    if args.edge_case:
        state["phase"] = "probe:edge-case"
        update_state(state_path, state)
        state["edge_case_ok"] = hunt.run_edge_case_fuzzer(
            target, deep=not args.quick
        )

    state["phase"] = "screen"
    verdict = evaluate_target(target)
    json_path, md_path = write_outputs(target, verdict)
    state["verdict"] = verdict
    state["verdict_json"] = json_path
    state["verdict_markdown"] = md_path

    if verdict["decision"] == "PASS":
        state["phase"] = "brief"
        state["reports_generated"] = hunt.generate_reports(target)
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
        live_urls_path = repo_path("recon", target, "live", "urls.txt")
        if os.path.exists(live_urls_path):
            try:
                with open(live_urls_path, encoding="utf-8", errors="replace") as f:
                    endpoints_tested = [l.strip() for l in f if l.strip()][:50]
            except Exception:
                pass
        save_session(
            target=target,
            summary=f"Autonomous mission '{mission_name}' — decision: {state['decision']}",
            endpoints_tested=endpoints_tested,
            findings_count=len(verdict.get("findings", [])),
            notes="; ".join(state["notes"]),
        )

    # Save individual findings to memory
    if save_finding and verdict.get("findings"):
        for finding in verdict["findings"]:
            save_finding(
                target=target,
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
