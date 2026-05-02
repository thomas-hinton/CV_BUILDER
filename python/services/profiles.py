"""
Profile service: CRUD operations on cv_profiles table.

DISCLAIMER: This module was written with assistance from GitHub Copilot
(Claude Sonnet 4.6) and reviewed by the project author.
"""
import re
import unicodedata
import uuid

from python.database.connection import get_connection


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Convert a string to a URL-safe slug (lowercase ASCII, hyphens)."""
    # Normalize unicode (é → e, à → a, etc.)
    normalized = unicodedata.normalize("NFD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    # Lowercase, replace spaces/underscores with hyphens, strip non-alphanum
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug


def _generate_unique_slug(base_slug: str, exclude_user_page: str | None = None) -> str:
    """
    Return a slug that does not already exist in cv_profiles.
    If base_slug is taken, append -2, -3, etc.
    exclude_user_page: skip the profile with this id when checking (for updates).
    """
    conn = get_connection()
    try:
        candidate = base_slug
        counter = 2
        while True:
            row = conn.execute(
                "SELECT id_user_page FROM cv_profiles WHERE slug = ?", (candidate,)
            ).fetchone()
            if row is None or (exclude_user_page and row[0] == exclude_user_page):
                return candidate
            candidate = f"{base_slug}-{counter}"
            counter += 1
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_profile(user_id: str, nom: str, prenom: str, **kwargs) -> dict:
    """
    Create a cv_profile for user_id.
    Returns error dict if user already has a profile.
    """
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id_user_page FROM cv_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if existing:
            return {"status": "error", "code": 409, "message": "Ce compte possède déjà un profil CV"}

        profile_id = str(uuid.uuid4())
        base_slug = _slugify(f"{prenom} {nom}")
        slug = _generate_unique_slug(base_slug)

        conn.execute(
            """
            INSERT INTO cv_profiles
                (id_user_page, nom, prenom, photo_profil, tel, email, adresse,
                 user_id, slug, is_public, show_email, show_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
            """,
            (
                profile_id, nom, prenom,
                kwargs.get("photo_profil"),
                kwargs.get("tel"),
                kwargs.get("email"),
                kwargs.get("adresse"),
                user_id, slug,
            ),
        )
        conn.commit()
        return {"status": "created", "id_user_page": profile_id, "slug": slug}
    finally:
        conn.close()


def get_profile_by_user_id(user_id: str) -> dict | None:
    """Return profile dict for user_id or None if not found."""
    conn = get_connection()
    try:
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        row = conn.execute(
            "SELECT * FROM cv_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row
    finally:
        conn.close()


def update_profile(user_id: str, updates: dict) -> dict:
    """
    Apply a partial update (only keys present in updates are changed).
    Returns error dict if profile not found.
    If nom/prenom changes and no explicit slug given, regenerate slug.
    """
    conn = get_connection()
    try:
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        profile = conn.execute(
            "SELECT * FROM cv_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not profile:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}

        # If slug explicitly provided, validate uniqueness
        if "slug" in updates:
            new_slug = _generate_unique_slug(updates["slug"], exclude_user_page=profile["id_user_page"])
            updates["slug"] = new_slug
        elif "nom" in updates or "prenom" in updates:
            # Regenerate slug from new name
            nom = updates.get("nom", profile["nom"])
            prenom = updates.get("prenom", profile["prenom"])
            base_slug = _slugify(f"{prenom} {nom}")
            updates["slug"] = _generate_unique_slug(base_slug, exclude_user_page=profile["id_user_page"])

        allowed = {
            "nom", "prenom", "photo_profil", "tel", "email", "adresse",
            "slug", "is_public", "show_email", "show_phone",
        }
        filtered = {k: v for k, v in updates.items() if k in allowed}
        if not filtered:
            return {"status": "error", "code": 422, "message": "Aucun champ valide à mettre à jour"}

        set_clause = ", ".join(f"{k} = ?" for k in filtered)
        values = list(filtered.values()) + [user_id]
        conn.execute(
            f"UPDATE cv_profiles SET {set_clause} WHERE user_id = ?", values  # noqa: S608
        )
        conn.commit()
        return {"status": "updated"}
    finally:
        conn.close()


def delete_profile(user_id: str) -> dict:
    """Delete the profile (and cascade-delete formations/experiences via FK)."""
    conn = get_connection()
    try:
        profile = conn.execute(
            "SELECT id_user_page FROM cv_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not profile:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        conn.execute("DELETE FROM cv_profiles WHERE user_id = ?", (user_id,))
        conn.commit()
        return {"status": "deleted"}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Helper: resolve id_user_page from user_id
# ---------------------------------------------------------------------------

def _get_profile_id(conn, user_id: str) -> str | None:
    row = conn.execute(
        "SELECT id_user_page FROM cv_profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    return row[0] if row else None


def _row_factory(conn):
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))


# ---------------------------------------------------------------------------
# Formations CRUD
# ---------------------------------------------------------------------------

def create_formation(user_id: str, data: dict) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        formation_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO formations
                (id_formation, nom_formation, date_debut, date_fin,
                 description_formation, organisme_formation, diplome_url, id_user_page)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                formation_id,
                data["nom_formation"],
                str(data["date_debut"]),
                str(data["date_fin"]) if data.get("date_fin") else None,
                data.get("description_formation"),
                data["organisme_formation"],
                data.get("diplome_url"),
                profile_id,
            ),
        )
        conn.commit()
        return {"status": "created", "id_formation": formation_id}
    finally:
        conn.close()


def get_formations(user_id: str) -> list[dict]:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return []
        _row_factory(conn)
        return conn.execute(
            "SELECT * FROM formations WHERE id_user_page = ?", (profile_id,)
        ).fetchall()
    finally:
        conn.close()


def update_formation(user_id: str, formation_id: str, updates: dict) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        row = conn.execute(
            "SELECT id_formation FROM formations WHERE id_formation = ? AND id_user_page = ?",
            (formation_id, profile_id),
        ).fetchone()
        if not row:
            return {"status": "error", "code": 404, "message": "Formation non trouvée"}
        allowed = {
            "nom_formation", "date_debut", "date_fin",
            "description_formation", "organisme_formation", "diplome_url",
        }
        filtered = {k: (str(v) if hasattr(v, "isoformat") else v)
                    for k, v in updates.items() if k in allowed}
        if not filtered:
            return {"status": "error", "code": 422, "message": "Aucun champ valide"}
        set_clause = ", ".join(f"{k} = ?" for k in filtered)
        conn.execute(
            f"UPDATE formations SET {set_clause} WHERE id_formation = ?",  # noqa: S608
            [*filtered.values(), formation_id],
        )
        conn.commit()
        return {"status": "updated"}
    finally:
        conn.close()


def delete_formation(user_id: str, formation_id: str) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        row = conn.execute(
            "SELECT id_formation FROM formations WHERE id_formation = ? AND id_user_page = ?",
            (formation_id, profile_id),
        ).fetchone()
        if not row:
            return {"status": "error", "code": 404, "message": "Formation non trouvée"}
        conn.execute("DELETE FROM formations WHERE id_formation = ?", (formation_id,))
        conn.commit()
        return {"status": "deleted"}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Experiences CRUD
# ---------------------------------------------------------------------------

def create_experience(user_id: str, data: dict) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        experience_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO experiences
                (id_experience, nom_experience, date_debut, date_fin,
                 description_experience, organisme_experience, lieu_experience, id_user_page)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experience_id,
                data["nom_experience"],
                str(data["date_debut"]),
                str(data["date_fin"]) if data.get("date_fin") else None,
                data.get("description_experience"),
                data.get("organisme_experience"),
                data.get("lieu_experience"),
                profile_id,
            ),
        )
        conn.commit()
        return {"status": "created", "id_experience": experience_id}
    finally:
        conn.close()


def get_experiences(user_id: str) -> list[dict]:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return []
        _row_factory(conn)
        return conn.execute(
            "SELECT * FROM experiences WHERE id_user_page = ?", (profile_id,)
        ).fetchall()
    finally:
        conn.close()


def update_experience(user_id: str, experience_id: str, updates: dict) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        row = conn.execute(
            "SELECT id_experience FROM experiences WHERE id_experience = ? AND id_user_page = ?",
            (experience_id, profile_id),
        ).fetchone()
        if not row:
            return {"status": "error", "code": 404, "message": "Expérience non trouvée"}
        allowed = {
            "nom_experience", "date_debut", "date_fin",
            "description_experience", "organisme_experience", "lieu_experience",
        }
        filtered = {k: (str(v) if hasattr(v, "isoformat") else v)
                    for k, v in updates.items() if k in allowed}
        if not filtered:
            return {"status": "error", "code": 422, "message": "Aucun champ valide"}
        set_clause = ", ".join(f"{k} = ?" for k in filtered)
        conn.execute(
            f"UPDATE experiences SET {set_clause} WHERE id_experience = ?",  # noqa: S608
            [*filtered.values(), experience_id],
        )
        conn.commit()
        return {"status": "updated"}
    finally:
        conn.close()


def delete_experience(user_id: str, experience_id: str) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        row = conn.execute(
            "SELECT id_experience FROM experiences WHERE id_experience = ? AND id_user_page = ?",
            (experience_id, profile_id),
        ).fetchone()
        if not row:
            return {"status": "error", "code": 404, "message": "Expérience non trouvée"}
        conn.execute("DELETE FROM experiences WHERE id_experience = ?", (experience_id,))
        conn.commit()
        return {"status": "deleted"}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Skills CRUD
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Public CV — no auth required
# ---------------------------------------------------------------------------

def get_public_cv(slug: str) -> dict | None:
    """
    Return the full public CV for a given slug, or None if not found/private.
    Respects show_email and show_phone flags.
    """
    conn = get_connection()
    try:
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))

        profile = conn.execute(
            "SELECT * FROM cv_profiles WHERE slug = ? AND is_public = 1", (slug,)
        ).fetchone()
        if not profile:
            return None

        profile_id = profile["id_user_page"]

        # Mask contact info if owner chose to hide it
        if not profile["show_email"]:
            profile["email"] = None
        if not profile["show_phone"]:
            profile["tel"] = None

        formations = conn.execute(
            "SELECT * FROM formations WHERE id_user_page = ?", (profile_id,)
        ).fetchall()

        experiences = conn.execute(
            "SELECT * FROM experiences WHERE id_user_page = ?", (profile_id,)
        ).fetchall()

        skills = conn.execute(
            "SELECT * FROM skills WHERE id_user_page = ?", (profile_id,)
        ).fetchall()

        return {
            "profile": profile,
            "formations": formations,
            "experiences": experiences,
            "skills": skills,
        }
    finally:
        conn.close()


def create_skill(user_id: str, data: dict) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        skill_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO skills (id_skill, nom_skill, niveau, categorie, id_user_page)
            VALUES (?, ?, ?, ?, ?)
            """,
            (skill_id, data["nom_skill"], data.get("niveau"), data.get("categorie"), profile_id),
        )
        conn.commit()
        return {"status": "created", "id_skill": skill_id}
    finally:
        conn.close()


