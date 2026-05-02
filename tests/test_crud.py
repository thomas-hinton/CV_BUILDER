"""
Tests for CRUD endpoints: profiles, formations, experiences, skills.

DISCLAIMER: These tests were proposed and written by GitHub Copilot (Claude Sonnet 4.6)
and reviewed by the project author. They cover the full profile lifecycle as defined in
python/routers/profiles.py and python/services/profiles.py.
"""
import sqlite3
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

import python.database.connection as conn_module
import python.services.auth as auth_module
import python.services.profiles as profiles_module
from main import app

_SCHEMA = (Path(__file__).resolve().parents[1] / "SQL" / "create_db.sql").read_text()


@pytest.fixture(autouse=True)
def reset_db(tmp_path, monkeypatch):
    """Fresh isolated SQLite DB for each test."""
    db_path = tmp_path / "test.db"

    def fresh_connection():
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    conn = fresh_connection()
    conn.executescript(_SCHEMA)
    conn.close()

    monkeypatch.setattr(conn_module, "get_connection", fresh_connection)
    monkeypatch.setattr(auth_module, "get_connection", fresh_connection)
    monkeypatch.setattr(profiles_module, "get_connection", fresh_connection)
    yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _register_and_login(client, email="user@test.com", password="pass"):
    await client.post("/auth/register", json={"email": email, "password": password})
    r = await client.post("/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


_PROFILE_PAYLOAD = {"nom": "Hinton", "prenom": "Thomas"}
_FORMATION_PAYLOAD = {
    "nom_formation": "Bac S",
    "date_debut": "2018-09-01",
    "organisme_formation": "Lycée X",
}
_EXPERIENCE_PAYLOAD = {
    "nom_experience": "Stage dev",
    "date_debut": "2023-06-01",
}
_SKILL_PAYLOAD = {"nom_skill": "Python", "niveau": "Avancé", "categorie": "Langage"}


# ---------------------------------------------------------------------------
# Profile tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_profile_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        r = await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
    assert r.status_code == 201
    data = r.json()
    assert data["nom"] == "Hinton"
    assert data["prenom"] == "Thomas"
    assert data["slug"] == "thomas-hinton"
    assert data["is_public"] is False


@pytest.mark.asyncio
async def test_create_profile_duplicate_returns_409():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        r = await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_get_profile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        r = await client.get("/profiles/me", headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["nom"] == "Hinton"


@pytest.mark.asyncio
async def test_get_profile_without_token_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/profiles/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_field():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        r = await client.patch("/profiles/me", json={"nom": "Dupont"}, headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["nom"] == "Dupont"


@pytest.mark.asyncio
async def test_update_profile_regenerates_slug():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        r = await client.patch("/profiles/me", json={"nom": "Dupont"}, headers=_auth(token))
    assert r.json()["slug"] == "thomas-dupont"


@pytest.mark.asyncio
async def test_delete_profile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        r = await client.delete("/profiles/me", headers=_auth(token))
        assert r.status_code == 204
        r2 = await client.get("/profiles/me", headers=_auth(token))
    assert r2.status_code == 404


# ---------------------------------------------------------------------------
# Formation tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_formation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        r = await client.post("/profiles/me/educations", json=_FORMATION_PAYLOAD, headers=_auth(token))
    assert r.status_code == 201
    assert r.json()["nom_formation"] == "Bac S"


@pytest.mark.asyncio
async def test_list_formations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        await client.post("/profiles/me/educations", json=_FORMATION_PAYLOAD, headers=_auth(token))
        r = await client.get("/profiles/me/educations", headers=_auth(token))
    assert r.status_code == 200
    assert len(r.json()) == 1


# ---------------------------------------------------------------------------
# Skill tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_skill():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        r = await client.post("/profiles/me/skills", json=_SKILL_PAYLOAD, headers=_auth(token))
    assert r.status_code == 201
    data = r.json()
    assert data["nom_skill"] == "Python"
    assert data["niveau"] == "Avancé"


@pytest.mark.asyncio
async def test_update_skill():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", json=_PROFILE_PAYLOAD, headers=_auth(token))
        r = await client.post("/profiles/me/skills", json=_SKILL_PAYLOAD, headers=_auth(token))
        skill_id = r.json()["id_skill"]
        r2 = await client.patch(
            f"/profiles/me/skills/{skill_id}",
            json={"niveau": "Expert"},
            headers=_auth(token),
        )
    assert r2.status_code == 200
    assert r2.json()["niveau"] == "Expert"
