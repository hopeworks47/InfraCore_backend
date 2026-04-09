import datetime

from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from typing import Optional
from app.schemas.user import UserCreate, UserLogin, Token, RefreshRequest
from app.services.user_service import (
    create_user,
    authenticate_user,
    get_user_by_email
)
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.mongo import get_db

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(
        email: str = Form(...),
        password: str = Form(...),
        name: str = Form(...),
        role: str = Form("member"),
        birthdate: Optional[str] = Form(None),
        profile_image: Optional[UploadFile] = File(None),
        db=Depends(get_db)
):
    existing_user = await get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = await create_user(db, email, password, name, role, birthdate, profile_image)

    access_token = create_access_token({"sub": str(new_user["_id"])})
    refresh_token = create_refresh_token({"sub": str(new_user["_id"])})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db=Depends(get_db)):
    db_user = await authenticate_user(db, user.email, user.password)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens
    access_token = create_access_token({"sub": str(db_user["_id"])})
    refresh_token = create_refresh_token({"sub": str(db_user["_id"])})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    payload = decode_token(request.refreshToken)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token payload")

    # Optionally verify user still exists in DB
    # user = await db.users.find_one({"_id": ObjectId(user_id)})
    # if not user: raise HTTPException(401, "User not found")

    # Create new access token
    new_access_token = create_access_token(data={"sub": user_id})
    # (Optional) create a new refresh token as well – rotate tokens
    new_refresh_token = create_refresh_token(data={"sub": user_id})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }