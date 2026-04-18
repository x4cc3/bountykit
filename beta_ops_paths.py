#!/usr/bin/env python3

import os
import ssl


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
TLS_TRUST_STORE_ERROR = (
    "No verified TLS trust store is available. Install certifi or configure "
    "system CA certificates."
)
_SSL_CTX: ssl.SSLContext | None = None


def repo_path(*parts: str) -> str:
    return os.path.join(REPO_ROOT, *parts)


def _build_ssl_context() -> ssl.SSLContext:
    errors = []

    try:
        import certifi

        ctx = ssl.create_default_context(cafile=certifi.where())
        if ctx.cert_store_stats().get("x509_ca", 0) > 0:
            return ctx
        errors.append("certifi trust store is empty")
    except ImportError:
        errors.append("certifi is not installed")
    except Exception as exc:
        errors.append(f"certifi trust store could not be loaded: {exc}")

    try:
        ctx = ssl.create_default_context()
        if ctx.cert_store_stats().get("x509_ca", 0) > 0:
            return ctx
        errors.append("system trust store is empty")
    except Exception as exc:
        errors.append(f"system trust store could not be loaded: {exc}")

    raise RuntimeError(f"{TLS_TRUST_STORE_ERROR} Details: {'; '.join(errors)}")


def get_ssl_context() -> ssl.SSLContext:
    global _SSL_CTX
    if _SSL_CTX is None:
        _SSL_CTX = _build_ssl_context()
    return _SSL_CTX
