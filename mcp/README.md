# MCP Integrations

Model Context Protocol (MCP) servers that bridge beta-ops with external security tools.

## Available Servers

### Burp Suite MCP (`burp_mcp.py`)

Reads proxy history, site map, and scan issues from Burp Suite Professional's REST API.

**Setup:**
1. In Burp: User Options → Misc → REST API → Enable on port 1337
2. Set env vars:
   ```bash
   export BURP_API_URL=http://127.0.0.1:1337
   export BURP_API_KEY=your-key   # optional
   ```

**Tools exposed:**
- `burp_proxy_history` — Recent proxy traffic with optional host filter
- `burp_site_map` — Crawled site tree for a URL prefix
- `burp_scan_issues` — Vulnerabilities found by Burp Scanner

### HackerOne MCP (`hackerone_mcp.py`)

Queries HackerOne programs, scope, and disclosed reports.

**Setup:**
1. Create API token at https://hackerone.com/settings/api_token
2. Set env vars:
   ```bash
   export HACKERONE_USERNAME=your-username
   export HACKERONE_API_TOKEN=your-token
   ```

**Tools exposed:**
- `h1_program_scope` — Program details and in-scope/out-of-scope assets
- `h1_hacktivity` — Disclosed bug reports with bounty amounts
- `h1_weaknesses` — Search CWE-like weakness taxonomy

## Client Configuration

### Claude Code

Use [mcp-config.json](./mcp-config.json) as the source snippet and merge its `mcpServers` entries into `~/.claude/config.json`.

### Other clients

This repository currently ships a ready-to-merge MCP snippet only for Claude Code. For other clients, point them at:

- `mcp/burp_mcp.py`
- `mcp/hackerone_mcp.py`

with `python3`, plus the environment variables shown above.

## Python dependencies

The MCP servers use only the standard library. If you also want the broader repo tooling to run with pinned packages, install them from the repo root with:

```bash
python3 -m pip install -r requirements.txt
```
