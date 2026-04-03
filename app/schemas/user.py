from fastapi import UploadFile, File
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = 'member'
    profileImage: UploadFile = File(None)
    birthdate: Optional[date] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    profileImage: Optional[str] = None
    birthdate: Optional[date] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"