from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_logger
from app.models import UploadedLinks

logger = get_logger("[app/repository/video_link]")


class VideoLinkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_video_link(
        self,
        user_id: int,
        links: Optional[List[dict]],
        source: str,
    ) -> List[UploadedLinks]:
        """
        Insert UploadedLinks rows. All metadata fields are optional.
        Expect each entry in `links` to be a dict having at least 'url' and optionally many other keys.
        """

        now = datetime.utcnow().replace(tzinfo=None)
        created = []
        try:
            for data in links or []:
                new = UploadedLinks(
                    url=data.get("url"),
                    video_id=data.get("video_id"),
                    title=data.get("title"),
                    description=data.get("description"),
                    channel_title=data.get("channel_title"),
                    thumbnail_url=data.get("thumbnail_url"),
                    duration_seconds=data.get("duration_seconds"),
                    view_count=data.get("view_count"),
                    like_count=data.get("like_count"),
                    comment_count=data.get("comment_count"),
                    tags=data.get("tags"),
                    source=source,
                    user_id=user_id,
                    uploaded_at=now,
                )
                self.db.add(new)
                created.append(new)

            await self.db.commit()

            for item in created:
                await self.db.refresh(item)

            return created

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error("DB Error on link creation: %s", e)
            raise

        except Exception as e:
            await self.db.rollback()
            logger.error("Unexpected DB error: %s", e)
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

    async def delete_links(self, user_id: int, id: int) -> bool:
        """
        Delete the link with a specific ID belonging to the given user.
        """
        try:
            link = await self.db.get(UploadedLinks, id)

            if not link or link.user_id != user_id:
                return False

            await self.db.delete(link)
            await self.db.commit()
            return True

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"DB Error: (delete_links): {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error in delete_links: {e}")
            raise
