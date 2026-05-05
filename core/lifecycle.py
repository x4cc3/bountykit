#!/usr/bin/env python3

import argparse
import json
import os
import re

from common import repo_path, utcnow


FINDINGS_ROOT = repo_path("findings")
EVIDENCE_FILES = {
    "request": ["request.http", "request.txt"],
    "response": ["response.http", "response.txt", "response.json"],
    "scope": ["scope.txt", "scope.md", "scope.json"],
    "victim": ["victim.txt", "object.txt", "target_object.txt"],
    "negative_control": ["negative_control.txt", "negative-control.txt"],
    "impact": ["impact.txt", "impact.md"],
    "metadata": ["metadata.json"],
}
CHAIN_CLASSES = {"ssrf", "redirect", "open_redirect", "cors", "clickjacking"}
PASS_CLASSES = {"idor", "auth_bypass", "authz", "access_control", "exposure"}
HIGH_NOISE_CLASSES = {
    "xss",
    "sqli",
    "graphql",
    "graphql_auth",
    "oauth",
    "oidc",
    "csrf",
    "file_upload",
    "ai",
    "prompt_injection",
    "subdomain_takeover",
}
MIN_EVIDENCE_BYTES = {
    "scope": 10,
    "request": 20,
    "response": 20,
    "victim": 3,
    "negative_control": 10,
    "impact": 20,
}
PLACEHOLDER_WORDS = {"todo", "placeholder", "example only", "tbd", "fill me"}
REQUEST_RE = re.compile(r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+\S+\s+HTTP/", re.I | re.M)
RESPONSE_RE = re.compile(r"^HTTP/\S+\s+\d{3}\b", re.I | re.M)


def normalize_bug_class(value: str) -> str:
    bug_class = (value or "unknown").strip().lower().replace("-", "_")
    aliases = {
        "bola": "idor",
        "broken_object_level_authorization": "idor",
        "access control": "access_control",
        "auth bypass": "auth_bypass",
        "authorization": "authz",
        "open redirect": "open_redirect",
        "graphql auth": "graphql_auth",
        "prompt injection": "prompt_injection",
        "file upload": "file_upload",
        "subdomain takeover": "subdomain_takeover",
    }
    return aliases.get(bug_class, bug_class)


def get_required_evidence_keys(bug_class: str) -> set[str]:
    required = {"scope", "request", "response"}

    if bug_class in PASS_CLASSES or bug_class in HIGH_NOISE_CLASSES:
        required.add("victim")

    if bug_class in HIGH_NOISE_CLASSES:
        required.add("impact")

    if bug_class in {"idor", "auth_bypass", "authz", "access_control", "csrf"}:
        required.add("negative_control")

    return required


def get_missing_keys(checks: dict[str, bool], required_keys: set[str]) -> list[str]:
    return sorted(name for name in required_keys if not checks.get(name, False))


def read_text(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read().strip()


def load_metadata(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def evidence_has_content(path: str | None, key: str) -> bool:
    if not path or not os.path.isfile(path):
        return False
    content = read_text(path)
    if len(content) < MIN_EVIDENCE_BYTES.get(key, 1):
        return False
    lowered = content.lower()
    if any(word in lowered for word in PLACEHOLDER_WORDS):
        return False
    if key == "request":
        return bool(REQUEST_RE.search(content) or re.search(r"https?://", content, re.I))
    if key == "response":
        body = content.lstrip()
        return bool(
            RESPONSE_RE.search(content)
            or body.startswith(("{", "["))
            or len(content) >= 80
        )
    return True


def first_existing(base_dir: str, names: list[str]) -> str | None:
    for name in names:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            return path
    return None


def collect_evidence_pack(pack_dir: str) -> dict:
    evidence = {}
    for key, names in EVIDENCE_FILES.items():
        evidence[key] = first_existing(pack_dir, names)
    metadata = load_metadata(evidence["metadata"]) if evidence["metadata"] else {}
    return {
        "path": pack_dir,
        "name": os.path.basename(pack_dir),
        "evidence": evidence,
        "metadata": metadata,
    }


def score_pack(pack: dict) -> dict:
    evidence = pack["evidence"]
    metadata = pack["metadata"]
    bug_class = normalize_bug_class(str(metadata.get("bug_class", pack["name"])))

    checks = {
        "scope": evidence_has_content(evidence["scope"], "scope"),
        "request": evidence_has_content(evidence["request"], "request"),
        "response": evidence_has_content(evidence["response"], "response"),
        "victim": evidence_has_content(evidence["victim"], "victim"),
        "negative_control": evidence_has_content(evidence["negative_control"], "negative_control"),
        "impact": evidence_has_content(evidence["impact"], "impact"),
    }
    score = sum(1 for passed in checks.values() if passed)
    required_keys = get_required_evidence_keys(bug_class)
    missing_required = get_missing_keys(checks, required_keys)

    if missing_required:
        decision = "KILL"
        reason = f"Missing required proof for {bug_class}: {', '.join(missing_required)}"
        confidence = "LOW"
    elif bug_class in CHAIN_CLASSES and not checks["impact"]:
        decision = "CHAIN REQUIRED"
        reason = "Bug class usually needs stronger impact proof"
        confidence = "MEDIUM"
    elif bug_class in HIGH_NOISE_CLASSES and not checks["negative_control"]:
        decision = "DOWNGRADE"
        reason = "High-noise bug class still needs a negative control for a final pass"
        confidence = "MEDIUM"
    elif score >= 6:
        decision = "PASS"
        reason = "Evidence pack is complete enough for validation"
        confidence = "HIGH"
    elif score >= 4:
        if bug_class in PASS_CLASSES:
            decision = "DOWNGRADE"
            reason = "Strong bug class but evidence pack is incomplete"
            confidence = "MEDIUM"
        else:
            decision = "CHAIN REQUIRED"
            reason = "Partial evidence exists but needs stronger proof or chain"
            confidence = "MEDIUM"
    else:
        decision = "KILL"
        reason = "Evidence pack is too incomplete"
        confidence = "LOW"

    return {
        "name": pack["name"],
        "path": pack["path"],
        "bug_class": bug_class,
        "checks": checks,
        "required_checks": sorted(required_keys),
        "missing_required": missing_required,
        "score": score,
        "decision": decision,
        "confidence": confidence,
        "reason": reason,
    }


def fallback_artifacts(target_dir: str) -> list[dict]:
    artifacts = []
    for entry in sorted(os.listdir(target_dir)):
        path = os.path.join(target_dir, entry)
        if os.path.isdir(path):
            continue
        if not os.path.isfile(path):
            continue
        content = read_text(path)
        if not content:
            continue
        artifacts.append(
            {
                "name": entry,
                "path": path,
                "bug_class": "unknown",
                "checks": {},
                "score": 1,
                "decision": "DOWNGRADE",
                "confidence": "LOW",
                "reason": "Loose artifact without structured evidence pack",
            }
        )
    return artifacts


def evaluate_target(target: str) -> dict:
    target_dir = os.path.join(FINDINGS_ROOT, target)
    result = {
        "target": target,
        "evaluated_at": utcnow(),
        "decision": "KILL",
        "confidence": "LOW",
        "reason": "No findings directory",
        "next_action": "Rotate or collect recon first",
        "packs": [],
        "verdict_totals": {"PASS": 0, "CHAIN REQUIRED": 0, "DOWNGRADE": 0, "KILL": 0},
    }
    if not os.path.isdir(target_dir):
        return result

    pack_results = []
    for entry in sorted(os.listdir(target_dir)):
        path = os.path.join(target_dir, entry)
        if not os.path.isdir(path):
            continue
        if any(first_existing(path, names) for names in EVIDENCE_FILES.values()):
            pack_results.append(score_pack(collect_evidence_pack(path)))

    if not pack_results:
        pack_results = fallback_artifacts(target_dir)

    result["packs"] = pack_results
    for pack in pack_results:
        result["verdict_totals"][pack["decision"]] += 1

    if result["verdict_totals"]["PASS"]:
        result["decision"] = "PASS"
        result["confidence"] = "HIGH"
        result["reason"] = "At least one evidence pack is validation-ready"
        result["next_action"] = "Run /gate or validate.py on the strongest pack"
    elif result["verdict_totals"]["CHAIN REQUIRED"]:
        result["decision"] = "CHAIN REQUIRED"
        result["confidence"] = "MEDIUM"
        result["reason"] = (
            "Evidence exists, but impact still needs chaining or stronger proof"
        )
        result["next_action"] = "Pivot the strongest pack into concrete impact"
    elif result["verdict_totals"]["DOWNGRADE"]:
        result["decision"] = "DOWNGRADE"
        result["confidence"] = "LOW"
        result["reason"] = "Only partial or weak evidence packs are present"
        result["next_action"] = "Fill the missing evidence fields before reporting"
    else:
        result["decision"] = "KILL"
        result["confidence"] = "LOW"
        result["reason"] = "No pack contains enough proof to continue"
        result["next_action"] = "Rotate to a new surface"

    return result


def write_outputs(target: str, result: dict) -> tuple[str, str]:
    findings_dir = os.path.join(FINDINGS_ROOT, target)
    os.makedirs(findings_dir, exist_ok=True)
    json_path = os.path.join(findings_dir, "autonomous_verdict.json")
    md_path = os.path.join(findings_dir, "autonomous_verdict.md")

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    lines = [
        f"# Autonomous Verdict - {target}",
        "",
        f"- Decision: `{result['decision']}`",
        f"- Confidence: `{result['confidence']}`",
        f"- Reason: {result['reason']}",
        f"- Next action: {result['next_action']}",
        "",
        "## Evidence Packs",
    ]
    for pack in result["packs"]:
        lines.append(
            f"- `{pack['name']}`: {pack['decision']} / {pack['confidence']} / score {pack['score']} - {pack['reason']}"
        )
        if pack["checks"]:
            checks = ", ".join(
                f"{name}={'yes' if ok else 'no'}" for name, ok in pack["checks"].items()
            )
            lines.append(f"  - checks: {checks}")
        if pack.get("missing_required"):
            lines.append(
                f"  - missing required: {', '.join(pack['missing_required'])}"
            )

    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Autonomous finding lifecycle evaluator"
    )
    parser.add_argument("target", help="Target name matching findings/<target>")
    args = parser.parse_args()

    result = evaluate_target(args.target)
    json_path, md_path = write_outputs(args.target, result)
    print(json.dumps(result, indent=2))
    print(f"\nSaved: {json_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
