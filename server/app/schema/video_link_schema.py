from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class VideoLinkRegister(BaseModel):
    """
    A schema for a video link register
    """

    links: List[str] = Field(..., description="A list of video links (URLs).")


class VideoMetadata(BaseModel):
    """
    A schema for a video metadata
    """

    id: int = Field(None, description="The unique id of the video links.")
    etag: Optional[str] = Field(
        None, description="The ETag of the YouTube video metadata."
    )
    title: Optional[str] = Field(None, description="The title of the YouTube video.")
    description: Optional[str] = Field(
        None, description="The description of the YouTube video."
    )
    published_at: Optional[str] = Field(
        None, description="Publish date of the video (ISO format)."
    )
    channel_title: Optional[str] = (
        Field(None, description="The name of the channel publishing the video."),
    )
    thumbnail_url: Optional[str] = (
        Field(None, description="The url of the video thumbnail."),
    )
    uploaded_at: Optional[str] = Field(
        None, description="uploaded date by user in the system"
    )
    embedded_url: Optional[str] = Field(
        None, description="The embed url to render in frontend (youtube embed)"
    )


class VideoLinkWithMetadata(BaseModel):
    """
    A schema with url and metadata
    """

    url: str = Field(..., description="The video link (URL).")
    metadata: Optional[VideoMetadata] = Field(
        None, description="Metadata for the video link."
    )


class VideoLinkResponse(BaseModel):
    """
    A schema to respond with video link information
    """

    version: str = Field(..., description="API version")
    status: int = Field(..., description="Response status code")
    links: List[VideoLinkWithMetadata] = Field(
        ..., description="List of video links with metadata"
    )
    source: Literal["manual"] = Field("manual", description="Source of the video links")
    uploader: EmailStr = Field(..., description="Uploader's email address")
    message: str = Field(..., description="Response message")


class VideoLinkFileResponse(BaseModel):
    """
    A schema for a video link response extracted by files.
    """

    version: str = Field(..., description="API version")
    status: int = Field(..., description="Response status code")
    links: List[VideoLinkWithMetadata] = Field(
        ..., description="List of video links with metadata"
    )
    source: Literal["file"] = Field("file", description="Source of the video links")
    uploader: EmailStr = Field(..., description="Uploader's email address")
    message: str = Field(..., description="Response message")


class LinkResponse(BaseModel):
    version: str = Field(..., description="API version")
    status: int = Field(..., description="Response status code")
    links: List[VideoLinkWithMetadata] = Field(
        ..., description="List of video links with metadata"
    )
    source: Literal["file", "manual", "mixed"] = Field(
        "file", description="Source of the video links"
    )
    uploader: EmailStr = Field(..., description="Uploader's email address")
    message: str = Field(..., description="Response message")
