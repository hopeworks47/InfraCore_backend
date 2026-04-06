from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class Comment(BaseModel):
    text: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"   # low, medium, high
    assignee_id: Optional[str] = None   # user ObjectId
    due_date: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    comments: Optional[List[Comment]] = None

class ProjectOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    priority: str
    assignee_id: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]