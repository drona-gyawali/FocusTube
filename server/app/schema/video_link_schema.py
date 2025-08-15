from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class DefaultResponse(BaseModel):
    """
    A Default Response to show
    """

    version: str = Field(..., description="API version")
    status: int = Field(..., description="Response status code")
    uploader: EmailStr = Field(..., description="Uploader's email address")
    message: str = Field(..., description="Response message")


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


class PlaylistRegister(BaseModel):
    name: str = Field(..., description="Name of the playlist")
    description: str = Field(None, description="Description of the playlist")


class PlaylistCreationResponse(BaseModel):
    version: str = Field(..., description="API version")
    status: int = Field(..., description="Response Status Code")
    creator: str = Field(..., description="Owner of the playlist")
    playlist_id: int = Field(..., description="Unique id of the playlist")
    playlist_name: str = Field(..., description="Name of the playlist")
    message: str = Field(..., description="Response Message")


class PlaylistAddLinks(BaseModel):
    video_id: int = Field(..., description="Unique Id of the Video")
    playlist_id: int = Field(..., description="Unique Id of the Playlist")


class AddVideoToPlaylistResponse(BaseModel):
    version: str = Field(..., description="API version")
    status: int = Field(..., description="Response status code")
    creator: str = Field(..., description="Owner of the playlist")
    video_id: int = Field(..., description="Unique Id of the Video")
    playlist_id: int = Field(..., description="Unique Id of the Playlist")
    message: str = Field(..., description="Response message")


class VisibilityRegister(BaseModel):
    playlist_id: int = Field(..., description="Unique id of playlist")
    visibility: str = Field(
        ..., description="Permission to public or private of playlist"
    )


class PlaylistVideos(BaseModel):
    playlist_id: int = Field(..., description="Unique ID of the playlist")
    playlist_name: str = Field(..., description="Name of the playlist")
    description: Optional[str] = Field(None, description="Description of the playlist")
    visibility: str = Field(..., description="Playlist visibility")
    creator_email: str = Field(..., description="Email of the creator")
    videos: List[VideoMetadata] = Field(
        ..., description="List of videos in the playlist"
    )


class PlaylistWithVideosResponse(BaseModel):
    version: str = Field(..., description="API version")
    status: int = Field(..., description="Response status code")
    playlists: List[PlaylistVideos] = Field(
        ..., description="List of playlists with their videos"
    )
    message: str = Field(..., description="Response message")


class ProgressTrackerRegister(BaseModel):
    last_time_watched: float = Field(..., description="Last watch time of the video")


class ProgressTrackerResponse(BaseModel):
    version: str = Field(..., description="API version")
    is_completed: bool = Field(
        default=False, description="Marker to know videos status"
    )
    last_time_watched: float = Field(..., description="Last WatchTime of the video")
    duration: float = Field(..., description="Total duration of the video")
    completion_percentage: float = Field(
        ..., description="Percentage by completion of the video"
    )
    message: str = Field(..., description="Response Message")


class PlaylistProgressTrackerResponse(BaseModel):
    version: str = Field(..., description="API version")
    status: int = Field(..., description="Status code of the http response")
    playlist_id: int = Field(..., desccription="Id of the playlist")
    playlist_name: str = Field(..., desccription="Name of the playlist")
    completion_percentage: float = Field(
        ..., description="Percentage by completion of the video"
    )
    videos_completed: int = Field(
        ..., desccription="Total count of the completed videos"
    )
    total_videos: int = Field(..., desccription="Total number of the videos")
