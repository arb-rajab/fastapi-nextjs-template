"""Authentication boundary tests: register, login, token verification, rate limits."""

import time

import jwt
from fastapi.testclient import TestClient

from starterapp.config import get_settings
from starterapp.main import app
from starterapp.security.tokens import issue_access_token

client = TestClient(app)


# --- Caller identity can only come from a verified token --------------------


def test_x_user_id_header_alone_does_not_authenticate_anyone(db) -> None:
    """A claimed identity in a client-controlled header must never be
    treated as authentication."""
    resp = client.get("/api/v1/auth/me", headers={"X-User-Id": "victim"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthenticated"


def test_no_authorization_header_is_unauthenticated(db) -> None:
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthenticated"


def test_malformed_authorization_header_is_unauthenticated(db) -> None:
    for bad_header in ("not-a-bearer-token", "Bearer", "Basic dXNlcjpwYXNz"):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": bad_header})
        assert resp.status_code == 401, bad_header
        assert resp.json()["error"]["code"] == "unauthenticated"


# --- Register / login issue real, working tokens ----------------------------


def test_register_then_use_token_round_trips(db) -> None:
    register_resp = client.post(
        "/api/v1/auth/register", json={"username": "alice", "password": "hunter2-but-long-enough"}
    )
    assert register_resp.status_code == 201
    body = register_resp.json()
    assert body["username"] == "alice"
    assert body["token_type"] == "bearer"
    token = body["access_token"]

    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "alice"


def test_duplicate_registration_is_rejected(db) -> None:
    first = client.post(
        "/api/v1/auth/register", json={"username": "bob", "password": "first-password-1"}
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/auth/register", json={"username": "bob", "password": "different-pw-2"}
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "username_taken"


def test_login_with_correct_password_succeeds(db) -> None:
    client.post(
        "/api/v1/auth/register", json={"username": "carol", "password": "carols-real-password"}
    )

    login_resp = client.post(
        "/api/v1/auth/login", json={"username": "carol", "password": "carols-real-password"}
    )
    assert login_resp.status_code == 200
    assert login_resp.json()["username"] == "carol"


def test_login_with_wrong_password_is_rejected(db) -> None:
    client.post(
        "/api/v1/auth/register", json={"username": "dave", "password": "daves-real-password"}
    )

    login_resp = client.post(
        "/api/v1/auth/login", json={"username": "dave", "password": "totally-wrong-password"}
    )
    assert login_resp.status_code == 401
    assert login_resp.json()["error"]["code"] == "invalid_credentials"


def test_login_for_unknown_username_gets_same_error_as_wrong_password(db) -> None:
    """A distinct error would let a caller enumerate registered usernames."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "nobody-has-ever-registered-this", "password": "whatever"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "invalid_credentials"


def test_login_does_equivalent_work_for_unknown_vs_known_username(db, monkeypatch) -> None:
    """Both cases must run exactly one PBKDF2 comparison at the same iteration
    count, so response time does not reveal whether a username exists. (A
    wall-clock assertion would be flaky on shared runners.)"""
    import starterapp.api.auth_routes as auth_routes

    real_verify_password = auth_routes.verify_password
    calls: list[str] = []

    def spy(password: str, stored_hash: str) -> bool:
        calls.append(stored_hash.split("$")[1])  # iteration count
        return real_verify_password(password, stored_hash)

    monkeypatch.setattr(auth_routes, "verify_password", spy)

    client.post(
        "/api/v1/auth/register", json={"username": "grace", "password": "graces-real-password"}
    )

    calls.clear()
    known_resp = client.post(
        "/api/v1/auth/login", json={"username": "grace", "password": "wrong-password-guess"}
    )
    assert known_resp.status_code == 401
    known_iterations = list(calls)

    calls.clear()
    unknown_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "nobody-has-ever-registered-this-one", "password": "whatever"},
    )
    assert unknown_resp.status_code == 401
    unknown_iterations = list(calls)

    # Same number of PBKDF2 comparisons, at the same iteration count,
    # regardless of whether the username exists.
    assert known_iterations == unknown_iterations
    assert len(known_iterations) == 1


def test_password_is_never_returned_or_stored_in_plaintext(db) -> None:
    resp = client.post(
        "/api/v1/auth/register", json={"username": "erin", "password": "erins-secret-password"}
    )
    assert "password" not in resp.text
    assert "erins-secret-password" not in resp.text

    from starterapp.db import models
    from starterapp.db.session import SessionLocal

    session = SessionLocal()
    try:
        user = session.query(models.AppUser).filter_by(username="erin").one()
        assert user.password_hash != "erins-secret-password"
        assert "erins-secret-password" not in user.password_hash
    finally:
        session.close()


# --- Forged / tampered / expired tokens are all rejected --------------------


def test_token_signed_with_wrong_secret_is_rejected(db) -> None:
    settings = get_settings()
    forged = jwt.encode(
        {"sub": "victim", "type": "access", "iat": time.time(), "exp": time.time() + 3600},
        "not-the-real-secret-but-long-enough-for-hs256",
        algorithm=settings.jwt_algorithm,
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthenticated"


def test_token_with_alg_none_is_rejected(db) -> None:
    """Algorithm-confusion attack: `alg: none` with no signature."""
    settings = get_settings()
    header = jwt.utils.base64url_encode(b'{"alg":"none","typ":"JWT"}').decode()
    payload = jwt.utils.base64url_encode(
        f'{{"sub":"victim","type":"access","iat":0,"exp":{time.time() + 3600}}}'.encode()
    ).decode()
    forged = f"{header}.{payload}."
    assert settings.jwt_algorithm != "none"

    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthenticated"


def test_expired_token_is_rejected(db) -> None:
    settings = get_settings()
    now = time.time()
    expired = jwt.encode(
        {"sub": "someone", "type": "access", "iat": now - 7200, "exp": now - 3600},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthenticated"


def test_token_with_wrong_type_claim_is_rejected(db) -> None:
    settings = get_settings()
    now = time.time()
    wrong_type = jwt.encode(
        {"sub": "someone", "type": "refresh", "iat": now, "exp": now + 3600},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {wrong_type}"})
    assert resp.status_code == 401


def test_verified_token_subject_is_authoritative(db) -> None:
    """A verified token's `sub` cannot be overridden by any other request
    data (headers, body)."""
    settings = get_settings()
    token_for_mallory = issue_access_token("mallory", settings)
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_for_mallory}", "X-User-Id": "alice"},
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "mallory"


# --- Rate-limited login -----------------------------------------------


def test_login_is_rate_limited_after_repeated_failures(db, monkeypatch) -> None:
    from starterapp.config import Settings

    test_settings = Settings(login_rate_limit_per_5_minutes=3)
    monkeypatch.setattr("starterapp.api.auth_routes.get_settings", lambda: test_settings)

    client.post(
        "/api/v1/auth/register", json={"username": "frank", "password": "franks-real-password"}
    )

    for _ in range(3):
        resp = client.post(
            "/api/v1/auth/login", json={"username": "frank", "password": "wrong-password-guess"}
        )
        assert resp.status_code == 401

    limited_resp = client.post(
        "/api/v1/auth/login", json={"username": "frank", "password": "wrong-password-guess"}
    )
    assert limited_resp.status_code == 429
    assert limited_resp.json()["error"]["code"] == "rate_limited"
    assert int(limited_resp.headers["retry-after"]) > 0


# --- /register is rate limited -----------------------------------------------


def test_register_is_rate_limited_after_repeated_attempts(db, monkeypatch) -> None:
    """Unlike login, this limit is global, so it must trip even when every
    attempt uses a different username."""
    from starterapp.config import Settings

    test_settings = Settings(register_rate_limit_per_5_minutes=3)
    monkeypatch.setattr("starterapp.api.auth_routes.get_settings", lambda: test_settings)

    for i in range(3):
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": f"register-limit-user-{i}", "password": "a-real-password-123"},
        )
        assert resp.status_code == 201

    limited_resp = client.post(
        "/api/v1/auth/register",
        json={"username": "register-limit-user-overflow", "password": "a-real-password-123"},
    )
    assert limited_resp.status_code == 429
    assert limited_resp.json()["error"]["code"] == "rate_limited"
    assert int(limited_resp.headers["retry-after"]) > 0
