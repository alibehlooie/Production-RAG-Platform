import base64
import hashlib
import hmac
import json
import time
import uuid

import bcrypt

from app.core.config import settings


class InvalidTokenError(ValueError):
    """Raised when a JWT access token is invalid or expired."""


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    try:
        return base64.urlsafe_b64decode(segment + padding)
    except (ValueError, TypeError) as error:
        raise InvalidTokenError("Invalid token encoding") from error


def create_access_token(
    user_id: uuid.UUID,
    expires_minutes: int | None = None,
) -> str:
    ttl_minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + ttl_minutes * 60,
    }

    header_segment = _b64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    payload_segment = _b64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_segment = _b64url_encode(signature)
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def decode_access_token(token: str) -> uuid.UUID:
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidTokenError("Invalid token format")

    header_segment, payload_segment, signature_segment = parts
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_signature = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    actual_signature = _b64url_decode(signature_segment)

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise InvalidTokenError("Invalid token signature")

    try:
        header = json.loads(_b64url_decode(header_segment).decode("utf-8"))
        payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise InvalidTokenError("Invalid token payload") from error

    if not isinstance(header, dict) or header.get("alg") != "HS256":
        raise InvalidTokenError("Unsupported token algorithm")
    if not isinstance(payload, dict):
        raise InvalidTokenError("Invalid token claims")

    exp = payload.get("exp")
    if not isinstance(exp, int | float) or time.time() >= exp:
        raise InvalidTokenError("Token has expired")

    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise InvalidTokenError("Token subject is missing")

    try:
        return uuid.UUID(sub)
    except ValueError as error:
        raise InvalidTokenError("Invalid token subject") from error
