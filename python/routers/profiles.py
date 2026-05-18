"""
Profile, formation, experience and skill endpoints.

DISCLAIMER: This module was written with assistance from GitHub Copilot
(Claude Sonnet 4.6) and reviewed by the project author.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from python.routers.auth import get_current_user
from python.schemas.profiles import (
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
    FormationCreate,
    FormationResponse,
    FormationUpdate,
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
)
from python.services.profiles import (
    create_experience,
    create_formation,
    create_profile,
    create_skill,
    delete_experience,
    delete_formation,
    delete_profile,
    delete_skill,
    get_experiences,
    get_formations,
    get_profile_by_user_id,
    get_skills,
    update_experience,
    update_formation,
    update_profile,
    update_skill,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProfileResponse)
def create_my_profile(
    payload: ProfileCreate,
    user_id: str = Depends(get_current_user),
):
    result = create_profile(
        user_id=user_id,
        nom=payload.nom,
        prenom=payload.prenom,
        photo_profil=payload.photo_profil,
        tel=payload.tel,
        email=str(payload.email) if payload.email else None,
        adresse=payload.adresse,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    profile = get_profile_by_user_id(user_id)
    return _to_response(profile)


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(user_id: str = Depends(get_current_user)):
    profile = get_profile_by_user_id(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return _to_response(profile)


@router.patch("/me", response_model=ProfileResponse)
def update_my_profile(
    payload: ProfileUpdate,
    user_id: str = Depends(get_current_user),
):
    updates = payload.model_dump(exclude_none=True)
    if payload.email is not None:
        updates["email"] = str(payload.email)
    result = update_profile(user_id, updates)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    return _to_response(get_profile_by_user_id(user_id))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_profile(user_id: str = Depends(get_current_user)):
    result = delete_profile(user_id)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])


# ---------------------------------------------------------------------------
# Formations
# ---------------------------------------------------------------------------

@router.post(
    "/me/educations",
    status_code=status.HTTP_201_CREATED,
    response_model=FormationResponse,
)
def add_education(payload: FormationCreate, user_id: str = Depends(get_current_user)):
    result = create_formation(user_id, payload.model_dump())
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    formations = get_formations(user_id)
    row = next(f for f in formations if f["id_formation"] == result["id_formation"])
    return FormationResponse(**row)


@router.get("/me/educations", response_model=list[FormationResponse])
def list_educations(user_id: str = Depends(get_current_user)):
    return [FormationResponse(**r) for r in get_formations(user_id)]


@router.patch("/me/educations/{formation_id}", response_model=FormationResponse)
def edit_education(
    formation_id: str,
    payload: FormationUpdate,
    user_id: str = Depends(get_current_user),
):
    result = update_formation(user_id, formation_id, payload.model_dump(exclude_none=True))
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    row = next(f for f in get_formations(user_id) if f["id_formation"] == formation_id)
    return FormationResponse(**row)


@router.delete("/me/educations/{formation_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_education(formation_id: str, user_id: str = Depends(get_current_user)):
    result = delete_formation(user_id, formation_id)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])


# ---------------------------------------------------------------------------
# Experiences
# ---------------------------------------------------------------------------

@router.post(
    "/me/experiences",
    status_code=status.HTTP_201_CREATED,
    response_model=ExperienceResponse,
)
def add_experience(payload: ExperienceCreate, user_id: str = Depends(get_current_user)):
    result = create_experience(user_id, payload.model_dump())
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    experiences = get_experiences(user_id)
    row = next(e for e in experiences if e["id_experience"] == result["id_experience"])
    return ExperienceResponse(**row)


@router.get("/me/experiences", response_model=list[ExperienceResponse])
def list_experiences(user_id: str = Depends(get_current_user)):
    return [ExperienceResponse(**r) for r in get_experiences(user_id)]


@router.patch("/me/experiences/{experience_id}", response_model=ExperienceResponse)
def edit_experience(
    experience_id: str,
    payload: ExperienceUpdate,
    user_id: str = Depends(get_current_user),
):
    result = update_experience(user_id, experience_id, payload.model_dump(exclude_none=True))
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    row = next(e for e in get_experiences(user_id) if e["id_experience"] == experience_id)
    return ExperienceResponse(**row)


@router.delete("/me/experiences/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_experience(experience_id: str, user_id: str = Depends(get_current_user)):
    result = delete_experience(user_id, experience_id)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

@router.post("/me/skills", status_code=status.HTTP_201_CREATED, response_model=SkillResponse)
def add_skill(payload: SkillCreate, user_id: str = Depends(get_current_user)):
    result = create_skill(user_id, payload.model_dump())
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    skills = get_skills(user_id)
    row = next(s for s in skills if s["id_skill"] == result["id_skill"])
    return SkillResponse(**row)


@router.get("/me/skills", response_model=list[SkillResponse])
def list_skills(user_id: str = Depends(get_current_user)):
    return [SkillResponse(**r) for r in get_skills(user_id)]


@router.patch("/me/skills/{skill_id}", response_model=SkillResponse)
def edit_skill(
    skill_id: str,
    payload: SkillUpdate,
    user_id: str = Depends(get_current_user),
):
    result = update_skill(user_id, skill_id, payload.model_dump(exclude_none=True))
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    row = next(s for s in get_skills(user_id) if s["id_skill"] == skill_id)
    return SkillResponse(**row)


@router.delete("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill(skill_id: str, user_id: str = Depends(get_current_user)):
    result = delete_skill(user_id, skill_id)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _to_response(row: dict) -> ProfileResponse:
    return ProfileResponse(
        id_user_page=row["id_user_page"],
        user_id=row["user_id"],
        nom=row["nom"],
        prenom=row["prenom"],
        photo_profil=row.get("photo_profil"),
        tel=row.get("tel"),
        email=row.get("email"),
        adresse=row.get("adresse"),
        slug=row.get("slug"),
        is_public=bool(row["is_public"]),
        show_email=bool(row["show_email"]),
        show_phone=bool(row["show_phone"]),
    )
