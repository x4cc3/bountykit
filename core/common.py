#!/usr/bin/env python3

import os
from datetime import UTC, datetime


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def repo_path(*parts: str) -> str:
    return os.path.join(REPO_ROOT, *parts)


def utcnow() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
