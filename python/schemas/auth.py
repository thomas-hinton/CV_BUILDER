"""
Pydantic schemas for authentication (register, login, token response).

DISCLAIMER: This module was written with assistance from GitHub Copilot
(Claude Sonnet 4.6) and reviewed by the project author.
"""
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
