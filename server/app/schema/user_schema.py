from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class ProfileResponse(BaseModel):
    version: str
    status: int
    id: int
    email: EmailStr
    profile_img: str = Field(default="profile/something")
    is_oauth: bool = Field(default=False)
    uploaded_links: List[str] = Field(default_factory=list)
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class Login(BaseModel):
    name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UploadProfile(BaseModel):
    version: str
    status: int
    file_id: str
    preview_url: str
    message: str
