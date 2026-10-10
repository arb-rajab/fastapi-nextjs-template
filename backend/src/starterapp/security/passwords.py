"""Password hashing: PBKDF2-HMAC-SHA256 from the standard library.

Iteration count and format are versioned into the stored hash string
(`pbkdf2_sha256$<iterations>$<salt>$<hex digest>`), so raising the count
later does not invalidate already-stored hashes.
"""

import hashlib
import hmac
import secrets

_ALGORITHM = "pbkdf2_sha256"
# OWASP Password Storage Cheat Sheet (2023) minimum for PBKDF2-HMAC-SHA256.
_ITERATIONS = 600_000
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_hex(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), _ITERATIONS
    )
    return f"{_ALGORITHM}${_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt, expected_hex = stored_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != _ALGORITHM:
        return False
    try:
        iterations = int(iterations_str)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    return hmac.compare_digest(digest.hex(), expected_hex)
