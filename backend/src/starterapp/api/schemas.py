"""Pydantic request/response models."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    # Only on validation_error: every problem, keyed by field name.
    fields: dict[str, list[str]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=256)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class MeOut(BaseModel):
    username: str
