from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.auth.supabase_auth import authenticate


router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def api_login(payload: LoginRequest) -> dict:
    try:
        user = authenticate(payload.email, payload.password)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return {
        "access_token": user.user_id,
        "token_type": "bearer",
        "user": asdict(user),
    }