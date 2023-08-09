from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import async_session
from core.exceptions import BackendException
from db.models import User


async def get_session():
    async with async_session() as session:
        yield session


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> User:
    user = await session.execute(select(User).where(User.api_key == api_key))
    user = user.scalars().one_or_none()

    if not user:
        raise BackendException(
            error_type="NO USER", error_message="No user with such api-key"
        )

    return user