def get_skills(user_id: str) -> list[dict]:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return []
        _row_factory(conn)
        return conn.execute(
            "SELECT * FROM skills WHERE id_user_page = ?", (profile_id,)
        ).fetchall()
    finally:
        conn.close()


def update_skill(user_id: str, skill_id: str, updates: dict) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        row = conn.execute(
            "SELECT id_skill FROM skills WHERE id_skill = ? AND id_user_page = ?",
            (skill_id, profile_id),
        ).fetchone()
        if not row:
            return {"status": "error", "code": 404, "message": "Compétence non trouvée"}
        allowed = {"nom_skill", "niveau", "categorie"}
        filtered = {k: v for k, v in updates.items() if k in allowed}
        if not filtered:
            return {"status": "error", "code": 422, "message": "Aucun champ valide"}
        set_clause = ", ".join(f"{k} = ?" for k in filtered)
        conn.execute(
            f"UPDATE skills SET {set_clause} WHERE id_skill = ?",  # noqa: S608
            [*filtered.values(), skill_id],
        )
        conn.commit()
        return {"status": "updated"}
    finally:
        conn.close()


def delete_skill(user_id: str, skill_id: str) -> dict:
    conn = get_connection()
    try:
        profile_id = _get_profile_id(conn, user_id)
        if not profile_id:
            return {"status": "error", "code": 404, "message": "Profil non trouvé"}
        row = conn.execute(
            "SELECT id_skill FROM skills WHERE id_skill = ? AND id_user_page = ?",
            (skill_id, profile_id),
        ).fetchone()
        if not row:
            return {"status": "error", "code": 404, "message": "Compétence non trouvée"}
        conn.execute("DELETE FROM skills WHERE id_skill = ?", (skill_id,))
        conn.commit()
        return {"status": "deleted"}
    finally:
        conn.close()
