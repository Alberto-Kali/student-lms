import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone


PBKDF2_ITERATIONS = 120_000
SESSION_TTL_DAYS = 7


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def hash_password(password: str, salt: str | None = None) -> str:
    resolved_salt = salt or secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        resolved_salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    digest = base64.urlsafe_b64encode(derived).decode("utf-8")
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${resolved_salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    scheme, iterations, salt, expected = password_hash.split("$", 3)
    if scheme != "pbkdf2_sha256":
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    )
    digest = base64.urlsafe_b64encode(derived).decode("utf-8")
    return hmac.compare_digest(digest, expected)


def create_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_expiry() -> datetime:
    return utc_now() + timedelta(days=SESSION_TTL_DAYS)
