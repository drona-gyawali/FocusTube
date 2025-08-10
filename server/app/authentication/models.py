from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.config.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_oauth = Column(Boolean, default=False)
    profile_img = Column(String, default="profile/something")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    uploaded_links = relationship(
        "UploadedLinks", back_populates="uploader", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
