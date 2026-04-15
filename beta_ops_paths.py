#!/usr/bin/env python3

import os


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))


def repo_path(*parts: str) -> str:
    return os.path.join(REPO_ROOT, *parts)
