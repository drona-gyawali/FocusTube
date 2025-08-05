from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.authentication.jwt.token import verify_token
from app.repository.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    token_data = verify_token(token)
    user = await repo.find_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user