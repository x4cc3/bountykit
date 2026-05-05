#!/usr/bin/env python3

import os
import re
from datetime import UTC, datetime


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN_LABEL_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def repo_path(*parts: str) -> str:
    return os.path.join(REPO_ROOT, *parts)


def utcnow() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def normalize_domain(value: str, *, allow_wildcard: bool = False) -> str:
    domain = (value or "").strip().lower().rstrip(".")
    if not domain:
        raise ValueError("empty domain")
    if "://" in domain or any(char in domain for char in "/?#:@ \\"):
        raise ValueError("domain must be a hostname, not a URL or path")
    if domain.startswith("*."):
        if not allow_wildcard:
            raise ValueError("wildcard domains are not allowed here")
        suffix = domain[2:]
        if not _is_valid_plain_domain(suffix):
            raise ValueError(f"unsupported domain format: {value}")
        return f"*.{suffix}"
    if "*" in domain or not _is_valid_plain_domain(domain):
        raise ValueError(f"unsupported domain format: {value}")
    return domain


def _is_valid_plain_domain(domain: str) -> bool:
    if not domain or len(domain) > 253 or ".." in domain:
        return False
    labels = domain.split(".")
    if len(labels) < 2:
        return False
    if not labels[-1].isalpha() or len(labels[-1]) < 2:
        return False
    return all(DOMAIN_LABEL_RE.fullmatch(label) for label in labels)


def is_valid_domain(value: str, *, allow_wildcard: bool = False) -> bool:
    try:
        normalize_domain(value, allow_wildcard=allow_wildcard)
        return True
    except ValueError:
        return False


def validate_domain(value: str, *, name: str = "domain", allow_wildcard: bool = False) -> str:
    try:
        return normalize_domain(value, allow_wildcard=allow_wildcard)
    except ValueError as exc:
        raise ValueError(f"Unsupported {name} format: {value}") from exc


def sanitize_name(value: str, *, fallback: str = "name") -> str:
    cleaned = SAFE_NAME_RE.sub("-", (value or "").strip())
    cleaned = cleaned.strip("._-")
    return cleaned or fallback


def safe_join(root: str, *parts: str) -> str:
    root_abs = os.path.abspath(root)
    path = os.path.abspath(os.path.join(root_abs, *parts))
    if os.path.commonpath([root_abs, path]) != root_abs:
        raise ValueError(f"path escapes root: {path}")
    return path
