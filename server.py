#!/usr/bin/env python3
"""GoDaddy DNS MCP Server — manage DNS records via GoDaddy API."""

import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("godaddy-dns")

BASE_URL = "https://api.godaddy.com/v1"

TIMEOUT = httpx.Timeout(30.0)


def _headers() -> dict:
    key = os.environ.get("GODADDY_API_KEY")
    secret = os.environ.get("GODADDY_API_SECRET")
    if not key or not secret:
        raise RuntimeError(
            "GODADDY_API_KEY and GODADDY_API_SECRET must be set in the environment"
        )
    return {
        "Authorization": f"sso-key {key}:{secret}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _raise(r: httpx.Response) -> None:
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"GoDaddy API error {r.status_code}: {r.text}") from e


@mcp.tool()
def list_dns_records(domain: str, record_type: str = "", name: str = "") -> list:
    """List DNS records for a domain.

    Args:
        domain: The root domain, e.g. "example.com"
        record_type: Optional filter — A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, etc.
        name: Optional filter — record name/subdomain (requires record_type)
    """
    path = f"{BASE_URL}/domains/{domain}/records"
    if record_type:
        path += f"/{record_type.upper()}"
        if name:
            path += f"/{name}"
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.get(path, headers=_headers())
        _raise(r)
        return r.json()


@mcp.tool()
def add_dns_record(
    domain: str,
    record_type: str,
    name: str,
    data: str,
    ttl: int = 3600,
    priority: int = 0,
) -> str:
    """Add a DNS record without overwriting existing records of the same type.

    Args:
        domain: The root domain, e.g. "example.com"
        record_type: A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, etc.
        name: Record name/subdomain — use "@" for apex/root
        data: Record value (IP address, hostname, text, etc.)
        ttl: Time-to-live in seconds (default 3600)
        priority: Priority for MX/SRV records (default 0)
    """
    record: dict = {
        "data": data,
        "name": name,
        "ttl": ttl,
        "type": record_type.upper(),
    }
    if record_type.upper() in ("MX", "SRV"):
        record["priority"] = priority
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.patch(
            f"{BASE_URL}/domains/{domain}/records",
            headers=_headers(),
            json=[record],
        )
        _raise(r)
        return f"Added {record_type.upper()} record '{name}' → '{data}' on {domain}"


@mcp.tool()
def replace_dns_records(
    domain: str,
    record_type: str,
    name: str,
    data: str,
    ttl: int = 3600,
    priority: int = 0,
    dry_run: bool = False,
) -> str:
    """Replace ALL DNS records of a given type+name (overwrites any existing ones).

    Use this when you want exactly one record and need to ensure no duplicates exist.

    Args:
        domain: The root domain, e.g. "example.com"
        record_type: A, AAAA, CNAME, MX, TXT, etc.
        name: Record name/subdomain — use "@" for apex/root
        data: New record value
        ttl: Time-to-live in seconds (default 3600)
        priority: Priority for MX/SRV records (default 0)
        dry_run: When True, do NOT call the GoDaddy API — return a
            description of the change that WOULD be made (default False).
    """
    record: dict = {
        "data": data,
        "name": name,
        "ttl": ttl,
        "type": record_type.upper(),
    }
    if record_type.upper() in ("MX", "SRV"):
        record["priority"] = priority
    if dry_run:
        return (
            f"[dry_run] Would replace ALL {record_type.upper()} records "
            f"'{name}' on {domain} (PUT) with payload: {[record]}"
        )
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.put(
            f"{BASE_URL}/domains/{domain}/records/{record_type.upper()}/{name}",
            headers=_headers(),
            json=[record],
        )
        _raise(r)
        return f"Replaced {record_type.upper()} record '{name}' → '{data}' on {domain}"


@mcp.tool()
def delete_dns_record(
    domain: str, record_type: str, name: str, dry_run: bool = False
) -> str:
    """Delete all DNS records of a given type and name for a domain.

    Args:
        domain: The root domain, e.g. "example.com"
        record_type: A, AAAA, CNAME, MX, TXT, etc.
        name: Record name/subdomain to delete — use "@" for apex/root
        dry_run: When True, do NOT call the GoDaddy API — return a
            description of the record(s) that WOULD be deleted (default False).
    """
    if dry_run:
        return (
            f"[dry_run] Would delete ALL {record_type.upper()} records "
            f"'{name}' from {domain} (DELETE "
            f"/domains/{domain}/records/{record_type.upper()}/{name})"
        )
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.delete(
            f"{BASE_URL}/domains/{domain}/records/{record_type.upper()}/{name}",
            headers=_headers(),
        )
        _raise(r)
        return f"Deleted {record_type.upper()} record '{name}' from {domain}"


@mcp.tool()
def check_domain_availability(domain: str, check_type: str = "FAST") -> dict:
    """Check whether a domain is available to register.

    Args:
        domain: The domain to check, e.g. "example.com"
        check_type: "FAST" (cached, quicker) or "FULL" (authoritative)
    """
    with httpx.Client() as client:
        r = client.get(
            f"{BASE_URL}/domains/available",
            headers=_headers(),
            params={"domain": domain, "checkType": check_type.upper()},
        )
        _raise(r)
        return r.json()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
