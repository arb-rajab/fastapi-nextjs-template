"""Security primitives: password hashing and session-token issuance.

These have no FastAPI dependency-injection concerns of their own;
`starterapp.api.auth` wires them into the request pipeline.
"""
