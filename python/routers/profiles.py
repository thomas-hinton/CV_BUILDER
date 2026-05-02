from fastapi import APIRouter, Depends, HTTPException, status

from python.routers.auth import get_current_user
from python.schemas.profiles import ProfileCreate, ProfileResponse, ProfileUpdate
from python.services.profiles import (
    create_profile,
    delete_profile,
    get_profile_by_user_id,
    update_profile,
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
