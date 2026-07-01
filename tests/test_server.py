import httpx
import pytest
import respx

import server


@pytest.fixture(autouse=True)
def _creds(monkeypatch):
    monkeypatch.setenv("GODADDY_API_KEY", "test_key")
    monkeypatch.setenv("GODADDY_API_SECRET", "test_secret")


def test_missing_credentials_raises_runtime_error(monkeypatch):
    monkeypatch.delenv("GODADDY_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="must be set"):
        server.list_dns_records("example.com")


@respx.mock
def test_request_uses_configured_timeout():
    route = respx.get(
        "https://api.godaddy.com/v1/domains/example.com/records"
    ).mock(return_value=httpx.Response(200, json=[]))

    result = server.list_dns_records("example.com")

    assert result == []
    assert route.called
    timeout = respx.calls.last.request.extensions["timeout"]
    assert timeout["read"] == 30.0
    assert timeout["connect"] == 30.0
