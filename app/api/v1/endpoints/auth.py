from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.user_service import (
    create_user,
    authenticate_user,
    get_user_by_email
)
from app.core.security import create_access_token
from app.db.mongo import get_db

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db=Depends(get_db)):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = await create_user(db, user.email, user.password)

    token = create_access_token({"sub": str(new_user["_id"])})

    return {"access_token": token}

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db=Depends(get_db)):
    db_user = await authenticate_user(db, user.email, user.password)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(db_user["_id"])})

    return {"access_token": token}