
from fastapi import UploadFile, File, Form
from typing import Optional
from datetime import datetime

from app.utils.file_utils import save_profile_image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.schemas.user import UserOut
from app.core.security import verify_password, hash_password

async def get_user_by_email(db, email: str):
    return await db.users.find_one({"email": email})

async def fetch_users(db):
    return await db.users.find().to_list(length=None)

async def create_user(
        db,
        email: str = Form(...),
        password: str = Form(...),
        name: str = Form(...),
        role: str = Form(...),
        birthdate: Optional[str] = Form(None),
        profile_image: Optional[UploadFile] = File(None),
):
    profile_image_path = None
    if profile_image and profile_image.filename:
        profile_image_path = await save_profile_image(profile_image)

    # Hash password (implement hash_password accordingly)
    hashed = hash_password(password)

    new_user = {
        "email": email,
        "hashed_password": hashed,
        "name": name,
        "role": role,
        "profile_image": profile_image_path,
        "birthdate": birthdate,  # already string from Form
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)
    return new_user

async def authenticate_user(db, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

async def update_user_password(db: AsyncSession, user_id: int, new_hashed_password: str):
    await db.execute(
        update(UserOut).where(UserOut.id == user_id).values(hashed_password=new_hashed_password)
    )
    await db.commit()