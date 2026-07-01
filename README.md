# godaddy-mcp

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![MCP](https://img.shields.io/badge/MCP-compatible-green)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for managing GoDaddy DNS records. Lets AI assistants (Claude, etc.) list, add, replace, and delete DNS records on any domain in your GoDaddy account.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Tools](#tools)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [License](#license)

## Installation

### Option A — PyPI (recommended)

Requires [`uv`](https://docs.astral.sh/uv/) (Python 3.11+).

```bash
uvx godaddy-mcp
```

No cloning or path configuration needed.

### Option B — from source

```bash
git clone https://github.com/davidcjw/godaddy-mcp
cd godaddy-mcp
uv sync
```

## Configuration

### 1. Get GoDaddy API credentials

Generate a **Production** API key at [developer.godaddy.com](https://developer.godaddy.com/keys) (select Production, not OTE).

### 2. Register with Claude Code

Add the following to the `mcpServers` section of `~/.claude.json`:

**With PyPI install (recommended):**

```json
"godaddy-dns": {
  "command": "uvx",
  "args": ["godaddy-mcp"],
  "env": {
    "GODADDY_API_KEY": "your_api_key",
    "GODADDY_API_SECRET": "your_api_secret"
  }
}
```

**With source install:**

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

Restart Claude Code to activate the server.

### 3. Other MCP clients

Run the server directly:

```bash
GODADDY_API_KEY=your_key GODADDY_API_SECRET=your_secret uvx godaddy-mcp
# or from source:
GODADDY_API_KEY=your_key GODADDY_API_SECRET=your_secret uv run python server.py
```

## Usage

Once registered, Claude (or any MCP client) can manage DNS records conversationally:

> "Add a CNAME record for `app.example.com` pointing to `cname.vercel-dns.com`"

> "List all A records for `example.com`"

> "Delete the TXT record `_vercel` from `example.com`"

## Tools

| Tool | Description |
|---|---|
| `list_dns_records` | List all records for a domain, optionally filtered by type and/or name |
| `add_dns_record` | Add a record without overwriting existing ones of the same type (PATCH) |
| `replace_dns_records` | Overwrite all records of a given type+name — use when you need exactly one record (PUT) |
| `delete_dns_record` | Delete all records matching a given type and name |
| `check_domain_availability` | Check whether a domain is available to register, with price and currency |

**Supported record types:** A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, and others supported by the GoDaddy API.

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: describe change'`)
4. Push and open a pull request

Please make sure the server starts cleanly (`uv run python server.py`) before submitting a PR.

## Code of Conduct

This project follows the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating you agree to uphold a welcoming, harassment-free environment.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
