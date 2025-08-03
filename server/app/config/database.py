from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from typing import Annotated, AsyncGenerator

from dotenv import load_dotenv
import os

load_dotenv()

### Setting up the database
username = os.getenv("DATABASE_USERNAME")
password = os.getenv("DATABASE_PASSWORD")
db_name = os.getenv("DATABASE_NAME")

DB_URL= f"postgresql+asyncpg://{username}:{password}@localhost:5432/{db_name}"

engine = create_async_engine(DB_URL, echo=True)

async_session_local = sessionmaker(
    autoflush=False,
    bind=engine,
    autocommit=False, 
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        yield session

session_depends = Annotated[AsyncSession, Depends(get_db)]