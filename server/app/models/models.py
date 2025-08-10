from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.config import Base


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
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    uploader = relationship("User", back_populates="uploaded_links")

    def __repr__(self):
        return f"<UploadedLink(id={self.id}, video_id='{self.video_id}', user_id={self.user_id})>"
