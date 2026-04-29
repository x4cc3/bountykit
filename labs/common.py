#!/usr/bin/env python3

import getpass
import os
import sys


def resolve_token(value: str | None, env_name: str, label: str) -> str:
    if value:
        return value

    env_value = os.environ.get(env_name, "").strip()
    if env_value:
        return env_value

    if sys.stdin.isatty():
        prompt_value = getpass.getpass(f"{label}: ").strip()
        if prompt_value:
            return prompt_value

    raise SystemExit(f"Provide {label.lower()} via CLI or {env_name}")
