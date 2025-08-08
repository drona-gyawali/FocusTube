from datetime import datetime
from typing import List, Optional

from app.config import get_logger
from app.models import UploadedLinks
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("[app/repository/video_link]")


class VideoLinkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_video_link(
        self, user_id: int, links: Optional[List[str]], source: str
    ) -> List[UploadedLinks]:
        now = datetime.utcnow().replace(tzinfo=None)
        created_links = []
        try:
            for link in links:
                new_link = UploadedLinks(
                    url=link,
                    source=source,
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

    async def get_existing_links(
        self,
        user_id: int,
        links: Optional[List[str]],
    ) -> List[str]:
        """
        Returns a list of URLs that already exist in DB for the given user.
        """
        if not links:
            return []

        try:
            query = select(UploadedLinks.url).where(
                UploadedLinks.user_id == user_id, UploadedLinks.url.in_(links)
            )

            result = await self.db.execute(query)
            existing_links = [row[0] for row in result.all()]
            return existing_links

        except Exception as e:
            logger.error(f"DB Error: (get_existing_links): {e}")
            raise

    async def get_all_links(self, user_id: int) -> List[UploadedLinks]:
        """
        Return all the links related to the user
        """
        try:
            query = select(UploadedLinks).where(UploadedLinks.user_id == user_id)
            result = await self.db.execute(query)
            all_links = result.scalars().all()
            return all_links
        except Exception as e:
            logger.error(f"DB Error: (get_all_links): {e}")
            raise
