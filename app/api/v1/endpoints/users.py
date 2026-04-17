from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from typing import Optional
from datetime import datetime
from app.core.security import get_current_user  # your dependency that extracts user from token
from app.schemas.user import UserOut, UserUpdate
from app.db.mongo import get_db
from app.utils.file_utils import save_profile_image, delete_old_image

from app.services.user_service import (
    fetch_users
)

router = APIRouter()

@router.get("/")
async def get_users(db=Depends(get_db)):
    users = await fetch_users(db)
    return jsonable_encoder(users, custom_encoder={ObjectId: str})

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get the currently logged-in user's information.
    The token is extracted from the Authorization header.
    """
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "name": current_user.get("name"),
        "role": current_user.get("role"),
        "profile_image": current_user.get("profile_image"),
        "created_at": current_user["created_at"],
    }

@router.put("/{user_id}")
async def update_user_by_id(
    user_id: str,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    birthdate: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    # 1. Authorization: only the user themselves or an admin can update
    if str(current_user["_id"]) != user_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 2. Validate user_id
    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, "Invalid user ID")

    update_dict = {}

    # 3. Text fields
    if name is not None:
        update_dict["name"] = name
    if email is not None:
        # Check email uniqueness (exclude current user)
        existing = await db.users.find_one({"email": email, "_id": {"$ne": ObjectId(user_id)}})
        if existing:
            raise HTTPException(400, "Email already in use")
        update_dict["email"] = email
    if role is not None:
        if role not in ["admin", "leader", "member"]:
            raise HTTPException(400, "Invalid role")
        update_dict["role"] = role
    if birthdate is not None:
        try:
            datetime.strptime(birthdate, "%Y-%m-%d")
            update_dict["birthdate"] = birthdate
        except ValueError:
            raise HTTPException(400, "Invalid date format (YYYY-MM-DD)")

    # 4. Profile image upload
    if profile_image and profile_image.filename:
        # Delete old image if it exists
        old_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if old_user and old_user.get("profile_image"):
            delete_old_image(old_user["profile_image"])
        # Save new image
        image_path = await save_profile_image(profile_image)
        update_dict["profile_image"] = image_path

    if not update_dict:
        raise HTTPException(400, "No fields to update")

    update_dict["updated_at"] = datetime.utcnow()
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "User not found")

    # Fetch updated user
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    return {
        "id": str(updated_user["_id"]),
        "email": updated_user["email"],
        "name": updated_user.get("name"),
        "role": updated_user.get("role"),
        "profileImage": updated_user.get("profile_image"),
        "birthdate": updated_user.get("birthdate"),
        "created_at": updated_user["created_at"],
    }