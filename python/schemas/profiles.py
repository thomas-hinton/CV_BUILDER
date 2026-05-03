"""
Pydantic schemas for cv_profiles, formations, experiences and skills.

DISCLAIMER: This module was written with assistance from GitHub Copilot
(Claude Sonnet 4.6) and reviewed by the project author.
"""
import re
from datetime import date

from pydantic import BaseModel, EmailStr, field_validator, model_validator

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_TEL_RE = re.compile(r"^\d{10}$")


# ---------------------------------------------------------------------------
# Profile — cv_profiles table
# ---------------------------------------------------------------------------

class ProfileCreate(BaseModel):
    nom: str
    prenom: str
    photo_profil: str | None = None
    tel: str | None = None
    email: EmailStr | None = None
    adresse: str | None = None

    @field_validator("nom", "prenom")
    @classmethod
    def max_50(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 50:
            raise ValueError("50 caractères maximum")
        if not v:
            raise ValueError("Ne peut pas être vide")
        return v

    @field_validator("tel")
    @classmethod
    def tel_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _TEL_RE.match(v):
            raise ValueError("Le téléphone doit contenir exactement 10 chiffres")
        return v


class ProfileUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    photo_profil: str | None = None
    tel: str | None = None
    email: EmailStr | None = None
    adresse: str | None = None
    slug: str | None = None
    is_public: bool | None = None
    show_email: bool | None = None
    show_phone: bool | None = None

    @field_validator("nom", "prenom")
    @classmethod
    def max_50(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError("50 caractères maximum")
        if not v:
            raise ValueError("Ne peut pas être vide")
        return v

    @field_validator("tel")
    @classmethod
    def tel_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _TEL_RE.match(v):
            raise ValueError("Le téléphone doit contenir exactement 10 chiffres")
        return v

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower()
        if not _SLUG_RE.match(v):
            raise ValueError(
                "Le slug ne peut contenir que des lettres minuscules, "
                "des chiffres et des tirets (ex: thomas-hinton)"
            )
        if len(v) > 100:
            raise ValueError("100 caractères maximum pour le slug")
        return v


class ProfileResponse(BaseModel):
    id_user_page: str
    user_id: str
    nom: str
    prenom: str
    photo_profil: str | None
    tel: str | None
    email: str | None
    adresse: str | None
    slug: str | None
    is_public: bool
    show_email: bool
    show_phone: bool


# ---------------------------------------------------------------------------
# Formation — formations table
# ---------------------------------------------------------------------------

class FormationCreate(BaseModel):
    nom_formation: str
    date_debut: date
    date_fin: date | None = None
    description_formation: str | None = None
    organisme_formation: str
    diplome_url: str | None = None

    @field_validator("nom_formation", "organisme_formation")
    @classmethod
    def max_50(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 50:
            raise ValueError("50 caractères maximum")
        if not v:
            raise ValueError("Ne peut pas être vide")
        return v

    @model_validator(mode="after")
    def date_fin_after_debut(self) -> "FormationCreate":
        if self.date_fin is not None and self.date_fin < self.date_debut:
            raise ValueError("date_fin doit être postérieure ou égale à date_debut")
        return self


class FormationUpdate(BaseModel):
    nom_formation: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    description_formation: str | None = None
    organisme_formation: str | None = None
    diplome_url: str | None = None

    @field_validator("nom_formation", "organisme_formation")
    @classmethod
    def max_50(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError("50 caractères maximum")
        if not v:
            raise ValueError("Ne peut pas être vide")
        return v

    @model_validator(mode="after")
    def date_fin_after_debut(self) -> "FormationUpdate":
        if (
            self.date_fin is not None
            and self.date_debut is not None
            and self.date_fin < self.date_debut
        ):
            raise ValueError("date_fin doit être postérieure ou égale à date_debut")
        return self


class FormationResponse(BaseModel):
    id_formation: str
    nom_formation: str
    date_debut: date
    date_fin: date | None
    description_formation: str | None
    organisme_formation: str
    diplome_url: str | None
    id_user_page: str


# ---------------------------------------------------------------------------
# Experience — experiences table
# ---------------------------------------------------------------------------

class ExperienceCreate(BaseModel):
    nom_experience: str
    date_debut: date
    date_fin: date | None = None
    description_experience: str | None = None
    organisme_experience: str | None = None
    lieu_experience: str | None = None

    @field_validator("nom_experience")
    @classmethod
    def max_50(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 50:
            raise ValueError("50 caractères maximum")
        if not v:
            raise ValueError("Ne peut pas être vide")
        return v

    @field_validator("organisme_experience")
    @classmethod
    def organisme_max_50(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError("50 caractères maximum")
        return v

    @model_validator(mode="after")
    def date_fin_after_debut(self) -> "ExperienceCreate":
        if self.date_fin is not None and self.date_fin < self.date_debut:
            raise ValueError("date_fin doit être postérieure ou égale à date_debut")
        return self


class ExperienceUpdate(BaseModel):
    nom_experience: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    description_experience: str | None = None
    organisme_experience: str | None = None
    lieu_experience: str | None = None

    @field_validator("nom_experience")
    @classmethod
    def max_50(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError("50 caractères maximum")
        if not v:
            raise ValueError("Ne peut pas être vide")
        return v

    @field_validator("organisme_experience")
    @classmethod
    def organisme_max_50(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError("50 caractères maximum")
        return v

    @model_validator(mode="after")
    def date_fin_after_debut(self) -> "ExperienceUpdate":
        if (
            self.date_fin is not None
            and self.date_debut is not None
            and self.date_fin < self.date_debut
        ):
            raise ValueError("date_fin doit être postérieure ou égale à date_debut")
        return self


class ExperienceResponse(BaseModel):
    id_experience: str
    nom_experience: str
    date_debut: date
    date_fin: date | None
    description_experience: str | None
    organisme_experience: str | None
    lieu_experience: str | None
    id_user_page: str


# ---------------------------------------------------------------------------
# Skill — skills table
# ---------------------------------------------------------------------------

class SkillCreate(BaseModel):
    nom_skill: str
    niveau: str | None = None
    categorie: str | None = None

    @field_validator("nom_skill")
    @classmethod
    def max_100(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 100:
            raise ValueError("100 caractères maximum")
        if not v:
            raise ValueError("Ne peut pas être vide")
        return v

    @field_validator("niveau", "categorie")
    @classmethod
    def max_100_optional(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 100:
            raise ValueError("100 caractères maximum")
        return v


class SkillUpdate(BaseModel):
    nom_skill: str | None = None
    niveau: str | None = None
    categorie: str | None = None

    @field_validator("nom_skill")
    @classmethod
    def max_100(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 100:
            raise ValueError("100 caractères maximum")
        if not v:
            raise ValueError("Ne peut pas être vide")
        return v

    @field_validator("niveau", "categorie")
    @classmethod
    def max_100_optional(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 100:
            raise ValueError("100 caractères maximum")
        return v


class SkillResponse(BaseModel):
    id_skill: str
    nom_skill: str
    niveau: str | None
    categorie: str | None
    id_user_page: str

