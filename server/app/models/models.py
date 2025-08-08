from datetime import datetime, timezone

from app.config import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class UploadedLinks(Base):
    __tablename__ = "uploaded_links"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    source = Column(String, default="manual")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    uploader = relationship("User", back_populates="uploaded_links")

    def __repr__(self):
        return f"<UploadedLink(id={self.id}, url='{self.url}', user_id={self.user_id})>"
