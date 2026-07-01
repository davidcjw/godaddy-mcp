"""Tests for the GoDaddy DNS MCP server tools.

All HTTP traffic is mocked with respx — no real GoDaddy API calls are made.
"""

import json

import httpx
import pytest
import respx

import server

BASE = "https://api.godaddy.com/v1"
DOMAIN = "example.com"


@pytest.fixture(autouse=True)
def _creds(monkeypatch):
    """Provide fake credentials so ``_headers()`` never touches real secrets."""
    monkeypatch.setenv("GODADDY_API_KEY", "test-key")
    monkeypatch.setenv("GODADDY_API_SECRET", "test-secret")


EXPECTED_AUTH = "sso-key test-key:test-secret"


def _assert_auth(request: httpx.Request) -> None:
    assert request.headers["Authorization"] == EXPECTED_AUTH
    assert request.headers["Content-Type"] == "application/json"


# --- list_dns_records --------------------------------------------------------


@respx.mock
def test_list_dns_records_all():
    route = respx.get(f"{BASE}/domains/{DOMAIN}/records").mock(
        return_value=httpx.Response(200, json=[{"type": "A", "name": "@", "data": "1.2.3.4"}])
    )
    result = server.list_dns_records(DOMAIN)

    assert route.called
    assert str(route.calls.last.request.url) == f"{BASE}/domains/{DOMAIN}/records"
    _assert_auth(route.calls.last.request)
    assert result == [{"type": "A", "name": "@", "data": "1.2.3.4"}]


@respx.mock
def test_list_dns_records_filtered_by_type_and_name():
    route = respx.get(f"{BASE}/domains/{DOMAIN}/records/A/www").mock(
        return_value=httpx.Response(200, json=[])
    )
    server.list_dns_records(DOMAIN, record_type="a", name="www")

    assert route.called
    assert str(route.calls.last.request.url) == f"{BASE}/domains/{DOMAIN}/records/A/www"


# --- add_dns_record ----------------------------------------------------------


@respx.mock
def test_add_dns_record_patches_correct_body():
    route = respx.patch(f"{BASE}/domains/{DOMAIN}/records").mock(
        return_value=httpx.Response(200)
    )
    msg = server.add_dns_record(DOMAIN, "a", "www", "1.2.3.4", ttl=600)

    assert route.called
    request = route.calls.last.request
    _assert_auth(request)
    assert json.loads(request.content) == [
        {"data": "1.2.3.4", "name": "www", "ttl": 600, "type": "A"}
    ]
    assert "Added A record" in msg


@respx.mock
def test_add_dns_record_mx_includes_priority():
    route = respx.patch(f"{BASE}/domains/{DOMAIN}/records").mock(
        return_value=httpx.Response(200)
    )
    server.add_dns_record(DOMAIN, "MX", "@", "mail.example.com", ttl=3600, priority=10)

    body = json.loads(route.calls.last.request.content)
    assert body[0]["priority"] == 10
    assert body[0]["type"] == "MX"


# --- replace_dns_records -----------------------------------------------------


@respx.mock
def test_replace_dns_records_puts_to_typed_url_with_body():
    route = respx.put(f"{BASE}/domains/{DOMAIN}/records/A/www").mock(
        return_value=httpx.Response(200)
    )
    msg = server.replace_dns_records(DOMAIN, "a", "www", "5.6.7.8", ttl=120)

    assert route.called
    request = route.calls.last.request
    assert str(request.url) == f"{BASE}/domains/{DOMAIN}/records/A/www"
    _assert_auth(request)
    assert json.loads(request.content) == [
        {"data": "5.6.7.8", "name": "www", "ttl": 120, "type": "A"}
    ]
    assert "Replaced A record" in msg


# --- delete_dns_record -------------------------------------------------------


@respx.mock
def test_delete_dns_record_deletes_typed_url():
    route = respx.delete(f"{BASE}/domains/{DOMAIN}/records/CNAME/blog").mock(
        return_value=httpx.Response(200)
    )
    msg = server.delete_dns_record(DOMAIN, "cname", "blog")

    assert route.called
    request = route.calls.last.request
    assert str(request.url) == f"{BASE}/domains/{DOMAIN}/records/CNAME/blog"
    _assert_auth(request)
    assert "Deleted CNAME record" in msg


# --- error handling ----------------------------------------------------------


@respx.mock
def test_error_response_raises_runtimeerror():
    respx.get(f"{BASE}/domains/{DOMAIN}/records").mock(
        return_value=httpx.Response(404, text="Not Found")
    )
    with pytest.raises(RuntimeError, match="GoDaddy API error 404"):
        server.list_dns_records(DOMAIN)


# --- credential + timeout robustness -----------------------------------------


def test_missing_credentials_raises_runtime_error(monkeypatch):
    monkeypatch.delenv("GODADDY_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="must be set"):
        server.list_dns_records(DOMAIN)


@respx.mock
def test_request_uses_configured_timeout():
    route = respx.get(f"{BASE}/domains/{DOMAIN}/records").mock(
        return_value=httpx.Response(200, json=[])
    )

    result = server.list_dns_records(DOMAIN)

    assert result == []
    assert route.called
    timeout = respx.calls.last.request.extensions["timeout"]
    assert timeout["read"] == 30.0
    assert timeout["connect"] == 30.0
