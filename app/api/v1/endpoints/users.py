from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from app.services.user_service import (
    fetch_users
)
from app.db.mongo import get_db
router = APIRouter()

@router.get("/")
async def get_users(db=Depends(get_db)):
    users = await fetch_users(db)
    return jsonable_encoder(users, custom_encoder={ObjectId: str})
