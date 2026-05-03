"""
Tests for authentication endpoints (register, login, JWT protection).

DISCLAIMER: These tests were proposed and written by GitHub Copilot (Claude Sonnet 4.6)
and reviewed by the project author. They cover user registration, login, and access
control as defined in python/routers/auth.py and python/services/auth.py.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture(autouse=True)
def reset_db(tmp_path, monkeypatch):
    """
    Redirect the database to a fresh temp file for each test so tests
    are fully isolated without touching data/db.db.
    """
    import sqlite3
    from pathlib import Path

    import python.database.connection as conn_module
    import python.services.auth as auth_module

    db_path = tmp_path / "test.db"
    schema = (Path(__file__).resolve().parents[1] / "SQL" / "create_db.sql").read_text()

    def fresh_connection():
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # Initialise schema once
    conn = fresh_connection()
    conn.executescript(schema)
    conn.close()

    # Patch both the module attribute AND the already-imported reference in auth.py
    monkeypatch.setattr(conn_module, "get_connection", fresh_connection)
    monkeypatch.setattr(auth_module, "get_connection", fresh_connection)
    yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def _register(client, email="user@example.com", password="StrongPass1!"):
    return await client.post("/auth/register", json={"email": email, "password": password})


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/auth/register",
                              json={"email": "a@b.com", "password": "password123"})
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
        r = await client.post("/auth/register", json={"email": "a@b.com", "password": "other1234"})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password_returns_422():
    """Backend must reject passwords shorter than 8 characters (front can be bypassed)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/auth/register", json={"email": "a@b.com", "password": "short"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_success_returns_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
        r = await client.post("/auth/login", json={"email": "a@b.com", "password": "password123"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
        r = await client.post("/auth/login", json={"email": "a@b.com", "password": "wrongpass"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/auth/login",
                              json={"email": "nobody@x.com", "password": "password123"})
    assert r.status_code == 401
