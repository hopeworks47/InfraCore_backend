from fastapi import UploadFile, File
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = 'member'
    profile_image: UploadFile = File(None)
    birthdate: Optional[date] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    birthdate: Optional[date] = None
    profile_image: Optional[str] = None   # URL or path, for file upload use separate endpoint

    @validator('role')
    def validate_role(cls, v):
        allowed = ['admin', 'leader', 'member']
        if v and v not in allowed:
            raise ValueError(f'Role must be one of {allowed}')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    profile_image: Optional[str] = None
    birthdate: Optional[date] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refreshToken: str