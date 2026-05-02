"""
Public CV router — no authentication required.

DISCLAIMER: This module was written with assistance from GitHub Copilot
(Claude Sonnet 4.6) and reviewed by the project author.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from python.services.profiles import get_public_cv

router = APIRouter(prefix="/cv", tags=["cv"])

BASE_DIR = Path(__file__).resolve().parents[2]


@router.get("/{slug}/data")
def get_cv_data(slug: str):
    """
    Return the full public CV as JSON for a given slug.
    Returns 404 if the CV does not exist or is not public.
    """
    cv = get_public_cv(slug)
    if cv is None:
        raise HTTPException(status_code=404, detail="CV non trouvé ou non public")
    return cv


@router.get("/{slug}")
def get_cv_page(slug: str):
    """Serve the public CV HTML page for a given slug."""
    cv = get_public_cv(slug)
    if cv is None:
        raise HTTPException(status_code=404, detail="CV non trouvé ou non public")
    return FileResponse(BASE_DIR / "cv.html")
