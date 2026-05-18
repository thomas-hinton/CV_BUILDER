"""
Auth service: password hashing and JWT token management.

DISCLAIMER: This module was written with assistance from GitHub Copilot
(Claude Sonnet 4.6) and reviewed by the project author.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
from dotenv import load_dotenv
from jose import JWTError, jwt

from python.database.connection import get_connection

# ---------------------------------------------------------------------------
# Configuration (loaded from .env at project root)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")

_app_env = os.getenv("APP_ENV")
if not _app_env or not _app_env.strip():
    raise RuntimeError(
        "Missing APP_ENV in .env. Set APP_ENV to 'development' or 'production'."
    )

APP_ENV = _app_env.strip().lower()
if APP_ENV not in ("development", "production"):
    raise RuntimeError(
        f"Invalid APP_ENV={_app_env!r}. Expected 'development' or 'production'."
    )

_DEV_KEY = os.getenv("JWT_SECRET_KEY_DEV")
_PROD_KEY = os.getenv("JWT_SECRET_KEY_PROD")

if APP_ENV == "production":
    SECRET_KEY = _PROD_KEY
    _key_name = "JWT_SECRET_KEY_PROD"
else:
    SECRET_KEY = _DEV_KEY
    _key_name = "JWT_SECRET_KEY_DEV"

if not SECRET_KEY:
    raise RuntimeError(
        f"Missing {_key_name} in .env (APP_ENV={APP_ENV}). "
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------

def create_user(email: str, password: str) -> dict:
    """Create a new user. Returns error dict if email already exists."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            return {"status": "error", "code": 409, "message": "Email already registered"}

        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        conn.execute(
            "INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)",
            (user_id, email, password_hash),
        )
        conn.commit()
        return {"status": "created", "user_id": user_id}
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> dict:
    """Verify credentials. Returns user_id on success or error dict."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
        if not row or not verify_password(password, row[1]):
            return {"status": "error", "code": 401, "message": "Invalid credentials"}
        return {"status": "ok", "user_id": row[0]}
    finally:
        conn.close()
