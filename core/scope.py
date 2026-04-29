#!/usr/bin/env python3

import argparse
import csv
import json
import os
import re
import ssl
import urllib.request
from html import unescape

from common import repo_path, utcnow


SCOPE_ROOT = repo_path("scope")
TLS_CONTEXT = ssl.create_default_context()
DOMAIN_RE = re.compile(r"(?<![A-Za-z0-9.-])(?:\*\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
URL_RE = re.compile(r"https?://[^\s'\"]+")
TRUE_WORDS = {"1", "true", "yes", "y", "eligible", "in_scope", "in scope"}
FALSE_WORDS = {
    "0",
    "false",
    "no",
    "n",
    "out_of_scope",
    "out of scope",
    "not eligible",
    "ineligible",
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9.-]+", "-", value.lower()).strip("-") or "program-scope"


def fetch_url(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "bountykit Scope Ingestor/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30, context=TLS_CONTEXT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_html(html: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(
        r"</?(?:p|div|li|br|h1|h2|h3|h4|section|article|ul|ol|tr|td|th)>",
        "\n",
        text,
        flags=re.I,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\r", "", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def extract_title(html: str, fallback: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
    if not match:
        return fallback
    title = unescape(match.group(1)).strip()
    return re.sub(r"\s+", " ", title) or fallback


def classify_scope_lines(text: str) -> tuple[list[str], list[str], list[str]]:
    in_scope = set()
    out_of_scope = set()
    notes = []
    mode = ""
    for raw_line in re.split(r"[\r\n]+", text):
        line = raw_line.strip(" -\t")
        if not line:
            continue
        domains = DOMAIN_RE.findall(line)
        lowered = line.lower()
        if "out of scope" in lowered or lowered.startswith("excluded"):
            mode = "out"
            out_of_scope.update(domains)
        elif "in scope" in lowered or lowered.startswith("eligible"):
            mode = "in"
            in_scope.update(domains)
        elif domains:
            if mode == "out" or any(
                key in lowered
                for key in ["staging", "third-party", "sandbox", "test only"]
            ):
                out_of_scope.update(domains)
            else:
                in_scope.update(domains)
        if any(
            key in lowered
            for key in [
                "safe harbor",
                "rate limit",
                "no automated",
                "do not use",
                "brute force",
            ]
        ):
            notes.append(line)
    return sorted(in_scope), sorted(out_of_scope), notes


def derive_program_name(source: str, title: str) -> str:
    if title and title != source:
        return title
    source = source.rstrip("/")
    return source.split("/")[-1] or "program-scope"


def normalize_bool(value: str) -> bool | None:
    lowered = value.strip().lower()
    if lowered in TRUE_WORDS:
        return True
    if lowered in FALSE_WORDS:
        return False
    return None


def get_row_value(row: dict, candidates: list[str]) -> str:
    lowered = {str(key).strip().lower(): value for key, value in row.items()}
    for candidate in candidates:
        if candidate in lowered and str(lowered[candidate]).strip():
            return str(lowered[candidate]).strip()
    return ""


def scope_from_csv(csv_path: str) -> dict:
    in_scope = set()
    out_of_scope = set()
    notes = []
    asset_rows = []

    with open(csv_path, encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            asset = get_row_value(
                row,
                [
                    "asset_identifier",
                    "asset",
                    "identifier",
                    "asset value",
                    "asset_value",
                    "target",
                    "scope",
                ],
            )
            asset_type = get_row_value(
                row,
                ["asset_type", "asset type", "type", "category"],
            )
            eligible_raw = get_row_value(
                row,
                [
                    "eligible_for_bounty",
                    "eligible for bounty",
                    "eligible",
                    "in_scope",
                    "in scope",
                    "status",
                ],
            )
            instruction = get_row_value(
                row,
                ["instruction", "instructions", "description", "notes", "note"],
            )

            if instruction:
                notes.append(instruction)

            if not asset:
                continue

            domains = DOMAIN_RE.findall(asset)
            if not domains and asset_type.lower() not in {
                "url",
                "api",
                "domain",
                "wildcard",
            }:
                continue

            eligible = normalize_bool(eligible_raw)
            if eligible is None:
                lowered = f"{eligible_raw} {instruction}".lower()
                if any(
                    word in lowered
                    for word in ["out of scope", "excluded", "ineligible"]
                ):
                    eligible = False
                elif any(word in lowered for word in ["in scope", "eligible"]):
                    eligible = True

            for domain in domains or [asset]:
                if eligible is False:
                    out_of_scope.add(domain)
                else:
                    in_scope.add(domain)

            asset_rows.append(
                {
                    "asset": asset,
                    "asset_type": asset_type,
                    "eligible": eligible,
                    "instruction": instruction,
                }
            )

    program = os.path.splitext(os.path.basename(csv_path))[0]
    return {
        "program": program,
        "source": csv_path,
        "generated_at": utcnow(),
        "in_scope_domains": sorted(in_scope - out_of_scope),
        "out_of_scope": sorted(out_of_scope),
        "notes": sorted(set(note for note in notes if note)),
        "raw_reference_urls": [],
        "asset_rows": asset_rows,
    }


def build_scope(source: str, raw_text: str, title: str) -> dict:
    in_scope, out_of_scope, notes = classify_scope_lines(raw_text)
    return {
        "program": derive_program_name(source, title),
        "source": source,
        "generated_at": utcnow(),
        "in_scope_domains": in_scope,
        "out_of_scope": out_of_scope,
        "notes": notes,
        "raw_reference_urls": sorted(set(URL_RE.findall(raw_text)))[:20],
    }


def write_scope(scope: dict, output: str | None = None) -> str:
    os.makedirs(SCOPE_ROOT, exist_ok=True)
    path = output or os.path.join(SCOPE_ROOT, f"{slugify(scope['program'])}.json")
    output_dir = os.path.dirname(path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(scope, handle, indent=2)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate scope JSON from a program page, CSV, or text file"
    )
    parser.add_argument("--url", help="Program page URL")
    parser.add_argument("--csv", help="Scope CSV exported from the bounty platform")
    parser.add_argument(
        "--text-file", help="Local text or HTML file containing scope policy"
    )
    parser.add_argument("--output", help="Output JSON path")
    args = parser.parse_args()

    provided = [bool(args.url), bool(args.csv), bool(args.text_file)]
    if sum(provided) == 0:
        raise SystemExit("Provide --url, --csv, or --text-file")

    if sum(provided) > 1:
        raise SystemExit("Use only one of --url, --csv, or --text-file")

    if args.url:
        html = fetch_url(args.url)
        title = extract_title(html, args.url)
        text = strip_html(html)
        scope = build_scope(args.url, text, title)
    elif args.csv:
        scope = scope_from_csv(args.csv)
    else:
        with open(args.text_file, encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
        title = os.path.basename(args.text_file)
        text = strip_html(raw) if "<html" in raw.lower() else raw
        scope = build_scope(args.text_file, text, title)

    path = write_scope(scope, args.output)
    print(json.dumps(scope, indent=2))
    print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()
