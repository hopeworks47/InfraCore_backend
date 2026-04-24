from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File, Request
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import get_current_user
from app.db.mongo import get_db
from app.schemas.project import Comment, ProjectUpdate, ProjectCreate, ProjectOut
from app.utils.file_utils import save_image

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_projects(current_user = Depends(get_current_user), db = Depends(get_db)):
    cursor = db.projects.find()
    projects = await cursor.to_list(length=100)
    for p in projects:
        p["_id"] = str(p["_id"])
    return projects

# --- CREATE Project ---
@router.post("/new-project", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    priority: str = Form("medium"),
    task_type: str = Form("Task"),
    assignee_id: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),
    status: str = Form("todo"),
    attachments: List[UploadFile] = File([]),  # 👈 accept multiple files
    db=Depends(get_db),
):
    # Parse due_date
    due_date_parsed = None
    if due_date:
        try:
            due_date_parsed = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(400, "Due date must be in YYYY-MM-DD format")

    # Handle multiple attachments
    attachment_paths = []
    for file in attachments:
        if file and file.filename:
            path = await save_image(file, "project_attachments")
            attachment_paths.append(path)

    # MongoDB document
    new_project = {
        "title": title,
        "description": description,
        "priority": priority,
        "task_type": task_type,
        "assignee_id": assignee_id,
        "due_date": due_date_parsed.isoformat() if due_date_parsed else None,
        "status": status,
        "attachments": attachment_paths,   # 👈 store array of paths
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.projects.insert_one(new_project)
    created = await db.projects.find_one({"_id": result.inserted_id})
    created["id"] = str(created["_id"])
    return created

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