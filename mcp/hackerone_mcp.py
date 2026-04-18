#!/usr/bin/env python3
"""
hackerone_mcp.py — Minimal MCP server for HackerOne API v1.

Exposes program scope, disclosed reports, and weakness queries as MCP tools.

Env vars:
  HACKERONE_USERNAME   API username
  HACKERONE_API_TOKEN  API token
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

H1_USERNAME = os.environ.get("HACKERONE_USERNAME", "")
H1_TOKEN = os.environ.get("HACKERONE_API_TOKEN", "")
H1_BASE = "https://api.hackerone.com/v1"


# ─── MCP protocol helpers ────────────────────────────────────────────────────

def send_response(id, result):
    msg = json.dumps({"jsonrpc": "2.0", "id": id, "result": result})
    sys.stdout.write(f"Content-Length: {len(msg)}\r\n\r\n{msg}")
    sys.stdout.flush()


def send_error(id, code, message):
    msg = json.dumps({"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}})
    sys.stdout.write(f"Content-Length: {len(msg)}\r\n\r\n{msg}")
    sys.stdout.flush()


def read_message():
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == "":
            break
        if ":" in line:
            key, val = line.split(":", 1)
            headers[key.strip().lower()] = val.strip()
    length = int(headers.get("content-length", 0))
    if length == 0:
        return None
    body = sys.stdin.read(length)
    return json.loads(body)


# ─── HackerOne API helpers ───────────────────────────────────────────────────

def h1_request(path, params=None):
    url = f"{H1_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {"Accept": "application/json"}
    if H1_USERNAME and H1_TOKEN:
        creds = base64.b64encode(f"{H1_USERNAME}:{H1_TOKEN}".encode()).decode()
        headers["Authorization"] = f"Basic {creds}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def get_program(handle):
    """Get program details and scope."""
    data = h1_request(f"/hackers/programs/{handle}")
    if "error" in data:
        return data

    program = data.get("data", data)
    attrs = program.get("attributes", {})
    result = {
        "name": attrs.get("name", handle),
        "handle": attrs.get("handle", handle),
        "state": attrs.get("state", ""),
        "offers_bounties": attrs.get("offers_bounties", False),
        "response_efficiency": attrs.get("average_time_to_first_program_response"),
    }

    # Fetch scope
    scope_data = h1_request(f"/hackers/programs/{handle}/structured_scopes", {"page[size]": "50"})
    if "data" in scope_data:
        in_scope = []
        out_scope = []
        for item in scope_data["data"]:
            sa = item.get("attributes", {})
            entry = {
                "asset_identifier": sa.get("asset_identifier", ""),
                "asset_type": sa.get("asset_type", ""),
                "instruction": sa.get("instruction", ""),
                "eligible_for_bounty": sa.get("eligible_for_bounty", False),
                "max_severity": sa.get("max_severity", ""),
            }
            if sa.get("eligible_for_submission", True):
                in_scope.append(entry)
            else:
                out_scope.append(entry)
        result["in_scope"] = in_scope
        result["out_of_scope"] = out_scope

    return result


def get_hacktivity(handle=None, limit=20):
    """Get disclosed reports from hacktivity."""
    params = {"page[size]": str(limit)}
    if handle:
        params["filter[program][]"] = handle
    data = h1_request("/hackers/hacktivity", params)
    if "error" in data:
        return data

    results = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {})
        results.append({
            "title": attrs.get("title", ""),
            "severity": attrs.get("severity_rating", ""),
            "state": attrs.get("state", ""),
            "disclosed_at": attrs.get("disclosed_at", ""),
            "bounty": attrs.get("total_awarded_amount", 0),
            "weakness": attrs.get("weakness", {}).get("name", ""),
        })
    return {"count": len(results), "reports": results}


def search_weaknesses(query):
    """Search HackerOne weakness taxonomy."""
    data = h1_request("/hackers/weaknesses", {"filter[keyword]": query, "page[size]": "10"})
    if "error" in data:
        return data

    results = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {})
        results.append({
            "name": attrs.get("name", ""),
            "description": attrs.get("description", "")[:200],
            "external_id": attrs.get("external_id", ""),
        })
    return {"count": len(results), "weaknesses": results}


# ─── MCP tool definitions ────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "h1_program_scope",
        "description": "Get a HackerOne program's details and in-scope/out-of-scope assets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "handle": {"type": "string", "description": "Program handle (e.g. 'github')"},
            },
            "required": ["handle"],
        },
    },
    {
        "name": "h1_hacktivity",
        "description": "Get disclosed bug reports from HackerOne Hacktivity, optionally filtered by program.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "handle": {"type": "string", "description": "Program handle to filter by (optional)"},
                "limit": {"type": "integer", "description": "Max reports to return (default 20)", "default": 20},
            },
        },
    },
    {
        "name": "h1_weaknesses",
        "description": "Search HackerOne weakness taxonomy (CWE-like).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Weakness search query (e.g. 'IDOR', 'XSS')"},
            },
            "required": ["query"],
        },
    },
]


def handle_tool_call(name, args):
    if name == "h1_program_scope":
        return get_program(args["handle"])
    elif name == "h1_hacktivity":
        return get_hacktivity(args.get("handle"), args.get("limit", 20))
    elif name == "h1_weaknesses":
        return search_weaknesses(args["query"])
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
                "serverInfo": {"name": "hackerone-mcp", "version": "1.0.0"},
            })
        elif method == "tools/list":
            send_response(id, {"tools": TOOLS})
        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            result = handle_tool_call(tool_name, tool_args)
            send_response(id, {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            })
        elif method == "notifications/initialized":
            pass
        else:
            if id:
                send_error(id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
