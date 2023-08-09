from sqlalchemy import select, delete, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import BackendException
from db.models import followers, User
from dependencies import get_user_by_api_key


async def add_follow_to_user(
        session: AsyncSession, api_key: str, user_id: int
):
    following_user = await get_user_by_api_key(
        session=session, api_key=api_key
    )
    if following_user.id == user_id:
        raise BackendException(
            error_type="BAD FOLLOW", error_message="User can't follow himself"
        )

    q = await session.execute(select(User).where(User.id == user_id))
    user_followed = q.scalars().one_or_none()
    if not user_followed:
        raise BackendException(
            error_type="NO USER",
            error_message="No user with user_id to follow",
        )
    try:
        await session.execute(
            insert(followers).values(
                following_user_id=following_user.id,
                followed_user_id=user_id,
            )
        )
    except IntegrityError:
        raise BackendException(
            error_type="BAD FOLLOW", error_message="Such follow already exists"
        )
    await session.commit()


async def delete_follow_from_user(
        session: AsyncSession, api_key: str, user_id: int
):
    following_user = await get_user_by_api_key(
        session=session, api_key=api_key
    )
    q = await session.execute(
        select(followers).where(
            followers.c.following_user_id == following_user.id,
            followers.c.followed_user_id == user_id,
        )
    )
    follower = q.scalars().one_or_none()
    if not follower:
        raise BackendException(
            error_type="BAD FOLLOW DELETE", error_message="No such follow"
        )

    await session.execute(
        delete(followers).where(
            followers.c.following_user_id == following_user.id,
            followers.c.followed_user_id == user_id,
        )
    )
    await session.commit()


async def get_user_me(session: AsyncSession, api_key: str):
    user = await get_user_by_api_key(session=session, api_key=api_key)

    q = await session.execute(
        select(User)
        .options(selectinload(User.following))
        .options(selectinload(User.followers))
        .where(User.api_key == api_key)
    )

    user = q.scalars().one_or_none()

    return {"result": True, "user": user}


async def get_user(session: AsyncSession, user_id: int):
    q = await session.execute(
        select(User)
        .options(selectinload(User.following))
        .options(selectinload(User.followers))
        .where(User.id == user_id)
    )

    user = q.scalars().one_or_none()
    if not user:
        raise BackendException(
            error_type="NO USER", error_message="No user with such id"
        )

    return {"result": True, "user": user}


async def post_user(session: AsyncSession, user) -> User:
    new_user = User(**user.dict())
    async with session.begin():
        session.add(new_user)
        await session.commit()
    return new_user
