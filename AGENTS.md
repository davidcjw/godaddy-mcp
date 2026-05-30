# AGENTS.md

MCP server for managing GoDaddy DNS records via Claude and other AI assistants.

## Installation / Setup

Requires Python 3.11+ and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/davidcjw/godaddy-mcp
cd godaddy-mcp
uv sync
```

### Configuration

1. Generate a **Production** API key at [developer.godaddy.com/keys](https://developer.godaddy.com/keys) (select Production, not OTE).

2. Register with Claude Code by adding to `~/.claude.json`:
```json
"godaddy-dns": {
  "command": "/path/to/godaddy-mcp/.venv/bin/python",
  "args": ["/path/to/godaddy-mcp/server.py"],
  "env": {
    "GODADDY_API_KEY": "your_api_key",
    "GODADDY_API_SECRET": "your_api_secret"
  }
}
```

3. For other MCP clients, run directly:
```bash
GODADDY_API_KEY=your_key GODADDY_API_SECRET=your_secret uv run python server.py
```

## Executable Commands

```bash
uv sync
uv run python server.py
```

## Folder Structure

```
godaddy-mcp/
├── server.py          # Main MCP server entry point
├── pyproject.toml     # Project metadata and dependencies
├── uv.lock            # Dependency lock file
├── LICENSE
└── README.md
```

## Available Tools

- `list_dns_records` — List all records for a domain, optionally filtered by type and/or name
- `add_dns_record` — Add a record without overwriting existing ones (PATCH)
- `replace_dns_records` — Overwrite all records of a given type+name (PUT)
- `delete_dns_record` — Delete all records matching a given type and name

Supported types: A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, and others supported by GoDaddy API.

## PR Instructions

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit with conventional format: `git commit -m 'feat: describe change'`
4. Push and open a pull request
5. Ensure the server starts cleanly: `uv run python server.py`

## Do-Not Rules

- Do not use OTE (test) API keys — use Production keys only
- Do not commit API credentials to the repository
- Do not modify the MCP protocol implementation without testing with Claude
