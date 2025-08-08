from datetime import datetime
from typing import List, Optional

from app.config import get_logger
from app.models import UploadedLinks
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("[app/repository/video_link]")


class VideoLinkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_video_link(
        self, user_id: int, links: Optional[List[str]]
    ) -> List[UploadedLinks]:
        now = datetime.utcnow().replace(tzinfo=None)
        created_links = []
        try:
            for link in links:
                new_link = UploadedLinks(
                    url=link,
                    source="manual",
                    user_id=user_id,
                    uploaded_at=now,
                )
                self.db.add(new_link)
                created_links.append(new_link)

            await self.db.commit()

            for link in created_links:
                await self.db.refresh(link)

            return created_links

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"DB Error on link creation: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error on link creation: {e}")
            raise
