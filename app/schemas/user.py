from dataclasses import Field

from fastapi import UploadFile, File
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, validator

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

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('new_password and confirm_password do not match')
        return v