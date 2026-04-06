from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import get_current_user
from app.db.mongo import get_db
from app.schemas.project import Comment, ProjectUpdate, ProjectCreate, ProjectOut

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_projects(current_user = Depends(get_current_user), db = Depends(get_db)):
    cursor = db.projects.find()
    projects = await cursor.to_list(length=100)
    for p in projects:
        p["_id"] = str(p["_id"])
    return projects

# --- CREATE Project ---
@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user),   # authentication
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    new_project = project.dict()
    new_project["created_at"] = datetime.utcnow()
    new_project["updated_at"] = None
    new_project["comments"] = []      # optional, for future comments

    result = await db.projects.insert_one(new_project)
    created_project = await db.projects.find_one({"_id": result.inserted_id})

    # Convert _id to string for response
    created_project["id"] = str(created_project.pop("_id"))
    return created_project

# --- DELETE Project ---
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")

    result = await db.projects.delete_one({"_id": ObjectId(project_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")

    return None   # 204 No Content

@router.post("/{project_id}/comments")
async def add_comment(
    project_id: str,
    comment: Comment,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(400, "Invalid ID")
    comment.created_by = current_user["email"]  # or name
    result = await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$push": {"comments": comment.dict()}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Project not found")
    return {"message": "Comment added"}

@router.patch("/{project_id}")
async def update_project(
    project_id: str,
    update: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(400, "Invalid ID")
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(400, "No fields to update")
    result = await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": update_data, "$currentDate": {"updated_at": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Project not found")
    updated = await db.projects.find_one({"_id": ObjectId(project_id)})
    return updated