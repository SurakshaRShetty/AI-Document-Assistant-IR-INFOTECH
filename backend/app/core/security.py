from datetime import datetime, timedelta
from jose import jwt
import bcrypt
import os
import secrets

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# bcrypt only hashes the first 72 bytes of a password and raises ValueError
# on longer input (newer bcrypt versions) instead of silently truncating,
# so truncate explicitly ourselves before hashing/verifying.
BCRYPT_MAX_BYTES = 72


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token():
    return secrets.token_urlsafe(64)


def refresh_token_expiry(days: int = 7):
    return datetime.utcnow() + timedelta(days=days)


def _prepare_password(password: str) -> bytes:
    return password.encode("utf-8")[:BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_prepare_password(password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_prepare_password(password), hashed.encode("utf-8"))
    except ValueError:
        # hashed value isn't a valid bcrypt hash (e.g. corrupt/legacy data)
        return False
