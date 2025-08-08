from typing import List, Literal

from pydantic import BaseModel, EmailStr, Field


class VideoLinkRegister(BaseModel):
    """
    A schema for a video link register
    """

    links: List[str] = Field(None, description="A list of video links (URLs).")


class VideoLinkResponse(BaseModel):
    """
    A schema for a video link response.
    """

    version: str = Field(..., description="The API version number.")
    status: int = Field(..., description="The HTTP status code of the response.")
    links: List[str] = Field(None, description="A list of video links (URLs).")
    source: Literal["manual"] = Field(
        "manual", description="The source of the video link."
    )
    uploader: EmailStr = Field(
        ..., description="The email of the user who uploaded the video."
    )
