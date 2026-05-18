"""
Authentication endpoints (register, login, logout) and JWT dependency.

DISCLAIMER: This module was written with assistance from GitHub Copilot
(Claude Sonnet 4.6) and reviewed by the project author.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from python.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from python.services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    decode_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Dependency: extract and validate JWT, return user_id."""
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    result = create_user(payload.email, payload.password)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    return {"message": "Account created"}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    result = authenticate_user(payload.email, payload.password)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])
    token = create_access_token(result["user_id"])
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout():
    # JWT is stateless — logout is handled client-side by deleting the token
    return {"message": "Logged out"}
