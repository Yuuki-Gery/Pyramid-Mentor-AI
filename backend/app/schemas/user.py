from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=128)
    display_name: Optional[str] = ""


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    is_vip: bool
    background: str = ""
    skills: list = []
    interests: list = []
    goal: str = ""
    resources: list = []
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProfileUpdate(BaseModel):
    background: Optional[str] = None
    skills: Optional[list] = None
    interests: Optional[list] = None
    goal: Optional[str] = None
    resources: Optional[list] = None
    display_name: Optional[str] = None