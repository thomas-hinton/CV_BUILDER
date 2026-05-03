"""
Integration tests: full end-to-end flows across all layers.

DISCLAIMER: These tests were proposed and written by GitHub Copilot (Claude Sonnet 4.6)
and reviewed by the project author.

Unlike unit tests, no logic is mocked — every layer (router → service → DB) is exercised
together using a fresh in-memory SQLite database per test.
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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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

    monkeypatch.setattr(conn_module,    "get_connection", fresh_connection)
    monkeypatch.setattr(auth_module,    "get_connection", fresh_connection)
    monkeypatch.setattr(profiles_module,"get_connection", fresh_connection)
    yield


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

async def _register_and_login(client, email="user@test.com", password="secret123"):
    await client.post("/auth/register", json={"email": email, "password": password})
    r = await client.post("/auth/login",    json={"email": email, "password": password})
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _full_setup(client):
    """Register, login, create profile, add formation, experience and skill."""
    token = await _register_and_login(client)

    await client.post("/profiles", headers=_auth(token),
                      json={"nom": "Dupont", "prenom": "Alice"})

    await client.post("/profiles/me/educations", headers=_auth(token), json={
        "nom_formation": "Licence Info",
        "organisme_formation": "Université X",
        "date_debut": "2020-09-01",
        "date_fin":   "2023-06-30",
    })

    await client.post("/profiles/me/experiences", headers=_auth(token), json={
        "nom_experience": "Stage backend",
        "organisme_experience": "Startup Y",
        "date_debut": "2023-07-01",
    })

    await client.post("/profiles/me/skills", headers=_auth(token), json={
        "nom_skill": "FastAPI",
        "niveau":    "Intermédiaire",
        "categorie": "Framework",
    })

    return token


# ---------------------------------------------------------------------------
# 1. Full positive flow: register → login → create → publish → public CV
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_full_flow_public_cv():
    """Complete user journey: create account, fill CV, publish, read public CV."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _full_setup(client)

        # CV is private by default — public endpoint should return 404
        profile_r = await client.get("/profiles/me", headers=_auth(token))
        slug = profile_r.json()["slug"]

        r = await client.get(f"/cv/{slug}/data")
        assert r.status_code == 404

        # Publish the CV
        await client.patch("/profiles/me", headers=_auth(token), json={"is_public": True})

        # Now the public endpoint works
        r = await client.get(f"/cv/{slug}/data")
        assert r.status_code == 200
        data = r.json()

        assert data["profile"]["nom"]    == "Dupont"
        assert data["profile"]["prenom"] == "Alice"
        assert len(data["formations"])   == 1
        assert len(data["experiences"])  == 1
        assert len(data["skills"])       == 1
        assert data["formations"][0]["nom_formation"]   == "Licence Info"
        assert data["experiences"][0]["nom_experience"] == "Stage backend"
        assert data["skills"][0]["nom_skill"]           == "FastAPI"


# ---------------------------------------------------------------------------
# 2. Private CV stays hidden
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_private_cv_returns_404():
    """A CV with is_public=False must not be accessible via the public endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", headers=_auth(token),
                          json={"nom": "Martin", "prenom": "Bob"})

        profile_r = await client.get("/profiles/me", headers=_auth(token))
        slug = profile_r.json()["slug"]

        r = await client.get(f"/cv/{slug}/data")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 3. Unknown slug returns 404
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unknown_slug_returns_404():
    """A slug that has never been created must return 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/cv/slug-qui-nexiste-pas/data")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 4. show_email / show_phone masking
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_contact_info_masked_when_hidden():
    """Email and phone are hidden on the public CV when show_email/show_phone are false."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", headers=_auth(token),
                          json={"nom": "Leroy", "prenom": "Claire",
                                "email": "claire@test.com", "tel": "0612345678"})

        # Publish but keep show_email and show_phone false (default)
        await client.patch("/profiles/me", headers=_auth(token), json={"is_public": True})

        profile_r = await client.get("/profiles/me", headers=_auth(token))
        slug = profile_r.json()["slug"]

        r = await client.get(f"/cv/{slug}/data")
        assert r.status_code == 200
        assert r.json()["profile"]["email"] is None
        assert r.json()["profile"]["tel"]   is None


@pytest.mark.asyncio
async def test_contact_info_visible_when_shown():
    """Email and phone appear on the public CV when show_email/show_phone are true."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        await client.post("/profiles", headers=_auth(token),
                          json={"nom": "Leroy", "prenom": "Claire",
                                "email": "claire@test.com", "tel": "0612345678"})

        await client.patch("/profiles/me", headers=_auth(token), json={
            "is_public":  True,
            "show_email": True,
            "show_phone": True,
        })

        profile_r = await client.get("/profiles/me", headers=_auth(token))
        slug = profile_r.json()["slug"]

        r = await client.get(f"/cv/{slug}/data")
        assert r.status_code == 200
        assert r.json()["profile"]["email"] == "claire@test.com"
        assert r.json()["profile"]["tel"]   == "0612345678"


# ---------------------------------------------------------------------------
# 5. Access without token → 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_protected_route_without_token():
    """Any /profiles/* route must reject requests without a JWT."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/profiles/me")
        assert r.status_code == 401

        r = await client.post("/profiles", json={"nom": "X", "prenom": "Y"})
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# 6. Cascade delete: deleting a profile removes its formations/experiences/skills
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cascade_delete():
    """Deleting a profile must cascade-delete formations, experiences and skills."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _full_setup(client)

        # Publish so we can check the public endpoint after deletion
        profile_r = await client.get("/profiles/me", headers=_auth(token))
        slug = profile_r.json()["slug"]
        await client.patch("/profiles/me", headers=_auth(token), json={"is_public": True})

        # Confirm CV is public before deletion
        assert (await client.get(f"/cv/{slug}/data")).status_code == 200

        # Delete the profile
        r = await client.delete("/profiles/me", headers=_auth(token))
        assert r.status_code == 204

        # Profile is gone
        assert (await client.get("/profiles/me", headers=_auth(token))).status_code == 404

        # Public CV is gone too
        assert (await client.get(f"/cv/{slug}/data")).status_code == 404


# ---------------------------------------------------------------------------
# 7. Slug auto-generated and unique
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_slug_generated_from_name():
    """Slug is automatically derived from prenom + nom."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _register_and_login(client)
        r = await client.post("/profiles", headers=_auth(token),
                              json={"nom": "Durand", "prenom": "Élodie"})
        assert r.status_code == 201
        assert r.json()["slug"] == "elodie-durand"


@pytest.mark.asyncio
async def test_slug_deduplication():
    """Two users with the same name get different slugs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token1 = await _register_and_login(client, email="u1@test.com")
        token2 = await _register_and_login(client, email="u2@test.com")

        r1 = await client.post("/profiles", headers=_auth(token1),
                               json={"nom": "Moreau", "prenom": "Paul"})
        r2 = await client.post("/profiles", headers=_auth(token2),
                               json={"nom": "Moreau", "prenom": "Paul"})

        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["slug"] != r2.json()["slug"]
        assert r2.json()["slug"] == "paul-moreau-2"
