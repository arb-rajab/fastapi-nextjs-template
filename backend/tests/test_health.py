from fastapi.testclient import TestClient

from starterapp.main import app

client = TestClient(app)


def test_health_returns_200_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_200_when_database_is_reachable() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_validation_errors_use_the_error_envelope() -> None:
    response = client.post("/api/v1/auth/login", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_validation_error_names_the_field_and_lists_all_fields() -> None:
    response = client.post("/api/v1/auth/register", json={"username": "ab", "password": "short"})

    error = response.json()["error"]
    assert response.status_code == 422
    assert error["field"] == "username"
    assert set(error["fields"]) == {"username", "password"}
