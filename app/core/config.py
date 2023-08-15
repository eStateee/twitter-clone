from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path


# CONSTANTS
MEDIA_PATH = "/static/media_files/"
OUT_PATH = Path(__file__).parent.parent / "media_files"
OUT_PATH = OUT_PATH.absolute()

DATABASE_URL = "postgresql+asyncpg://admin:admin@db:5432/twitter_clone"
engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()
