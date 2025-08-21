import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.config import Base
from app.models.constants import PlaylistVisibility


class UploadedLinks(Base):
    __tablename__ = "uploaded_links"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    video_id = Column(String(11), nullable=False, index=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    channel_title = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    view_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    comment_count = Column(Integer, nullable=True)
    tags = Column(Text, nullable=True)
    source = Column(String, default="manual")
    last_watched_time = Column(Float, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    playlist_id = Column(Integer, ForeignKey("playlist.id"), nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    uploader = relationship("User", back_populates="uploaded_links")
    playlist = relationship("Playlist", back_populates="videos")

    def __repr__(self):
        return f"<UploadedLink(id={self.id}, video_id='{self.video_id}', user_id={self.user_id})>"


class Playlist(Base):
    __tablename__ = "playlist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    visibility = Column(Enum(PlaylistVisibility), default=PlaylistVisibility.PRIVATE)

    videos = relationship("UploadedLinks", back_populates="playlist")
    owner = relationship("User", back_populates="playlists")
