"""
Tests for database schema integrity.
Uses an in-memory SQLite database so no files are created on disk.

DISCLAIMER: These tests were proposed and written by GitHub Copilot (Claude Sonnet 4.6)
and reviewed by the project author. They cover schema creation and foreign key enforcement
as defined in SQL/create_db.sql.
"""
import sqlite3
from pathlib import Path
import pytest

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "SQL" / "create_db.sql"
EXPECTED_TABLES = {"users", "cv_profiles", "formations", "experiences", "skills"}


def get_in_memory_db() -> sqlite3.Connection:
    """Create a fresh in-memory DB from the SQL schema."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema)
    return conn


# ---------------------------------------------------------------------------
# Schema creation tests
# ---------------------------------------------------------------------------

def test_schema_file_exists():
    assert SCHEMA_PATH.exists(), f"Schema file not found: {SCHEMA_PATH}"


def test_all_tables_created():
    conn = get_in_memory_db()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    assert EXPECTED_TABLES.issubset(tables), (
        f"Missing tables: {EXPECTED_TABLES - tables}"
    )


def test_users_table_columns():
    conn = get_in_memory_db()
    cursor = conn.execute("PRAGMA table_info(users);")
    columns = {row[1] for row in cursor.fetchall()}
    assert {"id", "email", "password_hash", "created_at"}.issubset(columns)


def test_cv_profiles_table_columns():
    conn = get_in_memory_db()
    cursor = conn.execute("PRAGMA table_info(cv_profiles);")
    columns = {row[1] for row in cursor.fetchall()}
    assert {"id_user_page", "nom", "prenom", "user_id"}.issubset(columns)


# ---------------------------------------------------------------------------
# Foreign key enforcement tests
# ---------------------------------------------------------------------------

def test_fk_cv_profile_requires_existing_user():
    """Inserting a cv_profile with a non-existent user_id must fail."""
    conn = get_in_memory_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO cv_profiles (id_user_page, nom, prenom, user_id)
            VALUES ('profile-1', 'Dupont', 'Jean', 'nonexistent-uuid')
            """
        )
        conn.commit()


def test_fk_cv_profile_with_valid_user_succeeds():
    """Inserting a cv_profile linked to an existing user must succeed."""
    conn = get_in_memory_db()
    conn.execute(
        "INSERT INTO users (id, email, password_hash) VALUES ('uuid-1', 'user@test.com', 'hashed')"
    )
    conn.execute(
        """
        INSERT INTO cv_profiles (id_user_page, nom, prenom, user_id, slug)
        VALUES ('profile-1', 'Dupont', 'Jean', 'uuid-1', 'jean-dupont')
        """
    )
    conn.commit()
    cursor = conn.execute("SELECT nom FROM cv_profiles WHERE id_user_page = 'profile-1'")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "Dupont"


def test_fk_formation_requires_existing_cv_profile():
    """Inserting a formation with a non-existent id_user_page must fail."""
    conn = get_in_memory_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO formations (id_formation, nom_formation, date_debut, organisme_formation, id_user_page)
            VALUES ('form-1', 'Bac', '2020-01-01', 'Lycée X', 'nonexistent-profile')
            """
        )
        conn.commit()
