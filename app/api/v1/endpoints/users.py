from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from app.core.security import get_current_user  # your dependency that extracts user from token
from app.schemas.user import UserOut
from app.db.mongo import get_db

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
        "profileImage": current_user.get("profile_image"),
        "created_at": current_user["created_at"],
    }