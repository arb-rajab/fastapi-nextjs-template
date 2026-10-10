"""Test helper: obtain a real bearer token through the real register/login
endpoints, exactly as a genuine caller would. There is deliberately no
shortcut that bypasses `starterapp.api.auth`, so a regression there cannot go
unnoticed."""

from fastapi.testclient import TestClient

_DEFAULT_PASSWORD = "correct-horse-battery-staple"  # noqa: S105


def bearer_headers_for(
    client: TestClient, username: str, password: str = _DEFAULT_PASSWORD
) -> dict[str, str]:
    """Registers `username`, or logs in if it already exists within this test
    (the autouse cleanup fixture only truncates between tests)."""
    resp = client.post("/api/v1/auth/register", json={"username": username, "password": password})
    if resp.status_code == 409:
        resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
        assert resp.status_code == 200, resp.text
    else:
        assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
