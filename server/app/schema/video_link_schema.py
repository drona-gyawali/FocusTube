from typing import List, Literal, Optional

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


class VideoLinkFileResponse(BaseModel):
    """
    A schema for a video link response extracted by files.
    """

    version: str = Field(..., description="The API version number.")
    status: int = Field(..., description="The HTTP status code of the response.")
    links: List[str] = Field(None, description="A list of video links (URLs).")
    source: Literal["file"] = Field("file", description="The source of the video link.")
    uploader: int = Field(..., description="The id of the user who uploaded the video.")
    message: str = Field(..., description="Message to be shown to user")


class LinkResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the user.")
    links: List[str] = Field(..., description="List of video URLs.")
    source: str = Field(..., description="Source of the video links.")
    uploader: str = Field(..., description="Uploader's email or identifier.")
    version: str = Field(..., description="API version.")
    message: Optional[str] = Field(None, description="Optional user message.")
    uploaded_at: Optional[str] = Field(
        None, description="Uploaded timestamp (ISO format)."
    )
