from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class ProfileResponse(BaseModel):
    """
    Response schema for user profile information.
    """

    version: str
    status: int
    id: int
    email: EmailStr
    profile_img: str = Field(
        default="profile/something",
        description="URL or path to the user's profile image",
    )
    is_oauth: bool = Field(
        default=False, description="Indicates if the user registered via OAuth"
    )
    uploaded_links: int = Field(
        default_factory=list, description="Count of uploaded link URLs"
    )
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    """
    Schema for user registration.
    """

    email: EmailStr
    password: str


class Login(BaseModel):
    """
    Schema for user login.
    """

    name: str
    password: str


class Token(BaseModel):
    """
    Schema for authentication token.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for token data.
    """

    user_id: Optional[int] = None


class UploadProfile(BaseModel):
    """
    Response schema for profile upload.
    """

    version: str
    status: int
    file_id: str
    preview_url: str
    message: str
