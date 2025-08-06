import traceback
from datetime import datetime, timezone
from typing import List

from app.authentication.models import User
from app.config.logger import get_logger
from app.models.models import UploadedLinks
from app.utils import helper
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = get_logger("[app/repository/user]")


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, user_id: int) -> User | None:
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
        except Exception as e:
            logger.error(f"ERROR: {e}")
        return result.scalars().first()

    async def find_by_email(self, email: EmailStr) -> User | None:
        try:
            result = await self.db.execute(select(User).where(User.email == email))
        except Exception as e:
            logger.error(f"ERROR: {e}")
        return result.scalars().first()

    async def get_image_id(self, user_id: int):
        try:
            image_url = await self.db.scalar(
                select(User.profile_img).where(User.id == user_id)
            )

            if not image_url:
                return None

            return helper.extract_file_id(image_url)

        except Exception as e:
            logger.error(f"DB Error : {e.message}\n{traceback.format_exc()}")

    async def get_uploaded_links(self, user_id: int) -> List[UploadedLinks]:
        try:
            result = await self.db.execute(
                select(UploadedLinks).where(UploadedLinks.user_id == user_id)
            )
        except Exception as e:
            logger.error(f"ERROR: {e}")
        return result.scalars().all()

    async def create_user(self, email: EmailStr, password: str) -> User:
        hashed_password = pwd_context.hash(password)
        now = datetime.utcnow().replace(tzinfo=None)

        try:
            new_user = User(
                email=email,
                password=hashed_password,
                is_oauth=False,
                profile_img="",
                created_at=now,
                updated_at=now,
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"DB Error on user creation: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error on user creation: {e}")
            raise

    async def profile_details(self, user_id: int) -> User | None:
        try:
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.uploaded_links))
                .where(User.id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"ERROR fetching profile details: {e}")
            return None

    async def update_profile_image(self, user_id: int, image_url: str) -> User | None:
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if not user:
                logger.error(
                    f"User with id {user_id} not found for profile image update."
                )
                return None
            user.profile_img = image_url
            user.updated_at = datetime.utcnow().replace(tzinfo=None)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"DB Error on profile image update: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error on profile image update: {e}")
            return None

    def verify_password(self, plain_password: str, hashed_password: str | None) -> bool:
        if not hashed_password:
            return False
        return pwd_context.verify(plain_password, hashed_password)
