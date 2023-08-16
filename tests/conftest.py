import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.models import Tweet, User, Base
from dependencies import get_session
from main import app

DATABASE_URL_TEST = "postgresql+asyncpg://admin:admin@localhost:5432/test"

engine_test = create_async_engine(DATABASE_URL_TEST, echo=True)


async_session_maker = sessionmaker(
    engine_test, expire_on_commit=False, class_=AsyncSession
)
Base.metadata.bind = engine_test


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def insert_data():
    async with async_session_maker() as session:
        await session.execute(
            insert(User).values(name="Oleg", password="test1", api_key="oleg")
        )
        await session.execute(
            insert(User).values(name="Serega", password="xxxxx", api_key="serega")
        )
        await session.execute(insert(Tweet).values(content="Hello", user_id=1))

        await session.commit()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
