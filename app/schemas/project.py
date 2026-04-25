from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from bson import ObjectId

class Comment(BaseModel):
    text: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = "medium"
    task_type: str = "Task"
    assignee_id: Optional[str] = None
    due_date: Optional[date] = None
    status: str = "todo"
    attachments: Optional[List[str]] = None  # 👈 array of URLs

class ProjectOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: str
    task_type: str
    assignee_id: Optional[str] = None
    due_date: Optional[str] = None
    status: str
    attachments: Optional[List[str]] = None   # 👈 array of URLs
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectUpdate(BaseModel):
    _id: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    task_type: str
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    attachments: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)