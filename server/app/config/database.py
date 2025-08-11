import os
from typing import Annotated, AsyncGenerator

from app.config import conf
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DB_URL = f"postgresql+asyncpg://{conf.username}:{conf.password}@localhost:5432/{conf.db_name}"

engine = create_async_engine(DB_URL, echo=True)

async_session_local = sessionmaker(
    autoflush=False,
    class_=AsyncSession,
    bind=engine,
    autocommit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        yield session


session_depends = Annotated[AsyncSession, Depends(get_db)]
