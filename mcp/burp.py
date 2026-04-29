#!/usr/bin/env python3
"""
burp.py — Minimal MCP server for Burp Suite REST API.

Exposes Burp proxy history and site map as MCP tools.
Requires Burp Suite Professional with REST API enabled.

Configure Burp:
  User Options → Misc → REST API → Enable on port 1337

Env vars:
  BURP_API_URL  (default http://127.0.0.1:1337)
  BURP_API_KEY  (optional, for authenticated API)
"""

import json
import os
import re
import ssl
import urllib.error
import urllib.request
from base64 import b64decode

from common import read_message, send_error, send_response

BURP_URL = os.environ.get("BURP_API_URL", "http://127.0.0.1:1337")
BURP_KEY = os.environ.get("BURP_API_KEY", "")

# ─── Burp API helpers ────────────────────────────────────────────────────────

def burp_request(path):
    url = f"{BURP_URL}{path}"
    headers = {"Accept": "application/json"}
    if BURP_KEY:
        headers["Authorization"] = f"Bearer {BURP_KEY}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def get_proxy_history(limit=50, filter_host=None):
    """Fetch proxy history from Burp REST API."""
    data = burp_request("/v0.1/proxy/history")
    if "error" in data:
        return data

    items = data if isinstance(data, list) else data.get("items", data.get("messages", []))
    if filter_host:
        items = [i for i in items if filter_host.lower() in i.get("host", "").lower()]

    results = []
    for item in items[:limit]:
        entry = {
            "method": item.get("method", ""),
            "host": item.get("host", ""),
            "url": item.get("url", item.get("path", "")),
            "status": item.get("status", item.get("statusCode", "")),
            "length": item.get("length", item.get("responseLength", "")),
            "mime": item.get("mime", item.get("mimeType", "")),
        }
        # Include request body if present and short
        req_b64 = item.get("request", "")
        if req_b64 and isinstance(req_b64, str) and len(req_b64) < 5000:
            try:
                entry["request_preview"] = b64decode(req_b64).decode("utf-8", errors="replace")[:500]
            except Exception:
                pass
        results.append(entry)
    return {"count": len(results), "items": results}


def get_site_map(url_prefix=""):
    """Fetch site map from Burp."""
    path = "/v0.1/target/sitemap"
    if url_prefix:
        path += f"?urlPrefix={urllib.parse.quote(url_prefix)}"
    return burp_request(path)


def get_scan_issues(url_prefix=""):
    """Fetch scan issues from Burp."""
    path = "/v0.1/scan/issues"
    if url_prefix:
        path += f"?urlPrefix={urllib.parse.quote(url_prefix)}"
    data = burp_request(path)
    if "error" in data:
        return data

    issues = data if isinstance(data, list) else data.get("issues", data.get("issue_events", []))
    results = []
    for iss in issues:
        results.append({
            "name": iss.get("name", iss.get("issueName", "")),
            "severity": iss.get("severity", ""),
            "confidence": iss.get("confidence", ""),
            "url": iss.get("url", iss.get("origin", "")),
            "type": iss.get("issueType", ""),
        })
    return {"count": len(results), "issues": results}


# ─── MCP tool definitions ────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "burp_proxy_history",
        "description": "Get HTTP proxy history from Burp Suite. Returns method, URL, status, and response size for recent requests.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max entries to return (default 50)", "default": 50},
                "host": {"type": "string", "description": "Filter by hostname"},
            },
        },
    },
    {
        "name": "burp_site_map",
        "description": "Get the site map tree from Burp Suite for a target URL prefix.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url_prefix": {"type": "string", "description": "URL prefix to filter (e.g. https://target.com)"},
            },
        },
    },
    {
        "name": "burp_scan_issues",
        "description": "Get vulnerability scan issues found by Burp Scanner.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url_prefix": {"type": "string", "description": "URL prefix to filter"},
            },
        },
    },
]


def handle_tool_call(name, args):
    if name == "burp_proxy_history":
        return get_proxy_history(
            limit=args.get("limit", 50),
            filter_host=args.get("host"),
        )
    elif name == "burp_site_map":
        return get_site_map(args.get("url_prefix", ""))
    elif name == "burp_scan_issues":
        return get_scan_issues(args.get("url_prefix", ""))
    else:
        return {"error": f"Unknown tool: {name}"}


# ─── Main loop ───────────────────────────────────────────────────────────────

def main():
    while True:
        msg = read_message()
        if msg is None:
            break

        method = msg.get("method", "")
        id = msg.get("id")

        if method == "initialize":
            send_response(id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "burp-proxy-mcp", "version": "1.0.0"},
            })
        elif method == "core/list":
            send_response(id, {"tools": TOOLS})
        elif method == "core/call":
            params = msg.get("params", {})
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            result = handle_tool_call(tool_name, tool_args)
            send_response(id, {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            })
        elif method == "notifications/initialized":
            pass  # Acknowledge
        else:
            if id:
                send_error(id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
